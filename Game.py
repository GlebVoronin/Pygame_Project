import pygame
import random

pygame.init()

CELL_SIZE = {'X': 20, 'Y': 20}
CELL_COUNT = {'X': 31, 'Y': 31}
SCREEN_SIZE = CELL_SIZE['X'] * CELL_COUNT['X'], CELL_SIZE['Y'] * CELL_COUNT['Y']
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
SYMB_FOR_WALL = '#'
SYMB_FOR_ENEMY = 'X'
SYMB_FOR_PLAYER = '@'
SYMB_FOR_DESTROYABLE_WALL = 'd'
SYMB_FOR_GRASS = '.'
SYMB_FOR_EXIT = 'E'


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


IMAGES = {'Enemy': None,
          'Player': None,
          'Grass': None,
          'Exit': None,
          'Shell': None,
          'Wall': None,
          'Wall(Destroyable)': None}


def load_base_images(dictionary):
    enemy_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    enemy_image.fill((255, 0, 0))
    player_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    player_image.fill((0, 0, 255))
    exit_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    exit_image.fill((255, 255, 0))
    wall_destroyable_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    wall_destroyable_image.fill((100, 100, 100))
    wall_not_destroyable_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    wall_not_destroyable_image.fill((180, 180, 180))
    shell_image = pygame.Surface((CELL_SIZE['X'], CELL_SIZE['Y']))
    rect = pygame.draw.rect(shell_image, (0, 255, 0), (0, 0, CELL_SIZE['X'], CELL_SIZE['Y']))
    shell = pygame.draw.circle(shell_image,
                               (0, 0, 0),
                               (CELL_SIZE['X'] // 2,
                                CELL_SIZE['Y'] // 2),
                               CELL_SIZE['X'] // 2 - 2)
    dictionary['Enemy'] = enemy_image
    dictionary['Exit'] = exit_image
    dictionary['Wall'] = wall_not_destroyable_image
    dictionary['Wall(Destroyable)'] = wall_destroyable_image
    dictionary['Player'] = player_image
    dictionary['Shell'] = shell_image


load_base_images(IMAGES)
other_group = pygame.sprite.Group()


def way_to_point_in_labirint(start_point_index, end_point_index, map):
    dict_of_points = {start_point_index: [(0, 0)]}
    past_ways = []
    current_points = []
    while end_point_index not in dict_of_points.keys():
        if current_points == list(dict_of_points.keys()):
            return []
        current_points = list(dict_of_points.keys())
        points_in_dict = list(dict_of_points.keys())
        for point in points_in_dict:
            if point in past_ways:
                continue
            new_ways = [(point[0] - 1, point[1]),
                        (point[0] + 1, point[1]),
                        (point[0], point[1] - 1),
                        (point[0], point[1] + 1)]
            new_ways = [way
                        for way in new_ways
                        if -1 < way[0] < len(map[0])
                        and -1 < way[1] < len(map)
                        and way not in past_ways]
            for way in new_ways:
                if (map[way[1]][way[0]] == SYMB_FOR_PLAYER
                        or map[way[1]][way[0]] == SYMB_FOR_GRASS):
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


class Exit(WallBrickDestroyable):
    def check_exit(self, player_position):
        if self.rect.x == player_position[0] and self.rect.y == player_position[1]:
            return True
        return False

    def destroy(self):
        self.image = IMAGES['Exit']


class Shell(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = IMAGES['Shell']
        self.rect = self.image.get_rect()
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
                        or new_ways[index][0] >= SCREEN_SIZE[0]
                        or new_ways[index][1] < 0
                        or new_ways[index][1] >= SCREEN_SIZE[1]):
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
                    self.board.enemy_move.append({self.index: [*new_ways[index], vector_x, vector_y]})
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
                    self.board.enemy_move.append({self.index: [new_index[0] * CELL_SIZE['X'],
                                                  new_index[1] * CELL_SIZE['Y'], vector_x,
                                                  vector_y]})
                    self.board.replace_symbols_after_move(index_before_move,
                                                          new_index,
                                                          SYMB_FOR_ENEMY)


class Board:
    def __init__(self, all_sprites_group, level=1):
        self.all_sprites_group = all_sprites_group
        self.level = level
        self.map_list = None
        self.player = None
        self.stop = False
        self.win = False
        self.exit = None
        self.enemy_move = []
        self.shells = []
        self.enemys = []

    def end_game(self, win=False):
        if not self.stop:
            self.stop = True
            [print(i) for i in self.map_list]
            self.win = win

    def print_end_game(self):
        if self.stop:
            font = pygame.font.Font(None, 50)
            if self.win:
                text = font.render('Вы победили', 1, (100, 0, 255))
            else:
                text = font.render('Вы проиграли', 1, (100, 0, 255))

            screen.blit(text, ((SCREEN_SIZE[0] - text.get_width()) // 2,
                               (SCREEN_SIZE[1] - text.get_height()) // 2))

    def replace_symbols_after_move(self, index_before, index_after, type_of_creature):
        try:
            self.map_list[index_before[1]][index_before[0]] = SYMB_FOR_GRASS
            self.map_list[index_after[1]][index_after[0]] = type_of_creature
        except IndexError:
            print('Index Error')

    def update_shells(self, event):
        coordinates_bombs = []
        for shell in self.shells:
            if event != 'ALL' and shell.rect.collidepoint(event.pos):
                coordinates_bombs.append((shell.rect.x, shell.rect.y))
                shell.destroy()
            elif event == 'ALL':
                coordinates_bombs.append((shell.rect.x, shell.rect.y))
                shell.destroy()
        for coordinates in coordinates_bombs:
            new_coordinates = [(coordinates[0] + i * CELL_SIZE['X'],
                                coordinates[1]) for i in range(-5, 6)]
            new_coordinates_two = [(coordinates[0],
                                    coordinates[1] + i * CELL_SIZE['Y']) for i in range(-5, 6)]
            new_coordinates.extend(new_coordinates_two)
            for coord in new_coordinates:
                index = count_cell_index(*coord)
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
            wall = WallBrickDestroyable(coords[1] * CELL_SIZE['X'], coords[0] * CELL_SIZE['Y'])
            wall.add(self.all_sprites_group)
            self.map_list[coords[1]][coords[0]] = SYMB_FOR_DESTROYABLE_WALL


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, board):
        super().__init__()
        self.image = IMAGES['Player']
        self.board = board
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self, vector_x, vector_y):
        index_before_move = count_cell_index(self.rect.x,
                                             self.rect.y)
        index_after_move = count_cell_index((vector_x + index_before_move[0]) * CELL_SIZE['X'],
                                            (vector_y + index_before_move[1]) * CELL_SIZE['Y'])
        if (-1 < index_after_move[0] < CELL_COUNT['X']
                and -1 < index_after_move[1] < CELL_COUNT['Y']):
            if self.board.map_list[index_after_move[1]][index_after_move[0]] == SYMB_FOR_GRASS:
                global player_move
                player_move = [index_after_move[0] * CELL_SIZE['X'],
                               index_after_move[1] * CELL_SIZE['Y'],
                               vector_x,
                               vector_y]
                self.board.replace_symbols_after_move(index_before_move,
                                                      index_after_move,
                                                      SYMB_FOR_PLAYER)
            elif self.board.map_list[index_after_move[1]][index_after_move[0]] == SYMB_FOR_EXIT:
                self.board.end_game(win=True)

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
all_sprites_group = pygame.sprite.Group()

board = Board(all_sprites_group, 1)
board.generate_new_level()
start_game = True
running = True
buttons_pressed = {'ENTER': False}
counter = 0
player_speed = 2
enemy_speed = 2 + board.level * 3 / 100
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
    screen.fill(color)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            board.update_shells(event)
    keys = pygame.key.get_pressed()
    if not player_move[2] and not player_move[3] and counter % 3 == 0:
        if keys[pygame.K_LEFT]:
                board.player.update(-1, 0)
        if keys[pygame.K_RIGHT]:
                board.player.update(1, 0)
        if keys[pygame.K_UP]:
                board.player.update(0, -1)
        if keys[pygame.K_DOWN]:
                board.player.update(0, 1)
    if keys[pygame.K_RETURN]:
        board.update_shells('ALL')
    if keys[pygame.K_KP_ENTER]:
        if not buttons_pressed['ENTER']:
            buttons_pressed['ENTER'] = True
            shell = Shell(board.player.rect.x, board.player.rect.y)
            shell.add(board.all_sprites_group)
            board.shells.append(shell)
    else:
        buttons_pressed['ENTER'] = False
    if keys[pygame.K_LCTRL]:
        [print(i) for i in board.map_list]
        [print(en.index) for en in board.enemys]
    if counter == 40:
        for enemy in board.enemys:
            enemy.update((board.player.rect.x, board.player.rect.y))
            counter = 0
    for enemy in board.enemys:
        if enemy.index in board.enemy_move:
            if board.enemy_move[enemy.index][2]:
                enemy.rect.x += board.enemy_move[enemy.index][2] * enemy_speed
            if board.enemy_move[enemy.index][3]:
                enemy.rect.y += board.enemy_move[enemy.index][3] * enemy_speed
            check_coordinates_and_rewrite_that(enemy, board.enemy_move[enemy.index])
    if player_move[2]:
        board.player.rect.x += player_move[2] * player_speed
    if player_move[3]:
        board.player.rect.y += player_move[3] * player_speed
    check_coordinates_and_rewrite_that(board.player, player_move)
    if board.stop:
        board.print_end_game()
    else:
        board.all_sprites_group.draw(screen)
    pygame.display.flip()
    clock.tick(100)

pygame.quit()
