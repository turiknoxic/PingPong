import pygame
import os
import sys
import datetime as dt
# чтобы звуки воспроизодились без задержки
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
size = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Понг')

# настройка музыки и звуков
pygame.mixer.music.load("sound/background.mp3")
pygame.mixer.music.set_volume(0.2)
victory = pygame.mixer.Sound('sound/victory.wav')
bounce = pygame.mixer.Sound('sound/bounce.wav')
bounce.set_volume(0.5)
score = pygame.mixer.Sound('sound/score.wav')
score.set_volume(0.5)
# группа спрайтов
all_sprites = pygame.sprite.Group()
paddles = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
borders = pygame.sprite.Group()

# настройка шрифтов
FONT = pygame.font.SysFont('comicsans', 30)
ERR_FONT = pygame.font.SysFont('comicsans', 20)

# необходимые переменные
l_score = r_score = 0
collisions = []     # список столкновений со стенками
ticks = 0
game_on = True
inital_game_on = False
win = False
turn = 1
victory_played = False


def record_result(winner):
    with open('results.txt', 'a', encoding='utf8') as file:
        print(f"{dt.datetime.now()}: {winner}", file=file)


def draw_error_font():      # функция рисования текста при застрявании шарика
    text = "Упс, шарик застрял внутри стенки! Перезапускаем.."
    show_text = ERR_FONT.render(text, True, pygame.Color('red'))
    screen.blit(show_text, (SCREEN_WIDTH // 2 - show_text.get_width() // 2,
                            SCREEN_HEIGHT // 2 - show_text.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(2000)     # задержка по времени для того,
    # чтобы текст можно было прочитать


def terminate():
    pygame.quit()


def initial_menu():     # рисование начального меню
    text = "Выберите режим: 1 - медленный / 2 - средний / 3 - быстрый"
    show_text = FONT.render(text, True, pygame.Color('red'))
    screen.blit(show_text, (SCREEN_WIDTH // 2 - show_text.get_width() // 2,
                            SCREEN_HEIGHT // 2 - show_text.get_height() // 2))
    pygame.display.update()


def choose_gamemode(ball_speed, speed_incr, paddle_velocity):
    ball.orig_vx = ball_speed
    ball.speed_incr = speed_incr
    l_paddle.vel = paddle_velocity
    r_paddle.vel = paddle_velocity
    ball.reset()

def draw_score_and_line():
    l_text = FONT.render(str(l_score), True, pygame.Color('white'))
    r_text = FONT.render(str(r_score), True, pygame.Color('white'))
    screen.blit(l_text, (SCREEN_WIDTH // 4 - l_text.get_width() // 2, 10))
    screen.blit(r_text, (SCREEN_WIDTH * (3/4) - r_text.get_width() // 2, 10))
    for i in range(10, SCREEN_HEIGHT, SCREEN_HEIGHT // 20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(screen, pygame.Color('black'),
                         (SCREEN_WIDTH // 2 - 5, i, 10, SCREEN_HEIGHT // 20))

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Border(pygame.sprite.Sprite):
    image = load_image("border.png")

    def __init__(self, group, left, top):
        super().__init__(group)
        self.add(borders)
        self.image = Border.image
        self.rect = self.image.get_rect()
        self.rect.x = left
        self.rect.y = top


top_bord = Border(all_sprites, 5, 50)
bottom_bord = Border(all_sprites, 5, SCREEN_HEIGHT - 50)


class LeftPaddle(pygame.sprite.Sprite):
    image = load_image("paddle.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.add(paddles)
        self.image = LeftPaddle.image
        self.rect = self.image.get_rect()
        self.rect.x = self.orig_x = 10
        self.rect.y = self.orig_y = (SCREEN_HEIGHT - self.rect.height) // 2
        self.vel = 10

    def move(self, up):
        if up:
            self.rect.y -= self.vel
        else:
            self.rect.y += self.vel

    def update(self, *events):
        if keys[pygame.K_w] and self.rect.y - self.vel \
                >= top_bord.rect.y + top_bord.rect.height:
            # если зажата W, и не упирается
            # в верхнюю стенку, двигаем вверх
            self.move(up=True)
        if keys[pygame.K_s] and self.rect.y + self.rect.height \
                + self.vel <= bottom_bord.rect.y:
            # если зажата S, и не упирается
            # в нижнюю стенку, двигаем вниз
            self.move(up=False)

    def reset(self):
        self.rect.topleft = (self.orig_x, self.orig_y)
        # возвращаем к оригинальным координатам


class RightPaddle(pygame.sprite.Sprite):
    image = load_image("paddle.png", -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.add(paddles)
        self.image = RightPaddle.image
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.x = self.orig_x =  SCREEN_WIDTH - 10 - self.rect.width
        self.rect.y = self.orig_y = (SCREEN_HEIGHT - self.rect.height) // 2
        self.vel = 10

    def move(self, up):
        if up:
            self.rect.y -= self.vel
        else:
            self.rect.y += self.vel

    def update(self, *events):
        if keys[pygame.K_UP] and self.rect.y - self.vel\
                >= top_bord.rect.y + top_bord.rect.height:
            # если зажата стрелочка вверх, и не упирается
            # в верхнюю стенку, двигаем вверх
            self.move(up=True)
        if keys[pygame.K_DOWN] and self.rect.y + self.rect.height \
                + self.vel <= bottom_bord.rect.y:
            # если зажата стрелочка вниз, и не упирается
            # в нижнюю стенку, двигаем вниз
            self.move(up=False)

    def reset(self):
        self.rect.topleft = (self.orig_x, self.orig_y)


l_paddle = LeftPaddle(all_sprites)
r_paddle = RightPaddle(all_sprites)


class Ball(pygame.sprite.Sprite):
    image = load_image('ball.png', -1)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Ball.image
        self.add(ball_group)
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = self.orig_x = SCREEN_WIDTH // 2 - 25
        self.rect.y = self.orig_y = SCREEN_HEIGHT // 2
        self.orig_vx = 1
        self.v_x = self.orig_vx
        self.v_y = 0
        self.speed_incr = 1

    def move(self):
        self.rect.x += self.v_x
        self.rect.y += self.v_y

    def reset(self):
        if turn == 1:
            self.v_x = self.orig_vx
        elif turn == -1:
            self.v_x = -self.orig_vx
        self.v_y = 0
        self.rect.x = self.orig_x
        self.rect.y = self.orig_y

    def update(self, *events):
        if pygame.sprite.collide_mask(self, l_paddle):
            bounce.play()
            if self.v_x < 0:
                self.v_x = -(self.v_x - self.speed_incr)
            else:
                self.v_x = -(self.v_x + self.speed_incr)
            # логика вычисления направления: мы высчитываем серединный
            # координат у платформы об которую бьется шарик, далее считаем
            # разницу в координатах между серединой и левым верхним углом
            # шарика. После, мы находим количество координат(как одно деление)
            # , на которое мы будем делить нашу рахницу в координатах.
            # Результат и будет нашей скоростью
            middle_y = l_paddle.rect.y + (l_paddle.rect.height // 2)
            y_diff = middle_y - self.rect.y
            red_f = (l_paddle.rect.height // 2) // 5
            y_vel = y_diff / red_f
            self.v_y = -y_vel
        if pygame.sprite.collide_mask(self, r_paddle):
            bounce.play()
            if self.v_x < 0:
                self.v_x = -(self.v_x - self.speed_incr)
            else:
                self.v_x = -(self.v_x + self.speed_incr)
            middle_y = r_paddle.rect.y + (r_paddle.rect.height // 2)
            y_diff = middle_y - self.rect.y
            red_f = (r_paddle.rect.height // 2) // 5
            y_vel = y_diff / red_f
            self.v_y = -y_vel
        if pygame.sprite.spritecollideany(self, borders):
            # каждый раз как шарик сталкивается со стенкой,
            # True добавляется в список столкновений
            collisions.append(True)
            bounce.play()
            if len(collisions) > 4:
                # Если столковений за короткий промежуток (за 5 тиков) слишком
                # много, то мы перезапускаем позиции плит и шарика
                draw_error_font()
                self.reset()
                l_paddle.reset()
                r_paddle.reset()
            else:
                # иначе шарик просто отскакивает
                self.v_y = -self.v_y
        self.move()


clock = pygame.time.Clock()
fps = 60
running = True
ball = Ball(all_sprites)
bg = load_image("background.jpg")
while running:
    screen.blit(bg, (0, 0))     # картинка заднего фона
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        keys = pygame.key.get_pressed()     # хранилище всех зажатых ключей
    if ticks == 5:   # очистка массива столкновений
        collisions.clear()
        ticks = 0
    if not inital_game_on:      # если игра еще не запущена
        initial_menu()
        pygame.mixer.music.play(-1)
    if keys[pygame.K_1]:    # выбираем медленный режим
        choose_gamemode(ball_speed=2, speed_incr=1, paddle_velocity=5)
        inital_game_on = True
    if keys[pygame.K_2]:    # выбираем средний режим
        choose_gamemode(ball_speed=5, speed_incr=2, paddle_velocity=7)
        inital_game_on = True
    if keys[pygame.K_3]:    # выбираем быстрый режим
        choose_gamemode(ball_speed=7, speed_incr=4, paddle_velocity=13)
        inital_game_on = True
    if game_on and inital_game_on:   # если игра запущена и режим игры выбран
        all_sprites.draw(screen)
        all_sprites.update(event)
        draw_score_and_line()
    clock.tick(fps)
    ticks += 1

    if ball.rect.x < 0:     # если залетел влево
        r_score += 1
        turn = -turn
        score.play()
        ball.reset()
    elif ball.rect.x > SCREEN_WIDTH:    # если залетел вправо
        l_score += 1
        turn = -turn
        score.play()
        ball.reset()
    if l_score == 10:    # выигрывает левый
        win = True
        winner = 1
    elif r_score == 10:      # выигрывает правый
        win = True
        winner = 2

    if win:     # проверяем выигрыш
        if winner == 1:
            res = "Выиграл левый игрок!"
        elif winner == 2:
            res = "Выиграл правый игрок!"
        res_text = FONT.render(res, True, pygame.Color('black'))
        screen.blit(res_text, (SCREEN_WIDTH // 2 - res_text.get_width() // 2,
                               SCREEN_HEIGHT // 2 - res_text.get_height() // 2))
        continue_game = "Чтобы перезапустить игру, нажмите на пробел"
        continue_text = FONT.render(continue_game, True, pygame.Color('black'))
        screen.blit(continue_text, (SCREEN_WIDTH // 2 -
                                    continue_text.get_width() // 2,
                                    SCREEN_HEIGHT // 2 +
                                    continue_text.get_height() // 2))
        pygame.display.update()
        game_on = False
        win = False
        pygame.mixer.music.stop()
        if not victory_played:
            victory.play()
            victory_played = True
            record_result(res)
    if keys[pygame.K_SPACE]:     # перезагрузка игры
        game_on = True
        pygame.mixer.music.play(-1)
        ball.reset()
        l_paddle.reset()
        r_paddle.reset()
        l_score = 0
        r_score = 0
        victory_played = False
    pygame.display.flip()
terminate()