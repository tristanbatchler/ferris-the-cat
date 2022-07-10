import pygame as pg
import threading
import re
import enum
import queue
import time


class Item:
    def __init__(self, passable: bool, sprite_filename: str = 'sprites/unknown.png'):
        self.name = sprite_filename.split('/')[-1].split('.')[0]
        self.passable: bool = passable
        self.sprite: pg.Surface = pg.image.load(sprite_filename)


class Direction(enum.IntEnum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3


WALL = Item(False, 'sprites/wall.png')
BICKIE = Item(True, 'sprites/bickie.png')


class Game:
    def __init__(self, window_width: int, window_height: int, window_title: str, level_file, geometry_file, game_speed: float = 1.0):
        self.window_width: int = window_width
        self.window_height: int = window_height
        self.window_title: str = window_title
        self.level_file = level_file.read().split('\n')
        self.geometry_file = geometry_file.read().split('\n')

        self.clock: pg.time.Clock = pg.time.Clock()
        self.quit: bool = False

        self.game_speed: float = 0.2 * game_speed
        self.game_sleep: float = 0.2 / game_speed

        self.bickie_count: int = 0
        self.ferris_dir: Direction = Direction.RIGHT
        self.ferris_x: int = 0
        self.ferris_y: int = 0
        self.geometry: dict[tuple(int, int), list[item]] = {}
        self.initialise_game_state()

        imgs_dir: str = 'sprites/'
        self.ferris_sprites: list[pg.Surface] = [
            pg.image.load(imgs_dir + 'right.png'),
            pg.image.load(imgs_dir + 'up.png'),
            pg.image.load(imgs_dir + 'left.png'),
            pg.image.load(imgs_dir + 'down.png')
        ]
        
        self.level_width = max(x for x, y in self.geometry) - min(x for x, y in self.geometry) + 1
        self.level_height = max(y for x, y in self.geometry) - min(y for x, y in self.geometry) + 1
        self.cell_size: float = min(window_width / self.level_width, window_height / self.level_height)

        # Rescale sprites if necessary
        sprite_dimensions: tuple[int, int] = (self.cell_size, self.cell_size)
        for i in range(4):
            self.ferris_sprites[i] = pg.transform.scale(self.ferris_sprites[i], sprite_dimensions)
        BICKIE.sprite = pg.transform.scale(BICKIE.sprite, sprite_dimensions)
        WALL.sprite = pg.transform.scale(WALL.sprite, sprite_dimensions)
        

    def add_item_to_geometry(self, x: int, y: int, item: Item):
        coord: tuple[int, int] = (x, y)
        if coord not in self.geometry:
            self.geometry[coord] = []
        self.geometry[coord].append(item)

    def initialise_game_state(self):
        self.bickie_count = 0
        self.ferris_dir = 0
        self.geometry = {}

        reading_metadata: bool = False
        for y, line in enumerate(self.geometry_file):
            if line == '--':
                reading_metadata = True
                continue

            if not reading_metadata:
                for x, char in enumerate(line):
                    if char == '#':
                        self.add_item_to_geometry(x, y, WALL)
                    elif char in 'FX':
                        self.ferris_x = x
                        self.ferris_y = y
                    elif char in '$X':
                        self.add_item_to_geometry(x, y, BICKIE)
            else:
                line = ''.join(line.split()).replace(':', '').lower()
                if line.startswith('bickies'):
                    line = line.replace('bickies', '')
                    self.bickie_count = int(line)


    def _run_level(self, error_queue: queue.Queue, fast: bool = False):
        exec_file = 'import time\nstart=time.time()\n'
        if not fast:
            exec_file += 'time.sleep(0.5)\n'
        
        for line in self.level_file:
            # Add timeout checks to all while loops if this is a fast run
            if fast and re.match("^.*(?<!\w)while\s+.*?:\s*$", line):
                exec_file += f"{line[:line.rfind(':')]} and (time.time() - start < 1):\n"

            # Add sleeps between actions if this is not a fast run
            elif not fast and re.match("^.*(?<!\w)(move|turn_left|eat|throwup)\(\s*\).*$", line):
                exec_file += f"{line}; time.sleep({self.game_sleep})\n"

            # Add all other lines except game import (which can make sad errors)
            elif not line.startswith("from game import *"):
                exec_file += line + '\n'

            
        # Define the functions scope to pass to the exec environment
        exec_scope: dict[str, any] = {
            "move": self.move, "turn_left": self.turn_left, "can_move": self.can_move, 
            "bickie_here": self.bickie_here, "get_bickie_count": self.get_bickie_count, 
            "eat": self.eat, "throwup": self.throwup, "get_direction": self.get_direction
        }
        try:
            exec(exec_file, exec_scope)
        except Exception as e:
            error_queue.put(e)


    def start(self):
        pg.init()
        pg.font.init()
        backdrop: pg.Surface = pg.display.set_mode((self.window_width, self.window_height))
        font: pg.font.SysFont = pg.font.SysFont('Comic Sans MS', 20)
        pg.display.set_caption(self.window_title)

        error_queue: queue.Queue = queue.Queue()
        # Perform a first pass of the script to immediately raise errors
        test_thread: threading.Thread = threading.Thread(target=self._run_level, args=(error_queue, True))
        test_thread.start()
        # Block while waiting for the test thread to complete or timeout occurs (indicating it's likely an infinite loop)
        start = time.time()
        if test_thread.is_alive() and time.time() - start < 1:
            time.sleep(1)
        
        # Perform the real pass by first reinitialising the game state
        self.initialise_game_state()
        threading.Thread(target=self._run_level, args=(error_queue, False), daemon=True).start()

        # Main game loop
        while not self.quit:
            self.get_input()
            self.draw(backdrop, font)
            self.clock.tick(60)

            if not error_queue.empty():
                raise error_queue.get()
        
        pg.quit()

    def get_input(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True

    def draw(self, backdrop: pg.Surface, font: pg.font.SysFont):
        backdrop.fill((0, 0, 0))
        offset_x: float = (self.window_width - self.level_width * self.cell_size) / 2
        offset_y: float = (self.window_height - self.level_height * self.cell_size) / 2
        for coord, items in self.geometry.items():
            xy = (coord[0] * self.cell_size + offset_x, coord[1] * self.cell_size + offset_y)
            last_item = None
            stack_count = 1
            for item in items[::-1]:
                if item == last_item:
                    stack_count += 1
                else:
                    backdrop.blit(item.sprite, xy)
                    stack_count = 1
                last_item = item

            if stack_count > 1:
                text_surface: pg.Surface = font.render(str(stack_count), False, (255, 255, 255))
                backdrop.blit(text_surface, (xy))
        
        backdrop.blit(self.ferris_sprites[self.ferris_dir], (self.ferris_x * self.cell_size + offset_x, self.ferris_y * self.cell_size + offset_y))

        text_surface: pg.Surface = font.render(f'Bickies: {self.bickie_count}', False, (255, 255, 255))
        backdrop.blit(text_surface, (0, 0))

        pg.display.update()

    def _get_coords_ahead(self) -> tuple[int, int]:
        target_x: int = self.ferris_x
        target_y: int = self.ferris_y

        if self.ferris_dir == Direction.RIGHT:
            target_x += 1
        elif self.ferris_dir == Direction.LEFT:
            target_x -= 1
        elif self.ferris_dir == Direction.DOWN:
            target_y += 1
        elif self.ferris_dir == Direction.UP:
            target_y -= 1 

        return target_x, target_y   

    def can_move(self) -> bool:
        """
        Returns `True` if there is no obstacle directly in front of Ferris that would prevent him from moving one cell forward.
        Returns `False` if there is one and Ferris can't move.
        """
        target_x, target_y = self._get_coords_ahead()
        if target_x < 0 or target_x >= self.level_width:
            return False
        if target_y < 0 or target_y >= self.level_height:
            return False
        coords: tuple[int, int] = (target_x, target_y)
        if coords in self.geometry and len(self.geometry[coords]) > 0 and not sum(item.passable for item in self.geometry[coords]):
            return False
        
        return True

    def turn_left(self) -> None:
        """
        Turns Ferris to face 90 degrees counter-clockwise. E.g. if Ferris is facing East, after this function he will be facing North.
        """
        self.ferris_dir = (self.ferris_dir + 1) % 4

    def bickie_here(self) -> bool:
        """"
        If there is a bickie directly underneath Ferris, returns `True`. Otherwise, returns `False`.
        """
        coords: tuple[int, int] = (self.ferris_x, self.ferris_y)
        return coords in self.geometry and BICKIE in self.geometry[coords]

    def eat(self) -> None:
        """"
        If there is a bickie directly underneath Ferris, he eats it and his total bickie count is increased by 1. Otherwise, this function does nothing.
        """
        if self.bickie_here():
            coords: tuple[int, int] = self.ferris_x, self.ferris_y
            items: list[Item] = self.geometry[coords]
            items.remove(BICKIE)
            self.bickie_count += 1

    def get_bickie_count(self) -> int:
        """
        Returns the number of bickies Ferris currently has in his stomach.
        """
        return self.bickie_count

    def get_direction(self) -> chr:
        """
        Returns the direction Ferris is currently facing. Will be either `'N'`, `'S'`, `'E'`, or `'W'` to represent  north, south, east, or west respectively.
        """
        if self.ferris_dir == 0:
            return 'E'
        if self.ferris_dir == 1:
            return 'N'
        if self.ferris_dir == 2:
            return 'W'
        if self.ferris_dir == 3:
            return 'S'

    def throwup(self) -> None:
        """
        Ferris throws up exactly one of his stored bickies (if he has any), decreasing his total 
        bickie count by 1 and placing a bickie directly underneath him.
        
        If there are already bickie(s) underneath Ferris before he throws up, the number of bickies 
        on the ground at that location will be increased by one.

        If Ferris has no bickies in his stomach before this function is called, this function does nothing.
        """
        if self.bickie_count > 0:
            self.add_item_to_geometry(self.ferris_x, self.ferris_y, BICKIE)
            self.bickie_count -= 1        

    def move(self) -> None:
        """
        Moves Ferris one cell forward in the direction he is facing. For example, if Ferris is facing `East`, he will move one cell to the right after this function is called.
        If there is an obstacle in the way of intended movement, this function does nothing.
        """
        target_x, target_y = self._get_coords_ahead()

        if self.can_move():
            self.ferris_x = target_x
            self.ferris_y = target_y


move = Game.move
turn_left = Game.turn_left
can_move = Game.can_move
bickie_here = Game.bickie_here
get_bickie_count = Game.get_bickie_count
eat = Game.eat
throwup = Game.throwup
get_direction = Game.get_direction
