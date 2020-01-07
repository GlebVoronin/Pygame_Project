import pygame
import random
import os

pygame.init()

CELL_SIZE = {'X': 20, 'Y': 20}
CELL_COUNT = {'X': 31, 'Y': 31}
EXPANSION_TIME = 300  # милисекунд
CURRENT_LEVEL_FOR_BOARD = 1
SCREEN_SIZE_FOR_LEVEL = CELL_SIZE['X'] * CELL_COUNT['X'], CELL_SIZE['Y'] * CELL_COUNT['Y'] + 100
CURRENT_PLAYER_LEVEL = 1
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
    expansion_image = load_image('expansion.png')
    background_image = load_image('background.png')
    arrow_right_image = load_image('arrow_right.png')
    arrow_left_image = load_image('arrow_left.png')
    arrow_top_image = load_image('arrow_top.png')
    arrow_bottom_image = load_image('arrow_bottom.png')
    choose_level_image = load_image('choose_level.png')
    continue_button_lose_image = load_image('back_to_main_screen.png')
    continue_button_win_image = load_image('back_to_main_screen_after_win.png')
    level_1_image = load_image('level_1.png')
    level_2_image = load_image('level_2.png')
    level_3_image = load_image('level_3.png')
    level_4_image = load_image('level_4.png')
    level_5_image = load_image('level_5.png')
    level_6_image = load_image('level_6.png')
    level_7_image = load_image('level_7.png')
    level_8_image = load_image('level_8.png')
    level_9_image = load_image('level_9.png')
    level_10_image = load_image('level_10.png')
    dictionary['Enemy'] = enemy_image
    dictionary['Exit'] = exit_image
    dictionary['Wall'] = wall_not_destroyable_image
    dictionary['Wall(Destroyable)'] = wall_destroyable_image
    dictionary['Player'] = player_image
    dictionary['Shell'] = shell_image
    dictionary['Expansion'] = expansion_image
    dictionary['Background'] = background_image
    dictionary['Arrow_right'] = arrow_right_image
    dictionary['Arrow_left'] = arrow_left_image
    dictionary['Arrow_top'] = arrow_top_image
    dictionary['Arrow_bottom'] = arrow_bottom_image
    dictionary['Choose_level'] = choose_level_image
    dictionary['level_1'] = level_1_image
    dictionary['level_2'] = level_2_image
    dictionary['level_3'] = level_3_image
    dictionary['level_4'] = level_4_image
    dictionary['level_5'] = level_5_image
    dictionary['level_6'] = level_6_image
    dictionary['level_7'] = level_7_image
    dictionary['level_8'] = level_8_image
    dictionary['level_9'] = level_9_image
    dictionary['level_10'] = level_10_image
    dictionary['continue_button_lose'] = continue_button_lose_image
    dictionary['continue_button_win'] = continue_button_win_image


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
                        or map_list[way[1]][way[0]] == SYMB_FOR_GRASS):
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
        self.image = IMAGES['Enemy']
        self.level = level
        self.index = index
        self.board = board
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

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
        self.game_duration_in_seconds = self.level * 30 + 120
        self.enemy_move = {}
        self.shells = {}
        self.shell_limit = 3
        self.enemys = []

    def fill_enemy_move(self):
        for enemy in self.enemys:
            self.enemy_move[enemy.index] = [0, 0, 0, 0]

    def end_game(self, win=False):
        if not self.stop:
            self.stop = True
            self.win = win

    def print_info_about_game(self, screen):
        font = pygame.font.Font(None, 35)
        seconds_left = (pygame.time.get_ticks() - self.start_ticks) // 1000
        seconds = self.game_duration_in_seconds - seconds_left
        if seconds <= 0:
            self.end_game(False)
        else:
            minutes, seconds = seconds // 60, seconds % 60
            text = font.render(f'времени осталось: {minutes}:{seconds}      '
                               f'мин осталось: {self.shell_limit - len(self.shells)}',
                               1, (0, 0, 0))
            screen.blit(text, ((CELL_SIZE['X'] * CELL_COUNT['X'] - text.get_width()) // 2,
                               (CELL_SIZE['Y'] * CELL_COUNT['Y'] + 50 - text.get_height() // 2)))

    def print_end_game(self, screen):
        if self.stop:
            font = pygame.font.Font(None, 50)
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
        new_coordinates.append([count_cell_index(*coord) for coord in coordinates_bombs])
        if self.player.level == 1:
            for i in range(1, 6):
                new_coordinates.append([])

                def check_index(index_x, index_y):
                    if -1 < index_x < CELL_COUNT['X'] and -1 < index_y < CELL_COUNT['Y']:
                        return True
                    return False

                def check_map_for_wall(index_x, index_y):
                    if self.map_list[index_x][index_y] == SYMB_FOR_WALL:
                        return True
                    return False

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
                    self.player = Player(col * CELL_SIZE['X'], row * CELL_SIZE['Y'], self)
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
    def __init__(self, x, y, board, level=1):
        super().__init__()
        self.image = IMAGES['Player']
        self.board = board
        self.level = level
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self, vector_x, vector_y, player_move):
        index_before_move = count_cell_index(self.rect.x,
                                             self.rect.y)
        index_after_move = count_cell_index((vector_x + index_before_move[0]) * CELL_SIZE['X'],
                                            (vector_y + index_before_move[1]) * CELL_SIZE['Y'])
        if (-1 < index_after_move[0] < CELL_COUNT['X']
                and -1 < index_after_move[1] < CELL_COUNT['Y']):
            if self.board.map_list[index_after_move[1]][index_after_move[0]] == SYMB_FOR_GRASS:
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
    screen_for_level = pygame.display.set_mode(SCREEN_SIZE_FOR_LEVEL)
    all_sprites_group = pygame.sprite.Group()
    board = Board(all_sprites_group, level)
    board.generate_new_level()
    board.fill_enemy_move()
    running = True
    buttons_pressed = {'SPACE': False, 'RETURN': False}
    counter = 0
    button_group = pygame.sprite.Group()
    shell_limit = 3
    player_speed = 2
    enemy_speed = 1
    index_to_shell = 0
    exit_button = None
    player_move = [0, 0, 0, 0]
    game_colors = {'RUN': (0, 255, 0), 'WIN': (200, 255, 20), 'LOSE': (150, 20, 20)}
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
            a = sum([i.count('@') for i in board.map_list])
            if a > 1:
                print(a, [print(k) for k in board.map_list])
                print(""" \n\n""")
            for index in board.enemy_move:
                values = board.enemy_move[index]
                if not values[2] and not values[3]:
                    for enemy in board.enemys:
                        if enemy.index == index:
                            enemy.update((board.player.rect.x, board.player.rect.y))
                            break
            for enemy in board.enemys:
                if enemy.index in board.enemy_move:
                    values = board.enemy_move[enemy.index]
                    if values[2]:
                        enemy.rect.x += int(values[2] * enemy_speed)
                    if values[3]:
                        enemy.rect.y += int(values[3] * enemy_speed)
                    check_coordinates_and_rewrite_that(enemy, values)
            if player_move[2]:
                board.player.rect.x += player_move[2] * player_speed
            if player_move[3]:
                board.player.rect.y += player_move[3] * player_speed
            check_coordinates_and_rewrite_that(board.player, player_move)
            pygame.draw.rect(screen_for_level, (150, 150, 150),
                             [0,
                              CELL_SIZE['Y'] * CELL_COUNT['Y'],
                              CELL_SIZE['X'] * CELL_COUNT['X'],
                              CELL_SIZE['Y'] * CELL_COUNT['Y'] + 100])
            keys = pygame.key.get_pressed()
            if not player_move[2] and not player_move[3] and counter % 3 == 0:
                if keys[pygame.K_LEFT]:
                    player_move = board.player.update(-1, 0, player_move)
                if keys[pygame.K_RIGHT]:
                    player_move = board.player.update(1, 0, player_move)
                if keys[pygame.K_UP]:
                    player_move = board.player.update(0, -1, player_move)
                if keys[pygame.K_DOWN]:
                    player_move = board.player.update(0, 1, player_move)
            if keys[pygame.K_RETURN]:
                if not buttons_pressed['RETURN'] and len(board.shells):
                    buttons_pressed['RETURN'] = True
                    board.update_shells()
            else:
                buttons_pressed['RETURN'] = False
            if keys[pygame.K_SPACE]:
                if not buttons_pressed['SPACE'] and len(board.shells) < shell_limit:
                    buttons_pressed['SPACE'] = True
                    shell = Shell(board.player.rect.x, board.player.rect.y, index_to_shell)
                    shell.add(board.all_sprites_group)
                    board.shells[index_to_shell] = shell
                    index_to_shell += 1
            else:
                buttons_pressed['SPACE'] = False
            if keys[pygame.K_LCTRL]:
                [print(i) for i in board.map_list]
                [print(en.index) for en in board.enemys]
                print(999999999999999999)
        if board.expansion_sprites:
            for sprite in board.expansion_sprites:
                sprite.update()
        if board.expansion:
            board.expansion_sprites.draw(screen_for_level)
            if board.expansion_wave_index == 6:
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
                    del screen_for_level
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
                rect = image.get_rect()
                exit_button = Button((SCREEN_SIZE_FOR_LEVEL[0] - rect.w) // 2,
                                     SCREEN_SIZE_FOR_LEVEL[1] - 100 - rect.h,
                                     image,
                                     button_group,
                                     lambda: go_to_start_screen())
            button_group.draw(screen_for_level)
        else:

            board.expansion_sprites.draw(screen_for_level)
            board.print_info_about_game(screen_for_level)
            board.all_sprites_group.draw(screen_for_level)
        pygame.display.flip()
        clock.tick(100)
    del screen_for_level


def subtract_one_in_level():
    global CURRENT_LEVEL_FOR_BOARD
    CURRENT_LEVEL_FOR_BOARD -= 1


def add_one_in_level():
    global CURRENT_LEVEL_FOR_BOARD
    CURRENT_LEVEL_FOR_BOARD += 1


def go_to_start_screen():
    global CURRENT_LEVEL_FOR_BOARD
    screen = pygame.display.set_mode(SCREEN_SIZE_FOR_LEVEL)

    sprites = pygame.sprite.Group()

    rect_for_choose_button = IMAGES['Choose_level'].get_rect()
    choose_level_button = Button((SCREEN_SIZE_FOR_LEVEL[0] - rect_for_choose_button.w) // 2,
                                 SCREEN_SIZE_FOR_LEVEL[1] - rect_for_choose_button.h - 50,
                                 IMAGES['Choose_level'],
                                 sprites,
                                 lambda level: start_game(level))
    choose_player_level_button = Button((SCREEN_SIZE_FOR_LEVEL[0] - rect_for_choose_button.w) // 2,
                                        50,
                                        IMAGES['Choose_level'],
                                        sprites,
                                        lambda: change_heroes_screen())
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
        font = pygame.font.Font(None, 40)
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
                    del screen
                    running = False
                if choose_level_button.press(event, CURRENT_LEVEL_FOR_BOARD):
                    del screen
                    running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                left_button.press(event)
                right_button.press(event)
                choose_player_level_button.press(event)
                choose_level_button.press(event, CURRENT_LEVEL_FOR_BOARD)
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
    possible_characters_str.append('персонажлямбдауровня')
    for value in data:
        decoded_value = code_str(value, decode=True)
        if decoded_value in possible_characters_str:
            current_character_levels.append(decoded_value[8:-6])
    buttons = pygame.sprite.Group()
    font = pygame.font.Font(None, 40)
    y = None
    counter = 0
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
        y += (SCREEN_SIZE_FOR_LEVEL[1] - 6 * height) // 7 + height
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(IMAGES['Background'], (0, 0))
        buttons.draw(screen)
        if changed:
            text = font.render('Сохранено!', 1, (255, 255, 255))
            width, height = text.get_width(), text.get_height()
            screen.blit(text, ((SCREEN_SIZE_FOR_LEVEL[0] - width) // 2,
                               (SCREEN_SIZE_FOR_LEVEL[1] - height) // 2))
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
