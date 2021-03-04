from __future__ import annotations


class Character:
    def __init__(self, id_, health, range_, movement, class_):
        self.id = id_
        self.health = health
        self.range = range_
        self.movement = movement
        self.class_ = class_
        self.has_moved = False
        self.has_attack = False
        self.has_spell = False
        self.fly = False
        self.swim = False

    def __eq__(self, other):
        return self.id == other.id

    def take_damage(self, attacker: Character, damage: int = 1):
        self.health -= damage
        print(f'{attacker} attacked {self}')
        print(f'{self} has {self.health} health left\n')

    def __str__(self) -> str:
        return self.__class__.__name__

    def is_live(self) -> bool:
        if self.health > 0:
            return True
        return False

    def attack(self, target: Character, damage: int = 1):
        target.take_damage(self, damage)

    def get_info(self):
        info = f"{self}\n"
        info += f"      ID: {self.id}\n"
        info += f"      Health: {self.health}\n"
        info += f"      Movement: {self.movement}\n"
        info += f"      Range: {self.range}\n"
        info += f"      Class: {self.class_}\n"
        if self.fly:
            info += f"      Can Fly\n"
        elif self.swim:
            info += f"      Can Swim\n"
        return info


class Test_Zeus(Character):
    def __init__(self, id_):
        super().__init__(id_, 2, 3, 3, 'brawler')
        self.fly = True

    def get_info(self):
        info = super().get_info()
        info += 'Faith: Deal 1 damage to everyone (1 faith)\n'
        return info


class Test_Hades(Character):
    def __init__(self, id_):
        super().__init__(id_, 3, 2, 3, 'support')


class Test_Poseidon(Character):
    def __init__(self, id_):
        super().__init__(id_, 3, 1, 3, 'range')


class Test_Jesus(Character):
    def __init__(self, id_):
        super().__init__(id_, 3, 4, 3, 'range')


class Test_Isis(Character):
    def __init__(self, id_):
        super().__init__(id_, 3, 4, 3, 'range')


class Test_Sam(Character):
    def __init__(self, id_):
        super().__init__(id_, 3, float('inf'), 3, 'range')

    def get_info(self):
        info = super().get_info()
        info += 'Test Character, has infinite range\n'
        return info


class Test_Vincent(Character):
    def __init__(self, id_):
        super().__init__(id_, 3, 3, float('inf'), 'range')

    def get_info(self):
        info = super().get_info()
        info += 'Test Character, has infinite movement\n'
        return info


class Test_One_health(Character):
    def __init__(self, id_):
        super().__init__(id_, 1, 3, 10, 'range')

    def get_info(self):
        info = super().get_info()
        info += 'Test Character, has one health\n'
        return info


if __name__ == '__main__':
    a = Test_Isis(1)
    b = Test_Zeus(2)
    print(b.get_info())
