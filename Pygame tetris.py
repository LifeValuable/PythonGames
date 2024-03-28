import pygame
from copy import deepcopy
from random import choice, randrange

TILE_COLS, TILE_ROWS = 10, 20
TILE = 43
GAME_RES = TILE_COLS * TILE, TILE_ROWS * TILE
RES = TILE_COLS * TILE + 300, TILE_ROWS * TILE
FPS = 60
MOVING = pygame.USEREVENT

pygame.init()
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(TILE_COLS) for y in range(TILE_ROWS)]

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

figures = [[pygame.Rect(x + TILE_COLS // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(1, 1, TILE - 2, TILE - 2)
field = [[0 for i in range(TILE_COLS)] for j in range(TILE_ROWS)]

#сделать через события
anim_count, anim_speed, anim_limit = 0, 60, 2000



main_font = pygame.font.SysFont("Futura PT", 65)
font = pygame.font.SysFont("Futura PT", 45)

title_tetris = main_font.render('TETRIS', True, pygame.Color('darkorange'))
title_score = font.render('score:', True, pygame.Color('green'))

get_color = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}





def check_borders():
    for i in range(4):
        if figure[i].x < 0 or figure[i].x > TILE_COLS - 1:
            return True
        elif figure[i].y > TILE_ROWS - 1 or field[figure[i].y][figure[i].x]:
            return True
    return False

def move_x():
    global figure
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if check_borders():
            figure = deepcopy(figure_old)
            break

def move_y():
    global anim_count, anim_limit, anim_speed, figure, color, next_color, next_figure
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_speed = 60
                break

def rotate():
    global figure, rotating
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotating:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
            if check_borders():
                figure = deepcopy(figure_old)
                break
        rotating = False

def check_lines():
    global score, anim_limit
    #проверяем линии снизу вверх
    line, lines = TILE_ROWS - 1, 0
    for row in range(TILE_ROWS - 1, -1, -1):
        #кол-во непустых ячеек
        count = 0
        for i in range(TILE_COLS):
            #если ячейка непустая, то увеличиваем count
            if field[row][i]:
                count += 1
        #копируем из строки row в строку line   
        field[line] = field[row]
        #если не весь ряд заполнился поднимаемся выше
        if count < TILE_COLS:
            line -= 1
        #иначе увеличиваем скорость и кол-во собранных линий
        else:
            anim_limit *= 0.95
            lines += 1
    # compute score
    score += scores[lines]

def draw():
    sc.fill((0,0,0))
    sc.blit(game_sc, (0,0))

    game_sc.fill((28,50,30))

    # draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]
    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)
    # draw field
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)
    # draw next figure
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 380
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figure_rect)
    # draw titles
    sc.blit(title_tetris, (485, 0))
    sc.blit(title_score, (535, 580))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (550, 640))

def check_game_over():
    for i in range(TILE_COLS):
        if field[0][i]:
            return True
    return False

def game_over():
    global field, anim_count, anim_speed, anim_limit, score
    field = [[0 for i in range(TILE_COLS)] for i in range(TILE_ROWS)]
    anim_count, anim_speed, anim_limit = 0, 60, 2000
    score = 0
    for i_rect in grid:
        pygame.draw.rect(game_sc, get_color(), i_rect)
        sc.blit(game_sc, (0, 0))
        pygame.display.flip()
        clock.tick(200)

while True:
    dx, rotating = 0, False
    # control
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_UP:
                rotating = True
            elif event.key == pygame.K_DOWN:
                if anim_speed == 60:
                    anim_speed = 500
                else:
                    anim_speed = 60
    
    # move x
    move_x()
    # move y
    move_y()
    # rotate
    rotate()
    # check lines
    check_lines()
    draw()
    # game over
    if check_game_over():
        game_over()

    pygame.display.flip()
    clock.tick(FPS)