from copy import deepcopy
from random import choice, randint
from typing import List, Optional, Tuple, Union, cast

import pandas as pd


def create_grid(rows: int = 15, cols: int = 15) -> List[List[str]]:
    """Создает начальную сетку лабиринта со стенами."""
    return [["■"] * cols for _ in range(rows)]


def remove_wall(grid: List[List[str]], coord: Tuple[int, int]) -> List[List[str]]:
    """Удаляет стену на указанной координате."""
    x, y = coord
    if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
        grid[x][y] = " "
    return grid


def bin_tree_maze(rows: int = 15, cols: int = 15, random_exit: bool = True) -> List[List[str]]:
    """Генерация лабиринта с помощью алгоритма двоичного дерева."""
    grid = create_grid(rows, cols)

    for x in range(1, rows, 2):
        for y in range(1, cols, 2):
            grid[x][y] = " "

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

    grid[x_in][y_in] = "X"
    grid[x_out][y_out] = "X"

    return grid


def get_exits(grid: List[List[str]]) -> List[Tuple[int, int]]:
    """Находит все выходы (клетки с 'X') в лабиринте."""
    exits = []
    for x, row in enumerate(grid):
        for y, cell in enumerate(row):
            if cell == "X":
                exits.append((x, y))
    return exits


def make_step(grid: List[List[Union[str, int]]], k: int) -> List[List[Union[str, int]]]:
    """Распространяет волну на один шаг."""
    rows, cols = len(grid), len(grid[0])
    new_grid = deepcopy(grid)

    for x in range(rows):
        for y in range(cols):
            cell = grid[x][y]

            if isinstance(cell, int) and cell == k:
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < rows and 0 <= ny < cols:
                        neighbor = grid[nx][ny]

                        if neighbor == " " or neighbor == "X":
                            new_grid[nx][ny] = k + 1

    return new_grid


def shortest_path(grid: List[List[Union[str, int]]], exit_coord: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """Находит кратчайший путь до выхода."""
    path = [exit_coord]
    x, y = exit_coord

    cell_value = grid[x][y]
    if not isinstance(cell_value, int):
        return None

    current_value = cell_value

    while current_value > 1:
        found = False
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                neighbor = grid[nx][ny]
                if isinstance(neighbor, int) and neighbor == current_value - 1:
                    path.append((nx, ny))
                    x, y = nx, ny
                    current_value -= 1
                    found = True
                    break

        if not found:
            break

    path.reverse()
    return path if len(path) > 1 else None


def encircled_exit(grid: List[List[str]], coord: Tuple[int, int]) -> bool:
    """Проверяет, окружен ли выход стенами."""
    x, y = coord
    rows, cols = len(grid), len(grid[0])

    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols:
            if grid[nx][ny] != "■":
                return False

    return True


def solve_maze(
    grid: List[List[str]],
) -> Tuple[List[List[Union[str, int]]], Optional[List[Tuple[int, int]]]]:
    """
    Решает лабиринт с помощью волнового алгоритма.

    :param grid: лабиринт (только строки)
    :return: кортеж (лабиринт с номерами шагов, путь или None)
    """

    exits = get_exits(grid)
    if len(exits) != 2:

        result_grid: List[List[Union[str, int]]] = [[cell for cell in row] for row in grid]
        return result_grid, None

    for exit_coord in exits:
        if encircled_exit(grid, exit_coord):

            result_grid: List[List[Union[str, int]]] = [[cell for cell in row] for row in grid]
            return result_grid, None

    wave_grid: List[List[Union[str, int]]] = [[cell for cell in row] for row in grid]

    start, end = exits[0], exits[1]

    wave_grid[start[0]][start[1]] = 1

    changed = True
    step = 1

    while changed:
        changed = False
        prev_grid = deepcopy(wave_grid)
        wave_grid = make_step(wave_grid, step)

        ex, ey = end
        end_cell = wave_grid[ex][ey]
        if isinstance(end_cell, int):

            path = shortest_path(wave_grid, end)
            return wave_grid, path

        if wave_grid != prev_grid:
            changed = True
            step += 1
        else:

            break

    return wave_grid, None


def add_path_to_grid(
    grid: List[List[str]],
    path: Optional[List[Tuple[int, int]]],
) -> List[List[str]]:
    """Добавляет путь в лабиринт."""
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

        display_maze = [[str(cell) for cell in row] for row in solved_maze]
        print(pd.DataFrame(display_maze))
