"""
===========================================================
EGS FIRE ACADEMY
Knowledge Engine
===========================================================
"""

import json
from pathlib import Path


class KnowledgeEngine:

    def __init__(self):

        self.base_path = Path(__file__).resolve().parent.parent / "knowledge"

        self.sources = {}

    def load(self, filename):

        file = self.base_path / filename

        if not file.exists():
            raise FileNotFoundError(f"No existe: {file}")

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.sources[filename] = data

        return data

    def get_source(self, filename):

        return self.sources.get(filename)

    def list_sources(self):

        return list(self.sources.keys())


if __name__ == "__main__":

    engine = KnowledgeEngine()

    engine.load("dispatch_protocol.json")
    fire = engine.load("fire_classes.json")

    print("=" * 60)
    print("KNOWLEDGE ENGINE")
    print("=" * 60)

    print()
    print("Fuentes cargadas:")
    print(engine.list_sources())

    print()
    print("Clase B:")
    print(fire["B"])