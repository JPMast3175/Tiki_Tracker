"""QR code generation for recipe sharing (JSON payload)."""

import io
import json
import tempfile
from pathlib import Path

try:
    import qrcode
    from qrcode.image.pil import PilImage
    _QR_AVAILABLE = True
except ImportError:
    _QR_AVAILABLE = False

from tiki_tracker.models.recipe import Recipe


class QRService:
    def is_available(self) -> bool:
        return _QR_AVAILABLE

    def generate_recipe_qr(self, recipe: Recipe, output_path: Path | None = None) -> Path | None:
        """
        Encode the recipe as a compact JSON payload and write a QR PNG.
        Returns the path to the PNG, or None if qrcode is unavailable.
        """
        if not _QR_AVAILABLE:
            return None

        payload = json.dumps(recipe.to_dict(), separators=(",", ":"), ensure_ascii=False)

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=2,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1A4A1A", back_color="white")

        if output_path is None:
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            output_path = Path(tmp.name)
            tmp.close()

        img.save(str(output_path))
        return output_path

    def decode_recipe_json(self, json_str: str) -> dict | None:
        """
        Parse a recipe JSON string (from a scanned QR code).
        # TODO: wire up camera-based QR scanning once a cross-platform
        #       scanner library is available (e.g., zxing-cpp Python bindings).
        """
        try:
            data = json.loads(json_str)
            return data if isinstance(data, dict) else None
        except (json.JSONDecodeError, TypeError):
            return None
