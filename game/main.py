import pygame
import random
import os
import itertools

pygame.init()


# make animations start at different times
# to check if something is a sunflower the program currently uses i.image == sunflower (change later)
# print costs under icon
# add tower features
# balance game / change tower prices
# remove occupied
# fix sun cooldown

class Entities:
    def __init__(self, x, y, vx, width, length, power, cooldown, image):
        self.x = x
        self.y = y
        self.vx = vx
        self.hitbox = pygame.Rect(x, y, width, length)
        self.power = power
        self.start = pygame.time.get_ticks()
        self.cooldown = cooldown
        self.image = image

    def move(self):
        self.hitbox = self.hitbox.move(self.vx, 0)
        self.x = self.hitbox.left

    def draw(self, colour):
        pygame.draw.rect(screen, colour, self.hitbox, 0)  # debugging

    def timer(self):
        now = pygame.time.get_ticks()
        if now - self.start >= self.cooldown:
            self.start = now
            return True

    def collide(self, objects):
        for j in objects:
            if self.hitbox.colliderect(j.hitbox):
                if self.timer():
                    j.health -= self.power
                return True


class Bullets(Entities):
    def __init__(self, x, y, vx, width, length, power, image):
        super().__init__(x, y, vx, width, length, power, 0, image)


class Enemy(Entities):
    def __init__(self, x, y, vx, health, power, cooldown, image, eat):
        super().__init__(x, y, vx, 30, 100, power, cooldown, image)
        self.health = health
        self.temp_vx = self.vx
        self.eat = eat


class Plant(Entities):
    def __init__(self, x, y, health, cooldown, image, shoot, attack, cost):
        super().__init__(x, y, 0, 50, 100, 0, cooldown, image)
        self.health = health
        self.shoot = shoot
        self.attack = attack
        self.cost = cost


def image_load(image, direct):
    temp = [pygame.image.load(os.path.join(direct, i)) for i in image]
    return temp


def collapse(array_2d):
    new_array = [i for i in list(itertools.chain.from_iterable(array_2d)) if i is not None]
    return new_array


