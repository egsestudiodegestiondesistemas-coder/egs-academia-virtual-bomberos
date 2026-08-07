"""
===========================================================
EGS FIRE ACADEMY
Scenario Manager
===========================================================
"""

import json
from pathlib import Path


class ScenarioManager:

    def __init__(self):

        self.base_path = Path(__file__).resolve().parent.parent / "scenarios"
    def load(self, filename):

        file = self.base_path / filename

        if not file.exists():
            raise FileNotFoundError(file)

        with open(file, encoding="utf-8") as f:

            return json.load(f)

    def list(self):

        return sorted([x.name for x in self.base_path.glob("*.json")])


if __name__ == "__main__":

    manager = ScenarioManager()

    print("=" * 60)
    print("SCENARIO MANAGER")
    print("=" * 60)

    print()

    print("Escenarios disponibles:")

    for scenario in manager.list():

        print("-", scenario)

    print()

    print("Escenario cargado:")

    print(manager.load("house_fire_001.json"))