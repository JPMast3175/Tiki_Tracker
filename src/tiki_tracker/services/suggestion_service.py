"""Drink-of-the-day logic — stable per calendar date, inventory-aware."""

import hashlib
from datetime import date

from tiki_tracker.models.recipe import Recipe
from tiki_tracker.services.recipe_service import RecipeService
from tiki_tracker.services.inventory_service import InventoryService


class SuggestionService:
    def __init__(self, recipe_service: RecipeService, inventory_service: InventoryService) -> None:
        self.recipe_service = recipe_service
        self.inventory_service = inventory_service

    def get_drink_of_the_day(self) -> Recipe | None:
        # Prefer recipes that can be made with current inventory
        candidates = self.recipe_service.get_makeable()
        if not candidates:
            candidates = self.recipe_service.get_all()
        if not candidates:
            return None

        # Deterministic daily selection using date hash
        today_str = date.today().isoformat()
        digest = int(hashlib.sha256(today_str.encode()).hexdigest(), 16)
        pick = candidates[digest % len(candidates)]
        return self.recipe_service.get_by_id(pick.id)
