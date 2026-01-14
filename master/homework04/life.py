import pathlib
import random
import typing as tp

import pygame
from pygame.locals import *

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: tp.Tuple[int, int],
        randomize: bool = True,
        max_generations: tp.Optional[float] = None,
    ) -> None:

        self.rows, self.cols = size

        self.prev_generation = self.create_grid()

        self.curr_generation = self.create_grid(randomize=randomize)

        self.max_generations = max_generations

        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        """
        Создание списка клеток.

        Клетка считается живой, если ее значение равно 1, в противном случае клетка
        считается мертвой, то есть, ее значение равно 0.

        Parameters
        ----------
        randomize : bool
            Если значение истина, то создается матрица, где каждая клетка может
            быть равновероятно живой или мертвой, иначе все клетки создаются мертвыми.

        Returns
        ----------
        out : Grid
            Матрица клеток размером `rows` х `cols`.
        """
        grid = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                if randomize:

                    cell_value = random.randint(0, 1)
                else:

                    cell_value = 0
                row.append(cell_value)
            grid.append(row)
        return grid

    def get_neighbours(self, cell: Cell) -> Cells:
        """
        Вернуть список соседних клеток для клетки `cell`.

        Соседними считаются клетки по горизонтали, вертикали и диагоналям,
        то есть, во всех направлениях.

        Parameters
        ----------
        cell : Cell
            Клетка, для которой необходимо получить список соседей. Клетка
            представлена кортежем, содержащим ее координаты на игровом поле.

        Returns
        ----------
        out : Cells
            Список соседних клеток.
        """
        row, col = cell
        neighbours = []

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue

                neighbor_row = row + i
                neighbor_col = col + j

                if 0 <= neighbor_row < self.rows and 0 <= neighbor_col < self.cols:
                    neighbours.append(self.curr_generation[neighbor_row][neighbor_col])

        return neighbours

    def get_next_generation(self) -> Grid:
        """
        Получить следующее поколение клеток.

        Returns
        ----------
        out : Grid
            Новое поколение клеток.
        """
        new_grid = self.create_grid(randomize=False)

        for i in range(self.rows):
            for j in range(self.cols):
                current_cell = self.curr_generation[i][j]
                neighbours = self.get_neighbours((i, j))
                live_neighbours = sum(neighbours)

                if current_cell == 1:
                    if live_neighbours < 2 or live_neighbours > 3:
                        new_grid[i][j] = 0
                    else:
                        new_grid[i][j] = 1
                else:
                    if live_neighbours == 3:
                        new_grid[i][j] = 1
                    else:
                        new_grid[i][j] = 0

        return new_grid

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """

        self.prev_generation = [row[:] for row in self.curr_generation]

        self.curr_generation = self.get_next_generation()

        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """

        if self.max_generations is None:
            return False

        return self.generations >= self.max_generations

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return self.curr_generation != self.prev_generation

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.

        Формат файла: каждая строка - строка сетки, значения через пробел.
        Пример:
        0 1 0
        1 0 1
        0 1 0
        """
        with open(filename, "r") as f:
            lines = f.readlines()

        grid = []
        for line in lines:
            line = line.strip()
            if line:
                row = [int(x) for x in line.split()]
                grid.append(row)

        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        for row in grid:
            if len(row) != cols:
                raise ValueError("All rows must have the same length")

        game = GameOfLife(size=(rows, cols), randomize=False, max_generations=None)
        game.curr_generation = grid
        game.prev_generation = game.create_grid()

        return game

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.

        Формат файла: каждая строка - строка сетки, значения через пробел.
        """
        with open(filename, "w") as f:
            for row in self.curr_generation:
                line = " ".join(str(cell) for cell in row)
                f.write(line + "\n")


if __name__ == "__main__":

    game1 = GameOfLife(size=(20, 20), randomize=True, max_generations=None)
    print(f"Игра 1: ограничений поколений нет")
    print(f"Превышен лимит поколений? {game1.is_max_generations_exceeded}")

    game2 = GameOfLife(size=(20, 20), randomize=True, max_generations=100)
    print(f"\nИгра 2: ограничение {game2.max_generations} поколений")
    print(f"Превышен лимит поколений? {game2.is_max_generations_exceeded}")

    for _ in range(5):
        game2.step()

    print(f"После 5 шагов: поколение {game2.generations}")
    print(f"Превышен лимит поколений? {game2.is_max_generations_exceeded}")
