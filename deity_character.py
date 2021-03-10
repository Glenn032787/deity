from __future__ import annotations
from typing import TYPE_CHECKING, List, Union
from abc import ABC
from deity_error import *
from deity_helper_function import turn_into_coordinate, distance

if TYPE_CHECKING:
    from deity_game import Deity, Player
    from deity_board import Tile


class Character:
    def __init__(self, id_, health, range_, movement, class_, attribute=None):
        self.id = id_
        self.max_health = health
        self.health = health
        self.range = range_
        self.movement = movement
        self.class_ = class_
        self.has_moved = False
        self.has_attack = False
        self.has_spell = False
        self.attribute = attribute  # flight, aquatic or None
        self.status_effect = {'disarm': 0, 'blinded': 0,
                              'slowed': 0, 'stun': 0, 'grounded': 0}

    def __eq__(self, other):
        return self.id == other.id

    def take_damage(self, attacker: Character, game: Deity,
                    attacking_player: Player, damage: int = 1):
        mother_love = self._check_mothers_love(attacker, game,
                                               attacking_player, damage)
        if not mother_love:
            self.health -= damage
            print(f'{attacker} attacked {self}')
            if self.health > 0:
                print(f'{self} has {self.health} health left\n')
            else:
                print(f'{self} is killed!!!\n')

    def _check_mothers_love(self, attacker: Character, game,
                            attacking_player, damage: int = 1) -> bool:
        player = game.opponent(attacking_player)
        for char in player.live_character():
            if isinstance(char, Isis_Guardian):
                coord = game.board.get_char_location(self)
                adjacent = game.board.adjacent_tiles(coord)
                isis_coord = game.board.get_char_location(char)
                if isis_coord in adjacent:
                    print(f'Isis Guardian is adjacent to {self}')
                    while True:
                        confirm = input(f'Do you want Isis passive ability, '
                                        f'Mother’s Love, to take damage damage '
                                        f'in place of {self} (y/n)? ')
                        try:
                            confirm = confirm.lower()
                            assert confirm in ['y', 'n']
                            break
                        except (ValueError, AssertionError):
                            print('Type y or n')
                            continue
                    if confirm == 'y':
                        char.take_damage(attacker, game, attacking_player,
                                         damage)
                        return True
                    elif confirm == 'n':
                        return False
        return False

    def __str__(self) -> str:
        return self.__class__.__name__.replace("_", " ")

    def is_live(self) -> bool:
        if self.health > 0:
            return True
        return False

    def attack(self, target: Character, game: Deity,
               attacker: Player, damage: int = 1):
        target.take_damage(self, game, attacker, damage)
        self.has_attack = True

    def get_info(self):
        info = f"\n{self}\n"
        info += f"      ID: {self.id}\n"
        info += f"      Health: {self.health}/{self.max_health}\n"
        info += f"      Movement: {self.movement}\n"
        info += f"      Range: {self.range}\n"
        info += f"      Class: {self.class_}\n"
        info += f"      Attribute: {self.attribute}\n"
        effect = ''
        for status in self.status_effect:
            if self.status_effect[status] > 0:
                effect += f'{status}, '
        if effect == '':
            info += f"      Status Effect: None\n"
        else:
            info += f"      Status Effect: {effect[:-2]}\n"
        return info

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        raise NotImplementedError

    def get_status_effects(self) -> List[str]:
        total_effects = []
        for effect in self.status_effect:
            if self.status_effect[effect] > 0:
                total_effects.append(effect)
        return total_effects

    def passive_ability(self, time: str, p: Player, game: Deity) -> None:
        pass


# === DEITY CLASSES ===
class Melee(Character, ABC):
    def __init__(self, id_, attribute=None):
        super().__init__(id_, 4, 1, 3, 'melee', attribute)


class Ranged(Character, ABC):
    def __init__(self, id_, attribute=None):
        super().__init__(id_, 3, 2, 2, 'range', attribute)


class Support(Character, ABC):
    def __init__(self, id_, attribute=None):
        super().__init__(id_, 3, 1, 2, 'support', attribute)
        self.faith_description_1 = ''
        self.faith_description_2 = ''

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        print(self.faith_description_1)
        print(self.faith_description_2)

        while True:
            faith_id = input('Select faith ability to use '
                             '(type 1, 2 or cancel): ')
            if faith_id.lower() == 'cancel':
                raise ReturnError

            try:
                faith_id = int(faith_id)
                assert (faith_id == 1 or faith_id == 2)

            except (ValueError, AssertionError):
                print('Not valid faith ability')
                continue

            try:
                if faith_id == 1:
                    self.faith_ability_1(p, game, discount)
                elif faith_id == 2:
                    self.faith_ability_2(p, game, discount)
                break
            except (ReturnError, NotEnoughFaith):
                continue

    def faith_ability_1(self, p: Player, game: Deity, discount: int = 0):
        raise NotImplementedError

    def faith_ability_2(self, p: Player, game: Deity, discount: int = 0):
        raise NotImplementedError


