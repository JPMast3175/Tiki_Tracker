"""Image service — fetch, cache, and manage recipe drink images."""

import logging
import shutil
import threading
import urllib.request
import urllib.parse
import json
from pathlib import Path

log = logging.getLogger("tiki_tracker.image_service")

_COCKTAILDB_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php?s={}"
_HEADERS = {"User-Agent": "TikiTracker/1.0"}


class ImageService:
    def __init__(self, data_dir: Path, recipe_service) -> None:
        self._img_dir = data_dir / "images"
        self._img_dir.mkdir(parents=True, exist_ok=True)
        self._recipe_service = recipe_service
        self._lock = threading.Lock()

    # ── Public API ────────────────────────────────────────────────────────

    def get_image_path(self, recipe_id: int) -> Path | None:
        """Return local image Path if it exists, else None."""
        for ext in ("jpg", "jpeg", "png", "webp"):
            p = self._img_dir / f"recipe_{recipe_id}.{ext}"
            if p.exists():
                return p
        return None

    def get_image_src(self, recipe_id: int) -> str | None:
        """Return Flet asset src string (e.g. /images/recipe_1.jpg) or None."""
        p = self.get_image_path(recipe_id)
        return f"/images/{p.name}" if p else None

    def save_from_file(self, recipe_id: int, src_path: str) -> bool:
        """Copy a user-chosen local file into the images cache."""
        src = Path(src_path)
        if not src.exists():
            log.warning("save_from_file: source not found: %s", src_path)
            return False
        suffix = src.suffix.lower() or ".jpg"
        dest = self._img_dir / f"recipe_{recipe_id}{suffix}"
        try:
            self._clear_existing(recipe_id)
            shutil.copy2(src, dest)
            log.info("Saved local image for recipe %d -> %s", recipe_id, dest.name)
            return True
        except Exception:
            log.exception("save_from_file failed for recipe %d", recipe_id)
            return False

    def save_from_url(self, recipe_id: int, url: str) -> bool:
        """Download an image from a URL and store it in the cache."""
        try:
            suffix = self._ext_from_url(url)
            dest = self._img_dir / f"recipe_{recipe_id}{suffix}"
            self._clear_existing(recipe_id)
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            dest.write_bytes(data)
            log.info("Downloaded image for recipe %d -> %s (%d bytes)",
                     recipe_id, dest.name, len(data))
            return True
        except Exception:
            log.exception("save_from_url failed for recipe %d (url=%s)", recipe_id, url)
            return False

    def fetch_all_seed_images(self, on_progress=None) -> None:
        """Background thread — fetch CocktailDB images for all recipes missing one."""
        def _run():
            recipes = self._recipe_service.get_all()
            for recipe in recipes:
                if self.get_image_path(recipe.id) is not None:
                    continue
                url = self._lookup_cocktaildb(recipe.name)
                if url:
                    ok = self.save_from_url(recipe.id, url)
                    if ok and on_progress:
                        on_progress(recipe.id)
                else:
                    log.debug("No CocktailDB image for %r", recipe.name)

        t = threading.Thread(target=_run, daemon=True, name="img-fetch")
        t.start()

    def fetch_for_recipe(self, recipe_id: int, recipe_name: str,
                         on_done=None) -> None:
        """Background fetch for a single recipe (used after add/edit)."""
        def _run():
            if self.get_image_path(recipe_id) is not None:
                return
            url = self._lookup_cocktaildb(recipe_name)
            if url:
                ok = self.save_from_url(recipe_id, url)
                if ok and on_done:
                    on_done(recipe_id)

        t = threading.Thread(target=_run, daemon=True, name=f"img-fetch-{recipe_id}")
        t.start()

    # ── Internals ─────────────────────────────────────────────────────────

    def _clear_existing(self, recipe_id: int) -> None:
        for ext in ("jpg", "jpeg", "png", "webp"):
            p = self._img_dir / f"recipe_{recipe_id}.{ext}"
            if p.exists():
                p.unlink()

    @staticmethod
    def _ext_from_url(url: str) -> str:
        path = urllib.parse.urlparse(url).path
        suffix = Path(path).suffix.lower()
        return suffix if suffix in (".jpg", ".jpeg", ".png", ".webp") else ".jpg"

    @staticmethod
    def _lookup_cocktaildb(name: str) -> str | None:
        """Query TheCocktailDB for the first matching drink image URL."""
        try:
            encoded = urllib.parse.quote(name)
            url = _COCKTAILDB_URL.format(encoded)
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            drinks = data.get("drinks") or []
            if drinks:
                return drinks[0].get("strDrinkThumb")
        except Exception:
            log.debug("CocktailDB lookup failed for %r", name)
        return None
