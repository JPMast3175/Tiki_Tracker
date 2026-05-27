#!/usr/bin/env python3
"""
Generate the Tiki Tracker app icon and macOS .app launcher bundle.

Run once:  python build_icon.py
"""

import math
import shutil
import subprocess
import stat
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

# ── Constants ──────────────────────────────────────────────────────────────────
SIZE   = 1024
HALF   = SIZE // 2
OUT    = Path(__file__).parent
PROJ   = OUT

# ── Palette (matches theme.py) ─────────────────────────────────────────────────
C_BG_TOP    = ( 10,  40,  10)   # dark forest green
C_BG_BOT    = ( 18,  13,   7)   # deep espresso
C_GLOW      = ( 30,  90,  30)   # radial centre glow
C_GOLD      = (201, 162,  39)
C_GOLD_D    = (130,  96,  18)
C_MUG       = (158, 102,  36)   # bamboo body
C_MUG_LT    = (205, 148,  62)   # highlight
C_MUG_DK    = ( 82,  50,  12)   # shadow/ring
C_CARVE     = ( 48,  26,   5)   # deep carved recesses
C_DRINK     = (185,  48,  18)   # tropical red
C_FOAM      = (235, 215, 165)   # cream
C_STRAW_W   = (240, 238, 228)
C_STRAW_R   = (208,  55,  45)
C_UMB_R     = (210,  55,  30)
C_UMB_G     = ( 28, 115,  45)
C_UMB_Y     = (210, 165,  30)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ── Background ─────────────────────────────────────────────────────────────────
def make_bg() -> Image.Image:
    """Vertical gradient squircle background."""
    grad = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    px   = grad.load()
    for y in range(SIZE):
        t = y / SIZE
        c = lerp(C_BG_TOP, C_BG_BOT, t) + (255,)
        for x in range(SIZE):
            px[x, y] = c

    # Squircle mask
    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, SIZE - 1, SIZE - 1], radius=int(SIZE * 0.19), fill=255
    )
    grad.putalpha(mask)

    # Centre radial glow via Gaussian blur
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse(
        [HALF - 320, HALF - 320, HALF + 320, HALF + 320],
        fill=C_GLOW + (160,),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    return Image.alpha_composite(grad, glow)


# ── Tiki mug ───────────────────────────────────────────────────────────────────
def draw_mug(img: Image.Image) -> ImageDraw.ImageDraw:
    """Draw the tiki mug body and return an up-to-date ImageDraw handle."""
    # ── Shadow layer ───────────────────────────────────────────────────────
    sh_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sh_d     = ImageDraw.Draw(sh_layer)

    MX   = 498          # mug centre-x (slightly left of canvas centre)
    TY   = 195          # top y
    BY   = 828          # bottom y
    TW2  = 188          # half-width at top
    BW2  = 152          # half-width at bottom
    OFF  = 16           # shadow offset

    def mug_pts(ox=0, oy=0):
        return [
            (MX - TW2 + ox, TY + oy),
            (MX + TW2 + ox, TY + oy),
            (MX + BW2 + ox, BY + oy),
            (MX - BW2 + ox, BY + oy),
        ]

    sh_d.polygon(mug_pts(OFF, OFF), fill=(0, 0, 0, 110))
    sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(22))
    img      = Image.alpha_composite(img, sh_layer)
    draw     = ImageDraw.Draw(img)

    # ── Mug body ────────────────────────────────────────────────────────────
    draw.polygon(mug_pts(), fill=C_MUG)

    # ── Edge shading via composited overlay layers ──────────────────────────
    edge_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge_layer)
    for i in range(42):
        t     = i / 42
        alpha = int(150 * (1 - t * t))
        x     = MX - TW2 + i
        ed.line([(x, TY + 4), (x, BY - 4)], fill=(0, 0, 0, alpha), width=1)
    for i in range(26):
        t     = i / 26
        alpha = int(110 * (1 - t * t))
        x     = MX + TW2 - i
        ed.line([(x, TY + 4), (x, BY - 4)], fill=(240, 230, 180, alpha), width=1)
    img = Image.alpha_composite(img, edge_layer)
    draw = ImageDraw.Draw(img)

    # ── Bamboo ring bands (positioned to avoid face features) ───────────────
    ring_ys = [300, 548, 660, 760]
    for ry in ring_ys:
        t  = (ry - TY) / (BY - TY)
        hw = int(TW2 + (BW2 - TW2) * t)
        draw.rectangle([MX - hw, ry,      MX + hw, ry + 20], fill=C_MUG_DK)
        draw.rectangle([MX - hw, ry + 20, MX + hw, ry + 26], fill=C_MUG_LT)

    # ── Tiki face ───────────────────────────────────────────────────────────
    FCX = MX

    # — forehead chevron —
    fy = 295
    draw.polygon(
        [(FCX, fy - 32), (FCX - 40, fy), (FCX - 24, fy),
         (FCX, fy - 12), (FCX + 24, fy), (FCX + 40, fy)],
        fill=C_CARVE,
    )

    # — eyebrow ridges —
    for sign in (-1, 1):
        bx = FCX + sign * 82
        draw.polygon(
            [(bx - 55, 338), (bx + 55, 338), (bx + 42, 360), (bx - 42, 360)],
            fill=C_CARVE,
        )

    # — eyes (almond) —
    eye_y = 400
    for sign in (-1, 1):
        ex = FCX + sign * 82
        # Socket
        draw.ellipse([ex - 42, eye_y - 32, ex + 42, eye_y + 32], fill=C_CARVE)
        # Iris/sclera
        draw.ellipse([ex - 34, eye_y - 24, ex + 34, eye_y + 24], fill=C_MUG_LT)
        # Pupil
        draw.ellipse([ex - 16, eye_y - 20, ex + 16, eye_y + 20], fill=C_CARVE)
        # Pupil highlight
        draw.ellipse([ex - 5, eye_y - 16, ex + 2, eye_y - 10], fill=(255, 250, 230, 200))

    # — nose bridge —
    draw.polygon(
        [(FCX - 22, 450), (FCX + 22, 450),
         (FCX + 48, 526), (FCX - 48, 526)],
        fill=C_CARVE,
    )
    # nostrils
    draw.ellipse([FCX - 44, 494, FCX - 18, 524], fill=(24, 10, 2))
    draw.ellipse([FCX + 18, 494, FCX + 44, 524], fill=(24, 10, 2))

    # — mouth grimace —
    mouth_y = 596
    mw      = 140
    mh      = 68
    # Outer carved cavity
    draw.ellipse([FCX - mw, mouth_y - mh // 2,
                  FCX + mw, mouth_y + mh], fill=C_CARVE)
    # Upper lip cover (restores mug colour above mouth line)
    draw.rectangle([FCX - mw - 6, mouth_y - mh // 2 - 6,
                    FCX + mw + 6, mouth_y + 2], fill=C_MUG)
    # Top corners re-carved (downturned grimace)
    for sign in (-1, 1):
        cx_ = FCX + sign * (mw - 22)
        draw.ellipse([cx_ - 24, mouth_y - 32, cx_ + 24, mouth_y + 16], fill=C_CARVE)

    # Teeth (7 alternating)
    tw = 28
    for i in range(7):
        tx   = FCX - 3 * tw - tw // 2 + i * tw + 3
        fill = C_FOAM if i % 2 == 0 else C_CARVE
        draw.rectangle([tx, mouth_y + 3, tx + tw - 6, mouth_y + 44], fill=fill)
    # Redraw bottom arc lip
    draw.arc([FCX - mw, mouth_y - mh // 2,
              FCX + mw, mouth_y + mh], start=0, end=180, fill=C_MUG_DK, width=5)

    # ── Gold rim (top band) ─────────────────────────────────────────────────
    rim_h = 36
    t_rim = (TY - TY) / (BY - TY)   # = 0, top of mug
    draw.rectangle([MX - TW2, TY, MX + TW2, TY + rim_h], fill=C_GOLD)
    draw.rectangle([MX - TW2, TY, MX + TW2, TY + 6],     fill=C_MUG_LT)
    draw.rectangle([MX - TW2, TY + rim_h - 5, MX + TW2, TY + rim_h], fill=C_GOLD_D)

    # ── Drink visible at the top ────────────────────────────────────────────
    draw.ellipse([MX - TW2 + 8, TY - 14, MX + TW2 - 8, TY + 26], fill=C_DRINK)
    # Foam bubbles
    for bx, by, br in [
        (MX - 90, TY + 4, 18), (MX - 45, TY - 10, 22), (MX, TY + 6, 16),
        (MX + 50, TY - 8, 20), (MX + 95, TY + 5, 17),
    ]:
        draw.ellipse([bx - br, by - br, bx + br, by + br], fill=C_FOAM)

    # Re-draw gold rim over the foam that bled over it
    draw.rectangle([MX - TW2, TY, MX + TW2, TY + rim_h], outline=C_GOLD_D, width=3)

    # ── Gold bottom band ────────────────────────────────────────────────────
    bot_h = 24
    draw.rectangle([MX - BW2, BY - bot_h, MX + BW2, BY], fill=C_GOLD)
    draw.rectangle([MX - BW2, BY - bot_h, MX + BW2, BY - bot_h + 4], fill=C_MUG_LT)

    # ── Mug outline ─────────────────────────────────────────────────────────
    draw.polygon(mug_pts(), outline=C_MUG_DK, width=5)

    # ── Handle ──────────────────────────────────────────────────────────────
    hx1 = MX + TW2 - 6
    hy1, hy2 = 430, 640
    hw  = 96
    draw.arc([hx1, hy1, hx1 + hw, hy2], start=270, end=90, fill=C_MUG_DK, width=36)
    draw.arc([hx1, hy1, hx1 + hw, hy2], start=270, end=90, fill=C_MUG,    width=24)
    draw.arc([hx1, hy1, hx1 + hw, hy2], start=270, end=90, fill=C_MUG_LT, width=8)

    return img


