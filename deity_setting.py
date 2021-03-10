# Number of deity per player (max 4)
MAX_CHARACTER = 3

# Size of board
BOARD_HEIGHT = 8
BOARD_WIDTH = 8

# Number of actions (move, attack, spell) each player has per turn
MOVES_PER_TURN = 2

# Number of tiles players draw at the end of turn
NUM_TILE_PLACE = 2

# Player 1 deck composition (30 max)
NUM_FORT_1 = 4
NUM_WATER_1 = 4
NUM_CLOUD_1 = 4
NUM_FOREST_1 = 4
NUM_FAITH_1 = 6
P1_TILE_DECK = (['fort'] * NUM_FORT_1) + (['water'] * NUM_WATER_1) + \
            (['cloud'] * NUM_CLOUD_1) + (['forest'] * NUM_FOREST_1) + \
            (['faith'] * NUM_FAITH_1)

# Player 2 deck composition (30 max)
NUM_FORT_2 = 4
NUM_WATER_2 = 4
NUM_CLOUD_2 = 4
NUM_FOREST_2 = 4
NUM_FAITH_2 = 6
P2_TILE_DECK = (['fort'] * NUM_FORT_2) + (['water'] * NUM_WATER_2) + \
            (['cloud'] * NUM_CLOUD_2) + (['forest'] * NUM_FOREST_2) + \
            (['faith'] * NUM_FAITH_2)

