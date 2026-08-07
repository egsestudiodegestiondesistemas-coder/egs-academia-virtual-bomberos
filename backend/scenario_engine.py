"""
===========================================================
EGS FIRE ACADEMY
Scenario Engine
Versión 0.1
===========================================================
"""


class Scenario:

    def __init__(
        self,
        name,
        occupancy,
        fire_class,
        fuel,
        victims
    ):
        self.name = name
        self.occupancy = occupancy
        self.fire_class = fire_class
        self.fuel = fuel
        self.victims = victims

    def info(self):
        return {
            "Escenario": self.name,
            "Ocupación": self.occupancy,
            "Clase": self.fire_class,
            "Combustible": self.fuel,
            "Víctimas": self.victims
        }


if __name__ == "__main__":
    house = Scenario(
        name="Incendio en vivienda",
        occupancy="Residencial",
        fire_class="A",
        fuel="Muebles de madera",
        victims=2
    )

    print("=" * 60)
    print("SCENARIO ENGINE")
    print("=" * 60)
    print(house.info())