from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple
from abc import ABC
from deity_error import *
from deity_helper_function import turn_into_coordinate, distance
from random import randint

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
        self.status_effect = {'disarmed': 0, 'blinded': 0, 'mummified': 0,
                              'slowed': 0, 'stun': 0, 'grounded': 0,
                              'mobile': 0, 'divine': 0, 'vigor': 0}
        if attribute:
            self.attribute = attribute  # flight, aquatic or standard
        else:
            self.attribute = 'standard'

    def __eq__(self, other):
        return self.id == other.id

    def take_damage(self, attacker: Character, game: Deity,
                    attacking_player: Player, damage: int = 1):
        mother_love = self._check_mothers_love(attacker, game,
                                               attacking_player, damage)
        if not mother_love:
            my_player = game.opponent(attacking_player)
            self.passive_ability('take_damage_attack', my_player, game)

            self.health -= damage
            print(f'\n{attacker} attacked {self}')
            if self.health > 0:
                print(f'{self} has {self.health} health left\n')
            else:
                print(f'{self} is killed!!!\n')

    def _check_mothers_love(self, attacker: Character, game,
                            attacking_player, damage: int = 1) -> bool:
        player = game.opponent(attacking_player)
        for char in player.live_character():
            if isinstance(char, (Isis_The_Mother, WIP_Isis_Guardian)):
                coord = game.board.get_char_location(self)
                adjacent = game.board.adjacent_tiles(coord)
                isis_coord = game.board.get_char_location(char)
                if isis_coord in adjacent:
                    print(f'Isis Guardian is adjacent to {self}')
                    while True:
                        confirm = input(f'Do you want to use Isis passive, '
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

    def heal(self, amount: int) -> None:
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def add_status_effect(self, effect: str, amount: int) -> None:
        if effect not in self.status_effect:
            raise NotValidStatusEffect

        if self.status_effect[effect] != float('-inf'):  # Check if immune
            self.status_effect[effect] = max(self.status_effect[effect], amount)

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
        super().__init__(id_)
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

            if 'divine' in char.get_status_effects():
                print(f'{char} is divine and is immune to faith ability')
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
                char.add_status_effect('disarmed', 1)
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
                    char.add_status_effect('grounded', 1)
                    print(f'Zeus grounded {char} this turn')


class Isis_The_Mother(Support, ABC):
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
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

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
        self.add_status_effect('stun', 2)
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
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

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
        self.faith_description = '\nEarthquake (3 faith):\nAll enemy units on ' \
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
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

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
            elif 'divine' in char.get_status_effects():
                continue
            char.passive_ability('take_damage_spell', p, game)
            char.health -= 1
            print(f'{char} takes 1 damage')

            curr_coord = game.board.get_char_location(char)
            adjacent = game.board.adjacent_tiles(curr_coord)
            adjacent.append(curr_coord)
            for coord in adjacent:
                tile = game.board.get_tile(coord)
                if tile.terrain in ['cloud', 'water', 'fort']:
                    char.add_status_effect('stun', 1)
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


class Amaterasu_Warrior_of_Light(Melee, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.range += 1  # Passive ability

        self.faith_description = '\nPiercing Light (2 Faith):\nAmaterasu fires ' \
                                 'a beam of light in one direction damaging ' \
                                 'all enemy units in a line between herself ' \
                                 'and the edge of the board by 1. This ' \
                                 'ability cannot be used diagonally. '
        self.passive_description = '\nShining Blade:\nAmaterasu attacks have ' \
                                   '+1 range.\n '

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 2 - discount
        game.print()
        print(self.faith_description)
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        while True:
            direction = input(f'\nWhich direction to fire Piercing Light ('
                              f'left, right, up, down or cancel)? ')
            try:
                direction = direction.lower()
                assert direction in ['left', 'right', 'up', 'down', 'cancel']
                break
            except AssertionError:
                print('Not valid answer')
                continue

        if direction == 'cancel':
            raise ReturnError

        opponent = game.opponent(p)
        coord = game.board.get_char_location(self)

        curr_coord = get_next_coord(coord, direction)
        while game.board.possible_tile(curr_coord):
            t = game.board.get_tile(curr_coord)
            if t.character is not None and \
                    t.character in opponent.live_character():
                if 'divine' in t.character.get_status_effects():
                    curr_coord = get_next_coord(curr_coord, direction)
                    continue
                t.character.health -= 1
                t.character.passive_ability('take_damage_spell', p, game)
                print(f'{t.character} took 1 damage')
            curr_coord = get_next_coord(curr_coord, direction)

        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Ability '
        info += self.passive_description
        info += '\nFaith Ability '
        info += self.faith_description
        return info


class Isis_Goddess_of_Magic(Ranged, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.range += 1
        self.faith_description_1 = "\nMetamorphmagus (2 Faith):\nIsis unlocks " \
                                   "her ability to transform and shapeshift " \
                                   "for the remainder of the game. Isis " \
                                   "permanently gains +1 movement and becomes " \
                                   "mobile: mobile units can walk on any " \
                                   "terrain tiles. [Anytime Isis uses " \
                                   "metamorphmagus after the first time, " \
                                   "Isis gains one movement at cost one 1 " \
                                   "faith.]\n"
        self.faith_description_2 = "\nMetamorphmagus (1 Faith):\nIsis unlocks " \
                                   "her ability to transform and shapeshift " \
                                   "for the remainder of the game. Isis " \
                                   "permanently gains +1 movement\n"
        self.casted_faith_ability = False
        self.passive_description = '\nRoyal Authority:\nIsis has +1 attack ' \
                                   'range.\n '

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        if not self.casted_faith_ability:
            faith_cost = 2 - discount
            game.print()
            print(self.faith_description_1)
        else:
            faith_cost = 1 - discount
            game.print()
            print(self.faith_description_2)
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        while True:
            confirm = input(f'\nUse {faith_cost} faith to increase Isis '
                            f'movement by 1 and become mobile (y/n)? ')
            try:
                confirm = confirm.lower()
                assert confirm in ['y', 'n']
                break
            except AssertionError:
                print('Not valid answer')
                continue

        if confirm == 'n':
            raise ReturnError

        self.add_status_effect('mobile', float('inf'))
        p.faith -= faith_cost
        self.movement += 1
        self.casted_faith_ability = True
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Ability '
        info += self.passive_description
        info += '\nFaith Ability'
        info += self.faith_description_1
        return info


class Odin_The_Wise(Support, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.faith_description_1 = "\n1. Well of Urðr (1 Health):\nGain one " \
                                   "faith. "
        self.faith_description_2 = "2. An Eye for an Eye (1 Health):\nYour " \
                                   "opponent loses one faith. "
        self.passive_description = '\nRavenclaw:\nEnemy units that attack ' \
                                   'Odin within one range will lose 1 hp from ' \
                                   'retaliatory damage. This ability does not ' \
                                   'work for faith attacks. Faith ability ' \
                                   'uses health instead.\n'  # TODO update passive description

    def faith_ability_1(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 1 - discount
        if self.health < faith_cost:
            print(f'Not enough health to use faith '
                  f'ability (cost {faith_cost} health)')
            raise NotEnoughFaith

        self.health -= faith_cost
        p.faith += 1
        print(f'{self} took {faith_cost} damage and gained 1 faith')

    def faith_ability_2(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 1 - discount
        if self.health < faith_cost:
            print(f'Not enough health to use faith '
                  f'ability (cost {faith_cost} health)')
            raise NotEnoughFaith

        opponent = game.opponent(p)
        self.health -= faith_cost
        opponent.faith -= 1
        print(f"{self} took {faith_cost} damage and "
              f"stole 1 of {opponent.name}'s faith")

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Abilities'
        info += self.passive_description
        info += '\nFaith Abilities'
        info += self.faith_description_1
        info += '\n' + self.faith_description_2
        return info

    def take_damage(self, attacker: Character, game: Deity,
                    attacking_player: Player, damage: int = 1):
        mother_love = self._check_mothers_love(attacker, game,
                                               attacking_player, damage)
        if not mother_love:
            self.health -= damage
            print(f'\n{attacker} attacked {self}')

            # Passive Ability (Ravenclaw)
            attacker_coord = game.board.get_char_location(attacker)
            self_coord = game.board.get_char_location(self)
            dis = distance(attacker_coord, self_coord)
            if dis <= 1:
                attacker.health -= 1
                attacker.passive_ability('take_damage_attack',
                                         attacking_player, game)
                print(f'Odin uses Ravenclaw and retaliated 1 '
                      f'damage to {attacker}')
                if attacker.health > 0:
                    print(f'{attacker} has {attacker.health} health left')
                else:
                    print(f'{attacker} is killed!!!')

            if self.health > 0:
                print(f'{self} has {self.health} health left\n')
            else:
                print(f'{self} is killed!!!\n')


class Zeus_God_of_Thunder(Ranged, ABC):
    def __init__(self, id_):
        super().__init__(id_, 'flight')
        self.faith_description = '\nMaster Bolt (1 Faith):\nZeus calls upon ' \
                                 'his master bolt and can strike any opposing ' \
                                 'unit at any place on the map for 1 damage. ' \
                                 'Cannot be used on an opponent with 1 ' \
                                 'Health.\n '
        self.passive_description = '\nOn the Clouds:\nZeus is flying: Can ' \
                                   'walk on all forms of terrain. Cannot use ' \
                                   'forts.\n '

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        game.print()
        print(self.faith_description)
        faith_cost = 1 - discount
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

            if 'divine' in char.get_status_effects():
                print(f'{char} is divine and is immune to faith ability')
                continue

            if char.health == 1:
                print('Cannot pick target with 1 health')
                continue
            break

        char.health -= 1
        char.passive_ability('take_damage_spell', p, game)
        print(f'Zeus master bolt hit {char} for 1 damage')
        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += 'Passive Ability'
        info += self.passive_description
        info += '\nFaith Ability: '
        info += self.faith_description
        return info


class Hermes_Messenger_of_the_Gods(Support, ABC):
    def __init__(self, id_):
        super().__init__(id_, 'flight')
        self.faith_description_1 = '\nTailwind (3 Faith)\nAll your units become ' \
                                   'mobile, mobile units can move onto any ' \
                                   'terrain types. [Anytime tailwind is used a ' \
                                   'second time, all allied units gain +1 ' \
                                   'movement at the cost of 2 faith.]\n '
        self.faith_description_2 = "\nTailwind (2 Faith)\nAll allied units " \
                                   "gain +1 movement\n"
        self.passive_description_1 = '\n1. Winged boots\nHermes is flying: Can ' \
                                     'walk on all forms of terrain. Cannot use ' \
                                     'forts.\n '
        self.passive_description_2 = '2. Traveller\nAny allied gods have ' \
                                     'one extra movement of starting a turn ' \
                                     'next to Hermes.\n'
        self.casted_faith_ability = False

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        game.print()
        if not self.casted_faith_ability:
            print(self.faith_description_1)
            faith_cost = 3 - discount
        else:
            print(self.faith_description_2)
            faith_cost = 2 - discount

        while True:
            if not self.casted_faith_ability:
                confirm = input(f'\nUse {faith_cost} faith to '
                                f'gain mobile (y/n)? ')
            else:
                confirm = input(f'\nUse {faith_cost} faith to '
                                f'give all allies (y/n)? ')
            try:
                confirm = confirm.lower()
                assert confirm in ['y', 'n']
                break
            except AssertionError:
                print('Not valid answer')
                continue
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        if not self.casted_faith_ability:
            self.add_status_effect('mobile', float('inf'))
            print('Hermes become mobile (can move on any terrain)')
        else:
            for char in p.live_character():
                char.add_status_effect('vigor', 1)

        print('All allied deity gain +1 movement this round')

        self.casted_faith_ability = True
        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def passive_ability(self, time: str, p: Player, game: Deity) -> None:
        if time != 'start_turn' or self not in p.live_character():
            # Check that passive trigger during start of char turn
            return

        coord = game.board.get_char_location(self)
        adjacent = game.board.adjacent_tiles(coord)

        for tile in adjacent:
            t = game.board.get_tile(tile)
            if t.character and t.character in p.live_character():
                t.character.add_status_effect('vigor', 1)
                print(f'{t.character} gain +1 movement this turn from Hermes')

    def get_info(self):
        info = super().get_info()
        info += 'Passive Ability'
        info += self.passive_description_1
        info += self.passive_description_2
        info += '\nFaith Ability: '
        info += self.faith_description_1
        return info


class Odin_Allfather(Melee, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.movement += 1
        self.faith_description = '\nGungnir (2 Faith)\nOdin gains strength ' \
                                 'through his fallen allies. Gungnir deals ' \
                                 '1 damage. For each fallen allied unit, ' \
                                 'Gungnir’s damage is increased by 1.\n '

        self.passive_description = '\nSleipnir\nOdin has a horse. Movement ' \
                                   'is increased by 1.\n '

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        game.print()
        print(self.faith_description)
        faith_cost = 2 - discount
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        num_dead = len(p.dead_character())
        damage = 1 + num_dead

        opponent = game.opponent(p)
        targets = opponent.live_character()
        while True:
            for char in targets:
                print(f'{char.id} - {char}')
            deity_id = input(f'Pick enemy deity to deal {damage} damage'
                             f' (type id or cancel): ')

            if deity_id.lower() == 'cancel':
                raise ReturnError
            try:
                char = opponent.character[int(deity_id)]
                assert char in targets
            except (ValueError, KeyError, AssertionError):
                print('Not valid deity (please type id)')
                continue

            if 'divine' in char.get_status_effects():
                print(f'{char} is divine and is immune to faith ability')
                continue
            break
        char.passive_ability('take_damage_spell', p, game)
        char.health -= damage
        print(f'{char} took {damage} damage')

        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += 'Passive Ability'
        info += self.passive_description
        info += '\nFaith Ability: '
        info += self.faith_description
        return info


class Fortuna_Personification_of_Luck(Melee, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.faith_description = '\nGamble (1 Faith)\nRoll a dice, if the ' \
                                 'dice is 1-3, deal 1 damage. If the dice is ' \
                                 '4-6, deal 2 damage.\n '
        self.passive_description = '\nLuck of the draw\nWhenever Fortuna ' \
                                   'lands on a faith tile, roll a dice. If ' \
                                   'the dice is 4-6 gain one extra faith.\n '

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        game.print()
        print(self.faith_description)
        faith_cost = 1 - discount
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

            if 'divine' in char.get_status_effects():
                print(f'{char} is divine and is immune to faith ability')
                continue
            break

        random = randint(1, 6)
        if random <= 3:
            char.health -= 1
            print(f'Rolled a {random}, 1 damage dealt to {char}')
        else:
            char.health -= 2
            print(f'Rolled a {random}, 2 damage dealt to {char}')
        char.passive_ability('take_damage_spell', p, game)

        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def passive_ability(self, time: str, p: Player, game: Deity) -> None:
        if time != 'collect_faith' or self not in p.live_character():
            return
        random = randint(1, 6)
        print(f'Fortuna passive: Luck of the draw')
        print(f'Rolled a {random}')
        if random >= 4:
            p.faith += 1
            print(f'{p.name} gained 1 additional faiths!!!')
        else:
            print(f'Roll failed, better luck next time :(')

    def get_info(self):
        info = super().get_info()
        info += 'Passive Ability'
        info += self.passive_description
        info += '\nFaith Ability: '
        info += self.faith_description
        return info


class Khione_Daughter_of_the_North(Support, ABC):
    def __init__(self, id_):
        super().__init__(id_, 'aquatic')
        self.faith_description = '\nFlash Freeze (2 Faith)\nAll enemy units ' \
                                 'standing adjacent to Khione or a water tile ' \
                                 'are subject to Flash Freeze. Any enemy ' \
                                 'units affected by flash freeze take 1 ' \
                                 'damage and are stunned for 1 turn.\n '
        self.passive_description_1 = '\n1. Frozen Lake\nKhione is Aquatic: Can ' \
                                     'enter water tiles. Water tiles may be ' \
                                     'consumer to reduce the cost of Khione’s ' \
                                     'active ability by 1 faith\n '
        self.passive_description_2 = '2. Snow Cloak\nAllies standing next to ' \
                                     'Khione are immune to enemy faith ' \
                                     'attacks. Khione does not benefit from ' \
                                     'Snow Cloak’s effect.\n '

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 2 - discount
        game.print()
        print(self.faith_description)
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        while True:
            confirm = input(f'\nUse Flash Freeze for 2 faith (y/n): ')
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
            if 'divine' in char.get_status_effects():
                continue

            curr_coord = game.board.get_char_location(char)
            adjacent = game.board.adjacent_tiles(curr_coord)
            adjacent.append(
                curr_coord)  # TODO ASK IF ENEMY ON WATER TILE IS AFFECTED
            for coord in adjacent:
                tile = game.board.get_tile(coord)
                if tile.terrain == 'water' or \
                        (tile.character and tile.character == self):
                    char.add_status_effect('stun', 1)
                    char.health -= 1
                    char.passive_ability('take_damage_spell', p, game)
                    print(f'{char} is stunned for 1 turn '
                          f'(cannot make action) and took 1 damage')
                    break

        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def passive_ability(self, time: str, p: Player, game: Deity) -> None:
        if time != 'start_turn' or self in p.live_character():
            # Triggers at start of opponents turn
            return
        coord = game.board.get_char_location(self)
        adjacent = game.board.adjacent_tiles(coord)

        opponent = game.opponent(p)
        for tile in adjacent:
            t = game.board.get_tile(tile)
            if t.character and t.character in opponent.live_character():
                t.character.add_status_effect('divine', 1)
                print(f'{t.character} is immune to faith attacks')

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Ability'
        info += self.passive_description_1
        info += self.passive_description_2
        info += '\nFaith Ability: '
        info += self.faith_description
        return info


class Athena_Grandmaster(Melee, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.faith_description_1 = '\nDecisive Maneuver (3 Faith): \nAthena can ' \
                                   'immediately teleport to an enemy’s ' \
                                   'adjacent tile and attack them for 1 ' \
                                   'damage.\n '
        self.faith_description_2 = '\nDecisive Maneuver (1 Faith): \nAthena can ' \
                                   'immediately teleport to an enemy’s ' \
                                   'adjacent tile and attack them for 1 ' \
                                   'damage.\n '

        self.passive_description = '\nPromotion: \nIf Athena reaches the ' \
                                   'opponent’s baseline (the row of tiles ' \
                                   'closest to your opponents), change the ' \
                                   'cost of Decisive Maneuver to 1 Faith.\n '
        self.promotion = False

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        game.print()
        if self.promotion:
            print(self.faith_description_2)
            faith_cost = 1 - discount
        else:
            print(self.faith_description_1)
            faith_cost = 3 - discount
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

            if 'divine' in char.get_status_effects():
                print(f'{char} is divine and is immune to faith ability')
                continue
            break

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
                char.health -= 1
                char.passive_ability('take_damage_spell', p, game)
                game.print()
                print(f'{self} dealt 1 damage to {char}')
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
        info += self.faith_description_1
        return info

    def passive_ability(self, time: str, p: Player, game: Deity):
        if time != 'after_movement' or self not in p.live_character() \
                or self.promotion:
            return

        y_val = 0 if p.number == 1 else game.board.height-1

        coord = game.board.get_char_location(self)
        if coord[1] == y_val:
            print(f'{self} got promoted! Decisive Maneuver now cost 1 faith')
            self.promotion = True


class WIP_Amaterasu_Goddess_of_the_Sun(Support, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.faith_description = '\nRadiance (2 Faith):\nAmaterasu unleashes ' \
                                 'the power of the sun and blinds her enemy ' \
                                 'for 2 turns, if Hideaway Cave is active, ' \
                                 'enemies will be blinded for 3 turns. Using ' \
                                 'this ability deactivates Hideaway Cave if ' \
                                 'it was previously active.\n'
        self.passive_description_1 = '\n1. Hideaway Cave:\nAfter Amaterasu is ' \
                                     'inflicted with any type of damage, ' \
                                     'she retreats into the cave, while in ' \
                                     'the cave dark spirits torment the field ' \
                                     'and all enemy units have -1 movement. ' \
                                     'The cave will remain active until she ' \
                                     'is moved or until she takes damage ' \
                                     'again\n'
        self.passive_description_2 = '2. Divine Blessing:\nEvery 3 turns ' \
                                     'where Amaterasu is not moved by the ' \
                                     'player or attacked by the enemy, ' \
                                     'she gains one faith, if Hideaway Cave ' \
                                     'is active Amaterasu gains faith every 2 ' \
                                     'turns.\n'
        self.cave = False
        self.not_move = 0

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        game.print()
        print(self.faith_description)
        faith_cost = 1 - discount

        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        while True:
            confirm = input(f'\nUse Radiance ability for 2 faith (y/n)? ')
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
        blind_turn = 3 if self.cave else 2

        for char in opponent.live_character():
            char.add_status_effect('blinded', blind_turn)  # TODO add blind
        if self.cave:
            print('Hideaway Cave is inactivated')
            self.cave = False
        print(f"All of {opponent.name}'s deity are "
              f"blinded for {blind_turn} round")
        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += 'Passive Ability'
        info += self.passive_description_1
        info += self.passive_description_2
        info += '\nFaith Ability: '
        info += self.faith_description
        return info

    def passive_ability(self, time: str, p: Player, game: Deity):
        if time == 'take_damage_attack' or time == 'take_damage_spell':
            self.cave = not self.cave
            if self.cave:
                print('Hideaway Cave is activated')
            else:
                print('Hideaway Cave is inactivated')
        elif time == 'after_movement':
            self.not_move = 0
            if self.cave:
                print('Hideaway Cave is inactivated')
                self.cave = False

        elif time == 'start_turn' and self not in p.live_character():
            # enemy turn
            if self.cave:
                for char in p.live_character():
                    # TODO implement slowed (-1 movement)
                    char.add_status_effect('slowed', 1)
            print(f'Hideaway Cave is active, all {p.name} character has -1 '
                  f'movement')

        elif time == 'end_turn' and self in p.live_character():
            # my turn
            if not self.has_moved:
                self.not_move += 1

            if (self.cave and self.not_move >= 2) or \
                    (not self.cave and self.not_move >= 3):
                print('Amaterasu: Divine Blessing')
                print(f"{self} hasn't moved for {self.not_move} turns, "
                      f"{p.name} gain 1 faith")
                p.faith += 1
                self.not_move = 0


class WIP_Isis_Guardian(Support, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.faith_description = '\nBreath of Life (2 Faith)\nIsis can ' \
                                 'resurrect any fallen allied unit in ' \
                                 'mummified form with 2 Health. Mummies ' \
                                 'cannot move or attack for 3 turns and can ' \
                                 'be slain during this duration. After 3 ' \
                                 'turns, mummies will be able resume action. ' \
                                 'Mummies can be summoned onto any tile ' \
                                 'adjacent to Isis.\n '
        self.passive_description_1 = '\n1. Mother’s Love:\nIsis can choose to ' \
                                     'take the damage of any standard melee or ' \
                                     'ranged attacks in place of any allied ' \
                                     'units standing adjacent to Isis.\n '
        self.passive_description_2 = '2. Healer\nAny unit that stands adjacent ' \
                                     'to Isis for 2 consecutive turns gains 1 ' \
                                     'health, units cannot exceed the health ' \
                                     'point cap through this ability.\n '
        self.consecutive_char = []

    def passive_ability(self, time: str, p: Player, game: Deity) -> None:
        if time != 'start_turn' or self not in p.live_character():
            return

        curr_coord = game.board.get_char_location(self)
        adjacent = game.board.adjacent_tiles(curr_coord)
        chars = []
        for coord in adjacent:
            t = game.board.get_tile(coord)
            if t.character and t.character in p.live_character():
                chars.append(t.character)
                if t.character in self.consecutive_char:
                    t.character.heal(1)
                    print(f'{self} healed {t.character} for 1 health')
        self.consecutive_char = chars

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 2 - discount
        game.print()
        print(self.faith_description)
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
        curr_coord = game.board.get_char_location(self)
        adjacent = game.board.adjacent_tiles(curr_coord)
        while True:
            coord = input('Choose adjacent tile to spawn deity (type '
                          'coordinates or cancel): ')
            if coord.lower() == 'cancel':
                raise ReturnError
            try:
                coord = turn_into_coordinate(coord)
                assert coord in adjacent
                tile = game.board.get_tile(coord)
                if tile.character is not None:
                    print('Tile already has a character')
                    raise TileAlreadyHaveCharacter
                if tile.terrain is None or tile.terrain in ['water', 'cloud']:
                    print("Can't spawn character in water or cloud")
                    raise NotValidSpawn
                tile.character = char
                char.health = 2
                # TODO Check with Sam and Vincent, Change name to mummified
                char.add_status_effect('mummified', 3)
                print(f'{char} has been revived as a mummy!')
                p.faith -= faith_cost
                print(f'{p.name} has {p.faith} faith left')
                break
            except(ValueError, AssertionError,
                   NotValidSpawn, TileAlreadyHaveCharacter):
                game.print()
                print('Not valid spawn point')
                continue

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Abilities'
        info += self.passive_description_1
        info += self.passive_description_2
        info += '\nFaith Abilities'
        info += self.faith_description
        return info


class Athena_Goddess_of_Wisdom(Support, ABC):
    def __init__(self, id_):
        super().__init__(id_)
        self.faith_description = '\nForesight (2 Faith)\nFor the next 2 ' \
                                 'turns, you gain one extra action.\n'
        self.passive_description_1 = '\n1. Aegis:\nRanged attacks performed at ' \
                                     'greater than one range will be ' \
                                     'countered and both units take 1 ' \
                                     'damage.\n'
        self.passive_description_2 = '2. Odyssey: \nAll adjacent units ' \
                                     'starting a turn next to Athena will ' \
                                     'have +1 movement\n '
        self.consecutive_char = []

    def passive_ability(self, time: str, p: Player, game: Deity) -> None:
        if time != 'start_turn' or self not in p.live_character():
            # Check that passive trigger during start of char turn
            return

        coord = game.board.get_char_location(self)
        adjacent = game.board.adjacent_tiles(coord)

        for tile in adjacent:
            t = game.board.get_tile(tile)
            if t.character and t.character in p.live_character():
                t.character.add_status_effect('vigor', 1)
                print(f'{t.character} gain +1 movement this turn from Athena')

    def faith_ability(self, p: Player, game: Deity, discount: int = 0):
        faith_cost = 2 - discount
        game.print()
        print(self.faith_description)
        if p.faith < faith_cost:
            print(f'Not enough faith (you need {faith_cost} faith)')
            raise NotEnoughFaith

        while True:
            confirm = input(f'\nUse Foresight and for 2 faith (y/n)? ')
            try:
                confirm = confirm.lower()
                assert confirm in ['y', 'n']
                break
            except AssertionError:
                print('Not valid answer')
                continue

        if confirm == 'n':
            raise ReturnError

        p.additional_action['add'] += 2
        print(f'{p.name} has 1 additional actions next 2 turns')
        p.faith -= faith_cost
        print(f'{p.name} has {p.faith} faith left')

    def get_info(self):
        info = super().get_info()
        info += '\nPassive Abilities'
        info += self.passive_description_1
        info += self.passive_description_2
        info += '\nFaith Abilities'
        info += self.faith_description
        return info

    def take_damage(self, attacker: Character, game: Deity,
                    attacking_player: Player, damage: int = 1):
        mother_love = self._check_mothers_love(attacker, game,
                                               attacking_player, damage)
        if not mother_love:
            self.health -= damage
            print(f'\n{attacker} attacked {self}')

            attacker_coord = game.board.get_char_location(attacker)
            self_coord = game.board.get_char_location(self)
            dis = distance(attacker_coord, self_coord)
            if dis > 1:
                attacker.health -= 1
                attacker.passive_ability('take_damage_attack',
                                         attacking_player, game)
                print(f'Athena uses Aegis and retaliated 1 '
                      f'damage to {attacker}')
                if attacker.health > 0:
                    print(f'{attacker} has {attacker.health} health left')
                else:
                    print(f'{attacker} is killed!!!')

            if self.health > 0:
                print(f'{self} has {self.health} health left\n')
            else:
                print(f'{self} is killed!!!\n')

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


def get_next_coord(coord: Tuple[int, int], direction: str) -> Tuple[int, int]:
    """
    Returns coordinate that is adjacent to coord in certain direction.

    direction must be 'up', 'down', 'left' or 'right'

    :param coord: Coordinate
    :param direction: Direction of coordinate
    :return: Coordinate that corresponds to the adjacent coordinate in that direction
    """
    x = coord[0]
    y = coord[1]
    if direction == 'up':
        return x, y - 1
    elif direction == 'down':
        return x, y + 1
    elif direction == 'left':
        return x - 1, y
    elif direction == 'right':
        return x + 1, y


if __name__ == '__main__':
    a = Athena_Goddess_of_Wisdom(10)
    print(a.get_info())
