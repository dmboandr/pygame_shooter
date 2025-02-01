"""
Игра Shooter с помощью модуля Pygame
"""
# CTRL + F

import pygame
import os  # подключаю модуль os, в нём множество операция над файловой стр-рой
import random
import csv

# Глобальные настройки
pygame.init()  # активирует модуль pygame
SCREEN_WIDTH = 800  # значение ширины экрана
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)  # высота
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # настроили экран
pygame.display.set_caption("Shooter")
clock = pygame.time.Clock()  # для управления ФПС
GRAVITY = 0.75
FPS = 60
# переменные для тайлов
ROWS = 16  # строки
MAX_COLS = 150  # колонки
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
level = 0
current_tile = 0
scroll = 0
bg_scroll = 0
SCROLL_LINE = 200

# переменные движения игрока
moving_left = False
moving_right = False

# переменные для стрельбы и гранат
shoot = False
reload = False
grenade = False
grenade_thrown = False  # ограничить возможность бросать гранаты на зажатие клавиши

# переменные для цвета RGB
BG = (144, 201, 120)  # цвет заднего фона
RED = (255, 0, 0)
BLACK = (10, 10, 10)
GREEN = (65, 218, 24)
WHITE = (250, 245, 244)

# шрифты
font = pygame.font.SysFont("Futura", 35)  # само название

# звуки игры
boom_sound = pygame.mixer.Sound("audio/grenade.wav")
boom_sound.set_volume(0.8)  # 80% громкости
boom_sound.play()  # воспроизвести звук

shoot_sound = pygame.mixer.Sound("audio/shot.wav")
shoot_sound.set_volume(0.15)  # 15% громкости

jump_sound = pygame.mixer.Sound("audio/jump.wav")
jump_sound.set_volume(0.3)

music = pygame.mixer.Sound("audio/music2.mp3")
music.set_volume(0.1)
music.play(loops=999)

# необходимые для игры изображения
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
# подбираемые предметы
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
background = pygame.image.load("img/background/mountain.png").convert_alpha()
# тайлы для игрового мира
mountain = pygame.image.load("img/background/mountain.png").convert_alpha()
sky = pygame.image.load("img/background/sky_cloud.png").convert_alpha()
pine1 = pygame.image.load("img/background/pine1.png").convert_alpha()
pine2 = pygame.image.load("img/background/pine2.png").convert_alpha()
img_list = []  # пустой массив для тайлов
for x in range(TILE_TYPES):  # 0, 1, 2, ..., 20
    img = pygame.image.load(f"img/tile/{x}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)  # добавить в массив img_list картинку img

item_boxes = {
    "health"    : health_box_img,
    "grenade"   : grenade_box_img,
    "ammo"      : ammo_box_img,
}

# функции необходимые для игры
def draw_bg():
    """ Функция отрисовывающая задний фон """
    width = sky.get_width()
    for x in range(4):  # 0*1400, 1*1400, 2*1400, 3*1400
        screen.blit(sky, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain.get_height() - 200))
        screen.blit(pine2, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine2.get_height()))
        screen.blit(pine1, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine1.get_height()))


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


# Класс игрового мира
class World:
    def __init__(self):
        self.obstacle_list = []  # препятствие

    # метод считывания данных из csv файла
    def process_data(self, data):
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if 0 <= tile <= 8:
                        self.obstacle_list.append(tile_data)  # [obj0, obj, obj, 2, 4, 5, 7]
                    elif 9 <= tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif 11 <= tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:
                        player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5)  # создаю игрока на коорд. 400x200
                    elif tile == 16:
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5)  # объект класса солдат
                        enemy_group.add(enemy)
                    elif tile == 17:
                        item_box = ItemBox("ammo", x * TILE_SIZE, y * TILE_SIZE + 5)  # 0*40, 1*40, 2*40, 3*40, 4
                        item_box_group.add(item_box)
                        # создай объект паторонов на координате x * tile, y * tile
                        # добавь в группу патронов
                    elif tile == 18:
                        item_box = ItemBox("grenade", x * TILE_SIZE, y * TILE_SIZE + 5)
                        item_box_group.add(item_box)
                    elif tile == 19:
                        item_box = ItemBox("health", x * TILE_SIZE, y * TILE_SIZE + 5)
                        item_box_group.add(item_box)
                    elif tile == 20:
                        decoration = Decoration(img, x * TILE_SIZE + scroll, y * TILE_SIZE)
                        decoration_group.add(decoration)
        return player


    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], tile[1])  # (10, 20) + 0
            tile[1][0] += scroll



