"""Seed the database with classic tiki ingredients and recipes.

Runs only when the recipes table is empty; safe to call on every startup.
"""

from tiki_tracker.db.database import Database


# ── Ingredients ────────────────────────────────────────────────────────────

INGREDIENTS: list[tuple[str, str]] = [
    # (name, category)
    # Rum
    ("White Rum", "Rum"),
    ("Light Rum", "Rum"),
    ("Gold Rum", "Rum"),
    ("Aged Rum", "Rum"),
    ("Dark Rum", "Rum"),
    ("Jamaican Rum", "Rum"),
    ("Demerara Rum", "Rum"),
    ("Blackstrap Rum", "Rum"),
    ("151-Proof Rum", "Rum"),
    ("Overproof Rum", "Rum"),
    ("Pusser's Rum", "Rum"),
    # Spirits
    ("Brandy", "Spirits"),
    ("Gin", "Spirits"),
    ("Vodka", "Spirits"),
    ("Tequila", "Spirits"),
    # Liqueurs
    ("Blue Curaçao", "Liqueurs"),
    ("Orange Curaçao", "Liqueurs"),
    ("Campari", "Liqueurs"),
    ("Sweet Sherry", "Liqueurs"),
    ("Pernod", "Liqueurs"),
    ("Triple Sec", "Liqueurs"),
    # Citrus & Juices
    ("Fresh Lime Juice", "Citrus"),
    ("Fresh Lemon Juice", "Citrus"),
    ("Fresh Orange Juice", "Citrus"),
    ("Fresh Grapefruit Juice", "Citrus"),
    ("Pineapple Juice", "Juices"),
    ("Coconut Cream", "Juices"),
    ("Cream of Coconut", "Juices"),
    # Syrups
    ("Simple Syrup", "Syrups"),
    ("Orgeat", "Syrups"),
    ("Falernum", "Syrups"),
    ("Grenadine", "Syrups"),
    ("Cinnamon Syrup", "Syrups"),
    ("Honey Syrup", "Syrups"),
    ("Donn's Mix", "Syrups"),
    # Bitters
    ("Angostura Bitters", "Bitters"),
    ("Peychaud's Bitters", "Bitters"),
    # Mixers
    ("Club Soda", "Mixers"),
    ("Tonic Water", "Mixers"),
    # Garnishes
    ("Fresh Mint", "Garnishes"),
    ("Lime Wheel", "Garnishes"),
    ("Orange Slice", "Garnishes"),
    ("Pineapple Slice", "Garnishes"),
    ("Maraschino Cherry", "Garnishes"),
    ("Nutmeg (freshly grated)", "Garnishes"),
    ("Gardenia", "Garnishes"),
    ("Cinnamon Stick", "Garnishes"),
]

# ── Recipes ────────────────────────────────────────────────────────────────
# Format: (name, description, instructions, garnish, glassware, difficulty, prep_time, tags, ingredients)
# ingredients: list of (ingredient_name, amount, unit, notes, sort_order)

