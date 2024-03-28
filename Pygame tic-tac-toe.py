import pygame
from random import choice, randint

#инициализируем pygame
pygame.init()

#необходимые переменные
WIN_SIZE = 800
WIN_COLOR = "white"
CELL_SIZE = WIN_SIZE // 3
GRID_SIZE = 2
GRID_COLOR = "black"
CROSS_SIZE = 5
CROSS_COLOR = "red"
CIRCLE_SIZE = 5
CIRCLE_COLOR = "lightblue"
X = 'x'
O = 'o'
DRAW = "ничья"
CAPTION_GAME = "Крестики-нолики"
FONT_END = pygame.font.SysFont("Futura Pt", WIN_SIZE//5)
FONT_END_COLOR = "black"
#
#создаем переменные для игры
def start_game():
    #человек будет ходить либо крестиком, либо ноликом. Выбирается случайно
    human = choice([X, O])
    #бот
    bot = X if human == O else O
    #каждый элемент списка - клетка. 0 - пустая клетка, то есть изначально доска пустая
    table = [0 for i in range(9)]
    return human, bot, table


#рисовка доски
def draw_table(table):
    #рисовка сетки
    for i in range(1,3):
        pygame.draw.line(screen, GRID_COLOR, (0,i*CELL_SIZE), (WIN_SIZE, i*CELL_SIZE), GRID_SIZE)
        pygame.draw.line(screen, GRID_COLOR, (i*CELL_SIZE, 0), (i*CELL_SIZE,WIN_SIZE), GRID_SIZE)
    #рисовка крестиков и ноликов
    for i in range(9):
        #номер столбца
        x = i % 3
        #номер строки
        y = i // 3
        if table[i] == 'x':
            pygame.draw.line(screen, CROSS_COLOR, (x*CELL_SIZE,y*CELL_SIZE), ((x+1)*CELL_SIZE,(y+1)*CELL_SIZE), CROSS_SIZE)
            pygame.draw.line(screen, CROSS_COLOR, ((x+1)*CELL_SIZE,y*CELL_SIZE), (x*CELL_SIZE,(y+1)*CELL_SIZE), CROSS_SIZE)
        elif table[i] == 'o':
            pygame.draw.circle(screen, CIRCLE_COLOR, ((x+0.5)*CELL_SIZE,(y+0.5)*CELL_SIZE), CELL_SIZE//2, CIRCLE_SIZE)
            
    
#проверка победы
def check_win():
    for i in range(3):
        #проверка строки
        if table[i] == table[i+3] and table[i+3] == table[i+6] and table[i+6] != 0:
            return table[i]
        #проверка столбца
        if table[i*3] == table[i*3+1] and table[i*3+1] == table[i*3+2] and table[i*3+2] != 0:
            return table[i*3]
    #проверка двух диагоналей
    if table[0] == table[4] and table[4] == table[8] and table[8] != 0:
        return table[0]
    if table[2] == table[4] and table[4] == table[6] and table[6] != 0:
        return table[4]
    #проверка на ничью
    if 0 not in table:
        return DRAW
    #игра продолжается
    return False


#окончание игры
def game_over(winner):
    global human, bot, table
    human, bot, table = start_game()
    while True:
        for event in pygame.event.get():
            #выход
            if event.type == pygame.QUIT:
                pygame.quit()
            #перезапуск игры на space
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

        #отрисовывам фон
        screen.fill(WIN_COLOR)
        #рендерим текст
        text_render = FONT_END.render(winner, 1, FONT_END_COLOR)
        #отображаем победителя по середине экрана
        screen.blit(text_render,(WIN_SIZE//2 - text_render.get_width()//2,
                                WIN_SIZE//2 - text_render.get_height()//2))
        pygame.display.flip()



#ход бота         
def bot_move(table):
    #клетку выбираем по алгоритму минимакса https://habr.com/ru/post/329058/
    move = minmax(table,bot)
    #тк функция возвращает словарь, берем индекс
    ind = move["index"]
    if ind == -1:
        return
    #запоминаем ход
    table[ind] = bot
    winner = check_win()
    if winner:
        game_over(winner)



#move - кто ходит
def minmax(table, player):
    #проверяем победу
    winner = check_win()
    if winner == X:
        return {"score":-1,"index":-1}
    elif winner == O:
        return {"score":1,"index":-1}
    elif winner == DRAW:
        return {"score":0,"index":-1}
    #запоминаем оценку каждой клетки 
    moves = []
    for i in range(9):
        if table[i] == 0:
            #делаем ход
            table[i] = player
            #score, ind
            move = minmax(table, bot if player == human else human)
            move["index"] = i
            #очищаем
            table[i] = 0
            #запоминаем
            moves.append(move)

    #находим лучший ход
    best = moves[0]
    #для бота максимум
    if player == O:   
        for move in moves:
            if move['score'] > best["score"]:
                best = move
    #для игрока минимум
    else:
        for move in moves:
            if move['score'] < best["score"]:
                best = move
                
    return best

#ход человека 
def human_move(table, x,  y):
    #получаем номер строки и столбца, куда кликнули
    x //= CELL_SIZE
    y //= CELL_SIZE
    #проверяем, что клетка пустая
    if table[y*3 + x] == 0:
        #ходим
        table[y*3 + x] = human
        #проверяем победу
        winner = check_win()
        if winner:
            game_over(winner)
        #ход сделан, вернем true
        return True
    #ход не сделан, вернем false
    return False


human, bot, table = start_game()
#создаем поверхность, на которой будем рисовать
screen = pygame.display.set_mode((WIN_SIZE,WIN_SIZE))
#задаем заголовок игры
pygame.display.set_caption(CAPTION_GAME)
game = True
#основной цикл игры
while game:
    #если бот - крестик, то он ходит первым
    if bot == X and table.count(0) == 9:
        bot_move(table)
    
    #заливка фона
    screen.fill(WIN_COLOR)
    #отрисовка доски
    draw_table(table)
    #отображение на экране
    pygame.display.flip()

    #перебираем все события
    for event in pygame.event.get():
        #выход
        if event.type == pygame.QUIT:
            pygame.quit()
            game = False
        #перезапуск игры на space
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                human, bot, table = start_game()
        #проверка клика игроком
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                #если кликнули в пустую клетку
                check = human_move(table,*event.pos)
                if check:
                    bot_move(table)
    
