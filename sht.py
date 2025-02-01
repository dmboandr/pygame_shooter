"""
Игра Shooter с помощью модуля Pygame
"""

import pygame

# Глобальные настройки
pygame.init()  # активирует модуль pygame
SCREEN_WIDTH = 800  # значение ширины экрана
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)  # высота
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # настроили экран
pygame.display.set_caption("Shooter")
clock = pygame.time.Clock()  # для управления ФПС
GRAVITY = 0.75
FPS = 60

# переменные движения игрока
moving_left = False
moving_right = False
shoot = False

# переменные для цвета
BG = (144, 201, 120)  # цвет  заднего фона
RED = (255, 0, 0)

# необходимые для игры изображения
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (800, 300))


# Класс солдата, основное поведение солдатов описано здесь
class Soldier(pygame.sprite.Sprite):  # наследуем пайгеймовский инструмент работы со спрайтами
    # СПЕЦМЕТОД __init__ срабатывает при создании объекта
    # Метод - это функция, которая находится внутри класса
    def __init__(self, char_type, x, y, scale, speed):
        """ спецметод, который срабатывает при создании объекта """
        pygame.sprite.Sprite.__init__(self)  # подключали разные действия со спрайтами

        # анимация
        self.update_time = pygame.time.get_ticks()  # внутренний таймер pygame
        self.animation_list = []  # в этот лист будут помещаться картинки
        self.animation_index = 0  # список списков
        self.frame_index = 0  # картинки конкретной анимации
        self.action = 0  # ссылка о каком списке с анимациями идёт речь
        self.temp_list = []  # временный список для добавления картинок

        # переменные для прыжка
        self.vel_y = 0  # величина поднимающая нас
        self.jump = False  # мы совершаем прыжок
        self.in_air = False  # мы находимся в воздухе

        # переменные для движения
        self.speed = speed  # скорость движения солдата
        self.direction = 1  # направление куда смотрит солдат
        self.flip = False

        # переменные для стрельбы
        self.start_ammo = 10  # стартовое значение обоймы
        self.ammo = self.start_ammo  # ammo - обойма
        self.shoot_cooldown = 0  # задержка стрельбы

        for i in range(5):  # 0, 1, 2, 3, 4
            img = pygame.image.load(f"img/{char_type}/Idle/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.temp_list.append(img)
        self.animation_list.append(self.temp_list)  # [[1, 2, 3], [], []]
        self.temp_list = []

# [[img1, img2, ..., img5], [img6, im7, img8, ...]]
        for i in range(6):  # 0, 1, 2, 3, 4
            img = pygame.image.load(f"img/{char_type}/Run/{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.temp_list.append(img)
        self.animation_list.append(self.temp_list)  # [[1, 2, 3], [], []]
        self.temp_list = []

        self.image = self.animation_list[self.animation_index][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))

    def update_animation(self):
        """ метод обновления анимации солдата """
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()  # обновляю таймер
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update(self):
        self.update_animation()  # обнови анимации
        if self.shoot_cooldown > 0: # если ты стрельнул, то подожди
            self.shoot_cooldown -= 1

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def move(self, moving_left, moving_right):
        """ метод для движения солдата """
        dx = 0
        dy = 0
        # -2, -1, 0, 1, 2, 3
        if moving_left:
            dx = -self.speed  # -4 -4 -4 -4 -4 -4 -4
            self.direction = -1
            self.flip = True
        if moving_right:
            dx = self.speed   # +4 +4 +4 +4 +4
            self.direction = 1
            self.flip = False

        # прыжок
        if self.jump == True and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # применяю гравитацию
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # проверяем коллизию с поверхностью (чтобы не проваливаться под землю от гравитации)
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # применяем все изменения по координатам
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 15
            bullet = Bullet(self.rect.centerx + (0.45 * self.rect.size[0] * self.direction), self.rect.centery + 2, self.direction)
            bullet_group.add(bullet) # добавляем пулю в группу
            self.ammo -= 1

    def draw(self):
        """ этот метод отображает солдата """
        screen.blit(pygame.transform.flip(self.animation_list[self.action][self.frame_index], self.flip, False), self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):  # выполняет код сразу при создании объекта
        pygame.sprite.Sprite.__init__(self)
        # переменные для поведения пули
        self.speed = 10  # скорость полёта пули
        self.image = bullet_img  # картинка пули
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # движение пули
        self.rect.x += self.speed * self.direction  # меняем координату по направлению
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            # иначе говоря сборка мусора в программировании
            self.kill()  # уничтожаем объекты, не считаем их, не храним в памяти  и т.д.



# объекты солдат
player = Soldier("player", 400, 250, 2, 5)  # создаю игрока на коорд. 400x200
enemy = Soldier("enemy", 600, 250, 2, 5)  # объект класса солдат

# группы спрайтов
bullet_group = pygame.sprite.Group()


# ОСНОВНОЙ ЦИКЛ ИГРЫ
run = True
while run:
    # проход по событиям
    for event in pygame.event.get():
        # закрытие приложения
        if event.type == pygame.QUIT:
            run = False
        # нажатия на клавиши
        if event.type == pygame.KEYDOWN:
            # событие нажатие клавиши а
            if event.key == pygame.K_a:
                moving_left = True
            # событие нажатие клавиши d
            if event.key == pygame.K_d:
            # событие нажатие клавиши пробел (space)
                moving_right = True
            if event.key == pygame.K_SPACE:
                player.jump = True
                enemy.jump = True
            if event.key == pygame.K_e:
                shoot = True

        # отжатия клавиш (т.е. когда отпускаем клавишу)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_e:
                shoot = False

    # рисовать задний фон
    draw_bg()



    # обновлять анимации
    if moving_left or moving_right:
        player.update_action(1)
    else:
        player.update_action(0)


    if shoot:
        player.shoot()


    # обновляем состояния солдат
    player.update()
    enemy.update()

    # нарисовать солдат
    player.draw()  # рисуй игрока постоянно
    enemy.draw()  # рисуй противника enemy
    player.move(moving_left, moving_right)

    # нарисовать и обновить пули
    bullet_group.update()  # обновлять все объекты группы (рисовать их)
    bullet_group.draw(screen)  # указать в скобках название экрана

    # действия обновления экрана
    pygame.display.update()
    clock.tick(FPS)


pygame.quit()  # останови модуль pygame