# ── Cocktail umbrella ──────────────────────────────────────────────────────────
def draw_umbrella(img: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(img)

    # Straw (angled up-right from drink surface)
    sx1, sy1 = 556, 188
    sx2, sy2 = 660, 40
    for i in range(5):
        t1 = i / 5
        t2 = t1 + 0.18
        ax = int(sx1 + (sx2 - sx1) * t1)
        ay = int(sy1 + (sy2 - sy1) * t1)
        bx = int(sx1 + (sx2 - sx1) * min(t2, 1))
        by = int(sy1 + (sy2 - sy1) * min(t2, 1))
        c  = C_STRAW_R if i % 2 == 0 else C_STRAW_W
        draw.line([(ax, ay), (bx, by)], fill=c, width=12)

    # Umbrella canopy centred at top of straw
    ucx, ucy = sx2, sy2 - 8
    ur       = 88
    segments = [
        (C_UMB_R, 185, 245),
        (C_UMB_Y, 245, 305),
        (C_UMB_G, 305, 360),
        (C_UMB_R, 0,   60),
        (C_UMB_Y, 60,  120),
        (C_UMB_G, 120, 180),
    ]
    for col, a0, a1 in segments:
        draw.pieslice(
            [ucx - ur, ucy - ur // 2, ucx + ur, ucy + ur // 2],
            start=a0, end=a1, fill=col,
        )
    draw.arc(
        [ucx - ur, ucy - ur // 2, ucx + ur, ucy + ur // 2],
        start=180, end=360, fill=C_MUG_DK, width=4,
    )
    # Centre knob
    draw.ellipse([ucx - 8, ucy - 6, ucx + 8, ucy + 6], fill=C_STRAW_W)
    # Pole below canopy
    draw.line([(ucx, ucy + 4), (sx1, sy1)], fill=C_STRAW_W, width=6)

    return img


# ── Assemble ───────────────────────────────────────────────────────────────────
def build_1024() -> Image.Image:
    img = make_bg()
    img = draw_mug(img)
    img = draw_umbrella(img)
    return img


# ── ICNS helper ────────────────────────────────────────────────────────────────
ICNS_SIZES = {
    "icon_16x16.png":      16,
    "icon_16x16@2x.png":   32,
    "icon_32x32.png":      32,
    "icon_32x32@2x.png":   64,
    "icon_128x128.png":   128,
    "icon_128x128@2x.png":256,
    "icon_256x256.png":   256,
    "icon_256x256@2x.png":512,
    "icon_512x512.png":   512,
    "icon_512x512@2x.png":1024,
}


def build_icns(master: Image.Image, dest: Path) -> Path:
    iconset = dest / "AppIcon.iconset"
    iconset.mkdir(parents=True, exist_ok=True)

    for fname, sz in ICNS_SIZES.items():
        resized = master.resize((sz, sz), Image.LANCZOS)
        resized.save(iconset / fname, "PNG")

    icns_path = dest / "AppIcon.icns"
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(icns_path)],
        check=True,
    )
    shutil.rmtree(iconset)
    print(f"  ICNS → {icns_path}")
    return icns_path


# ── macOS .app bundle ──────────────────────────────────────────────────────────
INFO_PLIST = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>      <string>TikiTracker</string>
  <key>CFBundleIconFile</key>        <string>AppIcon</string>
  <key>CFBundleIdentifier</key>      <string>com.josephmast.tikitracker</string>
  <key>CFBundleName</key>            <string>Tiki Tracker</string>
  <key>CFBundleDisplayName</key>     <string>Tiki Tracker</string>
  <key>CFBundlePackageType</key>     <string>APPL</string>
  <key>CFBundleShortVersionString</key> <string>1.0</string>
  <key>CFBundleVersion</key>         <string>1</string>
  <key>LSMinimumSystemVersion</key>  <string>12.0</string>
  <key>NSHighResolutionCapable</key> <true/>
  <key>LSUIElement</key>             <false/>
</dict>
</plist>
"""

LAUNCHER_SH = """\
#!/bin/bash
# Tiki Tracker launcher
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ="{proj_path}"
cd "$PROJ"
source "$PROJ/venv/bin/activate"
exec python "$PROJ/run.py"
"""


def build_app(icns_path: Path, proj_path: Path) -> Path:
    app = proj_path / "TikiTracker.app"
    macos_dir     = app / "Contents" / "MacOS"
    resources_dir = app / "Contents" / "Resources"

    for d in (macos_dir, resources_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Info.plist
    (app / "Contents" / "Info.plist").write_text(INFO_PLIST)

    # Shell launcher
    launcher = macos_dir / "TikiTracker"
    launcher.write_text(LAUNCHER_SH.format(proj_path=proj_path))
    launcher.chmod(
        launcher.stat().st_mode
        | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )

    # Icon
    shutil.copy2(icns_path, resources_dir / "AppIcon.icns")

    # Ad-hoc codesign + clear quarantine so double-click works on macOS
    subprocess.run(["xattr", "-cr", str(app)], check=False)
    subprocess.run(
        ["codesign", "--deep", "--force", "--sign", "-", str(app)],
        check=False,
    )
    print(f"  .app  → {app}")
    return app


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Building Tiki Tracker icon…")
    master = build_1024()

    # Save full-size PNG (used by Flet as window icon too)
    png_path = OUT / "data" / "tiki_tracker_icon.png"
    png_path.parent.mkdir(parents=True, exist_ok=True)
    master.save(png_path, "PNG")
    print(f"  PNG  → {png_path}")

    # Build ICNS
    icns = build_icns(master, OUT / "data")

    # Build .app bundle
    build_app(icns, PROJ)

    print("\nDone!  Double-click TikiTracker.app to launch.")
