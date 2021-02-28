# Number of deity per player
MAX_CHARACTER = 2

# Size of board
BOARD_HEIGHT = 8
BOARD_WIDTH = 8

# Number of actions (move, attack, spell) each player has per turn
MOVES_PER_TURN = 2

# Deck composition
NUM_FORT = 4
NUM_WATER = 4
NUM_MOUNTAIN = 4
NUM_FOREST = 4
NUM_FAITH = 6
TILE_DECK = (['fort'] * NUM_FORT) + (['water'] * NUM_WATER) + \
            (['mountain'] * NUM_MOUNTAIN) + (['forest'] * NUM_FOREST) + \
            (['faith'] * NUM_FAITH)

# Number of tiles players draw at the ned of turn
NUM_TILE_PLACE = 3
