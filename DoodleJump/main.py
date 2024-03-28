import pygame
import random
import os
pygame.init()

WIDTH = 400
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumpy")
clock = pygame.time.Clock()

#variables
fps = 60
GRAVITY = 1
MAX_PLATFORMS = 10
SCROLL_THRESH = 200
scroll = 0
bg_scroll = 0
is_game_over = False
score = 0
high_score = 0

if os.path.exists("score.txt"):
    with open("score.txt", "r") as file:
        high_score = int(file.read())
#images
bg_image = pygame.image.load("assets/bg.png")
platform_image = pygame.image.load("assets/wood.png")

#fonts
font_small = pygame.font.SysFont("Lucida Sans", 20)
font_big = pygame.font.SysFont("Lucida Sans", 24)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/jump.png")
        self.rect = self.image.get_rect(center = (x,y))
        self.flip = False
        self.speed_x = 10
        self.speed_y = 0
    
    def draw(self, screen):
        screen.blit(
            pygame.transform.flip(self.image, self.flip, False), 
            self.rect
                    )

    def jump(self):
        self.speed_y = -20

    def move(self):
        global scroll
        #offset
        dx = 0
        dy = 0
        scroll = 0
       
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            dx = -self.speed_x
            self.flip = True
        if keys[pygame.K_d]:
            dx = self.speed_x
            self.flip = False

        #gravity
        self.speed_y += GRAVITY
        dy += self.speed_y

        #borders
        if dx + self.rect.left < 0:
            dx = -self.rect.left
        elif dx + self.rect.right > WIDTH:
            dx = WIDTH - self.rect.right

        """#ground
        if self.rect.bottom + dy > HEIGHT:
            dy = 0
            self.jump()"""
    
        #platforms
        for platform in platform_group:
            if (self.rect.bottom < platform.rect.centery and
                self.speed_y > 0 and 
                platform.rect.colliderect(self.rect.x + dx, self.rect.y + dy,
                                    self.rect.width, self.rect.height)):
                dy = 0
                self.jump()

        #scrolling
        if self.rect.top <= SCROLL_THRESH and self.speed_y < 0:
            scroll = -dy

        #move
        self.rect.x += dx
        self.rect.y += dy + scroll
    
    def update(self):
        self.move()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving = False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.rect = self.image.get_rect(topleft = (x, y))
        self.moving = moving
        self.direction = random.choice([-1, 1])
        self.move_counter = random.randint(0, 50)

    def update(self):
        if self.moving:
            self.move_counter += 1
            self.rect.x += self.direction
        if self.move_counter >= 100:
            self.direction *= -1
            self.move_counter = 0
        #update y
        self.rect.y += scroll
        if self.rect.y > HEIGHT:
            self.kill()


player = Player(WIDTH // 2, HEIGHT * 3 // 4)

platform_group = pygame.sprite.Group()
platform_group.add(Platform(WIDTH // 2 - 50, HEIGHT - 50, 100))
"""for i in range(MAX_PLATFORMS):
    platform_width = random.randint(40,60)
    platform_x = random.randint(0, WIDTH - platform_width)
    platform_y = i * random.randint(80,120)
    platform_group.add(Platform(platform_x, platform_y, platform_width))"""

    
def draw_background():
    global bg_scroll
    bg_scroll += scroll
    if bg_scroll >= HEIGHT:
        bg_scroll -= HEIGHT
    screen.blit(bg_image, (0, bg_scroll))
    screen.blit(bg_image, (0, bg_scroll - HEIGHT))

def draw_text(text, font: pygame.font.SysFont, color, x, y):
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

def draw_hight_score():
    y = score - high_score + SCROLL_THRESH
    draw_text("HIGH SCORE", font_small, (255, 255, 255), WIDTH - 130, y)
    pygame.draw.line(screen, (255, 255, 255), (0, y), (WIDTH, y))

def draw():
    draw_background()
    platform_group.draw(screen)
    player.draw(screen)
    draw_text(f"SCORE: {score}", font_small, (255, 255, 255), 10, 10)
    draw_hight_score()
    pygame.display.update()



def save_score():
    if score > high_score:
        with open("score.txt", "w") as file:
            file.write(str(score))

def set_score():
    global score
    if scroll > 0:
        score += scroll   

def check_game_over():
    global is_game_over
    if player.rect.top > HEIGHT:
        is_game_over = True


def game_over():
    global score, is_game_over, scroll, high_score
    draw_text("GAME OVER!", font_big, (255, 255, 255), 100, 200)
    draw_text(f"SCORE: {score}", font_big, (255, 255, 255), 130, 250)
    draw_text(f"HIGH SCORE: {max(score, high_score)}", font_big, (255, 255, 255), 130, 300)
    draw_text("PRESS SPACE TO RESTART", font_big, (255, 255, 255), 40, 350)
    pygame.display.update()
    key = pygame.key.get_pressed()
    if key[pygame.K_SPACE]:
        save_score()
        is_game_over = False
        score = 0
        scroll = 0
        player.rect.center = (WIDTH // 2, HEIGHT * 3 // 4)
        platform_group.empty()
        platform_group.add(Platform(WIDTH // 2 - 50, HEIGHT - 50, 100))



def game():
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if is_game_over == True:
            game_over()
            continue

        if len(platform_group) < MAX_PLATFORMS:
            platform_width = random.randint(40,60)
            platform_x = random.randint(0, WIDTH - platform_width)
            platform_y = platform_group.sprites()[-1].rect.y - random.randint(70, 110)
            platform_moving = random.choice([True, False])
            platform = Platform(platform_x, platform_y, platform_width, platform_moving)
            platform_group.add(platform)

        draw()
        set_score()
        player.move()
        platform_group.update() 
        check_game_over()
        clock.tick(60)


game()