class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):  # выполняет код сразу при создании объекта
        pygame.sprite.Sprite.__init__(self)
        # переменные для поведения предметов
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = ( x + TILE_SIZE // 2,
                            y + (TILE_SIZE - self.image.get_height()) )

    def update(self):
        self.rect.x += scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):  # выполняет код сразу при создании объекта
        pygame.sprite.Sprite.__init__(self)
        # переменные для поведения предметов
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2,
                            y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += scroll


# Класс солдата, основное поведение солдатов описано здесь
class Soldier(pygame.sprite.Sprite):  # наследуем пайгеймовский инструмент работы со спрайтами
    # СПЕЦМЕТОД __init__ срабатывает при создании объекта
    # Метод - это функция, которая находится внутри класса
    def __init__(self, char_type, x, y, scale, speed):
        """ спецметод, который срабатывает при создании объекта """
        pygame.sprite.Sprite.__init__(self)  # подключали разные действия со спрайтами

        # общие переменные
        self.alive = True
        self.char_type = char_type

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
        self.flip = False  # определяет в какую сторону повёрнута картинка солдата

        # для ИИ
        self.move_counter = 0
        self.idle_counter = 0
        self.idling = False
        self.vision = pygame.Rect(0, 0, 300, 20)

        # переменные для стрельбы
        self.start_ammo = 10  # стартовое значение обоймы
        self.ammo = self.start_ammo  # ammo - обойма
        self.shoot_cooldown = 0  # задержка стрельбы
        self.health = 100  # показатель здоровья
        self.grenade_ammo = 3


        # добавление анимаций (самих картинок)
        animation_types = ["Idle", "Run", "Death"]
        for animation in animation_types:
            temp_list = []

            num_of_frame = len(os.listdir(f"img/{char_type}/{animation}"))

            for i in range(num_of_frame):
                img = pygame.image.load(f"img/{char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.animation_index][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))

    def update_animation(self):
        """ метод обновления анимации солдата """
        # [img1, img2, img3, ...]
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()  # обновляю таймер
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action])-1
            else:
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
        scroll = 0
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
            self.vel_y = -14
            self.jump = False
            self.in_air = True
            jump_sound.play()

        # применяю гравитацию
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # проверяем коллизию с поверхностью (чтобы не проваливаться под землю от гравитации)
        # if self.rect.bottom + dy > 500:
        #     dy = 500 - self.rect.bottom
        #     self.in_air = False

        # проверка коллизии со стеной (лево-право), x
        for tile in world.obstacle_list:  # [[img, rect], [img, rect], [img, rect], [], [], [], [], [], []]
            if tile[1].colliderect(self.rect.x + dx, self.rect.y-2, self.rect.width, self.rect.height):
                dx = 0
                # если бот бежит в стену
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0

            # проверка коллизии с землей (вверх-вниз), y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # упали за экран
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        if self.char_type == "player":
            if self.rect.left + dx < 0:
                dx = 0
                player.rect.x = 15

            if self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # механика scroll
        if self.char_type == "player":  # 800 - 200 = 600 |||| player.rect.x = 600
            if ( (self.rect.right + dx > SCREEN_WIDTH - SCROLL_LINE) or (self.rect.left + dx < SCROLL_LINE) ):
                self.rect.x -= dx  #
                scroll = -dx

        # применяем все изменения по координатам
        self.rect.x += dx
        self.rect.y += dy

        return scroll

    def ai(self):
        if self.alive and player.alive:
            # здесь мы стоим, это начало
            # Мы бросаем игральный кубик на 200 граней и пытаемся 1 нужную
            if self.idling == False and random.randint(1, 200) == 1:
                # если поймали, то мы переходим в состояние idle
                self.update_action(0)
                self.idling = True
                self.idle_counter = 50
                # если не поймали, то мы двигаемся по направлению движения

            # если игрок в поле видимости, то останавливайся и стреляй
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()
                if self.ammo == 0:
                    self.ammo = 1000
            # иначе
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    elif self.direction == -1:
                        ai_moving_right = False
                    ai_moving_left = not moving_right

                    self.move(ai_moving_left, ai_moving_right)

                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 165 * self.direction, self.rect.centery)
                    #pygame.draw.rect(screen, RED, self.vision)
                    self.update_action(1)

                    # if pygame.sprite.collide_rect(player, enemy):
                    #     self.update_action(0)
                    #     self.shoot()
                    #     self.ammo = 100

                    if self.move_counter > 40:
                        self.direction *= -1
                        self.move_counter = 0
                else:
                    self.idle_counter -= 1
                    if self.idle_counter <= 0:
                        self.idling = False

        if player.alive == False:
            draw_text(f"ИГРОК УМЕР", font, BLACK, 200, 200)


    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 12
            bullet = Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction),
                            self.rect.centery + 2, self.direction)
            bullet_group.add(bullet) # добавляем пулю в группу
            self.ammo -= 1
            shoot_sound.play()

    def grenade(self):
        if self.grenade_ammo > 0:
            grnd = Grenade(self.rect.centerx + (0.45 * self.rect.size[0] * self.direction),
                           self.rect.centery + 2, self.direction)
            grenade_group.add(grnd) # добавляем пулю в группу
            self.grenade_ammo -= 1

    def reload(self):
        # перезарядка
        global reload  # я ссылаюсь на переменную именно из глобальной области видимости

        if reload:
            self.ammo = 20
            reload = False

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(2)

    def draw(self):
        """ этот метод отображает солдата """
        screen.blit(pygame.transform.flip(self.animation_list[self.action][self.frame_index], self.flip, False), self.rect)


