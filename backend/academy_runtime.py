"""
EGS FIRE ACADEMY
Academy Runtime
Versión 0.1
"""

from scenario_manager import ScenarioManager
from fire_physics_engine import FirePhysicsEngine
from decision_engine import DecisionEngine
from knowledge_engine import KnowledgeEngine


class AcademyRuntime:

    def __init__(self, scenario_filename: str):

        self.scenario_manager = ScenarioManager()
        self.scenario = self.scenario_manager.load(scenario_filename)

        self.fire = FirePhysicsEngine()
        self.decision = DecisionEngine()
        self.knowledge = KnowledgeEngine()

        self.active = False

    def start(self):

        self.active = True

        print("=" * 60)
        print("EGS FIRE ACADEMY")
        print("CENTRO DE SIMULACIÓN VIRTUAL")
        print("=" * 60)

        print()
        print("ESCENARIO")
        print("Nombre:", self.scenario["name"])
        print("Construcción:", self.scenario["construction"]["type"])
        print("Origen del incendio:", self.scenario["fire"]["origin"])
        print("Etapa inicial:", self.scenario["fire"]["stage"])
        print("Ventilación:", self.scenario["fire"]["ventilation"])
        print("Víctimas:", len(self.scenario["victims"]))

        self.decision.register_decision("Inicio del entrenamiento")

    def advance(self, steps: int = 1):

        if not self.active:
            raise RuntimeError("El entrenamiento no fue iniciado.")

        for _ in range(steps):
            self.fire.update()

            print()
            print("ESTADO DEL INCENDIO")
            print(self.fire.status())

    def finish(self):

        self.active = False

        print()
        print("=" * 60)
        print("DEBRIEFING")
        print("=" * 60)
        print(self.decision.summary())


if __name__ == "__main__":

    runtime = AcademyRuntime("house_fire_001.json")

    runtime.start()
    runtime.advance(5)
    runtime.finish()