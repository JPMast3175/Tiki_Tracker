"""Tiki Tracker — launch entry point."""

import flet as ft
from tiki_tracker.app import main


def run() -> None:
    ft.app(target=main)


if __name__ == "__main__":
    run()