def closest():
    closest_plant = [(0, 0)] * 5
    for j in collapse(plant_lane_map):
        if (j.x, j.y) > closest_plant[(j.y - 80) // 128]:
            closest_plant[(j.y - 80) // 128] = (j.x, j.y)
    return closest_plant


def Terminus(image):
    run = False

    while not run:

        run = prevent_crash(run)

        screen.blit(image, (0, 0))

        if pygame.mouse.get_pressed()[0]:
            run = True
        pygame.display.update()


def draw_game():
    global sun
    global lives
    pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, 1024, 80), 1)
    screen.blit(font.render(str(sun), True, (200, 200, 0)), (900, 30))

    for i in range(9):
        pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, i * 80, 80), 1)
        screen.blit(icons[i], (i * 80 + 10, 10))

    for i in bullets:
        screen.blit(i.image, (i.x - 60, i.y - 24))
        i.move()
        i.draw(WHITE)
        if i.collide(enemies) or i.x > 1024:
            bullets.remove(i)

    for i in collapse(plant_lane_map):
        i.draw(BLACK)
        if i.health <= 0:
            plant_lane_map[i.x // 128][(i.y - 80) // 128] = None
        if not occupied[(i.y - 80) // 128]:
            screen.blit(i.image[count // 6], (i.x, i.y))
        else:
            screen.blit(i.shoot[count // 6], (i.x, i.y))
            if i.timer():
                if i.attack:
                    if i.image == ip_shoot:
                        bullets.append(Bullets(i.x + 25, i.y + 20, 10, 16, 16, 4, pygame.image.load("ice_bullet.png")))
                    else:
                        bullets.append(Bullets(i.x + 25, i.y + 20, 10, 16, 16, 4, pygame.image.load("bullet.png")))
        plant_functions(i)

    for j in range(5):
        occupied[j] = False

    for i in enemies:
        i.move()
        i.draw(RED)
        if i.x <= 0:
            lives-=1
        if not occupied[(i.y - 80) // 128]:
            if (i.y - 80) // 128 == (closest()[(i.y - 80) // 128][1] - 80) // 128 and i.x > closest()[(i.y - 80) // 128][0]:
                occupied[(i.y - 80) // 128] = True
        if i.health <= 0 or i.x < 0:
            enemies.remove(i)
        if not i.collide(collapse(plant_lane_map)):
            screen.blit(i.image[count // 3], (i.x - 28, i.y))
            i.vx = i.temp_vx
        else:
            screen.blit(i.eat[count // 3], (i.x - 28, i.y))
            i.vx = 0


def plant_functions(i):
    if i.image == sunflower and i.timer():
        sun += 25
        if i.cooldown == 7000:
            i.cooldown = 24000

    if i.image == cherry_bomb and count == 26:
        for j in enemies[:]:
            if i.x - 128 <= j.x <= i.x + 255 and i.y - 130 <= j.y <= i.y + 254:
                j.draw(BLACK)
                enemies.remove(j)
        plant_lane_map[i.x // 128][(i.y - 80) // 128] = None

    if i.image == torchwood:
        for j in bullets:
            if i.hitbox.colliderect(j.hitbox):
                j.power = 20
                j.image = pygame.image.load("fire_bullet.png")


def plant_place():
    global sun
    if icon_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and not any(picked):
        picked[pygame.mouse.get_pos()[0] // 80] = True

    if picked[8]:
        see_if_the_square_is_legal()

    elif any(picked):

        index = picked.index(True)

        drop_rect = pygame.Rect(pygame.mouse.get_pos()[0] - 25, pygame.mouse.get_pos()[1] - 25, 50, 50)

        plants = plant_dictionary(drop_rect)

        pygame.draw.rect(screen, GRAY, drop_rect, 1)
        screen.blit(icons[index], (drop_rect.left, drop_rect.top))

        if 0 <= drop_rect.left <= 1024 and 80 <= drop_rect.top <= 720 and not plant_lane_map[int(drop_rect.left / 128)][
            int((drop_rect.top - 80) / 128)]:
            sun_cost_and_place_plant_calculator(plants, index, drop_rect,sun)

        if not pygame.mouse.get_pressed()[0]:
            picked[index] = False


def see_if_the_square_is_legal():
    drop_rect = pygame.Rect(pygame.mouse.get_pos()[0] - 25, pygame.mouse.get_pos()[1] - 25, 50, 50)
    pygame.draw.rect(screen, GRAY, drop_rect, 1)

    if 0 <= drop_rect.left <= 1024 and 80 <= drop_rect.top <= 720 and not plant_lane_map[int(drop_rect.left / 128)][
        int((drop_rect.top - 80) / 128)]:
        pygame.draw.rect(screen, GRAY,
                         pygame.Rect(drop_rect.left // 128 * 128, ((drop_rect.top - 80) // 128) * 128 + 80, 128,
                                     128), 1)

    if not pygame.mouse.get_pressed()[0]:
        plant_lane_map[int(drop_rect.left / 128)][int((drop_rect.top - 80) / 128)] = None
        picked[8] = False


def sun_cost_and_place_plant_calculator(plants,index,drop_rect,sun):
    if plants[index].cost <= sun:
        pygame.draw.rect(screen, GRAY,
                         pygame.Rect(drop_rect.left // 128 * 128, ((drop_rect.top - 80) // 128) * 128 + 80, 128,
                                     128), 1)
    else:
        pygame.draw.rect(screen, RED,
                         pygame.Rect(drop_rect.left // 128 * 128, ((drop_rect.top - 80) // 128) * 128 + 80,
                                     128,
                                     128), 0)
        screen.blit(icons[index], (drop_rect.left, drop_rect.top))

    if not pygame.mouse.get_pressed()[0]:
        temp = plants[index]
        if temp.cost <= sun:
            plant_lane_map[int(drop_rect.left / 128)][int((drop_rect.top - 80) / 128)] = temp
            sun -= temp.cost
        else:
            picked[index] = False
            plant_lane_map[int(drop_rect.left / 128)][int((drop_rect.top - 80) / 128)] = None


def plant_dictionary(drop_rect):
    plants = {
        0: Plant(abs(drop_rect.left) // 128 * 128 + 20, (drop_rect.top - 80) // 128 * 128 + 94, 10, 7000, sunflower,
                 sunflower, False, 50),
        1: Plant(abs(drop_rect.left) // 128 * 128 + 39, (drop_rect.top - 80) // 128 * 128 + 94, 10, 1500, ps_image,
                 ps_shoot, True, 100),
        2: Plant(abs(drop_rect.left) // 128 * 128 + 39, (drop_rect.top - 80) // 128 * 128 + 94, 10, 750, dps_image,
                 dps_shoot, True, 200),
        3: Plant(abs(drop_rect.left) // 128 * 128, (drop_rect.top - 80) // 128 * 128 + 84, 100000, 0, cherry_bomb,
                 cherry_bomb, False, 0),  # implement exploding / exploding animation doenst work
        4: Plant(abs(drop_rect.left) // 128 * 128 + 39, (drop_rect.top - 80) // 128 * 128 + 94, 10, 500, ip_image,
                 ip_shoot, True, 0),  # make ice peashooter shoot ice bullets
        5: Plant(abs(drop_rect.left) // 128 * 128 + 39, (drop_rect.top - 80) // 128 * 128 + 94, 150, 0, walnut,
                 walnut, False, 50),
        6: Plant(abs(drop_rect.left) // 128 * 128 + 39, (drop_rect.top - 80) // 128 * 128 + 94, 10, 0, torchwood,
                 torchwood, False, 0),
        7: Plant(abs(drop_rect.left) // 128 * 128 + 39, (drop_rect.top - 80) // 128 * 128 + 94, 10, 0, bok_choy,
                 bok_choy_punching, True, 0),
    }
    return plants


def zombie_wave(time):
    global randy
    global moveCount

    if 0 < time < 3000 :
        if time % 150 == 0:
            #print(time)
            enemies.append(Enemy(1024, 94 + randy * 128, -1, 40, 1, 1000, enemy_move, enemy_eat))
            randy = random.randint(0, 4)
        if time % 350 == 0:
            #print(time)
            enemies.append(Enemy(1024, 94 + randy * 128, -2, 30, 1, 1000, knight_move, knight_eat))
            randy = random.randint(0, 4)
    if 3000< time < 3100:
        screen.blit(font.render("Wave 1", True, (0, 0, 0)), (600, 30))
    if 3100 < time < 7000 :
        if time % 130 == 0:
            #print(time)
            enemies.append(Enemy(1024, 94 + randy * 128, -1, 40, 1, 1000, enemy_move, enemy_eat))
            randy = random.randint(0, 4)
        if time % 530 == 0:
            #print(time)
            enemies.append(Enemy(1024, 94 + randy * 128, -1, 30, 5, 1000, knight_move, knight_eat))
            randy = random.randint(0, 4)
    if 7000 < time < 7500:
        screen.blit(font.render("Wave 2", True, (0, 0, 0)), (600, 30))
    if 7500 <= time <= 8000 :
        if time % 100 == 0:
            #print(time)
            if time % 130 == 0:
                # print(time)
                enemies.append(Enemy(1024, 94 + randy * 128, -1, 40, 1, 1000, enemy_move, enemy_eat))
                randy = random.randint(0, 4)
            if time % 530 == 0:
                # print(time)
                enemies.append(Enemy(1024, 94 + randy * 128, -1, 30, 5, 1000, knight_move, knight_eat))
                randy = random.randint(0, 4)
            if time % 400 == 0:
                # print(time)
                enemies.append(Enemy(1024, 94 + randy * 128, -1, 70, 10, 1000, tank, tank))
                randy = random.randint(0, 4)

    if time == 8000:
        return True
    else:
        return False

    moveCount += 1
    if moveCount < 2:
        for i in enemies:
            i.temp_vx = i.vx
            i.vx = 0
    if moveCount == 2:
        for i in enemies:
            i.vx = i.temp_vx
        moveCount = 0


def prevent_crash(run):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True


WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
sun = 50
time = 0
font = pygame.font.SysFont("comicsansms", 30)
icon_rect = pygame.Rect(0, 0, 720, 80)
picked = [False] * 9

bullets = []
enemies = []
occupied = [False] * 5
plant_lane_map = [[None] * 5 for i in range(8)]

count = 0
moveCount = 0
win = False
randy = random.randint(0, 4)

size = [1024, 720]
screen = pygame.display.set_mode(size)

done = False
lives = 5
clock = pygame.time.Clock()


sunflower = image_load(os.listdir("sunflower"), "sunflower")
ps_image = image_load(os.listdir("peashooter"), "peashooter")
ps_shoot = image_load(os.listdir("peashooter shooting"), "peashooter shooting")
dps_image = image_load(os.listdir("double peashooter"), "double peashooter")
dps_shoot = image_load(os.listdir("double peashooter shooting"), "double peashooter shooting")
cherry_bomb = image_load(os.listdir("cherry bomb"), "cherry bomb")
ip_image = image_load(os.listdir("ice peashooter"), "ice peashooter")
ip_shoot = image_load(os.listdir("ice peashooter shooting"), "ice peashooter shooting")
walnut = image_load(os.listdir("walnut"), "walnut")
walnut_cracked = image_load(os.listdir("walnut_cracked"), "walnut_cracked")
torchwood = image_load(os.listdir("torchwood"), "torchwood")
bok_choy = image_load(os.listdir("bok choy"), "bok choy")
bok_choy_punching = image_load(os.listdir("bok choy punching"), "bok choy punching")

enemy_move = image_load(os.listdir("zombie move"), "zombie move")
enemy_eat = image_load(os.listdir("eating zombie"), "eating zombie")
knight_move = image_load(os.listdir("knight_move"), "knight_move")
knight_eat = image_load(os.listdir("knight_attack"), "knight_attack")
tank = image_load(os.listdir("zombie tank"), "zombie tank")

icons = image_load(os.listdir("icons"), "icons")
background = pygame.image.load("background.png")
lose_screen= pygame.image.load("lose_screen.png")
lose_screen = pygame.transform.scale(lose_screen, size)
start_screen = pygame.image.load("menu.jpg")
start_screen = pygame.transform.scale(start_screen, size)
instructions = pygame.image.load("how to play.png")
instructions = pygame.transform.scale(instructions, size)
win_screen = pygame.image.load("win screen.png")
win_screen = pygame.transform.scale(win_screen, size)


while not done:

    screen.fill(WHITE)
    screen.blit(background, (0, 80))

    done = prevent_crash(done)

    if time == 0:
        Terminus(start_screen)
        Terminus(instructions)

    if lives == 0:
        Terminus(lose_screen)
        break

    if win:
        Terminus(win_screen)

    plant_place()

    draw_game()

    win = zombie_wave(time)

    screen.blit(font.render(str(time / 54 * 100 // 100), True, (200, 200, 0)), (800, 30))

    if time % 351 == 0:
        sun += 25

    count = (count + 1) % 27

    time += 1

    pygame.display.update()

pygame.quit()


