class NotPossibleBase(Exception):

    def __str__(self):
        error = 'Not possible base \n ' \
                'Player 1 base must be on bottom row \n ' \
                'Player 2 base must be on top row'

        return error


class NotPossibleRoad(Exception):
    def __str__(self):
        error = 'Not possible Road \nRoads must be adjacent to your base'
        return error


class NotValidSpawn(Exception):
    def __str__(self):
        error = "Not possible spawn point \n" \
                "Deities must be spawned in your base"
        return error


class TileAlreadyHaveCharacter(Exception):
    def __str__(self):
        error = "Tile already has character. \n " \
                "Can't move to a tile already with a character"
        return error


class NotValidMove(Exception):
    def __str__(self):
        error = "Not a valid move"
        return error


class CharacterBlocking(Exception):
    def __str__(self):
        error = "Can't move onto a tile that already has another character"
        return error


class TilePlacementInvalid(Exception):
    def __str__(self):
        error = "Unable to place tile at that position"
        return error


class NotValidTerrain(Exception):
    def __str__(self):
        error = "Terrain is not valid"
        return error


class NoCharacterToMove(Exception):
    def __str__(self):
        error = "No characters left to move"
        return error


class NoCharacterToAttack(Exception):
    def __str__(self):
        error = "No characters left to attack"
        return error


class ReturnError(Exception):
    def __str__(self):
        error = "Return to previous question"
        return error


class NotEnoughFaith(Exception):
    def __str__(self):
        error = 'Not enough faith for this ability'
        return error


class NoCharacterToSpell(Exception):
    def __str__(self):
        error = 'No characters left to use faith ability'
        return error


class FaithAbilityError(Exception):
    def __str__(self):
        error = 'Error in faith ability'
        return error


class NotValidStatusEffect(Exception):
    def __str__(self):
        error = 'Not a valid status effect'
        return error
