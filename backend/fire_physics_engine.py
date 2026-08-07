"""
===========================================================
EGS FIRE ACADEMY
Fire Physics Engine
Versión 0.1
===========================================================
"""


class FirePhysicsEngine:

    def __init__(self):

        self.temperature = 25

        self.stage = "Incipiente"

        self.time = 0

        self.oxygen = 100

    def update(self):

        self.time += 30

        self.temperature += 45

        if self.temperature >= 150:
            self.stage = "Crecimiento"

        if self.temperature >= 350:
            self.stage = "Desarrollo"

        if self.temperature >= 600:
            self.stage = "Flashover"

    def status(self):

        return {

            "time": self.time,

            "temperature": self.temperature,

            "oxygen": self.oxygen,

            "stage": self.stage

        }


if __name__ == "__main__":

    fire = FirePhysicsEngine()

    print("=" * 60)
    print("FIRE PHYSICS ENGINE")
    print("=" * 60)

    for _ in range(15):

        fire.update()

        print(fire.status())