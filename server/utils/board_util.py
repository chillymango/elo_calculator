# TODO: if this ends up taking lots of time we should make this run in C++ or something


def check_line(
    arr: list[list[list[int]]],
    val: int,
    x: int,
    y: int,
    z: int,
    dx: int,
    dy: int,
    dz: int,
    board_size: int = 5
) -> bool:
    for i in range(board_size):
        new_x = x + i * dx
        new_y = y + i * dy
        new_z = z + i * dz
        if new_x < 0 or new_x >= board_size or new_y < 0 or new_y >= board_size or new_z < 0 or new_z >= board_size:
            return False
        if arr[new_x][new_y][new_z] != val:
            return False
    return True


def has_four_in_line(arr: list[list[list[int]]], val: int, board_size: int = 5):
    for x in range(0, board_size):
        for y in range(0, board_size):
            for z in range(0, board_size):
                if arr[x][y][z]:
                    if (
                        check_line(arr, val, val, x, y, z, 1, 0, 0),
                        check_line(arr, val, val, x, y, z, 0, 1, 0),
                        check_line(arr, val, val, x, y, z, 0, 0, 1),
                        check_line(arr, val, val, x, y, z, 1, 1, 0),
                        check_line(arr, val, val, x, y, z, 1, 0, 1),
                        check_line(arr, val, val, x, y, z, -1, 0, 1),
                        check_line(arr, val, val, x, y, z, 0, 1, 1),
                        check_line(arr, val, val, x, y, z, 1, 1, 1),
                        check_line(arr, val, val, x, y, z, -1, 1, 1),
                    ):
                        return True
    return False
