from typing import Tuple

def turn_into_coordinate(coord_str: str) -> Tuple[int, int]:
    """
    Used to change player input of coordinate from string to tuple

    :param coord_str: String version of coordinate separated by comma (e.g 1,2)
    :return: Return tuple representation of coordinate (e.g (1,2))
    """
    coord_str = coord_str.replace(' ', '')
    coord_str = coord_str.split(',')
    coord_tuple = (int(coord_str[0]), int(coord_str[1]))
    return coord_tuple


def distance(coord1: Tuple[int, int], coord2: Tuple[int, int]) -> int:
    x1 = coord1[0]
    y1 = coord1[1]
    x2 = coord2[0]
    y2 = coord2[1]
    x_dif = abs(x1 - x2)
    y_dif = abs(y1 - y2)
    return x_dif + y_dif
