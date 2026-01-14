import pygame
from life import GameOfLife
from pygame.locals import *
from ui import UI


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.cell_size = cell_size
        self.speed = speed
        
        
        self.width = self.life.cols * cell_size
        self.height = self.life.rows * cell_size
        
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game of Life")
        
        
        self.bg_color = (255, 255, 255)  
        self.grid_color = (128, 128, 128)  
        self.cell_color = (0, 128, 0)  
        self.text_color = (0, 0, 0)  
        
        
        self.font = pygame.font.SysFont(None, 24)
        
        
        self.paused = False
        self.generation_count = 0

    def draw_lines(self) -> None:
        """Отрисовать сетку"""
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.width, y))

    def draw_grid(self) -> None:
        """Отрисовка клеток"""
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                x = j * self.cell_size
                y = i * self.cell_size
                
                
                if self.life.curr_generation[i][j] == 1:
                    pygame.draw.rect(
                        self.screen, 
                        self.cell_color, 
                        (x, y, self.cell_size, self.cell_size)
                    )
                else:
                    pygame.draw.rect(
                        self.screen, 
                        self.bg_color, 
                        (x, y, self.cell_size, self.cell_size)
                    )
                
                
                pygame.draw.rect(
                    self.screen,
                    self.grid_color,
                    (x, y, self.cell_size, self.cell_size),
                    1
                )

    def draw_info(self) -> None:
        """Отрисовка информации о состоянии игры"""
        
        gen_text = f"Generation: {self.generation_count}"
        text_surface = self.font.render(gen_text, True, self.text_color)
        self.screen.blit(text_surface, (10, 10))
        
        
        pause_text = "PAUSED" if self.paused else "RUNNING"
        pause_surface = self.font.render(pause_text, True, self.text_color)
        self.screen.blit(pause_surface, (10, 40))
        
        
        instr_text = "SPACE: pause/resume  R: reset  ESC: exit"
        instr_surface = self.font.render(instr_text, True, self.text_color)
        self.screen.blit(instr_surface, (10, self.height - 30))

    def handle_click(self, pos: tuple) -> None:
        """Обработка клика мыши для изменения состояния клетки"""
        x, y = pos
        col = x // self.cell_size
        row = y // self.cell_size
        
        
        if 0 <= row < self.life.rows and 0 <= col < self.life.cols:
            
            self.life.curr_generation[row][col] = 1 - self.life.curr_generation[row][col]

    def run(self) -> None:
        """Запуск игры"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_SPACE:
                        self.paused = not self.paused
                    elif event.key == K_r:
                        
                        self.life = GameOfLife(
                            size=(self.life.rows, self.life.cols),
                            randomize=True,
                            max_generations=self.life.max_generations
                        )
                        self.generation_count = 0
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:  
                        self.handle_click(event.pos)
            
            
            if not self.paused:
                
                prev_generation = [row[:] for row in self.life.curr_generation]
                
                
                self.life.step()
                self.generation_count += 1
                
                
                if self.life.curr_generation == prev_generation:
                    
                    self.paused = True
            
            
            if self.life.is_max_generations_exceeded:
                self.paused = True
            
            
            self.screen.fill(self.bg_color)
            self.draw_grid()
            self.draw_lines()
            self.draw_info()
            
            pygame.display.flip()
            clock.tick(self.speed)
        
        pygame.quit()


if __name__ == "__main__":
    life = GameOfLife(
        size=(40, 60),  
        randomize=True,
        max_generations=float("inf") 
    )
    
    gui = GUI(life, cell_size=15, speed=10)
    
    gui.run()