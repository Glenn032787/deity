from deity_board import Board
from deity_character import Character
from deity_error import *
from deity_setting import *
from deity_helper_function import *

from typing import List, Tuple, Dict, Union, Callable
from random import shuffle

POSSIBLE_ACTION = {'move', 'spell', 'attack', 'info', 'skip'}
PASSIVE_ABILITY_TRIGGER = ['start_turn', 'collect_faith', 'after_movement',
                           'take_damage_attack', 'take_damage_spell', 'end_turn']


class Player:
    name: str
    character: Dict[int, Character]
    number: int
    faith: int
    tile_deck = list

    def __init__(self, name, number):
        self.name = name
        self.character = {}
        self.number = number
        self.faith = 0
        self.tile_deck = []
        self.additional_action = {'add': 0, 'sub': 0}

    def add_character(self, character: Character) -> None:
        if len(self.character) < MAX_CHARACTER:
            self.character[character.id] = character

    def print(self) -> None:
        result = f'{self.name} (Faith: {self.faith})\n    '
        live = self.live_character()
        for i in self.character:
            if self.character[i] in live:
                result += f'{i}: {self.character[i]} ' \
                          f'({self.character[i].health}/{self.character[i].max_health})  '
        print(result)

    def can_move(self):
        char_move = []
        for char in self.live_character():
            if not char.has_moved:
                char_move.append(char)
        return char_move

    def can_attack(self):
        char_attack = []
        for char in self.live_character():
            if not char.has_attack:
                char_attack.append(char)
        return char_attack

    def can_spell(self):
        char_spell = []
        for char in self.live_character():
            if not char.has_spell:
                char_spell.append(char)
        return char_spell

    def live_character(self) -> List[Character]:
        live = []
        for i in self.character:
            if self.character[i].is_live():
                live.append(self.character[i])
        return live

    def dead_character(self) -> List[Character]:
        dead = []
        for i in self.character:
            if not self.character[i].is_live():
                dead.append(self.character[i])
        return dead

    def reset_character(self):
        for char in self.live_character():
            char.has_moved = False
            char.has_spell = False
            char.has_attack = False

    def reduce_status_effect(self) -> None:
        for char in self.live_character():
            for effect in char.get_status_effects():
                if char.status_effect == 1:
                    print(f'{char} is no longer {effect}')
                char.status_effect[effect] -= 1

    def get_additional_action(self) -> int:
        action = 0
        if self.additional_action['add'] > 0:
            action += 1
            self.additional_action['add'] -= 1

        if self.additional_action['sub'] > 0:
            action -= 1
            self.additional_action['sub'] -= 1
        return action

