from typing import Tuple, List, Union
from deity_character import Character
from deity_error import *

TERRAIN_TYPES = ['fort', 'forest', 'water',
                 'cloud', 'empty', 'base', 'faith']


class Tile:
    def __init__(self):
        self.character = None
        self.terrain = None

        # Always none unless self.terrain == 'base'
        self.player_base = None
        self.dead_base = None

        self.faith = False

    def __str__(self):
        if self.terrain is None:
            return 'None'
        return self.terrain

    def __repr__(self):
        if self.terrain is None:
            return 'None'
        return self.terrain


class Board:
    """
    Board which stores terrains and characters locations

    === Public Attribute ===
    width: Width of the board
    height: Height of the board

    """

    def __init__(self, width: int = 8, height: int = 8) -> None:
        """
        Creates new board object

        >>> b = Board()
        >>> b.width
        8
        >>> b.height
        8
        """
        # Metadata about board
        self.width = width
        self.height = height

        # Creates board with empty tiles
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(Tile())
            self.board.append(row)

    def print(self) -> None:
        """
        Print out the board
        """
        width = self.width
        height = self.height

        print('')
        print(" ", end='')
        for i in range(width):
            print(f' {i}', end='')
        print('')
        for i in range(height):
            print("--" * width + "-")
            print(i, end='')
            for j in range(width):
                if self.board[i][j].character is not None:
                    char_id = self.board[i][j].character.id
                    print(f"|{char_id}", end="")
                elif self.board[i][j].dead_base:
                    print("|X", end="")
                elif self.board[i][j].terrain == 'base':
                    print("|B", end="")
                elif self.board[i][j].terrain == 'empty':
                    print("|O", end="")
                elif self.board[i][j].terrain == 'fort':
                    print("|M", end="")
                elif self.board[i][j].terrain == 'forest':
                    print("|F", end="")
                elif self.board[i][j].terrain == 'water':
                    print("|W", end="")
                elif self.board[i][j].terrain == 'cloud':
                    print("|C", end="")
                elif self.board[i][j].terrain == 'faith':
                    print("|$", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * width + "-")
        print(' ', end='')
        for i in range(width):
            print(f' {i}', end='')
        print('')

    def add_terrain(self, coord: Tuple[int, int], terrain: str) -> None:
        """
        Mutates board by changing tile at coord to have terrain
        If tile is changed to faith, tile.faith will turn to True.
        Can only add terrain to empty tile

        :param coord: Coordinates as (X, Y)
        :param terrain: One of the terrain from TERRAIN_TYPES
        :return: Nothing (Mutates board to add terrain)

        >>> b = Board()
        >>> b.add_terrain((3, 4), 'fort')
        >>> b.board[4][3].terrain
        'fort'
        """
        if terrain not in TERRAIN_TYPES:
            # Check if terrain is possible terrain type
            raise NotValidTerrain

        if self.board[coord[1]][coord[0]].terrain is not None:
            # Check if something is already on that terrain
            raise TilePlacementInvalid
        self.board[coord[1]][coord[0]].terrain = terrain

        if terrain == 'faith':
            self.board[coord[1]][coord[0]].faith = True

    def get_terrain(self, coord: Tuple[int, int]) -> str:
        """
        Return terrain of tile in coord

        :param coord: Coordinates as (X, Y)
        :return: Terrain at coordinate

        >>> b = Board()
        >>> b.add_terrain((3, 4), 'fort')
        >>> b.get_terrain((3, 4))
        'fort'
        """
        t = self.board[coord[1]][coord[0]].terrain
        return t

    def get_char_location(self, char: Character) -> Tuple:
        """
        Return coordinates of a character

        :param char: Character  that you are trying to find
        :return: Coordinates of character you are trying to find
        """
        for i in range(self.height):
            for j in range(self.width):
                curr_char = self.board[i][j].character
                if curr_char is not None and curr_char == char:
                    return j, i
        # TODO No character found

    def adjacent_tiles(self, coord: Tuple[int, int]) -> List[Tuple]:
        x = coord[0]
        y = coord[1]

        adjacent = []
        if 0 <= x - 1 <= self.width - 1:
            adjacent.append((x - 1, y))
        if 0 <= x + 1 <= self.width - 1:
            adjacent.append((x + 1, y))
        if 0 <= y - 1 <= self.height - 1:
            adjacent.append((x, y - 1))
        if 0 <= y + 1 <= self.height - 1:
            adjacent.append((x, y + 1))
        return adjacent

    def possible_tile(self,
                      coord: Union[Tuple[int, int], List[Tuple]]) -> bool:
        if isinstance(coord, tuple):
            y = coord[1]
            x = coord[0]
            x_possible = (0 <= x <= self.width - 1)
            y_possible = (0 <= y <= self.height - 1)
            return x_possible and y_possible
        else:
            result = True
            for coordinates in coord:
                y = coordinates[1]
                x = coordinates[0]
                x_possible = (0 <= x <= self.width - 1)
                y_possible = (0 <= y <= self.height - 1)
                if not (x_possible and y_possible):
                    result = False
            return result

    def move_character(self, char: Character,
                       new_coord: Tuple[int, int]) -> None:
        # Check new_coord is within coordinate
        if not self.possible_tile(new_coord):
            raise NotValidMove

        old_coord = self.get_char_location(char)

        # Check if new_coord already has a character
        if self.board[new_coord[1]][new_coord[0]].character is not None:
            raise CharacterBlocking

        if self.board[new_coord[1]][new_coord[0]].terrain is None:
            raise NotValidMove

        self.board[old_coord[1]][old_coord[0]].character = None
        self.board[new_coord[1]][new_coord[0]].character = char

    def spawn_character(self, char: Character, coord: Tuple[int, int],
                        player: int) -> None:
        tile = self.board[coord[1]][coord[0]]
        if tile.terrain == 'base' and tile.player_base == player \
                and tile.character is None:
            tile.character = char
        else:
            if tile.terrain != 'base' or tile.player_base != player:
                raise NotValidSpawn
            elif tile.character is not None:
                raise TileAlreadyHaveCharacter

    def remove_character(self, char: Character) -> None:
        coord = self.get_char_location(char)
        self.board[coord[1]][coord[0]].character = None

    def create_base_p1(self, coord: Tuple[int, int]) -> None:
        """
        Add a 4x4 base with coord as the bottom left corner of base
        that is owned by player

        Precondition: player == 1 or player == 2

        :param coord: Bottom left coordinate of 4x4 base
        :return: None (mutates board)
        """
        x = coord[0]
        y = coord[1]

        # Player 1 must have base on bottom of board
        if y != self.height - 1:
            raise NotPossibleBase

        # Base must be within 0 and width-1
        # Coord is bottom left corner so it can't be
        # on right most column
        if not (0 <= x < self.width - 1):
            raise NotPossibleBase

        self._create_base_tile(x, y, 1)
        self._create_base_tile(x + 1, y, 1)
        self._create_base_tile(x, y - 1, 1)
        self._create_base_tile(x + 1, y - 1, 1)

    def create_base_p2(self, coord: Tuple[int, int]) -> None:
        """
        Add a 4x4 base with coord as the top left corner of base
        that is owned by player


        :param coord: Top left coordinate of 4x4 base
        :return: None (mutates board)
        """
        x = coord[0]
        y = coord[1]

        # Player 2 must have base on top of board
        if y != 0:
            raise NotPossibleBase

        # Base must be within 0 and width-1
        # Coord is bottom left corner so it can't be
        # on right most column
        if not (0 <= x < self.width - 1):
            raise NotPossibleBase

        self._create_base_tile(x, y, 2)
        self._create_base_tile(x + 1, y, 2)
        self._create_base_tile(x, y + 1, 2)
        self._create_base_tile(x + 1, y + 1, 2)

    def _create_base_tile(self, x, y, player):
        self.board[y][x].player_base = player
        self.board[y][x].dead_base = False
        self.board[y][x].terrain = 'base'

    def get_base_tile(self, player: int) -> List[Tuple]:
        base_tiles = []
        for i in range(self.height):
            for j in range(self.width):
                tile = self.board[i][j]
                if tile.terrain == 'base' and tile.player_base == player:
                    base_tiles.append((j, i))
        return base_tiles

    def _get_adjacent_base_tiles(self, player: int) -> List[Tuple]:
        base_tiles = self.get_base_tile(player)
        all_adjacent_tiles = set()
        for tile in base_tiles:
            # Get all tiles adjacent to base tile
            adjacent = self.adjacent_tiles(tile)

            # Check if adjacent tile that are bases
            for adjacent_tile in adjacent:
                if adjacent_tile not in base_tiles and self.possible_tile(
                        tile):
                    all_adjacent_tiles.add(adjacent_tile)
        return list(all_adjacent_tiles)

    def create_big_road(self, player: int, coord1: Tuple[int, int],
                        coord2: Tuple[int, int] = None) -> None:
        adjacent_tiles = self._get_adjacent_base_tiles(player)
        base_tiles = self.get_base_tile(player)

        if coord1 not in adjacent_tiles:
            raise NotPossibleRoad

        x1 = coord1[0]
        y1 = coord1[1]
        if coord2 is not None:
            if coord2 not in adjacent_tiles:
                raise NotPossibleRoad

            x2 = coord2[0]
            y2 = coord2[1]
            if y1 == y2 and abs(x1 - x2) == 1:
                # Two coordinates are horizontal (add road above or below)
                self.add_terrain(coord1, 'empty')
                self.add_terrain(coord2, 'empty')
                if player == 1:
                    self.add_terrain((x1, y1 - 1), 'empty')
                    self.add_terrain((x2, y2 - 1), 'empty')
                else:
                    self.add_terrain((x1, y1 + 1), 'empty')
                    self.add_terrain((x2, y2 + 1), 'empty')
            elif x1 == x2 and abs(y1 - y2) == 1:
                left = [(x1 - 1, y1), (x2 - 1, y2)]
                right = [(x1 + 1, y1), (x2 + 1, y2)]
                if self.possible_tile(left) and \
                        not (any(item in left for item in base_tiles)):
                    self.add_terrain(coord1, 'empty')
                    self.add_terrain(coord2, 'empty')
                    self.add_terrain(left[0], 'empty')
                    self.add_terrain(left[1], 'empty')
                elif self.possible_tile(right) and \
                        not (any(item in right for item in base_tiles)):
                    self.add_terrain(coord1, 'empty')
                    self.add_terrain(coord2, 'empty')
                    self.add_terrain(right[0], 'empty')
                    self.add_terrain(right[1], 'empty')
                else:
                    raise NotPossibleRoad
        else:
            square = self._get_valid_square(x1, y1, player)
            if square is None:
                raise NotPossibleRoad
            for tile in square:
                self.add_terrain(tile, 'empty')

    def _get_valid_square(self, x: int, y: int, player: int):
        s1 = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
        if self._check_valid_tiles(s1, player, (x, y)):
            return s1
        s2 = [(x, y), (x - 1, y), (x, y + 1), (x - 1, y + 1)]
        if self._check_valid_tiles(s2, player, (x, y)):
            return s2
        s3 = [(x, y), (x + 1, y), (x, y - 1), (x + 1, y - 1)]
        if self._check_valid_tiles(s3, player, (x, y)):
            return s3
        s4 = [(x, y), (x - 1, y), (x, y - 1), (x - 1, y - 1)]
        if self._check_valid_tiles(s4, player, (x, y)):
            return s4
        return None

    def _check_valid_tiles(self, tiles: List, player: int,
                           original_tile: Tuple[int, int]) -> bool:
        adjacent_tiles = self._get_adjacent_base_tiles(player)
        adjacent_tiles.remove(original_tile)
        base_tiles = self.get_base_tile(player)

        adjacent_check = not (any(item in tiles for item in adjacent_tiles))
        base_check = not (any(item in tiles for item in base_tiles))
        possible_check = self.possible_tile(tiles)
        return adjacent_check and base_check and possible_check

    def check_dead_base(self, player: int) -> int:
        base = self.get_base_tile(player)
        counter = 0
        for t in base:
            if self.board[t[1]][t[0]].dead_base:
                counter += 1
        return counter

    def change_to_road(self, coord: Tuple[int, int]) -> None:
        x = coord[0]
        y = coord[1]
        self.board[y][x].terrain = 'empty'

    def valid_tile_placement(self, coord: Tuple[int, int]) -> bool:
        adjacent = self.adjacent_tiles(coord)
        for c in adjacent:
            if self.board[c[1]][c[0]].terrain is not None:
                return True
        return False

    def get_tile(self, coord: Tuple[int, int]) -> Tile:
        return self.board[coord[1]][coord[0]]

    def get_character_on_board(self) -> List[Character]:
        char = []
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i][j].character is not None:
                    char.append(self.board[i][j].character)
        return char

    def check_full_board(self) -> bool:
        for i in range(self.height):
            for j in range(self.width):
                tile = self.board[i][j]
                if tile.terrain is None:
                    return False
        return True

    def border_closing(self) -> None:
        top_row = self.board[0]
        bottom_row = self.board[-1]

        for tile in top_row + bottom_row:
            if tile.character is not None:
                tile.character.health = 0

        self.board.pop(0)
        self.board.pop(-1)

        for row in self.board:
            if row[0].character is not None:
                row[0].character.health = 0
            if row[-1].character is not None:
                row[-1].character.health = 0
            row.pop(0)
            row.pop(-1)

        self.height = len(self.board)
        self.width = len(self.board[0])

    def testing_fill_board(self, missing: Tuple[int, int] = (-1, -1)):
        for i in range(self.height):
            for j in range(self.width):
                if (j, i) == missing:
                    continue
                self.board[i][j].terrain = 'empty'


if __name__ == '__main__':
    b = Board()
    b.create_base_p1((1, 7))
    b.create_base_p2((6, 0))
    b.create_big_road(1, (1, 5))
    b.create_big_road(2, (5, 0), (5, 1))
    b.print()
    b.testing_fill_board((3, 0))
    b.print()
