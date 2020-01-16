import pygame
import random
import os
import sys

pygame.init()
os.environ['SDL_VIDEO_CENTERED'] = '1'
CELL_SIZE = {'X': 20, 'Y': 20}
CELL_COUNT = {'X': 31, 'Y': 31}
EXPANSION_TIME = 300  # милисекунд
CURRENT_LEVEL_FOR_BOARD = 1
SCREEN_SIZE_FOR_LEVEL = CELL_SIZE['X'] * CELL_COUNT['X'], CELL_SIZE['Y'] * CELL_COUNT['Y'] + 100
CURRENT_PLAYER_LEVEL = '1'
clock = pygame.time.Clock()
SYMB_FOR_WALL = '#'
SYMB_FOR_ENEMY = 'X'
SYMB_FOR_PLAYER = '@'
SYMB_FOR_DESTROYABLE_WALL = 'd'
SYMB_FOR_GRASS = '.'
SYMB_FOR_EXIT = 'E'


def load_image(name, colorkey=None):
    fullname = os.path.join('textures', name)
    image = pygame.image.load(fullname)  # .convert()
    # if colorkey is not None:
    #     image.set_colorkey(colorkey)
    # else:
    #     image = image.convert_alpha()
    return image


def load_level_from_file(file_name):
    map_list = []
    file = open(file_name, 'r')
    lines = file.readlines()
    for line in lines:
        map_list.append([k for k in line])
    return map_list


def calculate_distance(x1, y1, x2, y2):
    # По формуле расстояния в декартовой системе координат
    distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return distance


def count_cell_index(x, y):
    return x // CELL_SIZE['X'], y // CELL_SIZE['Y']


def check_coordinates_and_rewrite_that(object, move_info):
    if move_info[2] > 0 and object.rect.x > move_info[0]:
        object.rect.x = move_info[0]
        move_info[2] = 0
    elif move_info[2] < 0 and object.rect.x < move_info[0]:
        object.rect.x = move_info[0]
        move_info[2] = 0
    if move_info[3] > 0 and object.rect.y > move_info[1]:
        object.rect.y = move_info[1]
        move_info[3] = 0
    elif move_info[3] < 0 and object.rect.y < move_info[1]:
        object.rect.y = move_info[1]
        move_info[3] = 0


IMAGES = {}