# === DEITY CHARACTERS ===
class Zeus_Philanderer(Melee, ABC):
    def __init__(self, id_):
        super().__init__(id_, 'flight')
        self.faith_description = '\nKidnapping (2 Faith)\n' \
                                 'Zeus can kidnap any opposing unit at any ' \
                                 'point on the map and move them to any ' \
                                 'square adjacent to Zeus. Units that have ' \
                                 'been kidnapped cannot attack on the ' \
                                 'following turn. Zeus can only use Kidnap on ' \
                                 'isolated targets: a target is isolated when ' \
                                 'they are not standing directly adjacent to ' \
                                 'any allied units.\n '
        self.passive_description = '\nThe Chase:\nEnemy units starting a turn ' \
                                   'next to Zeus only have one move ' \
                                   'regardless of class or movement buffs.\n'

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        game.print()
        print(self.faith_description)
        faith_cost = 2 - discount
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        opponent = game.opponent(p)
        targets = opponent.live_character()
        while True:
            for char in targets:
                print(f'{char.id} - {char}')
            deity_id = input('Pick enemy deity to target (type id or cancel): ')

            if deity_id.lower() == 'cancel':
                raise ReturnError
            try:
                char = opponent.character[int(deity_id)]
                assert char in targets
            except (ValueError, KeyError, AssertionError):
                print('Not valid deity (please type id)')
                continue

            coord = game.board.get_char_location(char)
            adjacent = game.board.adjacent_tiles(coord)

            for adj_coord in adjacent:
                tile = game.board.get_tile(adj_coord)
                if tile.character is not None:
                    if tile.character.id in opponent.character.keys():
                        print(f'{char} is not isolated')
                        continue
            break

        coord = game.board.get_char_location(self)
        adjacent = game.board.adjacent_tiles(coord)
        game.print()
        while True:
            print(f'Adjacent tiles: {adjacent}')
            new_coord = input(f'Pick an adjacent tile to place {char} '
                              f'(type coordinate or cancel): ')
            if new_coord.lower() == 'cancel':
                raise ReturnError
            try:
                new_coord = turn_into_coordinate(new_coord)
                tile = game.board.get_tile(new_coord)
                assert new_coord in adjacent
                if not check_tile_char_valid(char, tile):
                    print(f'{char} cannot be placed on {tile.terrain} tile')
                    raise NotValidMove
                game.board.move_character(char, new_coord)
                char.status_effect['disarmed'] += 1
                print(f'{char} is disarmed for 1 turn (cannot attack)')
                p.faith -= faith_cost
                print(f'{p.name} has {p.faith} faith left')
                break
            except (NotValidMove, AssertionError,
                    ValueError, CharacterBlocking):
                print('Not valid tile coordinate')
                continue

    def get_info(self):
        info = super().get_info()
        info += 'Passive Ability'
        info += self.passive_description
        info += '\nFaith Ability: '
        info += self.faith_description
        return info

    def passive_ability(self, time: str, p: Player, game: Deity):
        if time != 'start_turn':
            return
        opponent = game.opponent(p)
        if self in opponent.live_character():  # Check that it is enemy turn
            self_coord = game.board.get_char_location(self)
            adjacent = game.board.adjacent_tiles(self_coord)
            for char in p.live_character():
                coord = game.board.get_char_location(char)
                if coord in adjacent:
                    char.status_effect['grounded'] += 1
                    print(f'Zeus grounded {char} this turn')


