"""Tiki Tracker — launch entry point."""

from pathlib import Path

import flet as ft
from tiki_tracker.app import main

_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


def run() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    ft.app(target=main, assets_dir=str(_DATA_DIR))


if __name__ == "__main__":
    run()
