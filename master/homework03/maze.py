from copy import deepcopy
from random import choice, randint
from typing import List, Optional, Tuple, Union

import pandas as pd


def create_grid(rows: int = 15, cols: int = 15) -> List[List[Union[str, int]]]:
    return [["■"] * cols for _ in range(rows)]


def remove_wall(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> List[List[Union[str, int]]]:
    """
    Удаляет стену на указанной координате.

    :param grid: лабиринт
    :param coord: координаты (x, y) стены для удаления
    :return: обновленный лабиринт
    """
    x, y = coord
    if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
        grid[x][y] = " "
    return grid


def bin_tree_maze(rows: int = 15, cols: int = 15, random_exit: bool = True) -> List[List[Union[str, int]]]:
    """
    Генерация лабиринта с помощью алгоритма двоичного дерева.

    :param rows: количество строк
    :param cols: количество столбцов
    :param random_exit: если True - случайные вход/выход, иначе фиксированные
    :return: сгенерированный лабиринт
    """
    grid = create_grid(rows, cols)
    empty_cells = []

    for x, row in enumerate(grid):
        for y, _ in enumerate(row):
            if x % 2 == 1 and y % 2 == 1:
                grid[x][y] = " "
                empty_cells.append((x, y))

    for x in range(1, rows, 2):
        for y in range(1, cols, 2):
            directions = []

            if x - 2 >= 1:
                directions.append(("up", x - 2, y))
            if y + 2 < cols:
                directions.append(("right", x, y + 2))

            if directions:
                direction, next_x, next_y = choice(directions)

                if direction == "up":
                    remove_wall(grid, (x - 1, y))
                elif direction == "right":
                    remove_wall(grid, (x, y + 1))

    if random_exit:

        x_in = randint(0, rows - 1)
        x_out = randint(0, rows - 1)

        y_in = randint(0, cols - 1) if x_in in (0, rows - 1) else choice((0, cols - 1))
        y_out = randint(0, cols - 1) if x_out in (0, rows - 1) else choice((0, cols - 1))
    else:

        x_in, y_in = 0, 1
        x_out, y_out = rows - 1, cols - 2

    if grid[x_in][y_in] == "■":
        grid[x_in][y_in] = "X"
    if grid[x_out][y_out] == "■":
        grid[x_out][y_out] = "X"

    return grid


def get_exits(grid: List[List[Union[str, int]]]) -> List[Tuple[int, int]]:
    """
    Находит все выходы (клетки с 'X') в лабиринте.

    :param grid: лабиринт
    :return: список координат выходов
    """
    exits = []
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            if cell == "X":
                exits.append((x, y))
    return exits


def make_step(grid: List[List[Union[str, int]]], k: int) -> List[List[Union[str, int]]]:
    """
    Распространяет волну на один шаг.

    :param grid: лабиринт с номерами шагов
    :param k: текущий номер шага
    :return: обновленный лабиринт
    """
    rows, cols = len(grid), len(grid[0])
    new_grid = deepcopy(grid)

    for x in range(rows):
        for y in range(cols):
            if grid[x][y] == k:

                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < rows and 0 <= ny < cols:
                        if grid[nx][ny] == " " or grid[nx][ny] == "X":
                            new_grid[nx][ny] = k + 1

    return new_grid


def shortest_path(
    grid: List[List[Union[str, int]]], exit_coord: Tuple[int, int]
) -> Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]:
    """
    Находит кратчайший путь до выхода.

    :param grid: лабиринт с номерами шагов
    :param exit_coord: координаты выхода
    :return: список координат пути или None, если путь не найден
    """

    path = [exit_coord]
    x, y = exit_coord

    if isinstance(grid[x][y], int):
        current_value = grid[x][y]
    else:

        return None

    while current_value > 1:
        found = False
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                cell = grid[nx][ny]
                if isinstance(cell, int) and cell == current_value - 1:
                    path.append((nx, ny))
                    x, y = nx, ny
                    current_value -= 1
                    found = True
                    break

        if not found:
            break

    path.reverse()
    return path if len(path) > 1 else None


def encircled_exit(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> bool:
    """
    Проверяет, окружен ли выход стенами.

    :param grid: лабиринт
    :param coord: координаты выхода
    :return: True если выход окружен, иначе False
    """
    x, y = coord
    rows, cols = len(grid), len(grid[0])

    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols:
            if grid[nx][ny] != "■":
                return False

    return True


def solve_maze(
    grid: List[List[Union[str, int]]],
) -> Tuple[List[List[Union[str, int]]], Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]]:
    """
    Решает лабиринт с помощью волнового алгоритма.

    :param grid: лабиринт
    :return: кортеж (лабиринт с номерами шагов, путь или None)
    """

    exits = get_exits(grid)
    if len(exits) != 2:
        return grid, None

    for exit_coord in exits:
        if encircled_exit(grid, exit_coord):
            return grid, None

    wave_grid = deepcopy(grid)
    start, end = exits[0], exits[1]

    if wave_grid[start[0]][start[1]] == "X":
        wave_grid[start[0]][start[1]] = 1

    changed = True
    step = 1

    while changed:
        changed = False
        prev_grid = deepcopy(wave_grid)
        wave_grid = make_step(wave_grid, step)

        ex, ey = end
        if isinstance(wave_grid[ex][ey], int):

            path = shortest_path(wave_grid, end)
            return wave_grid, path

        if wave_grid != prev_grid:
            changed = True
            step += 1
        else:

            break

    return wave_grid, None


def add_path_to_grid(
    grid: List[List[Union[str, int]]],
    path: Optional[Union[Tuple[int, int], List[Tuple[int, int]]]],
) -> List[List[Union[str, int]]]:
    """
    Добавляет путь в лабиринт.

    :param grid: лабиринт
    :param path: путь (список координат)
    :return: лабиринт с отмеченным путем
    """
    if path:
        for i, j in path:
            grid[i][j] = "X"
    return grid


if __name__ == "__main__":

    print("Сгенерированный лабиринт:")
    maze = bin_tree_maze(15, 15)
    print(pd.DataFrame(maze))

    print("\nРешение лабиринта:")
    solved_maze, path = solve_maze(maze)

    if path:
        print(f"Найден путь длиной {len(path)} шагов")
        final_maze = add_path_to_grid(deepcopy(maze), path)
        print(pd.DataFrame(final_maze))
    else:
        print("Путь не найден")
        print(pd.DataFrame(solved_maze))
