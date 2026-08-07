from dataclasses import dataclass

@dataclass
class FireScenario:

    scenario_id: str
    title: str
    phase: str
    fire_state: str
    smoke_level: str
    temperature: int
    victims: bool


class DecisionEngine:

    def __init__(self):

        self.score = 100
        self.errors = []
        self.decisions = []

    def register_decision(self, decision):

        self.decisions.append(decision)

    def add_error(self, error, penalty):

        self.errors.append(error)
        self.score -= penalty

    def summary(self):

        return {

            "score": self.score,
            "errors": self.errors,
            "decisions": self.decisions

        }


if __name__ == "__main__":

    engine = DecisionEngine()

    engine.register_decision("Recepción de alarma")

    engine.register_decision("Salida del cuartel")

    print(engine.summary())
    