# класс связанный с поведением пули
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
        self.rect.x += self.speed * self.direction + scroll  # меняем координату по направлению
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            # иначе говоря сборка мусора в программировании
            self.kill()  # уничтожаем объекты, не считаем их, не храним в памяти  и т.д.

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        for enemy in enemy_group:
            # проверяй коллизию с противником
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                # мы должны отнимать показатель здоровья
                if enemy.alive == True:
                    enemy.health -= 50
                    self.kill()

            # с игроком
        if pygame.sprite.spritecollide(player, bullet_group, False):
            # мы должны отнимать показатель здоровья
            player.health -= 10
            self.kill()

            if player.health <= 0:
                player.alive = False
                player.update_action(2)  # под индексом 2 у нас анимация смерти


# класс связанный с поведением гранаты
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):  # выполняет код сразу при создании объекта
        pygame.sprite.Sprite.__init__(self)
        # переменные для поведения гранаты
        self.timer = 100  # таймер срабатывания гранаты
        self.vel_y = -15  # velocity
        self.speed = 7  # скорость полёта пули
        self.image = grenade_img  # картинка пули
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.hit = False  # флажок столкновения

    def update(self):
        # логика изменения координат
        dx = 0
        dy = 0

        self.vel_y += GRAVITY  # постоянно на гранату действует гравитация
        if self.hit == False:
            dx = self.speed * self.direction  # граната летит то вправо, то влево
            dy = self.vel_y

        if self.hit:
            self.timer -= 2


        for tile in world.obstacle_list:
            if self.hit == False:
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                    self.hit = True
                    dy = tile[1].top - self.rect.bottom  # это вычисление теперь делается 1 раз
                    dx = 0
                    #print("граната столкнулась")

        # проверяем коллизию с поверхностью (чтобы не проваливаться под землю от гравитации)
        # if self.rect.bottom + dy > 300:
        #     self.timer -= 2
        #     dy = 300 - self.rect.bottom
        #     dx = 0

            if self.timer <= 0:
                self.kill()  # уничтожил объект гранаты
                self.timer = 100
                explosion = Explosion(self.rect.x, self.rect.y, 1.5)
                explosion_group.add(explosion)
                boom_sound.play()  # воспроизвести звук
                #print(len(explosion_group))
                for enemy in enemy_group:
                    if abs(self.rect.x - enemy.rect.x) < 100 and abs(self.rect.y - enemy.rect.y) < 100:
                        enemy.health -= 50  # сразу убиваем
                        #print(f"Enemy HP: {enemy.health}")
                if abs(self.rect.x - player.rect.x) < 100 and abs(self.rect.y - player.rect.y) < 100:
                    player.health -= 25  # сразу убиваем
                    #print(f"Player HP: {player.health}")

        # # проверяем коллизию со стеной
        # if self.rect.right + dx < 0 or self.rect.left + dx > SCREEN_WIDTH:
        #     self.direction *= -1  # умножаю на -1
        #     dx = self.speed * self.direction

        # применяю изменения координат
        self.rect.x += dx + scroll
        self.rect.y += dy


# класс описывающий поведение взрыва гранаты
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):  # выполняет код сразу при создании объекта
        pygame.sprite.Sprite.__init__(self)
        self.images = []  # список (массив) где будут картинки взрыва
        for num in range(1, 6):  # 1...5
            img = pygame.image.load(f"img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]  # картинка которую мы видим на экране
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0  # счётчик

    def update(self):
        EXPLOSION_SPEED = 4

        self.counter += 1

        if self.counter >= EXPLOSION_SPEED:
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


# класс связанный с поведением предметов
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):  # выполняет код сразу при создании объекта
        pygame.sprite.Sprite.__init__(self)
        # переменные для поведения предметов
        self.item_type = item_type
        self.image = item_boxes[item_type]  # картинка предметов
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y)

    def update(self):
        # коллизия с игроком
        self.rect.x += scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == "health":
                player.health = 100
                self.kill()
            elif self.item_type == "grenade":
                player.grenade_ammo += 3
                self.kill()
            elif self.item_type == "ammo":
                player.ammo = player.start_ammo
                self.kill()

