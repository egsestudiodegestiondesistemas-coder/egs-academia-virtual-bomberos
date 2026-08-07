"""
===========================================================
EGS FIRE ACADEMY
Centro de Investigación, Simulación y Entrenamiento Bomberil

Academy Core
Versión 0.2.0 Alpha
===========================================================
"""

from simulation_engine import SimulationEngine
from decision_engine import DecisionEngine


class AcademyCore:

    def __init__(self):

        self.version = "0.2.0 Alpha"

        self.module = "Operaciones en Incendios Estructurales"

        self.simulation = SimulationEngine()

        self.decision = DecisionEngine()

        self.training_active = False

    def start_training(self):

        self.training_active = True

        print("=" * 60)
        print("EGS FIRE ACADEMY")
        print("Centro de Simulación Virtual")
        print("=" * 60)

        print(f"Módulo: {self.module}")
        print(f"Versión: {self.version}")
        print()

    def finish_training(self):

        self.training_active = False

        print()

        print("===== DEBRIEFING =====")

        print(self.decision.summary())

        print("======================")