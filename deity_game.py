from deity_board import Board
from deity_character import Character
from deity_error import *
from deity_setting import *
from typing import List, Tuple, Dict, Union
from random import shuffle

POSSIBLE_ACTION = {'move', 'spell', 'attack', 'info', 'skip'}


class Player:
    name: str
    character: Dict[int, Character]
    number: int
    faith: int
    tile_deck = TILE_DECK.copy()

    def __init__(self, name, number):
        self.name = name
        self.character = {}
        self.number = number
        self.faith = 0

    def add_character(self, character: Character) -> None:
        if len(self.character) < MAX_CHARACTER:
            self.character[character.id] = character

    def print(self) -> None:
        result = f'{self.name} (Faith: {self.faith})\n    '
        for i in self.character:
            result += f'{i}: {self.character[i]}  '
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


class Deity:
    def __init__(self):
        self.turn = 0
        self.board = Board(BOARD_WIDTH, BOARD_HEIGHT)

        # Create Players
        p1_name = input('Enter name of player 1: ')
        self.player1 = Player(p1_name, 1)
        p2_name = input('Enter name of player 2: ')
        self.player2 = Player(p2_name, 2)

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
            action_left = MOVES_PER_TURN
            self.add_faith(p)
            self.destroy_base(p)
            if self.check_win():
                break

            while action_left != 0:
                print(f'\n{p.name}: {action_left} action remaining')
                while True:
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
                        except NoCharacterToMove:
                            continue

                    # Attack using character
                    elif action == 'attack':
                        try:
                            self.attack(p)
                            action_left -= 1
                            break
                        except (NoCharacterToAttack, ReturnError):
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

            # Reset characters
            if self.check_win() is not None:
                break

            # End of turn mechanism
            self.place_tile(p)
            self.turn += 1
            print('Next player turn')
        print(f'{self.check_win().name.upper()} IS THE WINNER')

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
            except IndexError:
                print('Not valid id')
                continue
            except ValueError:
                print('Please type in deity id')
                continue

    def attack(self, p: Player):
        char_attack = p.can_attack()

        if len(char_attack) == 0:
            print('No deities can attack')
            raise NoCharacterToAttack
        self.print()
        while True:
            # Ask which character used to attack
            print('\nDeities that can attack:')
            char_string = ' '
            for char in char_attack:
                char_string += f"{char.id} - {char} " \
                               f"(range: {char.range})       "
            print(char_string)

            char_id = input('Pick a deity to attack '
                            '(type deity id or cancel):')
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
            if curr_char not in char_attack:
                print('Not a valid deity, pick again')
                continue

            # Get range and coordinates of character
            p1_coord = self.board.get_char_location(curr_char)
            range_ = curr_char.range
            if self.board.get_tile(p1_coord).terrain == 'fort':
                range_ += 1

            # Check if character is in range to attack other character
            opponent = self.opponent(p)
            opponent_in_range = []
            for char in opponent.live_character():
                p2_coord = self.board.get_char_location(char)
                if _distance(p1_coord, p2_coord) <= range_:
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
                attack_message += f"{char.id} - {char}    "
            print(attack_message)

            attack_id = input('Pick deity to attack (type id or cancel): ')
            attack_id = attack_id.lower()
            if attack_id == 'cancel':
                raise ReturnError

            try:
                attack_id = int(attack_id)
                opponent_char = opponent.character[attack_id]
            except ValueError:
                print('Please type deity id')
                continue
            except IndexError:
                print('Not valid id, please type again')
                continue
            break

        # Attack target
        curr_char.attack(opponent_char)
        curr_char.has_attack = True

    def move(self, p: Player) -> None:
        char_move = p.can_move()

        # Check if available characters to move
        if len(char_move) == 0:
            print('No deities can move')
            raise NoCharacterToMove

        # Ask for player for character to move
        while True:
            self.print()
            print('\nDeities to move:')
            char_string = ' '
            for char in char_move:
                char_string += f"{char.id} - {char} " \
                               f"(movement: {char.movement})        "
            print(char_string)
            char_id = input('Pick a deity to move (type '
                            'id): ')
            try:
                curr_char = p.character[int(char_id)]
            except KeyError:
                print('Not a valid deity, pick again')
                continue
            except ValueError:
                print('Please type deity id')
                continue

            if curr_char not in char_move:
                print('Not a valid deity, pick again')
                continue
            break

        self.print()
        movement_left = curr_char.movement
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
                move_to = _turn_into_coordinate(move_to)

                # Check if chosen coord is adjacent to character
                if move_to not in adjacent:
                    print('\nNot valid move')
                    continue

                # Check tile terrain and if character can move to it
                tile_terrain = self.board.get_terrain(move_to)
                if tile_terrain == 'mountain' and not curr_char.fly:
                    print(
                        f"\n{curr_char} can't fly, only flying deity "
                        f"can enter mountain tile")
                    continue
                elif tile_terrain == 'water' and \
                        not curr_char.fly and not curr_char.swim:
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
                p1_base = _turn_into_coordinate(p1_base)
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
                p2_base = _turn_into_coordinate(p2_base)
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
            except ValueError:
                print('\nPlease type integers only (e.g 1, 7)')

    def choose_character(self) -> None:
        subclass = Character.__subclasses__()
        for i in range(MAX_CHARACTER):
            p1_character, subclass = _list_character_remaining(subclass,
                                                               self.player1)
            self.player1.add_character(p1_character(i + 1))

            p2_character, subclass = _list_character_remaining(subclass,
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
                    tile = _turn_into_coordinate(tile)
                    self.board.spawn_character(character, tile, player.number)
                    base_tiles_left.remove(tile)
                    self.board.print()
                    break
                except NotValidSpawn:
                    print('Not valid spawn point, '
                          'Deity must spawn in your base')
                except TileAlreadyHaveCharacter:
                    print("Tile already have deity, "
                          "choose another spawn point")

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
                    coord = _turn_into_coordinate(coord)
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


# === Helper Functions ===

def _list_character_remaining(subclass: List[Character], player: Player) -> \
        Tuple[Character, List[Character]]:
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
        remaining_class += f'{subclass[id_].__name__} -- {id_} \n'
    print(remaining_class)

    while True:
        try:
            char_index = int(input(f'{player.name} choose deity '
                                   f'(Type number): \n'))
            character = subclass[char_index]
            subclass.remove(subclass[char_index])
            return character, subclass
        except (IndexError, ValueError):
            print('Please choose a valid deity')
            continue


def _turn_into_coordinate(coord_str: str) -> Tuple[int, int]:
    """
    Used to change player input of coordinate from string to tuple

    :param coord_str: String version of coordinate separated by comma (e.g 1,2)
    :return: Return tuple representation of coordinate (e.g (1,2))
    """
    coord_str = coord_str.replace(' ', '')
    coord_str = coord_str.split(',')
    coord_tuple = (int(coord_str[0]), int(coord_str[1]))
    return coord_tuple


def _distance(coord1: Tuple[int, int], coord2: Tuple[int, int]) -> int:
    x1 = coord1[0]
    y1 = coord1[1]
    x2 = coord2[0]
    y2 = coord2[1]
    x_dif = abs(x1 - x2)
    y_dif = abs(y1 - y2)
    return x_dif + y_dif


if __name__ == "__main__":
    d = Deity()
    b = Board()
    b.create_base_p1((1, 7))
    b.create_base_p2((0, 0))
    b.create_big_road(1, (1, 5))
    b.create_big_road(2, (1, 2))
    b.print()

    d.board = b
    d.choose_character()
    b.board[3][1].character = d.player1.character[1]
    b.board[4][1].character = d.player2.character[3]
    b.board[0][0].character = d.player1.character[2]
    b.board[1][1].character = d.player2.character[4]

    d.play(True)