# класс связанный с поведением предметов
class HealthBar:
    def __init__(self, x, y, health, max_health):  # выполняет код сразу при создании объекта
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
        
    def draw(self, health):
        # обнови хп
        self.health = health
        # формула рассчета хп
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x-2, self.y-2, 150, 20))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))
        



# солдаты (противники)
enemy = Soldier("enemy", -1000, 0, 2, 5)  # объект класса солдат
#enemy_2 = Soldier("enemy", 100, 264, 2, 5)  # объект класса солдат

# группы спрайтов
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()  # [enemy, enemy, enemy]
item_box_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()

# предметы
# item_box = ItemBox("health", 150, 264)
# item_box_group.add(item_box)
# item_box = ItemBox("grenade", 250, 264)
# item_box_group.add(item_box)
# item_box = ItemBox("ammo", 350, 264)
# item_box_group.add(item_box)

# добавляю противников в группу
enemy_group.add(enemy)


# пустой мир
world_data = []
for row in range(ROWS):
    r = [-1] * MAX_COLS
    world_data.append(r)
# читаем данные из файла
with open(f"LevelEditor/level_0.csv") as file:
    reader = csv.reader(file, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

# нужно создать объект мира, т.к. у нас класс World
world = World()

# объект игрока
player = world.process_data(world_data)
hp_bar = HealthBar(15, 15, player.health, player.health)


# ОСНОВНОЙ ЦИКЛ ИГРЫ
run = True
while run:
    # проход по событиям
    for event in pygame.event.get():
        # закрытие приложения
        if event.type == pygame.QUIT:
            run = False

        # нажатия на клавиши
        if player.alive:
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
                if event.key == pygame.K_e:
                    shoot = True
                if event.key == pygame.K_r:
                    reload = True
                if event.key == pygame.K_g:
                    grenade = True


            # отжатия клавиш (т.е. когда отпускаем клавишу)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    moving_left = False
                if event.key == pygame.K_d:
                    moving_right = False
                if event.key == pygame.K_e:
                    shoot = False
                if event.key == pygame.K_g:
                    grenade = False
                    grenade_thrown = False


    # рисовать задний фон
    draw_bg()
    world.draw()

    #screen.blit(background, (0, 45))  # какая картина, на какой координате (x, y)

    # рисовать интерфейс
    hp_bar.draw(player.health)
    draw_text(f"AMMO: {player.ammo}", font, BLACK, 15, 60)
    draw_text(f"GRENADES: ", font, WHITE, 15, 40)
    for i in range(player.grenade_ammo):
        screen.blit(grenade_img, (  (170 + (i*20)), 45)  )

    #   0                               1                            2
    # [ [idle1, idle2, idle3, ...], [run1, run2, run3, ...], [death1, death2, death3, ....] ]
    # обновлять анимации
    if player.alive:
        if moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)

    if player.alive:
        # если нажали на клавишу выстрелить (E), то стреляем
        if shoot:
            player.shoot()
        # если нажали на клавишу перезарядить (R), то перезаряжаем
        if reload:
            player.reload()
        if grenade and grenade_thrown == False:
            player.grenade()
            grenade_thrown = True

    # обновляем состояния солдат
    player.update()
    # enemy.update()
    # enemy_2.update()

    # нарисовать солдат
    player.draw()  # рисуй игрока постоянно
    # enemy.draw()  # рисуй противника enemy
    # enemy_2.draw()
    scroll = player.move(moving_left, moving_right)
    player.check_alive()

    for enemy in enemy_group:
        enemy.rect.x += scroll
        enemy.ai()
        enemy.check_alive()
        enemy.draw()
        enemy.update()

    # Каждый проход цикла - это множество операций

    # for water in water_group:  # блоки воды
    #     water.rect.x += scroll
    #
    # for decoration in decoration_group:  # блоки камней, травы и пр.
    #     decoration.rect.x += scroll
    #
    # for item in item_box_group:  # блоки патронов, гранат и аптечек
    #     item.rect.x += scroll


    # нарисовать и обновить пули
    bullet_group.draw(screen)  # указать в скобках название экрана
    #enemy_group.draw(screen)
    grenade_group.draw(screen)  # указать в скобках название экрана
    explosion_group.draw(screen)
    item_box_group.draw(screen)
    water_group.draw(screen)
    decoration_group.draw(screen)

    bullet_group.update()  # обновлять все объекты группы (рисовать их)
    #enemy_group.update()
    grenade_group.update()  # обновлять все объекты группы (рисовать их)
    explosion_group.update()
    item_box_group.update()
    water_group.update()
    decoration_group.update()


    # действия обновления экрана
    pygame.display.update()
    clock.tick(FPS)


pygame.quit()  # останови модуль pygame