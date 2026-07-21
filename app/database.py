from datetime import date
from itertools import count

# ---------------------------------------------------------------------
# Users — in-memory only. username -> {"username": ..., "hashed_password": ...}
# ---------------------------------------------------------------------
users_db: dict[str, dict] = {}

# ---------------------------------------------------------------------
# Aquarium maintenance log entries
# ---------------------------------------------------------------------
entries_db: list[dict] = []
_entry_id_counter = count(1)

TASK_TYPES = {"feeding", "water_change", "filter_clean", "parameter_check"}


def get_next_entry_id() -> int:
    return next(_entry_id_counter)


def seed_entries() -> None:
    """Reset entries_db back to 3 example log entries."""
    global _entry_id_counter
    entries_db.clear()
    _entry_id_counter = count(1)

    seed_data = [
        {
            "tank_name": "Reef Tank A",
            "task_type": "water_change",
            "notes": "25% water change, topped up with fresh saltwater",
            "performed_at": str(date.today()),
            "completed": True,
        },
        {
            "tank_name": "Reef Tank A",
            "task_type": "parameter_check",
            "notes": "pH 8.1, salinity 1.025, nitrates 5ppm",
            "performed_at": str(date.today()),
            "completed": True,
        },
        {
            "tank_name": "Betta Tank",
            "task_type": "feeding",
            "notes": "Fed 3 pellets — skipping tomorrow for digestion",
            "performed_at": str(date.today()),
            "completed": False,
        },
    ]
    for item in seed_data:
        entries_db.append({"id": get_next_entry_id(), **item})


# Seed on import so the API has example data the moment it starts.
seed_entries()