RECIPES: list[dict] = [
    {
        "name": "Mai Tai",
        "description": (
            "Trader Vic's 1944 masterpiece. The name means 'out of this world' in Tahitian — "
            "and one sip explains why. Balanced, nuanced, and thoroughly tropical."
        ),
        "instructions": (
            "1. Combine rum, curaçao, lime juice, orgeat, and simple syrup in a shaker with ice.\n"
            "2. Shake well until chilled.\n"
            "3. Strain over fresh crushed ice into a double old fashioned glass.\n"
            "4. Garnish with a mint sprig, lime shell, and a cherry."
        ),
        "garnish": "Mint sprig, lime shell, maraschino cherry",
        "glassware": "Double Old Fashioned",
        "difficulty": 2,
        "prep_time": 10,
        "tags": '["Classic", "Shaken", "Citrus", "Trader Vic\'s"]',
        "ingredients": [
            ("Aged Rum", "2", "oz", "Jamaican preferred", 0),
            ("Orange Curaçao", "3/4", "oz", "", 1),
            ("Fresh Lime Juice", "3/4", "oz", "freshly squeezed", 2),
            ("Orgeat", "1/2", "oz", "", 3),
            ("Simple Syrup", "1/4", "oz", "rock candy syrup preferred", 4),
            ("Fresh Mint", "1", "sprig", "for garnish", 5),
            ("Lime Wheel", "1", "piece", "for garnish", 6),
            ("Maraschino Cherry", "1", "piece", "for garnish", 7),
        ],
    },
    {
        "name": "Zombie",
        "description": (
            "Don the Beachcomber's legendary 1934 creation. So potent it was limited to two per customer. "
            "Complex, citrusy, and dangerously drinkable — approach with respect."
        ),
        "instructions": (
            "1. Combine all ingredients except the 151-proof rum in a shaker with ice.\n"
            "2. Shake well.\n"
            "3. Strain into a zombie glass or tall glass over crushed ice.\n"
            "4. Float 151-proof rum on top.\n"
            "5. Garnish with a mint sprig and cherry. Limit 2 per customer."
        ),
        "garnish": "Mint sprig, maraschino cherry",
        "glassware": "Zombie Glass",
        "difficulty": 4,
        "prep_time": 15,
        "tags": '["Classic", "Shaken", "Strong", "Don the Beachcomber"]',
        "ingredients": [
            ("Light Rum", "1 1/2", "oz", "Puerto Rican preferred", 0),
            ("Jamaican Rum", "1 1/2", "oz", "dark", 1),
            ("Demerara Rum", "1", "oz", "El Dorado 151", 2),
            ("Fresh Lime Juice", "3/4", "oz", "", 3),
            ("Falernum", "1/2", "oz", "", 4),
            ("Donn's Mix", "1/2", "oz", "1:1 grapefruit juice & cinnamon syrup", 5),
            ("Grenadine", "1/2", "oz", "", 6),
            ("Angostura Bitters", "1", "dash", "", 7),
            ("Pernod", "6", "drops", "", 8),
            ("151-Proof Rum", "1", "oz", "float on top", 9),
            ("Fresh Mint", "1", "sprig", "garnish", 10),
            ("Maraschino Cherry", "1", "piece", "garnish", 11),
        ],
    },
    {
        "name": "Navy Grog",
        "description": (
            "Don the Beachcomber's 1941 tribute to the British Royal Navy. "
            "Three rums, citrus, and honey create a well-structured, sailor-worthy drink."
        ),
        "instructions": (
            "1. Combine all ingredients in a shaker with ice.\n"
            "2. Shake well until chilled.\n"
            "3. Pour into a double old fashioned glass over a large ice cone or crushed ice.\n"
            "4. Garnish with a lime wheel."
        ),
        "garnish": "Lime wheel",
        "glassware": "Double Old Fashioned",
        "difficulty": 3,
        "prep_time": 12,
        "tags": '["Classic", "Shaken", "Don the Beachcomber", "Rum"]',
        "ingredients": [
            ("White Rum", "1", "oz", "", 0),
            ("Demerara Rum", "1", "oz", "", 1),
            ("Jamaican Rum", "1", "oz", "dark", 2),
            ("Fresh Lime Juice", "3/4", "oz", "", 3),
            ("Fresh Grapefruit Juice", "3/4", "oz", "", 4),
            ("Honey Syrup", "3/4", "oz", "2:1 honey to water", 5),
            ("Club Soda", "3/4", "oz", "top", 6),
            ("Lime Wheel", "1", "piece", "garnish", 7),
        ],
    },
    {
        "name": "Painkiller",
        "description": (
            "Born at the Soggy Dollar Bar on Jost Van Dyke, BVI, circa 1971. "
            "Creamy, fruity, and coconut-forward with a mandatory nutmeg crown."
        ),
        "instructions": (
            "1. Combine rum, pineapple juice, orange juice, and cream of coconut in a shaker with ice.\n"
            "2. Shake vigorously (cream of coconut needs energy).\n"
            "3. Pour over ice in a hurricane glass.\n"
            "4. Grate fresh nutmeg generously over the top. Do not skip the nutmeg."
        ),
        "garnish": "Freshly grated nutmeg, pineapple slice",
        "glassware": "Hurricane",
        "difficulty": 1,
        "prep_time": 8,
        "tags": '["Classic", "Shaken", "Tropical", "Beginner Friendly"]',
        "ingredients": [
            ("Pusser's Rum", "2", "oz", "or any aged rum", 0),
            ("Pineapple Juice", "4", "oz", "", 1),
            ("Fresh Orange Juice", "1", "oz", "", 2),
            ("Cream of Coconut", "1", "oz", "Coco López", 3),
            ("Nutmeg (freshly grated)", "1", "pinch", "generous — do not skip", 4),
            ("Pineapple Slice", "1", "piece", "garnish", 5),
        ],
    },
    {
        "name": "Scorpion",
        "description": (
            "Trader Vic's communal bowl cocktail from the 1950s. "
            "Citrusy, brandy-kissed, and built for sharing — though perfectly fine solo."
        ),
        "instructions": (
            "1. Combine rum, brandy, orange juice, lemon juice, and orgeat in a blender with ice.\n"
            "2. Blend until smooth.\n"
            "3. Pour into a scorpion bowl or individual glasses.\n"
            "4. Garnish with a gardenia, citrus wheels, and colorful straws."
        ),
        "garnish": "Gardenia, citrus wheels, long straws",
        "glassware": "Scorpion Bowl (shared) or Tiki Mug",
        "difficulty": 2,
        "prep_time": 10,
        "tags": '["Classic", "Blended", "Shared", "Trader Vic\'s", "Citrus"]',
        "ingredients": [
            ("Light Rum", "2", "oz", "", 0),
            ("Brandy", "1", "oz", "", 1),
            ("Fresh Orange Juice", "2", "oz", "", 2),
            ("Fresh Lemon Juice", "1", "oz", "", 3),
            ("Orgeat", "1/2", "oz", "", 4),
            ("Gardenia", "1", "piece", "garnish", 5),
            ("Orange Slice", "1", "piece", "garnish", 6),
        ],
    },
    {
        "name": "Fog Cutter",
        "description": (
            "Trader Vic's 1947 multi-spirit behemoth. Rum, gin, and brandy share the stage "
            "with citrus and a float of sherry. Complex, refreshing, and surprisingly approachable."
        ),
        "instructions": (
            "1. Combine rum, brandy, gin, orange juice, lemon juice, and orgeat in a shaker with ice.\n"
            "2. Shake well.\n"
            "3. Pour over crushed ice in a tall glass.\n"
            "4. Float sweet sherry on top.\n"
            "5. Garnish with a mint sprig."
        ),
        "garnish": "Mint sprig",
        "glassware": "Fog Cutter Glass or Highball",
        "difficulty": 3,
        "prep_time": 12,
        "tags": '["Classic", "Shaken", "Multi-Spirit", "Trader Vic\'s"]',
        "ingredients": [
            ("Light Rum", "2", "oz", "", 0),
            ("Brandy", "1/2", "oz", "", 1),
            ("Gin", "1/2", "oz", "", 2),
            ("Fresh Orange Juice", "2", "oz", "", 3),
            ("Fresh Lemon Juice", "1", "oz", "", 4),
            ("Orgeat", "1/2", "oz", "", 5),
            ("Sweet Sherry", "1/2", "oz", "float on top", 6),
            ("Fresh Mint", "1", "sprig", "garnish", 7),
        ],
    },
    {
        "name": "Jet Pilot",
        "description": (
            "A close relative of the Zombie, streamlined for aviation speed. "
            "Three rums, falernum, and spice make this a potent, complex tiki classic."
        ),
        "instructions": (
            "1. Combine all ingredients in a shaker with crushed ice.\n"
            "2. Flash blend or shake vigorously for 5 seconds.\n"
            "3. Pour unstrained into a pilsner or zombie glass.\n"
            "4. Garnish with a mint sprig and cherry."
        ),
        "garnish": "Mint sprig, maraschino cherry",
        "glassware": "Pilsner or Zombie Glass",
        "difficulty": 4,
        "prep_time": 12,
        "tags": '["Classic", "Strong", "Blended", "Don the Beachcomber"]',
        "ingredients": [
            ("Gold Rum", "3/4", "oz", "", 0),
            ("Jamaican Rum", "3/4", "oz", "dark", 1),
            ("Demerara Rum", "3/4", "oz", "151-proof", 2),
            ("Fresh Lime Juice", "1/2", "oz", "", 3),
            ("Fresh Grapefruit Juice", "1/2", "oz", "", 4),
            ("Cinnamon Syrup", "1/2", "oz", "", 5),
            ("Falernum", "1/2", "oz", "", 6),
            ("Angostura Bitters", "1", "dash", "", 7),
            ("Fresh Mint", "1", "sprig", "garnish", 8),
            ("Maraschino Cherry", "1", "piece", "garnish", 9),
        ],
    },
    {
        "name": "Jungle Bird",
        "description": (
            "Created at the Kuala Lumpur Hilton in 1978, this overlooked gem was rediscovered "
            "in the craft cocktail renaissance. Bitter Campari meets blackstrap rum for magic."
        ),
        "instructions": (
            "1. Combine all ingredients in a shaker with ice.\n"
            "2. Shake well until chilled.\n"
            "3. Strain over fresh ice into a double old fashioned glass or tiki mug.\n"
            "4. Garnish with a pineapple frond and wedge."
        ),
        "garnish": "Pineapple frond, pineapple wedge",
        "glassware": "Double Old Fashioned or Tiki Mug",
        "difficulty": 2,
        "prep_time": 8,
        "tags": '["Classic", "Shaken", "Bitter", "Modern Tiki", "Campari"]',
        "ingredients": [
            ("Blackstrap Rum", "1 1/2", "oz", "Cruzan Blackstrap preferred", 0),
            ("Campari", "3/4", "oz", "", 1),
            ("Pineapple Juice", "1 1/2", "oz", "fresh preferred", 2),
            ("Fresh Lime Juice", "3/4", "oz", "", 3),
            ("Simple Syrup", "1/2", "oz", "", 4),
            ("Pineapple Slice", "1", "piece", "garnish", 5),
        ],
    },
    {
        "name": "Planter's Punch",
        "description": (
            "The original tiki template from 19th-century Jamaica: one of sour, two of sweet, "
            "three of strong, four of weak. Fruity, punchy, and effortlessly tropical."
        ),
        "instructions": (
            "1. Combine rum, lime juice, grenadine, and pineapple juice in a shaker with ice.\n"
            "2. Shake well.\n"
            "3. Strain into a tall glass over fresh ice.\n"
            "4. Top with club soda.\n"
            "5. Garnish with orange slice, cherry, and a mint sprig.\n"
            "6. Add a float of dark rum and 2 dashes Angostura on top."
        ),
        "garnish": "Orange slice, maraschino cherry, mint sprig",
        "glassware": "Highball or Collins",
        "difficulty": 2,
        "prep_time": 8,
        "tags": '["Classic", "Shaken", "Tropical", "Beginner Friendly", "Jamaican"]',
        "ingredients": [
            ("Jamaican Rum", "2", "oz", "", 0),
            ("Fresh Lime Juice", "1", "oz", "", 1),
            ("Grenadine", "1", "oz", "", 2),
            ("Pineapple Juice", "1", "oz", "", 3),
            ("Angostura Bitters", "2", "dashes", "", 4),
            ("Club Soda", "2", "oz", "to top", 5),
            ("Orange Slice", "1", "piece", "garnish", 6),
            ("Maraschino Cherry", "1", "piece", "garnish", 7),
            ("Fresh Mint", "1", "sprig", "garnish", 8),
        ],
    },
    {
        "name": "Blue Hawaiian",
        "description": (
            "Created by Harry Yee at the Hilton Hawaiian Village in 1957. "
            "Vivid blue, tropical, and celebratory — the unofficial drink of Waikiki."
        ),
        "instructions": (
            "1. Combine all ingredients in a blender with ice.\n"
            "2. Blend until smooth and frozen.\n"
            "3. Pour into a chilled hurricane glass.\n"
            "4. Garnish with a pineapple slice and cherry."
        ),
        "garnish": "Pineapple slice, maraschino cherry",
        "glassware": "Hurricane",
        "difficulty": 1,
        "prep_time": 8,
        "tags": '["Classic", "Blended", "Frozen", "Tropical", "Beginner Friendly"]',
        "ingredients": [
            ("White Rum", "1 1/2", "oz", "", 0),
            ("Blue Curaçao", "1", "oz", "", 1),
            ("Pineapple Juice", "2", "oz", "", 2),
            ("Cream of Coconut", "1", "oz", "Coco López", 3),
            ("Pineapple Slice", "1", "piece", "garnish", 4),
            ("Maraschino Cherry", "1", "piece", "garnish", 5),
        ],
    },
]