def load_base_images(dictionary):
    enemy_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    enemy_image.fill((0, 255, 0))
    pygame.draw.polygon(enemy_image, (255, 0, 0),
                        [(CELL_SIZE['X'] // 2, 0), (0, CELL_SIZE['Y']),
                         (CELL_SIZE['X'], CELL_SIZE['Y'])])
    player_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    player_image.fill((0, 0, 255))
    exit_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    exit_image.fill((255, 255, 0))
    wall_destroyable_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    wall_destroyable_image.fill((100, 100, 100))
    wall_not_destroyable_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    wall_not_destroyable_image.fill((180, 180, 180))
    shell_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    pygame.draw.rect(shell_image, (0, 255, 0), (0, 0, CELL_SIZE['X'], CELL_SIZE['Y']))
    pygame.draw.circle(shell_image,
                       (0, 0, 0),
                       (CELL_SIZE['X'] // 2,
                        CELL_SIZE['Y'] // 2),
                       CELL_SIZE['X'] // 2 - 2)
    dictionary['Enemy'] = load_image('animated_enemy_v3.png')
    dictionary['Exit'] = exit_image
    dictionary['Wall'] = wall_not_destroyable_image
    dictionary['Wall(Destroyable)'] = wall_destroyable_image
    dictionary['Player'] = load_image('animated_player_v3.png')
    dictionary['Shell'] = shell_image
    dictionary['Expansion'] = load_image('expansion.png')
    dictionary['Background'] = load_image('background.png')
    dictionary['Arrow_right'] = load_image('arrow_right.png')
    dictionary['Arrow_left'] = load_image('arrow_left.png')
    dictionary['Choose_level'] = load_image('choose_level.png')
    dictionary['level_1'] = load_image('level_1.png')
    dictionary['level_2'] = load_image('level_2.png')
    dictionary['level_3'] = load_image('level_3.png')
    dictionary['level_4'] = load_image('level_4.png')
    dictionary['level_5'] = load_image('level_5.png')
    dictionary['level_6'] = load_image('level_6.png')
    dictionary['level_7'] = load_image('level_7.png')
    dictionary['level_8'] = load_image('level_8.png')
    dictionary['level_9'] = load_image('level_9.png')
    dictionary['level_10'] = load_image('level_10.png')
    dictionary['continue_button_lose'] = load_image('back_to_main_screen.png')
    dictionary['continue_button_win'] = load_image('back_to_main_screen_after_win.png')
    dictionary['mine_expansion_1_level'] = load_image('mine_1_level.png')
    dictionary['mine_expansion_2_1_level'] = load_image('mine_2_1_level.png')
    dictionary['mine_expansion_2_2_level'] = load_image('mine_2_2_level.png')
    dictionary['mine_expansion_3_level'] = load_image('mine_3_level.png')
    dictionary['mine_expansion_4_level'] = load_image('mine_4_level.png')
    dictionary['mine_expansion_5_level'] = load_image('mine_5_level.png')
    dictionary['mine_expansion_λ_level'] = load_image('mine_λ_level.png')


load_base_images(IMAGES)
other_group = pygame.sprite.Group()


def way_to_point_in_labirint(start_point_index, end_point_index, map_list):
    dict_of_points = {start_point_index: [(0, 0)]}
    past_ways = []
    k = 0
    current_points = []
    while end_point_index not in dict_of_points.keys():
        if current_points == list(dict_of_points.keys()):
            return []
        if k == 10000:
            break
        current_points = list(dict_of_points.keys())
        points_in_dict = list(dict_of_points.keys())
        for point in points_in_dict:
            if point in past_ways:
                k += 1
                continue
            new_ways = [(point[0] - 1, point[1]),
                        (point[0] + 1, point[1]),
                        (point[0], point[1] - 1),
                        (point[0], point[1] + 1)]
            new_ways = [way
                        for way in new_ways
                        if -1 < way[0] < len(map_list[0])
                        and -1 < way[1] < len(map_list)
                        and way not in past_ways]
            for way in new_ways:
                if (map_list[way[1]][way[0]] == SYMB_FOR_PLAYER
                        or map_list[way[1]][way[0]] == SYMB_FOR_GRASS
                        or map_list[way[1]][way[0]] == SYMB_FOR_ENEMY):
                    if way in dict_of_points.keys():
                        dict_of_points[way].append(point)
                    else:
                        dict_of_points[way] = [point]
                else:
                    past_ways.append(way)
            past_ways.append(point)

    path = [end_point_index]
    current = end_point_index
    while True:
        if current == start_point_index:
            break
        current = dict_of_points[current][0]
        path.append(current)
    return path


class WallBrick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = IMAGES['Wall']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class WallBrickDestroyable(WallBrick):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = IMAGES['Wall(Destroyable)']

    def destroy(self):
        # self.image = wall_destroyable_fallen_image
        # pygame.time.
        self.kill()


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, image, group, function):
        super().__init__(group)
        self.image = image
        self.function = function
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.pressed = False

    def reset_function(self, function):
        self.function = function

    def press(self, event, *args):
        if (self.rect.x <= event.pos[0] <= self.rect.w + self.rect.x
                and self.rect.y <= event.pos[1] <= self.rect.h + self.rect.y
                and not self.pressed
                and event.type == pygame.MOUSEBUTTONDOWN):
            self.pressed = True
            self.function(*args)
            return True
        elif (self.rect.x <= event.pos[0] <= self.rect.w + self.rect.x
              and self.rect.y <= event.pos[1] <= self.rect.h + self.rect.y
              and self.pressed
              and event.type == pygame.MOUSEBUTTONUP):
            self.pressed = False
            return True


class ExpansionSector(pygame.sprite.Sprite):
    def __init__(self, x, y, group, start_ticks):
        super().__init__(group)
        self.start_ticks = start_ticks
        self.image = IMAGES['Expansion']
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        if pygame.time.get_ticks() - self.start_ticks > EXPANSION_TIME:
            self.kill()


class Exit(WallBrickDestroyable):
    def check_exit(self, player_position):
        if self.rect.x == player_position[0] and self.rect.y == player_position[1]:
            return True
        return False

    def destroy(self):
        self.image = IMAGES['Exit']


class Shell(pygame.sprite.Sprite):
    def __init__(self, x, y, index):
        super().__init__()
        self.image = IMAGES['Shell']
        self.rect = self.image.get_rect()
        self.index = index
        self.rect.x = x
        self.rect.y = y

    def destroy(self):
        self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, level, x, y, board, index):
        super().__init__()
        self.frames = []
        self.cut_sheet(IMAGES['Enemy'], 12, 4)
        self.cur_frame = 0
        self.image = self.frames[0][self.cur_frame]
        self.level = level
        self.index = index
        self.board = board
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update_frame(self, x_vector, y_vector):
        if x_vector == 1:
            index = 2
        elif x_vector == -1:
            index = 1
        elif y_vector == 1:
            index = 0
        elif y_vector == -1:
            index = 3
        if x_vector or y_vector:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[index])
            self.image = self.frames[index][self.cur_frame]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for row in range(rows):
            self.frames.append([])
            for col in range(columns):
                frame_location = (self.rect.w * col, self.rect.h * row)
                self.frames[-1].append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
        # self.frames[0] — front [1] — left [2] — right [3] — back

    def update(self, player_coordinates: list) -> None:
        distance_to_player = calculate_distance(self.rect.x, self.rect.y, *player_coordinates)
        distance_to_player_is_short = bool(distance_to_player < self.level // 2 * CELL_SIZE['X'] + CELL_SIZE['X'] * 12)
        index_before_move = count_cell_index(self.rect.x, self.rect.y)

        def random_move():
            new_ways = [[self.rect.x + CELL_SIZE['X'], self.rect.y],
                        [self.rect.x - CELL_SIZE['X'], self.rect.y],
                        [self.rect.x, self.rect.y + CELL_SIZE['Y']],
                        [self.rect.x, self.rect.y - CELL_SIZE['Y']]]
            random.shuffle(new_ways)
            for index in range(4):
                index_of_new_coordinate = count_cell_index(*new_ways[index])
                if (new_ways[index][0] < 0
                        or new_ways[index][0] >= CELL_SIZE['X'] * CELL_COUNT['X']
                        or new_ways[index][1] < 0
                        or new_ways[index][1] >= CELL_SIZE['Y'] * CELL_COUNT['Y']):
                    continue
                elif (self.board.map_list[index_of_new_coordinate[1]][index_of_new_coordinate[0]]
                      != SYMB_FOR_GRASS):
                    continue
                else:
                    index_after_move = count_cell_index(new_ways[index][0],
                                                        new_ways[index][1])
                    self.board.replace_symbols_after_move(index_before_move,
                                                          index_after_move,
                                                          SYMB_FOR_ENEMY)
                    vector_x = 1 if index_after_move[0] - index_before_move[0] > 0 else -1
                    vector_y = 1 if index_after_move[1] - index_before_move[1] > 0 else -1
                    self.board.enemy_move[self.index] = [*new_ways[index], vector_x, vector_y]
                    break

        if not distance_to_player_is_short:
            random_move()
        else:
            start_pos = count_cell_index(self.rect.x, self.rect.y)
            end_pos = count_cell_index(*player_coordinates)
            way = way_to_point_in_labirint(start_pos, end_pos, self.board.map_list)
            if len(way) >= 2:
                new_index = way[-2]
                if self.board.map_list[new_index[1]][new_index[0]] == SYMB_FOR_PLAYER:
                    self.board.end_game(win=False)
                else:
                    vector_x = 1 if new_index[0] - index_before_move[0] > 0 else -1
                    vector_y = 1 if new_index[1] - index_before_move[1] > 0 else -1
                    self.board.enemy_move[self.index] = [new_index[0] * CELL_SIZE['X'],
                                                         new_index[1] * CELL_SIZE['Y'], vector_x,
                                                         vector_y]
                    self.board.replace_symbols_after_move(index_before_move,
                                                          new_index,
                                                          SYMB_FOR_ENEMY)
            else:
                random_move()


class Board:
    def __init__(self, all_sprites_group, level=1):
        self.all_sprites_group = all_sprites_group
        self.level = level
        self.start_ticks = pygame.time.get_ticks()
        self.map_list = None
        self.expansion = False
        self.expansion_indexes_list = []
        self.expansion_wave_index = 0
        self.start_expansion = 10 ** 6
        self.expansion_sprites = pygame.sprite.Group()
        self.player = None
        self.stop = False
        self.win = False
        self.exit = None
        self.reload = 0
        self.game_duration_in_seconds = self.level * 30 + 120
        self.enemy_move = {}
        self.shells = {}
        if CURRENT_PLAYER_LEVEL == '1':
            self.shell_limit = 3
        elif CURRENT_PLAYER_LEVEL in ['2', '4', 'λ']:
            self.shell_limit = 2
        elif CURRENT_PLAYER_LEVEL in ['3', '5']:
            self.shell_limit = 1
        self.current_shells_possible_use = int(self.shell_limit)
        self.enemys = []

    def fill_enemy_move(self):
        for enemy in self.enemys:
            self.enemy_move[enemy.index] = [0, 0, 0, 0]

    def end_game(self, win=False):
        if not self.stop:
            self.stop = True
            self.win = win

    def print_info_about_game(self, screen):
        font = pygame.font.Font('FreeSansBold.ttf', 26)
        seconds_left = (pygame.time.get_ticks() - self.start_ticks) // 1000
        seconds = self.game_duration_in_seconds - seconds_left
        self.update_reload_status()
        if seconds <= 0:
            self.end_game(False)
        else:
            minutes, seconds = seconds // 60, seconds % 60

            if self.current_shells_possible_use:
                text = font.render(f'времени осталось: {minutes}:{seconds}      '
                                   f'мин осталось: {self.current_shells_possible_use}',
                                   1, (0, 0, 0))
            else:
                text = font.render(f'времени осталось: {minutes}:{seconds}      '
                                   f'перезарядка...   {self.reload - seconds_left}',
                                   1, (0, 0, 0))

            screen.blit(text, ((CELL_SIZE['X'] * CELL_COUNT['X'] - text.get_width()) // 2,
                               (CELL_SIZE['Y'] * CELL_COUNT['Y'] + 50 - text.get_height() // 2)))

    def start_reload(self, time):
        seconds_left = (pygame.time.get_ticks() - self.start_ticks) // 1000
        self.reload = seconds_left + time

    def update_reload_status(self):
        seconds_left = (pygame.time.get_ticks() - self.start_ticks) // 1000
        if self.reload and self.reload - seconds_left <= 0:
            self.reload = 0
            self.current_shells_possible_use = int(self.shell_limit)
            print(self.shell_limit)

    def print_end_game(self, screen):
        if self.stop:
            font = pygame.font.Font('FreeSansBold.ttf', 50)
            if self.win:
                text = font.render('Вы победили', 1, (100, 0, 255))
            else:
                text = font.render('Вы проиграли', 1, (100, 0, 255))

            screen.blit(text, ((CELL_SIZE['X'] * CELL_COUNT['X'] - text.get_width()) // 2,
                               (CELL_SIZE['Y'] * CELL_COUNT['Y'] - text.get_height()) // 2))

    def replace_symbols_after_move(self, index_before, index_after, type_of_creature):
        if index_before[0] != index_after[0] or index_before[1] != index_after[1]:
            self.map_list[index_before[1]][index_before[0]] = SYMB_FOR_GRASS
            self.map_list[index_after[1]][index_after[0]] = type_of_creature

    def update_shells(self):
        coordinates_bombs = []
        shells_to_delete = []

        def check_index(index_x, index_y):
            if -1 < index_x < CELL_COUNT['X'] and -1 < index_y < CELL_COUNT['Y']:
                return True
            return False

        def check_map_for_wall(index_x, index_y):
            if self.map_list[index_x][index_y] == SYMB_FOR_WALL:
                return True
            return False

        def add_shell_coordinates(shell_index):
            position = self.shells[shell_index].rect.x, self.shells[shell_index].rect.y
            coordinates_bombs.append(position)
            self.shells[shell_index].destroy()
            shells_to_delete.append(shell_index)

        for shell_index in self.shells:
            add_shell_coordinates(shell_index)
        for shell_index in shells_to_delete:
            del self.shells[shell_index]

        new_coordinates = []
        continue_expansion = {i: {'X-1': True, 'X+1': True, 'Y-1': True, 'Y+1': True}
                              for i in range(len(coordinates_bombs))}
        indexes = [count_cell_index(*coord) for coord in coordinates_bombs]
        new_coordinates.append(indexes)
        if self.player.level == '1':
            for i in range(1, 6):
                new_coordinates.append([])
                for index_bomb, coordinates in enumerate(coordinates_bombs):
                    index_of_coords = count_cell_index(*coordinates)
                    new_indexes_on_this_step = []
                    if continue_expansion[index_bomb]['X-1']:
                        index_of_coords_new = (index_of_coords[0] - i, index_of_coords[1])
                        if check_index(*index_of_coords_new):
                            if check_map_for_wall(*index_of_coords_new):
                                continue_expansion[index_bomb]['X-1'] = False
                            else:
                                new_indexes_on_this_step.append(index_of_coords_new)
                    if continue_expansion[index_bomb]['X+1']:
                        index_of_coords_new = (index_of_coords[0] + i, index_of_coords[1])
                        if check_index(*index_of_coords_new):
                            if check_map_for_wall(*index_of_coords_new):
                                continue_expansion[index_bomb]['X+1'] = False
                            else:
                                new_indexes_on_this_step.append(index_of_coords_new)
                    if continue_expansion[index_bomb]['Y-1']:
                        index_of_coords_new = (index_of_coords[0], index_of_coords[1] - i)
                        if check_index(*index_of_coords_new):
                            if check_map_for_wall(*index_of_coords_new):
                                continue_expansion[index_bomb]['Y-1'] = False
                            else:
                                new_indexes_on_this_step.append(index_of_coords_new)
                    if continue_expansion[index_bomb]['Y+1']:
                        index_of_coords_new = (index_of_coords[0], index_of_coords[1] + i)
                        if check_index(*index_of_coords_new):
                            if check_map_for_wall(*index_of_coords_new):
                                continue_expansion[index_bomb]['Y+1'] = False
                            else:
                                new_indexes_on_this_step.append(index_of_coords_new)
                    new_coordinates[i - 1].extend(new_indexes_on_this_step)
        elif self.player.level == '2':
            vector = random.choices(['x', 'y'], weights=[1, 1])[0]
            if vector == 'x':
                next_step_coords = sum([[(x, coord[1]) for x in range(CELL_COUNT['X'])]
                                        for coord in indexes], [])
            else:
                next_step_coords = sum([[(coord[0], y) for y in range(CELL_COUNT['Y'])]
                                        for coord in indexes], [])
            new_coordinates.append([])
            for coordinates in next_step_coords:
                if not check_map_for_wall(*coordinates):
                    new_coordinates[1].append(coordinates)
        elif self.player.level == '3':
            new_coordinates.append([])
            for x_index, y_index in indexes:
                for x_delta in range(-1, 2):
                    for y_delta in range(-1, 2):
                        cell_index = x_index + x_delta, y_index + y_delta
                        if (not check_map_for_wall(*cell_index)
                                and -1 < cell_index[0] < CELL_COUNT['X']
                                and -1 < cell_index[1] < CELL_COUNT['Y']):
                            new_coordinates[1].append(cell_index)
        elif self.player.level == '4':
            temporary_indexes = set()
            new_coordinates.append([])
            for x_index, y_index in indexes:
                for delta in range(-5, 6):
                    temporary_indexes.add((x_index + delta, y_index - 5))
                    temporary_indexes.add((x_index + delta, y_index))
                    temporary_indexes.add((x_index + delta, y_index + 5))
                    temporary_indexes.add((x_index - 5, y_index + delta))
                    temporary_indexes.add((x_index, y_index + delta))
                    temporary_indexes.add((x_index + 5, y_index + delta))
            for x_index, y_index in temporary_indexes:
                if (-1 < x_index < CELL_COUNT['X']
                        and -1 < y_index < CELL_COUNT['Y']
                        and not check_map_for_wall(x_index, y_index)):
                    new_coordinates[1].append((x_index, y_index))
        elif self.player.level == '5':
            temporary_indexes = set()
            new_coordinates[0] = list()  # Мина 5 уровня в исходном квадрате 5x5 не наносит вреда
            for num_of_squared_ring in range(6, 8):
                for x_index, y_index in indexes:
                    for delta in range(-5, 6):
                        temporary_indexes.add((x_index + delta, y_index - num_of_squared_ring))
                        temporary_indexes.add((x_index + delta, y_index + num_of_squared_ring))
                        temporary_indexes.add((x_index - num_of_squared_ring, y_index + delta))
                        temporary_indexes.add((x_index + num_of_squared_ring, y_index + delta))
                for x_index, y_index in temporary_indexes:
                    if (-1 < x_index < CELL_COUNT['X']
                            and -1 < y_index < CELL_COUNT['Y']
                            and not check_map_for_wall(x_index, y_index)):
                        new_coordinates[0].append((x_index, y_index))
        elif self.player.level == 'λ':
            new_coordinates[0] = list()  # Мина λ уровня в исходном квадрате 3x3 не наносит вреда
            temporary = set()
            for bomb_coords in indexes:
                """bottom right and left cell indexes"""
                for delta in range(2, 16):
                    for count in range(6):
                        y = bomb_coords[1] + delta
                        x_left = bomb_coords[0] - delta - 3 + count
                        x_right = bomb_coords[0] + delta + count
                        temporary.add((x_left, y))
                        temporary.add((x_right, y))
                """top cell indexes"""
                for delta in range(5, 15):
                    for count in range(7):
                        y = bomb_coords[1] - delta
                        x = bomb_coords[0] - delta // 2 - 2 + count
                        temporary.add((x, y))
                """pre top cell indexes"""
                for delta in range(2, 5):
                    for count in range(7):
                        y = bomb_coords[1] - delta
                        x = bomb_coords[0] - 3 + count
                        temporary.add((x, y))
                """center cell indexes"""
                for delta_y in range(-1, 2):
                    y = bomb_coords[1] + delta_y
                    x_left_one = bomb_coords[0] - 3
                    x_left_two = bomb_coords[0] - 2
                    x_right_one = bomb_coords[0] + 2
                    x_right_two = bomb_coords[0] + 3
                    temporary.add((x_left_one, y))
                    temporary.add((x_left_two, y))
                    temporary.add((x_right_one, y))
                    temporary.add((x_right_two, y))
                """result"""
            for x_index, y_index in temporary:
                if (-1 < x_index < CELL_COUNT['X']
                        and -1 < y_index < CELL_COUNT['Y']
                        and not check_map_for_wall(x_index, y_index)):
                    new_coordinates[0].append((x_index, y_index))

        if new_coordinates:
            self.expansion = True
            self.expansion_indexes_list = new_coordinates
            self.start_expansion = pygame.time.get_ticks()
        for step in range(len(new_coordinates)):
            for index in new_coordinates[step]:
                coord = index[0] * CELL_SIZE['X'], index[1] * CELL_SIZE['Y']
                for sprite in self.all_sprites_group.sprites():
                    if isinstance(sprite, Exit):
                        if sprite.rect.x == coord[0] and sprite.rect.y == coord[1]:
                            sprite.destroy()
                    elif isinstance(sprite, WallBrickDestroyable):
                        if sprite.rect.x == coord[0] and sprite.rect.y == coord[1]:
                            sprite.destroy()
                            self.all_sprites_group.remove(sprite)
                            self.map_list[index[1]][index[0]] = SYMB_FOR_GRASS
                    elif isinstance(sprite, Enemy):
                        if (abs(sprite.rect.x - coord[0]) < CELL_SIZE['X'] // 2
                                and abs(sprite.rect.y - coord[1]) < CELL_SIZE['Y'] // 2):
                            sprite.kill()
                            for count, enemy in enumerate(self.enemys):
                                if enemy.index == sprite.index:
                                    del self.enemys[count]
                            self.map_list[index[1]][index[0]] = SYMB_FOR_GRASS
                    elif isinstance(sprite, Player):
                        if sprite.rect.x == coord[0] and sprite.rect.y == coord[1]:
                            self.end_game(False)

    def generate_new_level(self):
        self.map_list = load_level_from_file(f'levels\level_{self.level}.dat')

        exits = []
        for row in range(len(self.map_list)):
            for col in range(len(self.map_list)):
                if self.map_list[row][col] == SYMB_FOR_ENEMY:
                    enemy = Enemy(self.level, col * CELL_SIZE['X'],
                                  row * CELL_SIZE['Y'], self, len(self.enemys))
                    enemy.add(self.all_sprites_group)
                    self.enemys.append(enemy)
                elif self.map_list[row][col] == SYMB_FOR_WALL:
                    wall = WallBrick(col * CELL_SIZE['X'], row * CELL_SIZE['Y'])
                    wall.add(self.all_sprites_group)
                elif self.map_list[row][col] == SYMB_FOR_DESTROYABLE_WALL:
                    wall = WallBrickDestroyable(col * CELL_SIZE['X'], row * CELL_SIZE['Y'])
                    wall.add(self.all_sprites_group)
                elif self.map_list[row][col] == SYMB_FOR_EXIT:
                    exits.append((col, row))
                elif self.map_list[row][col] == SYMB_FOR_GRASS:
                    continue
                elif self.map_list[row][col] == SYMB_FOR_PLAYER:
                    self.player = Player(col * CELL_SIZE['X'],
                                         row * CELL_SIZE['Y'],
                                         board=self,
                                         level=CURRENT_PLAYER_LEVEL)
                    self.player.add(self.all_sprites_group)
        exit_index = random.randint(0, len(exits) - 1)

        self.exit = Exit(exits[exit_index][0] * CELL_SIZE['X'],
                         exits[exit_index][1] * CELL_SIZE['Y'])
        self.exit.add(self.all_sprites_group)
        del exits[exit_index]
        for coords in exits:
            wall = WallBrickDestroyable(coords[0] * CELL_SIZE['X'], coords[1] * CELL_SIZE['Y'])
            wall.add(self.all_sprites_group)
            self.map_list[coords[1]][coords[0]] = SYMB_FOR_DESTROYABLE_WALL


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, board, level='1'):
        super().__init__()
        self.frames = []
        self.cut_sheet(IMAGES['Player'], 12, 4)
        self.cur_frame = 0
        self.image = self.frames[0][self.cur_frame]
        self.board = board
        self.level = level
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for row in range(rows):
            self.frames.append([])
            for col in range(columns):
                frame_location = (self.rect.w * col, self.rect.h * row)
                self.frames[-1].append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
        # self.frames[0] — front [1] — left [2] — right [3] — back

    def update_frame(self, x_vector, y_vector):
        if x_vector == 1:
            index = 2
        elif x_vector == -1:
            index = 1
        elif y_vector == 1:
            index = 0
        elif y_vector == -1:
            index = 3
        if x_vector or y_vector:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[index])
            self.image = self.frames[index][self.cur_frame]

    def update(self, vector_x, vector_y, player_move):
        index_before_move = count_cell_index(self.rect.x,
                                             self.rect.y)
        index_after_move = count_cell_index((vector_x + index_before_move[0]) * CELL_SIZE['X'],
                                            (vector_y + index_before_move[1]) * CELL_SIZE['Y'])
        if (-1 < index_after_move[0] < CELL_COUNT['X']
                and -1 < index_after_move[1] < CELL_COUNT['Y']):
            symb_on_map = self.board.map_list[index_after_move[1]][index_after_move[0]]
            if (symb_on_map == SYMB_FOR_GRASS
                    or symb_on_map == SYMB_FOR_ENEMY):
                player_move = [index_after_move[0] * CELL_SIZE['X'],
                               index_after_move[1] * CELL_SIZE['Y'],
                               vector_x,
                               vector_y]
                self.board.replace_symbols_after_move(index_before_move,
                                                      index_after_move,
                                                      SYMB_FOR_PLAYER)
            elif self.board.map_list[index_after_move[1]][index_after_move[0]] == SYMB_FOR_EXIT:
                self.board.end_game(win=True)
        return player_move


def start_game(level):
    pygame.mixer.music.stop()
    pygame.mixer.music.load('sounds/background.mp3')
    pygame.mixer.music.play(-1)
    screen_for_level = pygame.display.set_mode(SCREEN_SIZE_FOR_LEVEL)
    all_sprites_group = pygame.sprite.Group()
    board = Board(all_sprites_group, level)
    board.generate_new_level()
    board.fill_enemy_move()
    running = True
    result = False
    buttons_pressed = {'SPACE': False, 'RETURN': False}
    counter = 0
    button_group = pygame.sprite.Group()
    player_speed = 2
    enemy_speed = 1
    index_to_shell = 0
    exit_button = None
    player_move = [0, 0, 0, 0]
    game_colors = {'RUN': (0, 255, 0), 'WIN': (255, 150, 255), 'LOSE': (150, 20, 20)}
    while running:
        counter += 1
        if not board.stop:
            color = game_colors['RUN']
        else:
            if board.win:
                color = game_colors['WIN']
            else:
                color = game_colors['LOSE']
        screen_for_level.fill(color)
        if not board.stop:
            if player_move[2]:
                board.player.rect.x += player_move[2] * player_speed
            if player_move[3]:
                board.player.rect.y += player_move[3] * player_speed
            check_coordinates_and_rewrite_that(board.player, player_move)
            if counter % 2 == 0:
                board.player.update_frame(player_move[2], player_move[3])
            pygame.draw.rect(screen_for_level, (150, 150, 150),
                             [0,
                              CELL_SIZE['Y'] * CELL_COUNT['Y'],
                              CELL_SIZE['X'] * CELL_COUNT['X'],
                              CELL_SIZE['Y'] * CELL_COUNT['Y'] + 100])
            keys = pygame.key.get_pressed()
            if not player_move[2] and not player_move[3] and counter % 3 == 0:
                if keys[pygame.K_LEFT]:
                    player_move = board.player.update(-1, 0, player_move)
                # elif иначе возможно несколько вызовов update == ошибка
                elif keys[pygame.K_RIGHT]:
                    player_move = board.player.update(1, 0, player_move)
                elif keys[pygame.K_UP]:
                    player_move = board.player.update(0, -1, player_move)
                elif keys[pygame.K_DOWN]:
                    player_move = board.player.update(0, 1, player_move)
            if keys[pygame.K_RETURN]:
                if not buttons_pressed['RETURN'] and len(board.shells):
                    buttons_pressed['RETURN'] = True
                    board.update_shells()
            else:
                buttons_pressed['RETURN'] = False
            if keys[pygame.K_SPACE]:
                if (not buttons_pressed['SPACE']
                        and board.current_shells_possible_use):
                    buttons_pressed['SPACE'] = True
                    shell = Shell(board.player.rect.x, board.player.rect.y, index_to_shell)
                    shell.add(board.all_sprites_group)
                    board.shells[index_to_shell] = shell
                    index_to_shell += 1
                    board.current_shells_possible_use -= 1

                elif not board.current_shells_possible_use and not board.reload:
                    if CURRENT_PLAYER_LEVEL in ['1']:
                        time = 7
                    elif CURRENT_PLAYER_LEVEL in ['2', '3']:
                        time = 12
                    elif CURRENT_PLAYER_LEVEL in ['4']:
                        time = 18
                    elif CURRENT_PLAYER_LEVEL in ['5', 'λ']:
                        time = 30
                    else:
                        time = 1000
                    board.start_reload(time)
            else:
                buttons_pressed['SPACE'] = False
            for index in board.enemy_move:
                values = board.enemy_move[index]
                if not values[2] and not values[3]:
                    for enemy in board.enemys:
                        if enemy.index == index:
                            enemy.update((board.player.rect.x, board.player.rect.y))
                            break
            for enemy in board.enemys:
                if enemy.index in board.enemy_move:
                    enemy_move = board.enemy_move[enemy.index]
                    if enemy_move[2]:
                        enemy.rect.x += int(enemy_move[2] * enemy_speed)
                    elif enemy_move[3]:
                        enemy.rect.y += int(enemy_move[3] * enemy_speed)
                    if counter % 2 == 0:
                        enemy.update_frame(enemy_move[2], enemy_move[3])
                    check_coordinates_and_rewrite_that(enemy, enemy_move)
            if keys[pygame.K_LCTRL]:
                [print(i) for i in board.map_list]
                [print(en.index) for en in board.enemys]
                print(999999999999999999)
        if board.expansion_sprites:
            for sprite in board.expansion_sprites:
                sprite.update()
        if board.expansion and not board.stop:
            board.expansion_sprites.draw(screen_for_level)
            if board.player.level == '1':
                max_index = 6
            elif board.player.level == '2':
                max_index = 2
            elif board.player.level == '3':
                max_index = 2
            elif board.player.level == '4':
                max_index = 2
            elif board.player.level == '5':
                max_index = 1
            elif board.player.level == 'λ':
                max_index = 1
            else:
                max_index = 0
            if board.expansion_wave_index == 1:
                sound_of_expansion = pygame.mixer.Sound('sounds/expansion.wav')
                sound_of_expansion.play()
            if board.expansion_wave_index == max_index:
                board.expansion = False
                board.expansion_indexes_list = []
                board.expansion_wave_index = 0
            else:
                for index in board.expansion_indexes_list[board.expansion_wave_index]:
                    ExpansionSector(index[0] * CELL_SIZE['X'],
                                    index[1] * CELL_SIZE['Y'],
                                    board.expansion_sprites,
                                    pygame.time.get_ticks())
                board.expansion_wave_index += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and board.stop:
                if exit_button.press(event):
                    running = False
            elif event.type == pygame.MOUSEBUTTONUP and board.stop:
                exit_button.press(event)

        if board.stop:
            board.print_end_game(screen_for_level)
            if not exit_button:
                if not board.win:
                    image = IMAGES['continue_button_lose']
                else:
                    image = IMAGES['continue_button_win']
                    if not result:
                        possibility = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, 'λ': 0}
                        if board.level == 1:
                            possibility['2'] = 1000
                        elif board.level == 2:
                            possibility['2'] = 2500
                        elif board.level == 3:
                            possibility['2'] = 3000
                        elif board.level == 4:
                            possibility['2'] = 3500
                            possibility['3'] = 500
                        elif board.level == 5:
                            possibility['3'] = 750
                        elif board.level == 6:
                            possibility['3'] = 900
                            possibility['4'] = 100
                        elif board.level == 7:
                            possibility['3'] = 1000
                            possibility['4'] = 300
                        elif board.level == 8:
                            possibility['4'] = 400
                        elif board.level == 9:
                            possibility['4'] = 500
                            possibility['5'] = 25
                        elif board.level == 10:
                            possibility['5'] = 75
                            possibility['λ'] = 1
                        lose_possibility = 10000 - sum(value for value in possibility.values())
                        possibility['lose'] = lose_possibility
                        result = random.choices([key for key in possibility],
                                                weights=[value for value in possibility.values()])[0]
                        if result != 'lose':
                            add_new_hero_to_saves(result)

                rect = image.get_rect()
                exit_button = Button((SCREEN_SIZE_FOR_LEVEL[0] - rect.w) // 2,
                                     SCREEN_SIZE_FOR_LEVEL[1] - 100 - rect.h,
                                     image,
                                     button_group,
                                     lambda: go_to_start_screen())
            button_group.draw(screen_for_level)
            if result != 'lose' and os.path.isfile('file.save') and result:
                if result not in [code_str(value, True)
                                  for value in
                                  get_data_from_file('file.save').split('\n')]:
                    font = pygame.font.Font('FreeSansBold.ttf', 25)
                    text = font.render(f'Теперь вам доступен персонаж {result} уровня!',
                                       1, (0, 0, 0))
                    screen_for_level.blit(text,
                                          ((SCREEN_SIZE_FOR_LEVEL[0] - text.get_width()) // 2,
                                           (SCREEN_SIZE_FOR_LEVEL[1] - text.get_height()) // 2 + 150))
        else:

            board.expansion_sprites.draw(screen_for_level)
            board.print_info_about_game(screen_for_level)
            board.all_sprites_group.draw(screen_for_level)
        pygame.display.flip()
        clock.tick(100)
    pygame.mixer.music.stop()
    del screen_for_level


def subtract_one_in_level():
    global CURRENT_LEVEL_FOR_BOARD
    CURRENT_LEVEL_FOR_BOARD -= 1


def add_one_in_level():
    global CURRENT_LEVEL_FOR_BOARD
    CURRENT_LEVEL_FOR_BOARD += 1


def go_to_start_screen():
    pygame.mixer.music.stop()
    global CURRENT_LEVEL_FOR_BOARD
    font = pygame.font.Font('FreeSansBold.ttf', 30)
    screen = pygame.display.set_mode(SCREEN_SIZE_FOR_LEVEL)

    sprites = pygame.sprite.Group()

    rect_for_choose_button = IMAGES['Choose_level'].get_rect()
    choose_level_button = Button((SCREEN_SIZE_FOR_LEVEL[0] - rect_for_choose_button.w) // 2,
                                 SCREEN_SIZE_FOR_LEVEL[1] - rect_for_choose_button.h - 50,
                                 IMAGES['Choose_level'],
                                 sprites,
                                 lambda level: start_game(level))

    text_about_choose_player_level = font.render('Выбор персонажа', 1, (0, 0, 0))
    surface_to_choose_player_level = pygame.Surface((text_about_choose_player_level.get_width(),
                                                     text_about_choose_player_level.get_height()))
    surface_to_choose_player_level.fill((150, 150, 150))
    surface_to_choose_player_level.blit(text_about_choose_player_level, (0, 0))
    x = (SCREEN_SIZE_FOR_LEVEL[0] - text_about_choose_player_level.get_width()) // 2
    choose_player_level_button = Button(x,
                                        80,
                                        surface_to_choose_player_level,
                                        sprites,
                                        lambda: change_heroes_screen())

    text_about_support = font.render('Справка', 1, (0, 0, 0))
    surface_to_support = pygame.Surface((text_about_support.get_width(),
                                         text_about_support.get_height()))
    surface_to_support.fill((150, 150, 150))
    surface_to_support.blit(text_about_support, (0, 0))
    x = (SCREEN_SIZE_FOR_LEVEL[0] - text_about_support.get_width()) // 2
    support_button = Button(x, 20, surface_to_support, sprites, lambda: support_screen())

    rect_for_arrow_button = IMAGES['Arrow_right'].get_rect()
    right_button = Button(SCREEN_SIZE_FOR_LEVEL[0] - rect_for_arrow_button.w - 50,
                          (SCREEN_SIZE_FOR_LEVEL[1] - rect_for_arrow_button.h) // 2,
                          IMAGES['Arrow_right'],
                          sprites,
                          lambda: add_one_in_level())
    left_button = Button(50,
                         (SCREEN_SIZE_FOR_LEVEL[1] - rect_for_arrow_button.h) // 2,
                         IMAGES['Arrow_left'],
                         sprites,
                         lambda: subtract_one_in_level())
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(IMAGES['Background'], (0, 0))
        text = font.render(f'Уровень {CURRENT_LEVEL_FOR_BOARD}', 1, (0, 0, 0))
        screen.blit(text, ((SCREEN_SIZE_FOR_LEVEL[0] - text.get_width()) // 2,
                           SCREEN_SIZE_FOR_LEVEL[1] - 160))
        screen.blit(IMAGES[f'level_{CURRENT_LEVEL_FOR_BOARD}'], (155, 155))
        sprites.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                left_button.press(event)
                right_button.press(event)
                if choose_player_level_button.press(event):
                    running = False
                if choose_level_button.press(event, CURRENT_LEVEL_FOR_BOARD):
                    running = False
                if support_button.press(event):
                    running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                left_button.press(event)
                right_button.press(event)
                choose_player_level_button.press(event)
                choose_level_button.press(event, CURRENT_LEVEL_FOR_BOARD)
                support_button.press(event)
            elif event.type == pygame.QUIT:
                running = False
        if CURRENT_LEVEL_FOR_BOARD > 10:
            CURRENT_LEVEL_FOR_BOARD %= 10
        elif CURRENT_LEVEL_FOR_BOARD < 1:
            CURRENT_LEVEL_FOR_BOARD = 10 - CURRENT_LEVEL_FOR_BOARD

        pygame.display.flip()
        clock.tick(100)


class ChangeLevelButton(Button):
    def __init__(self, x, y, image, text, group, function, level):
        super().__init__(x, y, image, group, function)
        self.text = text
        self.level = level

    def set_color(self, color):
        width = self.text.get_width()
        height = self.text.get_height()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.image.blit(self.text, (0, 0))

    def update(self, current_character_levels, current_level):
        if self.level == current_level:
            self.set_color((255, 255, 255))
        elif self.level in current_character_levels:
            self.set_color((0, 180, 0))
        else:
            self.set_color((150, 150, 150))


def get_data_from_file(file_name):
    file = open(file_name, 'r', encoding='utf-8')
    data = file.read()
    return data


def change_heroes_screen():
    pygame.mixer.music.stop()
    screen = pygame.display.set_mode(SCREEN_SIZE_FOR_LEVEL)
    global CURRENT_PLAYER_LEVEL
    changed = False

    def change_function(current_character_levels, level):
        if level in current_character_levels:
            global CURRENT_PLAYER_LEVEL
            CURRENT_PLAYER_LEVEL = level
            nonlocal changed, counter
            changed = True
            counter = 0

    if not os.path.isfile('file.save'):
        add_new_hero_to_saves('1')

    data = get_data_from_file('file.save').split('\n')
    current_character_levels = []
    possible_characters_str = [f'персонаж{level}уровня' for level in range(1, 6)]
    possible_characters_str.append('персонажλуровня')
    for value in data:
        decoded_value = code_str(value, decode=True)
        if decoded_value in possible_characters_str:
            current_character_levels.append(decoded_value[8:-6])
    buttons = pygame.sprite.Group()
    font = pygame.font.Font('FreeSansBold.ttf', 40)
    y = None
    counter = 0
    info_pictures_coords = []
    for level in ['1', '2', '3', '4', '5', 'λ']:
        color = (0, 0, 0) if level.isdigit() else (255, 0, 0)
        text_about_level = font.render(f'{level} уровень', 1, color)
        height = text_about_level.get_height()
        if y is None:
            y = (SCREEN_SIZE_FOR_LEVEL[1] - 6 * height) // 7
        width = text_about_level.get_width()
        x = (SCREEN_SIZE_FOR_LEVEL[0] - width) // 2
        level_surface = pygame.Surface((x, y))
        level_surface.fill((0, 0, 0))
        level_surface.blit(text_about_level, (0, 0))
        ChangeLevelButton(x,
                          y,
                          level_surface,
                          text_about_level,
                          buttons,
                          lambda level: change_function(current_character_levels, level),
                          level)
        info_pictures_coords.append((x, y))
        y += (SCREEN_SIZE_FOR_LEVEL[1] - 6 * height) // 7 + height
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(IMAGES['Background'], (0, 0))
        screen.blit(IMAGES['mine_expansion_1_level'], (info_pictures_coords[0][0] + width + 30,
                                                       info_pictures_coords[0][1]))
        screen.blit(IMAGES['mine_expansion_2_1_level'], (info_pictures_coords[1][0] + width + 30,
                                                         info_pictures_coords[1][1]))
        screen.blit(IMAGES['mine_expansion_2_2_level'], (info_pictures_coords[1][0] + width + 100,
                                                         info_pictures_coords[1][1]))
        screen.blit(IMAGES['mine_expansion_3_level'], (info_pictures_coords[2][0] + width + 30,
                                                       info_pictures_coords[2][1]))
        screen.blit(IMAGES['mine_expansion_4_level'], (info_pictures_coords[3][0] + width + 30,
                                                       info_pictures_coords[3][1]))
        screen.blit(IMAGES['mine_expansion_5_level'], (info_pictures_coords[4][0] + width + 30,
                                                       info_pictures_coords[4][1]))
        screen.blit(IMAGES['mine_expansion_λ_level'], (info_pictures_coords[5][0] + width + 30,
                                                       info_pictures_coords[5][1]))
        buttons.draw(screen)
        if changed:
            text = font.render('Сохранено!', 1, (255, 255, 255))
            width_text, height_text = text.get_width(), text.get_height()
            screen.blit(text, ((SCREEN_SIZE_FOR_LEVEL[0] - width_text) // 2,
                               (SCREEN_SIZE_FOR_LEVEL[1] - height_text) // 2))
            if counter % 20 == 0:
                running = False
                go_to_start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons.sprites():
                    button.press(event, button.level)
            elif event.type == pygame.MOUSEBUTTONUP:
                for button in buttons.sprites():
                    button.press(event)
        for button in buttons.sprites():
            button.update(current_character_levels, CURRENT_PLAYER_LEVEL)
        pygame.display.flip()
        clock.tick(100)
        counter += 1


def support_screen():
    pygame.mixer.music.stop()
    screen = pygame.display.set_mode(SCREEN_SIZE_FOR_LEVEL)
    running = True
    font_simple = pygame.font.Font('FreeSansBold.ttf', 40)
    text = font_simple.render('Выйти', 1, (0, 0, 0))
    exit_text_width = text.get_width()
    exit_text_height = text.get_height()
    surface = pygame.Surface((exit_text_width, exit_text_height))
    surface.fill((150, 150, 150))
    surface.blit(text, (0, 0))
    buttons = pygame.sprite.Group()
    exit_button = Button((SCREEN_SIZE_FOR_LEVEL[0] - exit_text_width) // 2,
                         SCREEN_SIZE_FOR_LEVEL[1] - exit_text_height - 30,
                         surface,
                         buttons,
                         lambda: go_to_start_screen())
    main_font = pygame.font.Font('FreeSansBold.ttf', 16)
    support_text = ['1) В этой игре вам доступны 10 локаций для прохождения',
                    '2) Для победы вам надо найти выход и не попасться врагам.',
                    '3) Выход скрыт среди разрушаемых (тёмных) стен, ',
                    'чтобы его найти вам нужно разрушать их',
                    '4) Выход (при открытии) обозначен квадратом желтого цвета',
                    '5) Игрок (вы) обозначен квадратом синего цвета',
                    '6) Враги обозначены красными треугольниками',
                    '7) Ваши мины обозначены черными кругами',
                    '8) Светлые стены неразрушимы',
                    '',
                    '',
                    '#Вы можете подорваться на своих же минах и проиграть',
                    '#На каждом уровне существует ограниченное число мест,',
                    '#на месте которых при загрузке уровня появляется выход',
                    '#При успешном прохождении каждой локации есть',
                    '#вероятность открытия нового уровня вашего персонажа',
                    '#Вероятность получения более высокого уровня ниже, ',
                    '#чем более низкого. ',
                    '#Все вероятности вам неизвестны, но вероятность получить',
                    '#5 уровень персонажа равна 0.75%, λ-уровень — 0.01%.',
                    '#Открытие нового уровня персонажа случайно, следовательно ',
                    '#есть вероятность, что вы НИКОГДА не откроете',
                    '#определенный уровень персонажа...']
    colors = {'red': (255, 0, 0), 'white': (255, 255, 255)}
    text = []
    for line in support_text:
        if line.startswith('#'):
            text.append(main_font.render(line[1:], 1, colors['red']))
        else:
            text.append(main_font.render(line, 1, colors['white']))
    while running:
        screen.fill((0, 0, 0))
        x = (SCREEN_SIZE_FOR_LEVEL[0] - max([line.get_width() for line in text])) // 2
        y = 20
        for line in text:
            screen.blit(line, (x, y))
            y += line.get_height() + 5
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.press(event):
                    running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                exit_button.press(event)
        buttons.draw(screen)
        pygame.display.flip()
        clock.tick(100)


def add_new_hero_to_saves(level):
    if not os.path.isfile('file.save'):
        file = open('file.save', 'w', encoding='utf-8')
        file.write(code_str('персонаж1уровня'))
        file.close()
    code_strings = get_data_from_file('file.save').split('\n')
    new_string = code_str(f'персонаж{level}уровня')
    if new_string not in code_strings:
        code_strings.append(new_string)
        data = '\n'.join(code_strings)
        file = open('file.save', 'w', encoding='utf-8')
        file.write(data)
        file.close()


def code_str(string, decode=False):
    new_string = ''
    count = 0
    values = [17, 19, 13, 23, 11, 29, 57, 3]
    if decode:
        values = [-1 * value for value in values]
    for symb in string:
        new_string += chr(ord(symb) + values[count % len(values)])
        count += 1
    return new_string


"""Высокий приоритет задачи"""
# import psutil, os
# p = psutil.Process(os.getpid())
# p.nice(psutil.HIGH_PRIORITY_CLASS)
"""                                    """
go_to_start_screen()

pygame.quit()
