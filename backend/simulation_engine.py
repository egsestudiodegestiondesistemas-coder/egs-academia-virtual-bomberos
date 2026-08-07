"""
EGS FIRE ACADEMY
Simulation Engine
Versión 0.2
"""

from scenario_manager import ScenarioManager
from fire_physics_engine import FirePhysicsEngine


class SimulationEngine:

    def __init__(self, scenario_filename: str):

        self.scenario_manager = ScenarioManager()
        self.scenario = self.scenario_manager.load(scenario_filename)

        self.fire = FirePhysicsEngine()

        self.active = False

    def start(self):

        self.active = True

        print("=" * 60)
        print("EGS FIRE ACADEMY")
        print("CENTRO DE SIMULACIÓN VIRTUAL")
        print("=" * 60)

        print()
        print("ESCENARIO CARGADO")
        print(self.scenario["name"])

        print()
        print("CONDICIONES INICIALES")
        print("Origen:", self.scenario["fire"]["origin"])
        print("Etapa:", self.scenario["fire"]["stage"])
        print("Ventilación:", self.scenario["fire"]["ventilation"])
        print("Víctimas:", len(self.scenario["victims"]))

    def advance(self, steps: int = 1):

        if not self.active:
            raise RuntimeError("La simulación todavía no fue iniciada.")

        for _ in range(steps):

            self.fire.update()

            print(self.fire.status())

    def finish(self):

        self.active = False

        print()
        print("=" * 60)
        print("SIMULACIÓN FINALIZADA")
        print("=" * 60)


if __name__ == "__main__":

    simulation = SimulationEngine("house_fire_001.json")

    simulation.start()

    simulation.advance(10)

    simulation.finish()