from decision_engine import DecisionEngine
from simulation_engine import SimulationEngine


class FireAcademy:

    def __init__(self):

        self.simulation = SimulationEngine()
        self.decision = DecisionEngine()

    def dispatch(self):

        print("\n===================================")
        print("EGS FIRE ACADEMY")
        print("Centro de Simulación Virtual")
        print("Operaciones en Incendios Estructurales")
        print("===================================\n")

        print("ALARMA RECIBIDA")

        self.decision.register_decision("Recepción de alarma")

        print(self.simulation.status())

    def advance(self):

        self.simulation.advance()

        print(self.simulation.status())

    def report(self):

        print("\n========= DEBRIEFING =========")

        print(self.decision.summary())

        print("===============================")


if __name__ == "__main__":

    academy = FireAcademy()

    academy.dispatch()

    for _ in range(5):

        academy.advance()

    academy.report()
    