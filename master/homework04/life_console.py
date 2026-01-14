import curses
import time

from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife, speed: float = 0.1) -> None:
        super().__init__(life)
        self.speed = speed 

    def draw_borders(self, screen) -> None:
        """Отобразить рамку."""
        screen.addstr(0, 0, '+' + '-' * (self.life.cols * 2) + '+')
        
        for i in range(self.life.rows):
            screen.addstr(i + 1, 0, '|')
            screen.addstr(i + 1, self.life.cols * 2 + 1, '|')
        
        screen.addstr(self.life.rows + 1, 0, '+' + '-' * (self.life.cols * 2) + '+')

    def draw_grid(self, screen) -> None:
        """Отобразить состояние клеток."""
        for i in range(self.life.rows):
            for j in range(self.life.cols):
                x = j * 2 + 1
                y = i + 1
                
                if self.life.curr_generation[i][j] == 1:
                    screen.addstr(y, x, '██')  
                else:
                    screen.addstr(y, x, '  ')  

    def draw_info(self, screen, generation: int) -> None:
        """Отобразить информацию о состоянии игры."""
        info_y = self.life.rows + 2
        
        info_text = f"Generation: {generation}"
        if self.life.is_max_generations_exceeded:
            info_text += " (MAX GENERATIONS REACHED)"
        elif not self.life.is_changing:
            info_text += " (STABLE STATE)"
        
        screen.addstr(info_y, 0, info_text)
        
        instr_text = "Press 'q' to quit, 'r' to reset, SPACE to pause/resume"
        screen.addstr(info_y + 1, 0, instr_text)

    def run(self) -> None:
        """Запуск консольного интерфейса."""
        screen = curses.initscr()
        curses.noecho()  
        curses.cbreak()  
        screen.keypad(True)  
        curses.curs_set(0) 
        
        try:
            min_height = self.life.rows + 4  
            min_width = self.life.cols * 2 + 2  
            
            screen_height, screen_width = screen.getmaxyx()
            
            if screen_height < min_height or screen_width < min_width:
                screen.addstr(0, 0, f"Window too small! Need at least {min_width}x{min_height}, have {screen_width}x{screen_height}")
                screen.refresh()
                time.sleep(2)
                return
            
            paused = False
            running = True
            generation = 0
            
            while running:
                screen.clear()
                
                self.draw_borders(screen)
                self.draw_grid(screen)
                self.draw_info(screen, generation)
                
                screen.refresh()

                screen.timeout(int(self.speed * 1000)) 
                key = screen.getch()
                
                if key != -1: 
                    if key == ord('q') or key == ord('Q'):
                        running = False
                    elif key == ord('r') or key == ord('R'):
                        self.life = GameOfLife(
                            size=(self.life.rows, self.life.cols),
                            randomize=True,
                            max_generations=self.life.max_generations
                        )
                        generation = 0
                    elif key == ord(' ') or key == 10:  
                        paused = not paused
                
                if not paused:
                    self.life.step()
                    generation += 1
                    
                    if self.life.is_max_generations_exceeded:
                        paused = True
                    elif not self.life.is_changing:
                        paused = True
        
        except KeyboardInterrupt:
            pass
        finally:
            curses.nocbreak()
            screen.keypad(False)
            curses.echo()
            curses.endwin()


if __name__ == "__main__":
    life = GameOfLife(
        size=(20, 40),  
        randomize=True,
        max_generations=1000
    )
    
    console = Console(life, speed=0.05)  
    
    console.run()