def seed_database(db: Database) -> None:
    """Insert starter ingredients and recipes only if recipes table is empty."""
    existing = db.fetchone("SELECT COUNT(*) as cnt FROM recipes")
    if existing and existing["cnt"] > 0:
        return

    with db.connect() as conn:
        # Insert ingredients
        for name, category in INGREDIENTS:
            conn.execute(
                "INSERT OR IGNORE INTO ingredients (name, category) VALUES (?, ?)",
                (name, category),
            )

        # Insert recipes and their ingredients
        for recipe in RECIPES:
            cur = conn.execute(
                """INSERT INTO recipes
                   (name, description, instructions, garnish, glassware,
                    difficulty, prep_time, tags, is_custom)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                (
                    recipe["name"],
                    recipe["description"],
                    recipe["instructions"],
                    recipe["garnish"],
                    recipe["glassware"],
                    recipe["difficulty"],
                    recipe["prep_time"],
                    recipe["tags"],
                ),
            )
            recipe_id = cur.lastrowid

            for ing_name, amount, unit, notes, sort_order in recipe["ingredients"]:
                row = conn.execute(
                    "SELECT id FROM ingredients WHERE name = ? COLLATE NOCASE", (ing_name,)
                ).fetchone()
                if row is None:
                    ing_cur = conn.execute(
                        "INSERT OR IGNORE INTO ingredients (name, category) VALUES (?, 'Other')",
                        (ing_name,),
                    )
                    ing_id = ing_cur.lastrowid
                else:
                    ing_id = row["id"]

                conn.execute(
                    """INSERT INTO recipe_ingredients
                       (recipe_id, ingredient_id, amount, unit, notes, sort_order)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (recipe_id, ing_id, amount, unit, notes, sort_order),
                )
