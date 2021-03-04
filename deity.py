from deity_game import Deity
from deity_board import Board


def main_game():
    Deity().play()


def preset_game():
    d = Deity()
    b = Board()

    b.create_base_p1((1, 7))
    b.create_base_p2((5, 0))
    b.create_big_road(1, (2, 5))
    b.create_big_road(2, (5, 2))

    d.board = b
    d.choose_character()
    b.board[6][1].character = d.player1.character[1]
    b.board[6][2].character = d.player1.character[2]
    b.board[1][5].character = d.player2.character[3]
    b.board[1][6].character = d.player2.character[4]
    d.print()
    d.play(True)


def ragnarok():
    d = Deity()
    b = Board()
    b.create_base_p1((1, 7))
    b.create_base_p2((6, 0))
    b.create_big_road(1, (1, 5))
    b.create_big_road(2, (6, 2))
    b.testing_fill_board((0, 0))

    d.board = b
    d.choose_character()
    b.board[3][3].character = d.player1.character[1]
    b.board[4][3].character = d.player2.character[3]
    b.board[1][3].character = d.player1.character[2]
    b.board[1][1].character = d.player2.character[4]
    d.print()
    d.play(True)


if __name__ == '__main__':
    scenario = {1: main_game, 2: preset_game, 3: ragnarok}
    print('Available game scenarios:')
    for id_, game_mode in scenario.items():
        print(f'{id_} - {game_mode.__name__}')

    while True:
        scenario_id = input('Chose game scenarios (type id): ')
        try:
            print('')
            game = scenario[int(scenario_id)]
            break
        except (KeyError, ValueError):
            print('Not valid scenario, try again')
            continue

    game()
