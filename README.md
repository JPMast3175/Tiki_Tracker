# 🌴 Tiki Tracker

A modern, cross-platform Tiki cocktail tracking application built with Python and [Flet](https://flet.dev).

Runs on macOS, Windows, iPhone, Android, and tablets from a single codebase.

---

## Features

| Feature | Details |
|---|---|
| **10 Starter Recipes** | Mai Tai, Zombie, Navy Grog, Painkiller, Scorpion, Fog Cutter, Jet Pilot, Jungle Bird, Planter's Punch, Blue Hawaiian |
| **Custom Recipes** | Add, edit, and delete your own recipes |
| **Bar Inventory** | Track bottles, syrups, juices, bitters, garnishes with in-stock toggle |
| **"What Can I Make?"** | Automatically shows recipes you can craft from current inventory |
| **Drink of the Day** | Stable daily suggestion, inventory-aware |
| **Favorites & Ratings** | 1–5 star ratings, heart toggle, dedicated Favorites view |
| **QR Code Sharing** | Export any recipe as a scannable QR code (JSON payload) |
| **JSON Import/Export** | Back up and share recipe collections |
| **SQLite local storage** | Fully offline, single flat-file database |
| **Tiki-inspired dark theme** | Deep greens, warm amber accents |

---

## Quick Start

### Prerequisites

- Python 3.11 or newer (3.13 recommended)
- Git

### Setup

```bash
# Clone or open the project
cd /Users/josephmast/Tiki_Tracker

# Create virtual environment (if not already created)
python3.13 -m venv venv

# Activate
source venv/bin/activate          # macOS / Linux
# or
venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python -m tiki_tracker.main
```

The app opens a native desktop window. The SQLite database is created automatically at `data/tiki_tracker.db` on first launch.

---

## Project Structure

```
Tiki_Tracker/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
│
├── data/                        # SQLite database (auto-created)
│   └── tiki_tracker.db
│
├── exports/                     # JSON exports and DB backups
│   ├── recipes/
│   └── backups/
│
├── src/tiki_tracker/
│   ├── main.py                  # Entry point
│   ├── app.py                   # Flet routing + service wiring
│   │
│   ├── db/
│   │   ├── database.py          # SQLite connection manager
│   │   ├── schema.py            # DDL (create tables)
│   │   └── seed_data.py         # 10 classic tiki recipes
│   │
│   ├── models/
│   │   ├── recipe.py
│   │   ├── ingredient.py
│   │   └── inventory.py
│   │
│   ├── services/
│   │   ├── recipe_service.py    # Recipe CRUD + inventory match
│   │   ├── inventory_service.py # Inventory + ingredient CRUD
│   │   ├── suggestion_service.py# Drink of the day
│   │   ├── qr_service.py        # QR code generation
│   │   └── export_service.py    # JSON import/export + DB backup
│   │
│   └── ui/
│       ├── theme.py             # Colors, shared widgets
│       └── views/
│           ├── home.py
│           ├── recipes.py
│           ├── recipe_detail.py
│           ├── inventory.py
│           ├── favorites.py
│           ├── add_recipe.py
│           └── settings.py
│
└── tests/
    ├── test_recipe_service.py
    ├── test_inventory_service.py
    └── test_qr_service.py
```

---

## Running Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

---

## Building for Mobile / Distribution

Flet uses [Flet Build](https://flet.dev/docs/publish) to package for iOS, Android, macOS, Windows, and Linux.

```bash
# Install Flet CLI (if needed)
pip install flet

# macOS app bundle
flet build macos

# iOS (requires Xcode on macOS)
flet build ios

# Android (requires Android SDK)
flet build apk

# Windows executable
flet build windows
```

Output is placed in the `build/` directory.

---

## Backup & Export

### Via the app
Open **Settings** → use the export/backup buttons.

### Manual backup
```bash
# Copy the database file
cp data/tiki_tracker.db exports/backups/tiki_tracker_$(date +%Y%m%d).db

# Or export all recipes to JSON
python -c "
from tiki_tracker.db.database import Database
from tiki_tracker.db.schema import create_tables
from tiki_tracker.services.recipe_service import RecipeService
from tiki_tracker.services.inventory_service import InventoryService
from tiki_tracker.services.export_service import ExportService

db = Database()
create_tables(db)
rs = RecipeService(db)
inv = InventoryService(db)
es = ExportService(rs, inv)
print('Exported to:', es.export_recipes_json())
"
```

---

## Push to GitHub

```bash
# If you haven't already:
gh repo create Tiki_Tracker --public --source=. --remote=origin --push

# Or manually:
git remote add origin https://github.com/YOUR_USERNAME/Tiki_Tracker.git
git push -u origin main
```

---

## Database Location

| Platform | Path |
|---|---|
| Development | `Tiki_Tracker/data/tiki_tracker.db` |
| macOS (deployed) | `~/Library/Application Support/TikiTracker/` |
| Windows (deployed) | `%APPDATA%\TikiTracker\` |
| Linux (deployed) | `~/.local/share/TikiTracker/` |

The database is a standard SQLite file — back it up, copy it, or open it with any SQLite browser (e.g., [DB Browser for SQLite](https://sqlitebrowser.org)).

---

## Known Limitations

- **QR scanning** (importing from camera) is a TODO — the architecture supports it but requires a platform-specific scanner library
- **Images** use a styled placeholder; local image loading from paths is wired but not yet integrated with a file picker for the image field
- **Multi-user / cloud sync** is not implemented — the data layer is designed for it (clean service/DB separation) but no sync backend exists yet

## Future Enhancements

- Cloud sync (Supabase / Firebase)
- Camera QR scanning for recipe import
- Ingredient substitution suggestions
- Random drink picker
- Shopping list generator
- Nutritional info
- Cocktail photo capture
- Batch/party scaling