class Deity:
    def __init__(self):
        self.turn = 0
        self.ragnarok = False
        self.ragnarok_timer = None

        self.board = Board(BOARD_WIDTH, BOARD_HEIGHT)

        # Create Players
        p1_name = input('Enter name of player 1: ')
        self.player1 = Player(p1_name, 1)
        self.player1.tile_deck = P1_TILE_DECK
        p2_name = input('Enter name of player 2: ')
        self.player2 = Player(p2_name, 2)
        self.player2.tile_deck = P2_TILE_DECK

    def play(self, test: bool = False):
        # Set up game
        # Choose characters, base tiles and road tiles
        # Spawn characters on base
        if not test:
            self.set_up()

        while True:
            p = self.player_turn()

            # Start of turn mechanism
            p.reset_character()
            action_left = MOVES_PER_TURN + p.get_additional_action()
            self.destroy_base(p)
            self.passive('start_turn')
            if self.check_win():
                break

            # Player makes their actions
            while action_left != 0:
                self.print()
                print(f'\n{p.name}: {action_left} action remaining')
                while True:
                    self.remove_character()  # Removes dead character
                    action = input('Choose action (move, '
                                   'attack, spell, info, skip): ')
                    action = action.lower()
                    # Check if possible action
                    if action not in POSSIBLE_ACTION:
                        print('Not possible action')
                        continue

                    # Move Character
                    if action == 'move':
                        try:
                            self.move(p)
                            action_left -= 1
                            break
                        except (NoCharacterToMove, ReturnError):
                            continue

                    # Attack using character
                    elif action == 'attack':
                        try:
                            self.attack(p)
                            action_left -= 1
                            break
                        except (NoCharacterToAttack, ReturnError):
                            continue

                    # Use faith ability
                    elif action == 'spell':
                        try:
                            self.spell(p)
                            action_left -= 1
                            break
                        except (NoCharacterToSpell, ReturnError):
                            continue

                    # Get info on character (Doesn't use an action)
                    elif action == 'info':
                        self.info()
                        print(f'\n{p.name}: {action_left} action remaining')

                    # Skip action (Will have no remaining action)
                    elif action == 'skip':
                        action_left = 0
                        break

                if self.check_win() is not None:
                    break

            if self.check_win() is not None:
                break

            # End of turn mechanics
            self.passive('end_turn')
            self.place_tile(p)
            self.add_faith(p)
            p.reduce_status_effect()
            self.shrink_board()  # Shrink board if ragnarok
            self.start_ragnarok()  # Start ragnarok if board is full
            self.turn += 1
            print('Next player turn')

        # End of game
        print(f'{self.check_win().name.upper()} IS THE WINNER')

    def shrink_board(self):
        if self.ragnarok and self.board.height > 2 and self.board.width > 2:
            if self.ragnarok_timer == 0:
                self.board.border_closing()
                self.ragnarok_timer = 1
                self.print()
                print('The border has shrunk!!!')
            else:
                self.ragnarok_timer -= 1

    def start_ragnarok(self):
        if self.board.check_full_board() and not self.ragnarok:
            print('\nRagnarok has started, the board will shrink '
                  'after each round!!!\n')
            self.ragnarok = True
            self.ragnarok_timer = 1

    def info(self):
        self.print()
        all_char = dict(self.player1.character)
        all_char.update(self.player2.character)
        while True:
            deity_id = input('Which deity do you want info for? (type id): ')
            try:
                char = all_char[int(deity_id)]
                print(char.get_info())
                break
            except (IndexError, KeyError):
                print('Not valid id')
                continue
            except ValueError:
                print('Please type in deity id')
                continue

    def spell(self, p: Player):
        char_spell = p.can_spell()

        if len(char_spell) == 0:
            print('No deities can attack')
            raise NoCharacterToSpell
        self.print()
        while True:
            # Ask which character used to attack
            print('\nDeities that can use their faith ability:')
            char_string = ' '
            for char in char_spell:
                char_string += f"{char.id} - {char}         "
            print(char_string)

            char_id = input('Pick a deity to use faith ability '
                            '(type deity id or cancel): ')
            char_id = char_id.lower()
            if char_id == 'cancel':
                raise ReturnError
            # Check if valid character input
            try:
                curr_char = p.character[int(char_id)]
            except KeyError:
                print('Not a valid deity, pick again')
                continue
            except ValueError:
                print('Please type deity id')
                continue
            if curr_char not in char_spell:
                print('Not a valid deity, pick again')
                continue
            if 'stun' in curr_char.get_status_effects():
                self.print()
                print(f'\n{curr_char} is stun')
                continue
            if 'mummified' in curr_char.get_status_effects():
                self.print()
                print(f'\n{curr_char} is mummified for '
                      f'{curr_char.status_effect["mummified"]} turns')
                continue

            coord = self.board.get_char_location(curr_char)
            tile = self.board.get_tile(coord)
            opponent = self.opponent(p)
            try:
                before_spell_char = opponent.live_character()
                if curr_char.attribute == 'aquatic' and tile.terrain == 'water':
                    curr_char.faith_ability(p, self, 1)  # 1 faith discount
                    tile.terrain = 'empty'
                else:
                    curr_char.faith_ability(p, self)
                curr_char.has_spell = True

                # Prints deity which has been killed during
                after_spell_char = opponent.live_character()
                for live_char in before_spell_char:
                    if live_char not in after_spell_char:
                        print(f'{live_char} has been killed')
                break
            except (NotEnoughFaith, ReturnError, FaithAbilityError):
                continue

    def attack(self, p: Player):
        char_attack = p.can_attack()

        if len(char_attack) == 0:
            print('No deities can attack')
            raise NoCharacterToAttack
        self.print()
        # Ask which character used to attack
        while True:
            print('\nDeities that can attack:')
            char_string = ' '
            for char in char_attack:
                char_string += f"{char.id} - {char} " \
                               f"(range: {char.range})       "
            print(char_string)

            char_id = input('Pick a deity to attack '
                            '(type deity id or cancel): ')
            char_id = char_id.lower()
            if char_id == 'cancel':
                raise ReturnError
            # Check if valid character input
            try:
                curr_char = p.character[int(char_id)]
                assert curr_char in p.live_character()
            except (KeyError, ValueError, AssertionError):
                self.print()
                print('Not a valid deity, pick again')
                continue

            if curr_char not in char_attack:
                print('Not a valid deity, pick again')
                continue

            if 'disarm' in curr_char.get_status_effects():
                self.print()
                print(f'{curr_char} is disarmed this turn')
                continue

            if 'stun' in curr_char.get_status_effects():
                self.print()
                print(f'\n{curr_char} is stun')
                continue

            if 'mummified' in curr_char.get_status_effects():
                self.print()
                print(f'\n{curr_char} is mummified for '
                      f'{curr_char.status_effect["mummified"]} turns')
                continue

            # Get range and coordinates of character
            p1_coord = self.board.get_char_location(curr_char)
            range_ = curr_char.range
            terrain = self.board.get_tile(p1_coord).terrain

            if (terrain == 'fort' or terrain == 'base') and \
                    curr_char.attribute != 'flight':
                range_ += 1

            # Check if character is in range to attack other character
            opponent = self.opponent(p)
            opponent_in_range = []
            for char in opponent.live_character():
                p2_coord = self.board.get_char_location(char)
                if distance(p1_coord, p2_coord) <= range_:
                    opponent_in_range.append(char)

            if len(opponent_in_range) == 0:
                self.print()
                print(f"\n{curr_char} can't target anyone right now")
                continue

            break

        # Ask which character to target
        while True:
            self.print()
            print(f'\nDeities in range of {curr_char}: ')
            attack_message = "  "
            for char in opponent_in_range:
                attack_message += f"{char.id} - {char} (Health:{char.health})    "
            print(attack_message)

            attack_id = input('Pick deity to attack (type id or cancel): ')
            attack_id = attack_id.lower()
            if attack_id == 'cancel':
                raise ReturnError

            try:
                attack_id = int(attack_id)
                opponent_char = opponent.character[attack_id]
                assert opponent_char in opponent.live_character()
            except (ValueError, IndexError, AssertionError):
                print('Not valid id, please type again')
                continue
            break

        # Attack target
        curr_char.attack(opponent_char, self, p)

    def move(self, p: Player) -> None:
        char_move = p.can_move()

        # Check if available characters to move
        if len(char_move) == 0:
            print('No deities can move')
            raise NoCharacterToMove

        self.print()
        # Ask for player for character to move
        while True:
            print('\nDeities to move:')
            char_string = ' '
            for char in char_move:
                char_string += f"{char.id} - {char} " \
                               f"(movement: {char.movement})        "
            print(char_string)
            char_id = input('Pick a deity to move (type '
                            'id or cancel): ')
            if char_id == 'cancel':
                raise ReturnError

            try:
                curr_char = p.character[int(char_id)]
            except (KeyError, ValueError):
                self.print()
                print('Not a valid deity id, pick again')
                continue

            if curr_char not in char_move:
                self.print()
                print('Not a valid deity, pick again')
                continue

            if 'stun' in curr_char.get_status_effects():
                self.print()
                print(f'\n{curr_char} is stun')
                continue

            if 'mummified' in curr_char.get_status_effects():
                self.print()
                print(f'\n{curr_char} is mummified for '
                      f'{curr_char.status_effect["mummified"]} turns')
                continue
            break

        self.print()
        movement_left = curr_char.movement

        char_coord = self.board.get_char_location(curr_char)
        tile = self.board.get_tile(char_coord)
        if curr_char.attribute == 'flight' and tile.terrain == 'cloud':
            movement_left += 1

        if 'vigor' in curr_char.get_status_effects():
            print(f'\n{curr_char} has +1 movement')
            movement_left += 1
        if 'slowed' in curr_char.get_status_effects():
            print(f'\n{curr_char} has -1 movement')
            movement_left -= 1

        if 'grounded' in curr_char.get_status_effects():
            print(f'\n{curr_char} is grounded')
            movement_left = 1
        # Repeatedly ask player to move character based on character movement
        while movement_left > 0:
            # Get location of character and adjacent tiles
            char_coord = self.board.get_char_location(curr_char)
            adjacent = self.board.adjacent_tiles(char_coord)
            print(f'\n{curr_char} currently at {char_coord}')
            while True:

                # Ask which tile to move to
                print(f'Tiles to move: {adjacent}')
                move_to = input(f'{movement_left} moves left, '
                                f'pick a tile to move to (skip to stop moving): ')
                if move_to == 'skip':
                    movement_left = 0
                    break
                try:
                    move_to = turn_into_coordinate(move_to)
                except ValueError:
                    print('Not valid move')

                # Check if chosen coord is adjacent to character
                if move_to not in adjacent:
                    print('\nNot valid move')
                    continue

                # Check tile terrain and if character can move to it
                tile_terrain = self.board.get_terrain(move_to)
                if tile_terrain == 'cloud' and \
                        curr_char.attribute != 'flight' and \
                        'mobile' not in curr_char.get_status_effects():
                    print(
                        f"\n{curr_char} can't fly, only flying deity "
                        f"can enter cloud tile")
                    continue
                elif tile_terrain == 'water' and \
                        curr_char.attribute not in ['flight', 'aquatic'] and \
                        'mobile' not in curr_char.get_status_effects():
                    print(
                        f"\n{curr_char} can't fly or swim, only "
                        f"flying or swimming deity can "
                        f"enter water tile")
                    continue
                elif tile_terrain == 'forest' and movement_left != 1:
                    while True:
                        confirm = input(
                            f"\n{curr_char} is entering forest, it won't be "
                            f"able to move anymore this turn, confirm movement "
                            f"(y/n)?")
                        confirm = confirm.lower()
                        if confirm not in ['y', 'n']:
                            print('Type "y" or "n" only')
                            continue
                        break
                    if confirm == 'n':
                        continue
                    elif confirm == 'y':
                        self.board.move_character(curr_char,
                                                  move_to)
                        movement_left = 0
                        break
                else:
                    # Move the character to the coordinate
                    try:
                        self.board.move_character(curr_char,
                                                  move_to)
                        movement_left -= 1
                        self.print()
                        break
                    except CharacterBlocking:
                        print(
                            f'\nNot valid move, another '
                            f'deity already is on {move_to}')
                        continue
                    except NotValidMove:
                        print('\nNot valid move')
                        continue
                break
            curr_char.passive_ability('after_movement', self.player_turn(),
                                      self)
            curr_char.has_moved = True

    def set_up(self) -> None:
        # Both player choose characters
        self.choose_character()

        # Create Board
        self.board.print()

        # Set up bases for player 1 and 2
        self.set_up_base()
        self.board.print()

        # Set up road for player 1
        self.set_up_road(self.player1)
        self.board.print()

        # Set up road for player 2
        self.set_up_road(self.player2)
        self.board.print()

        # Spawn characters
        self.spawn_character(self.player1)
        self.spawn_character(self.player2)

    def set_up_base(self) -> None:
        while True:
            try:
                p1_base = input(f'{self.player1.name} (P1) choose '
                                f'base (separate x, y by comma): ')
                p1_base = turn_into_coordinate(p1_base)
                self.board.create_base_p1(p1_base)
                break
            except IndexError:
                print('Type two integers separated by comma (e.g 1, 7)')
                continue
            except ValueError:
                print('Please type integers only (e.g 1, 7)')
                continue
            except NotPossibleBase:
                error = 'Not possible base, please pick again \n' \
                        '   Player 1 base must be on bottom row \n'
                print(error)
                continue

        while True:
            try:
                p2_base = input(f'{self.player2.name} (P2) choose base '
                                f'(separate x, y by comma): ')
                p2_base = turn_into_coordinate(p2_base)
                self.board.create_base_p2(p2_base)
                break
            except IndexError:
                print('Type two integers separated by comma (e.g 0, 5)')
                continue
            except ValueError:
                print('Please type integers only (e.g 1, 7)')
                continue
            except NotPossibleBase:
                error = 'Not possible base, please pick again \n' \
                        '   Player 2 base must be on top row \n'
                print(error)
                continue

    def set_up_road(self, player: Player) -> None:
        while True:
            try:
                road = input(f'{player.name} choose big road '
                             '(Can choose 1 or 2 points): ')
                road = road.replace(' ', '')
                road = road.split(',')
                if len(road) == 2:
                    coord = (int(road[0]), int(road[1]))
                    self.board.create_big_road(player.number, coord)
                    break
                elif len(road) == 4:
                    coord1 = (int(road[0]), int(road[1]))
                    coord2 = (int(road[2]), int(road[3]))
                    self.board.create_big_road(player.number, coord1, coord2)
                    break
                else:
                    print('Type 2 or 4 int')
            except NotPossibleRoad:
                print('\nInvalid road. Roads must be adjacent to base')
                continue
            except ValueError:
                print('\nPlease type integers only (e.g 1, 7)')
                continue

    def choose_character(self) -> None:
        subclass_p1 = []
        subclass_p2 = []
        for class_ in Character.__subclasses__():
            subclass_p1 += class_.__subclasses__()
            subclass_p2 += class_.__subclasses__()

        for i in range(MAX_CHARACTER):
            p1_character, subclass_p1 = self._list_character_remaining(
                subclass_p1,
                self.player1)
            self.player1.add_character(p1_character(i + 1))

            p2_character, subclass_p2 = self._list_character_remaining(
                subclass_p2,
                self.player2)
            self.player2.add_character(p2_character(i + 1 + MAX_CHARACTER))

    def spawn_character(self, player: Player) -> None:
        base_tiles_left = self.board.get_base_tile(player.number)
        for char in player.character:
            while True:
                try:
                    character = player.character[char]
                    print(f'\nAvailable space at {player.name} '
                          f'base: {base_tiles_left}')
                    tile = input(f'{player.name} choose base tile '
                                 f'to spawn {character}: ')
                    tile = turn_into_coordinate(tile)
                    self.board.spawn_character(character, tile, player.number)
                    base_tiles_left.remove(tile)
                    self.board.print()
                    break
                except NotValidSpawn:
                    print('Not valid spawn point, '
                          'Deity must spawn in your base')
                    continue
                except TileAlreadyHaveCharacter:
                    print("Tile already have deity, "
                          "choose another spawn point")
                    continue

    def check_win(self) -> Union[None, Player]:
        if len(self.player1.live_character()) == 0 \
                or self.board.check_dead_base(1) >= 3:
            return self.player2
        elif len(self.player2.live_character()) == 0 \
                or self.board.check_dead_base(2) >= 3:
            return self.player1
        else:
            return None

    def player_turn(self) -> Player:
        if self.turn % 2 == 0:
            return self.player1
        else:
            return self.player2

    def add_faith(self, player: Player) -> None:
        """
        Checks if player's deity is on a faith square, if so,
        add faith to player

        :param player: Player that is being checked
        :return: None (Add faith to player)
        """
        faith = 0
        for char in player.live_character():
            coord = self.board.get_char_location(char)
            if self.board.get_terrain(coord) == 'faith':
                char.passive_ability('collect_faith', player, self)
                faith += 1
                self.board.change_to_road(coord)  # Remove faith tile
        player.faith += faith

    def print(self) -> None:
        self.board.print()
        self.player1.print()
        self.player2.print()

    def place_tile(self, p: Player) -> None:
        # Get player's tile deck and shuffle the deck
        deck = p.tile_deck
        shuffle(deck)
        drawn = []

        for i in range(NUM_TILE_PLACE):
            try:
                drawn.append(deck.pop())
            except IndexError:
                pass

        while len(drawn) > 0:
            if self.board.check_full_board():
                num_faith = drawn.count('faith')
                print(f'The board is full, you have automatically '
                      f'picked up {num_faith} faith')
                p.faith += num_faith
                break
            tile_message = 'Tiles drawn:\n      '
            for i in range(len(drawn)):
                tile_message += f'{i} - {drawn[i]}     '
            while True:
                print(tile_message)
                tile_id = input('Pick tile to place (choose id): ')
                if tile_id == 'test':  # USED FOR TESTING (DELETE AFTER)
                    drawn = []
                    break
                try:
                    tile_id = int(tile_id)
                except ValueError:
                    print('Please type a number')
                    continue

                if tile_id not in range(len(drawn)):
                    print('Not valid tile, please choose again')
                    continue
                try:
                    tile_id = int(tile_id)
                except ValueError:
                    print('Please type the tile id ')
                    continue
                break
            if tile_id == 'test':  # USED FOR TESTING (DELETE AFTER)
                break
            tile = drawn[tile_id]
            drawn.pop(tile_id)
            while True:
                tile_final = input(f'Play tile as empty or {tile} '
                                   f'(type empty or {tile}): ')
                if tile_final not in [tile, 'empty']:
                    print('Not valid choice, please choose again')
                    continue
                break
            while True:
                try:
                    self.print()
                    coord = input(f'Choose coordinate to place {tile_final} '
                                  '(must be adjacent to another tile): ')
                    coord = turn_into_coordinate(coord)
                    if not self.board.valid_tile_placement(coord):
                        print('Not valid tile placement, must be adjacent '
                              'to an existing tile')
                        continue
                except IndexError:
                    print('Type two integers separated by comma (e.g 1, 7)')
                    continue
                except ValueError:
                    print('Please type integers only (e.g 1, 7)')
                    continue

                try:
                    self.board.add_terrain(coord, tile_final)
                    self.print()
                    break
                except TilePlacementInvalid:
                    print(f'Not valid tile placement, there is already '
                          f'a tile at {coord}')
                    continue

    def opponent(self, p: Player) -> Player:
        if p.number == 1:
            return self.player2
        else:
            return self.player1

    def destroy_base(self, p: Player) -> None:
        opponent = self.opponent(p)
        for char in p.live_character():
            coord = self.board.get_char_location(char)
            tile = self.board.get_tile(coord)
            if tile.player_base == opponent.number:
                tile.dead_base = True

    def remove_character(self) -> None:
        char_board = self.board.get_character_on_board()
        for char in char_board:
            if not char.is_live():
                self.board.remove_character(char)

    def passive(self, time: str):
        p = self.player_turn()
        all_char = self.player1.live_character() + self.player2.live_character()

        for char in all_char:
            if 'mummified' in char.get_status_effects():
                continue
            char.passive_ability(time, p, self)

    # HELPER FUNCTIONS
    def _list_character_remaining(self, subclass: List[Character],
                                  player: Player) -> \
            Tuple[Callable, List[Character]]:
        """
        Helper function for Deity.choose_character. Print remaining
        subclasses (Deity) and prompt player to choose one of the characters.
        Return character class chosen and the remaining subclasses

        :param subclass: Remaining subclass that the Player will choose from
        :param player: Player choosing the subclass
        :return: Character class chosen by player and remaining subclasses
        """
        remaining_class = '\nAvailable Deities\n'
        for id_ in range(len(subclass)):
            remaining_class += f'{id_} -- {subclass[id_].__name__.replace("_", " ")}  \n'
        print(remaining_class)

        current_char = ''
        for i in self.player1.character:
            current_char += str(self.player1.character[i]) + ', '
        current_char = current_char[:-2]

        print(f'{self.player1.name} team: {current_char}')

        current_char = ''
        for i in self.player2.character:
            current_char += str(self.player2.character[i]) + ', '
        current_char = current_char[:-2]

        print(f'{self.player2.name} team: {current_char}')
        while True:
            try:
                char_index = int(input(f'{player.name} choose deity '
                                       f'(Type number): '))
                character = subclass[char_index]
                subclass.remove(subclass[char_index])
                return character, subclass
            except (IndexError, ValueError):
                print('Please choose a valid deity')
                continue


if __name__ == "__main__":
    d = Deity()
    b = Board()
    b.create_base_p1((1, 7))
    b.create_base_p2((0, 0))
    b.create_big_road(1, (1, 5))
    b.create_big_road(2, (1, 2))
    b.print()
    d.player1.faith = 10
    d.player2.faith = 10
    d.board = b
    d.choose_character()
    d.print()
    b.board[7][1].character = d.player1.character[1]
    b.board[7][2].character = d.player1.character[2]
    b.board[6][1].character = d.player1.character[3]
    b.board[1][1].character = d.player2.character[4]
    b.board[1][0].character = d.player2.character[5]
    b.board[0][1].character = d.player2.character[6]

    d.play(True)