class Isis_Guardian(Support, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.faith_description_1 = '\n1. Call of the Wounded (0 Faith)\nWhen ' \
                                   'an allied unit has 1 Health, Isis can ' \
                                   'move directly adjacent to them regardless ' \
                                   'of distance. '
        self.faith_description_2 = '2. Divine Blessing (1 Faith)\nIsis ' \
                                   'heals 1 Health to all adjacent ' \
                                   'characters.\n '
        self.passive_description = '\nMother’s Love:\nIsis can choose to take ' \
                                   'the damage of any standard melee or ' \
                                   'ranged attacks in place of any allied ' \
                                   'units standing adjacent to Isis.\n '

    def faith_ability_1(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 0 - discount
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith
        game.print()

        one_health = []
        one_health_str = ''
        for char in p.live_character():
            if char.health == 1 and char != self:
                one_health_str += f"{char.id} - {char}      "
                one_health.append(char)
        if len(one_health) == 0:
            print('No allied deity with 1 health')
            raise ReturnError
        print('Allied deity with 1 health:')
        print(one_health_str)
        while True:
            deity_id = input("Choose allied deity to move to (type id or "
                             "cancel): ")
            if deity_id.lower() == 'cancel':
                raise ReturnError

            try:
                char = p.character[int(deity_id)]
                assert char in one_health
                break
            except (ValueError, KeyError, AssertionError):
                print('Not valid deity id')
                continue

        coord = game.board.get_char_location(char)
        adjacent = game.board.adjacent_tiles(coord)
        game.print()
        print(f'Adjacent coordinates to {char}: {adjacent}')
        while True:
            coord = input(f'Choose coordinate to move {self} (type coordinate '
                          f'or cancel): ')
            if coord.lower() == 'cancel':
                raise ReturnError
            try:
                coord = turn_into_coordinate(coord)
                tile = game.board.get_tile(coord)
                assert check_tile_char_valid(self, tile)
                assert coord in adjacent

                game.board.move_character(self, coord)
                game.print()
                p.faith -= faith_cost
                print(f'{p.name} has {p.faith} faith left')
                break

            except (
                    ValueError, AssertionError, NotValidMove,
                    CharacterBlocking):
                game.print()
                print('Not valid coordinate')
                continue

    def faith_ability_2(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 1 - discount
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith
        print('')
        curr_coord = game.board.get_char_location(self)
        adjacent_coord = game.board.adjacent_tiles(curr_coord)
        heal_char = []
        for coord in adjacent_coord:
            t = game.board.get_tile(coord)
            if t.character is not None and t.character in p.live_character():
                char = t.character
                if char.health < char.max_health:
                    char.health += 1
                    print(f'{char} healed for 1 health')
                    heal_char.append(char)
        if len(heal_char) == 0:
            print(f"{self} used Divine Blessing but wasn't able to heal anyone")
        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Abilities'
        info += self.passive_description
        info += '\nFaith Abilities'
        info += self.faith_description_1
        info += '\n' + self.faith_description_2
        return info


class Asclepius_God_of_Medicine(Support, ABC):
    def __init__(self, id_):
        super().__init__(id_)

        self.faith_description_1 = '\n1. Divine Blessing (1 faith)\nAsclepius ' \
                                   'heals an allied unit for 1 health within ' \
                                   '2 range.'
        self.faith_description_2 = '2. Pharmacist (1 Faith)\nAsclepius ' \
                                   'cleanses an allied unit afflicted by a ' \
                                   'status effect.'
        self.faith_description_3 = '3. Against the Order (3 Faith)\nAsclepius ' \
                                   'resurrects a dead allied unit with 2 ' \
                                   'Health. The resurrected unit will be ' \
                                   'spawn on one of the base tiles. '

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        print("\n" + self.faith_description_1)
        print(self.faith_description_2)
        print(self.faith_description_3)

        while True:
            faith_id = input('Select faith ability to use '
                             '(type 1, 2, 3 or cancel): ')
            if faith_id.lower() == 'cancel':
                raise ReturnError

            try:
                faith_id = int(faith_id)
                assert faith_id in [1, 2, 3]

            except (ValueError, AssertionError):
                print('Not valid faith ability')
                continue

            try:
                if faith_id == 1:
                    self.faith_ability_1(p, game, discount)
                elif faith_id == 2:
                    self.faith_ability_2(p, game, discount)
                elif faith_id == 3:
                    self.faith_ability_3(p, game, discount)
                break
            except (ReturnError, NotEnoughFaith, FaithAbilityError):
                continue

    def faith_ability_1(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 1 - discount
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        nearby_char = p.live_character()
        nearby_char.remove(self)
        curr_coord = game.board.get_char_location(self)
        for char in nearby_char:
            coord = game.board.get_char_location(char)
            if distance(coord, curr_coord) > 2:
                nearby_char.remove(char)

        if len(nearby_char) == 0:
            print('No nearby allied deity')
            raise FaithAbilityError
        game.print()
        print('Nearby allies that can be healed (2 tiles away)')
        for char in nearby_char:
            print(
                f'{char.id} - {char}(Health: {char.health}/{char.max_health})      ')
        while True:
            deity_id = input('Choose deity to heal by 2 (type id or cancel): ')
            if deity_id.lower() == 'cancel':
                raise ReturnError
            try:
                char_heal = p.character[int(deity_id)]
                assert char_heal in nearby_char
                break
            except (ValueError, AssertionError):
                print('Not valid deity id')
                continue
        char_heal.health += 2
        if char_heal.health > char_heal.max_health:
            char_heal.health = char_heal.max_health
        print(f'{char_heal} is healed to {char_heal.health}')
        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def faith_ability_2(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 1 - discount
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        status_str = ''
        for char in p.live_character():
            if char.get_status_effects():
                status_str += f'{char.id} - {char} {char.get_status_effects()}'
        if status_str == '':
            print('No allied deity has status effect')
            raise FaithAbilityError
        game.print()
        print('Allied deity with status effects')
        print(status_str)

        while True:
            deity_id = input('Choose deity to cleanse status effect (type id '
                             'or cancel): ')
            if deity_id.lower() == 'cancel':
                raise ReturnError
            try:
                char = p.character[int(deity_id)]
                assert char.get_status_effects() != []
                for effect in char.status_effect:
                    char.status_effect[effect] = 0
                assert char.get_status_effects() == []
                print(f'{char} has been cleansed of its status effect(s)')
                p.faith -= faith_cost
                print(f'{p.name} has {p.faith} faith left')
                break
            except (ValueError, AssertionError, KeyError):
                game.print()
                print('Not valid deity id')
                continue

    def faith_ability_3(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 3 - discount
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        dead_char = p.dead_character()
        if len(dead_char) == 0:
            print('No dead deity to revive')
            raise FaithAbilityError

        dead_str = ''
        for char in dead_char:
            dead_str += f'{char.id} - {char}    '

        game.print()
        print('\nDead allied deities:')
        print(dead_str)

        while True:
            deity_id = input('Choose deity to revive (type id or cancel): ')
            if deity_id.lower() == 'cancel':
                raise ReturnError
            try:
                char = p.character[int(deity_id)]
                assert char in dead_char
                break
            except (ValueError, AssertionError, KeyError):
                game.print()
                print('Not valid deity id')
                continue

        game.print()
        base = game.board.get_base_tile(p.number)
        print(f'Base tile: {base}')
        while True:
            coord = input('Choose base tile to spawn deity (type coordinates '
                          'or cancel): ')
            if coord.lower() == 'cancel':
                raise ReturnError
            try:
                coord = turn_into_coordinate(coord)
                game.board.spawn_character(char, coord, p.number)
                char.health = 2
                print(f'{char} has been revived!')
                p.faith -= faith_cost
                print(f'{p.name} has {p.faith} faith left')
                break
            except(ValueError, NotValidSpawn, TileAlreadyHaveCharacter):
                game.print()
                print('Not valid spawn point')
                continue

    def get_info(self):
        info = super().get_info()
        info += 'Faith Ability: \n'
        info += self.faith_description_1
        info += '\n' + self.faith_description_2
        info += '\n' + self.faith_description_3
        return info


class Hermes_Patron_of_Thieves(Melee, ABC):
    def __init__(self, id_):
        super().__init__(id_, 'flight')
        self.faith_description = "\nSteal (0 Faith):\nIf Hermes is adjacent to " \
                                 "an opposing unit, he may steal one faith. " \
                                 "Only works if the opponent has at least one " \
                                 "faith. Hermes can not perform any actions " \
                                 "on the following turn. "
        self.passive_description = '\nWinged Boots\nHermes is flying: Can ' \
                                   'walk on all forms of terrain. Cannot use ' \
                                   'forts.\n'

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 0 - discount
        game.print()
        print(self.faith_description)

        opponent = game.opponent(p)
        if opponent.faith == 0:
            print('Opponent has no faith to steal')
            raise FaithAbilityError

        curr_coord = game.board.get_char_location(self)
        adjacent = game.board.adjacent_tiles(curr_coord)
        adjacent_char = False
        for coord in adjacent:
            t = game.board.get_tile(coord)
            if t.character is not None and t.character in opponent.live_character():
                adjacent_char = True

        if not adjacent_char:
            print('No adjacent opposing deity to steal from')
            raise FaithAbilityError

        while True:
            confirm = input(f'\nSteal 1 faith from {opponent.name} (y/n)? ')
            try:
                confirm = confirm.lower()
                assert confirm in ['y', 'n']
                break
            except AssertionError:
                print('Not valid answer')
                continue

        if confirm == 'n':
            raise ReturnError
        opponent.faith -= 1
        p.faith -= faith_cost
        self.status_effect['stun'] += 2
        print(f"{opponent.name}'s faith reduced to {opponent.faith}")
        print(f"Hermes is stun and won't be able to perform any "
              f"actions for the rest of this turn and the next")
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Ability'
        info += self.passive_description
        info += '\nFaith Ability:'
        info += self.faith_description
        return info


class Neith_The_Huntress(Ranged, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.faith_description_1 = "\nDeep Breathing (2 Faith):\nNeith gains " \
                                   "one attack range. [Neith can perform deep " \
                                   "breathing again to gain one more attack " \
                                   "range at the cost of 1 faith]"
        self.faith_description_2 = "\nDeep Breathing (1 Faith):\nNeith can " \
                                   "perform deep breathing again to gain one " \
                                   "more attack range] "
        self.casted_faith_ability = False
        self.passive_description = '\nHunter’s Volley:\nNeith can perform the ' \
                                   'attack action option twice in a single ' \
                                   'turn at the cost of the player’s team ' \
                                   'being unable to perform any other ' \
                                   'options\n '

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        if not self.casted_faith_ability:
            faith_cost = 2 - discount
            game.print()
            print(self.faith_description_1)
        else:
            faith_cost = 1 - discount
            game.print()
            print(self.faith_description_2)

        while True:
            confirm = input(f'\nUse {faith_cost} faith to increase Neith '
                            f'range by 1 (y/n)? ')
            try:
                confirm = confirm.lower()
                assert confirm in ['y', 'n']
                break
            except AssertionError:
                print('Not valid answer')
                continue

        if confirm == 'n':
            raise ReturnError

        p.faith -= faith_cost
        self.range += 1
        self.casted_faith_ability = True
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Ability '
        info += self.passive_description
        info += '\nFaith Ability'
        info += self.faith_description_1
        return info

    def attack(self, target: Character, game: Deity,
               attacker: Player, damage: int = 1):
        # Does not change has_attacked to true because
        # passive allows Neith to attack multiple times
        target.take_damage(self, game, attacker, damage)


class Neptune_Earthshaker(Ranged, ABC):
    def __init__(self, id_):
        super().__init__(id_, 'aquatic')
        self.faith_description = '\nEarthquake (3 faith)\nAll enemy units on ' \
                                 'the board take 1 damage, enemies standing ' \
                                 'on or adjacent to a water, fort or cloud ' \
                                 'tile are stunned for 1 turn. Stunned units ' \
                                 'are unable to move, attack or perform faith ' \
                                 'abilities. This ability does not affect ' \
                                 'flying units. This ability’s stun effect ' \
                                 'can be cleansed. '
        self.passive_description = '\nMuddy Waters:\nNeptune is Aquatic: Can ' \
                                   'enter water tiles. Water tiles can be ' \
                                   'consumed and reduces the faith cost of ' \
                                   'active attacks by 1. Water tiles become ' \
                                   'blank tiles after they are consumed\n '

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 3 - discount
        game.print()
        print(self.faith_description)

        while True:
            confirm = input(f'\nUse Earthquake (y/n): ')
            try:
                confirm = confirm.lower()
                assert confirm in ['y', 'n']
                break
            except AssertionError:
                print('Not valid answer')
                continue

        if confirm == 'n':
            raise ReturnError

        opponent = game.opponent(p)
        for char in opponent.live_character():
            if char.attribute == 'flight':
                continue
            char.health -= 1
            print(f'{char} takes 1 damage')

            curr_coord = game.board.get_char_location(char)
            adjacent = game.board.adjacent_tiles(curr_coord)
            adjacent.append(curr_coord)
            for coord in adjacent:
                tile = game.board.get_tile(coord)
                if tile.terrain in ['cloud', 'water', 'fort']:
                    char.status_effect['stun'] += 1
                    print(f'{char} is stunned for 1 turn '
                          f'(cannot make action)')
                    break

        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Ability '
        info += self.passive_description
        info += '\nFaith Ability '
        info += self.faith_description
        return info


# === HELPER FUNCTION ===
def check_tile_char_valid(char: Character, tile: Tile) -> bool:
    """
    Check if char can be placed on tile based on character attribute and tile
    terrain. Return True if char can be placed on tile

    :param char: Deity
    :param tile: Tile
    :return: Return true if char can be placed on tile
    """
    if tile.terrain == 'water':
        if char.attribute not in ['flying', 'aquatic']:
            return False
    elif tile.terrain == 'cloud':
        if char.attribute != 'flying':
            return False
    return True


if __name__ == '__main__':
    a = Isis_Guardian(10)
    print(a.get_info())
