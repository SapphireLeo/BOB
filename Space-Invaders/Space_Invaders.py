import pygame
import sys
import random

COLOR = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'white': (255, 255, 255)
}

SCREEN_SIZE = {
    'width': 600,
    'height': 800
}

PIXEL_SIZE = {
    'x': 2,
    'y': 2
}
PLAYER_MOVE_DELAY = 30
BULLET_MOVE_DELAY = 15
INVADER_FIRE_DELAY = 100
INVADER_MOVE_DELAY = 1300
MOVE_DISTANCE = 4
DISTANCE_BETWEEN_INVADERS = {
    'x': 23,
    'y': 16
}
BULLET_OFFSET = (
    (0, 0, COLOR['green']),
    (0, 1, COLOR['green']),
    (0, 2, COLOR['green']),
    (0, 3, COLOR['green']),
)
BARRIER_BLOCK_OFFSET = (
    (-1 * PIXEL_SIZE['x'], 0 * PIXEL_SIZE['y']),
    (0 * PIXEL_SIZE['x'], 0 * PIXEL_SIZE['y']),
    (1 * PIXEL_SIZE['x'], 0 * PIXEL_SIZE['y']),
    (-2 * PIXEL_SIZE['x'], 1 * PIXEL_SIZE['y']),
    (-1 * PIXEL_SIZE['x'], 1 * PIXEL_SIZE['y']),
    (0 * PIXEL_SIZE['x'], 1 * PIXEL_SIZE['y']),
    (1 * PIXEL_SIZE['x'], 1 * PIXEL_SIZE['y']),
    (2 * PIXEL_SIZE['x'], 1 * PIXEL_SIZE['y']),
    (-3 * PIXEL_SIZE['x'], 2 * PIXEL_SIZE['y']),
    (-2 * PIXEL_SIZE['x'], 2 * PIXEL_SIZE['y']),
    (-1 * PIXEL_SIZE['x'], 2 * PIXEL_SIZE['y']),
    (0 * PIXEL_SIZE['x'], 2 * PIXEL_SIZE['y']),
    (1 * PIXEL_SIZE['x'], 2 * PIXEL_SIZE['y']),
    (2 * PIXEL_SIZE['x'], 2 * PIXEL_SIZE['y']),
    (3 * PIXEL_SIZE['x'], 2 * PIXEL_SIZE['y']),
    (-3 * PIXEL_SIZE['x'], 3 * PIXEL_SIZE['y']),
    (-2 * PIXEL_SIZE['x'], 3 * PIXEL_SIZE['y']),
    (2 * PIXEL_SIZE['x'], 3 * PIXEL_SIZE['y']),
    (3 * PIXEL_SIZE['x'], 3 * PIXEL_SIZE['y']),
)
BlOCK_PIXEL_OFFSET = tuple([(row, col, COLOR['blue']) for row, col in zip((-1, 0, 1), (-1, 0, 1))])

def calculate_position(offset_x, offset_y, position_x, position_y):
    return position_x + offset_x * PIXEL_SIZE['x'], position_y + offset_y * PIXEL_SIZE['y']


class Pixel:
    def __init__(self, x, y, color):
        if not isinstance(x, int):
            raise TypeError(f'x offset of class Pixel must be integer type, got {x}:{type(x)}')
        if not isinstance(y, int):
            raise TypeError(f'x offset of class Pixel must be integer type, got {y}:{type(y)}')
        if not isinstance(color, tuple):
            raise TypeError(f'color of class Pixel must be tuple type, got {color}:{type(color)}')

        self.x = x
        self.y = y
        self.color = color

    def __repr__(self):
        return 'Pixel(x: ' + str(self.x) + ' y: ' + str(self.y) + ' color: ' + str(self.color) + ')'


class Shape:
    def __init__(self, **info):
        position = info.get('position')
        if position is not None and not isinstance(position, dict):
            raise TypeError('position of class Shape must be defined as dictionary.')
        if position.get('x') is None or position.get('y') is None:
            raise KeyError('position of class Shape must have x key and y key.')
        self.position = info.get('position')
        self.pixels = []
        self.leftmost, self.rightmost, self.topmost, self.bottommost = None, None, None, None

        pixels = info.get('pixels')
        if pixels is not None:
            for pixel in pixels:
                if not isinstance(pixel, tuple):
                    raise TypeError('points in class Shape must be defined as tuple')
                if len(pixel) < 3:
                    raise IndexError(f'number of pixel arguments must be 3, got {len(pixels)}')

                offset_x, offset_y, pixel_color = pixel[0], pixel[1], pixel[2]

                self.pixels.append(Pixel(offset_x, offset_y, pixel_color))

    def draw_rect(self, left, top, width, height, pixel_color):
        for offset_x in range(width):
            for offset_y in range(height):
                self.pixels.append(Pixel(left + offset_x, top + offset_y, pixel_color))

    def move(self, direction):
        if direction == 'left':
            self.position['x'] -= MOVE_DISTANCE * PIXEL_SIZE['x']
        elif direction == 'right':
            self.position['x'] += MOVE_DISTANCE * PIXEL_SIZE['x']
        elif direction == 'up':
            self.position['y'] -= MOVE_DISTANCE * PIXEL_SIZE['y']
        elif direction == 'down':
            self.position['y'] += MOVE_DISTANCE * PIXEL_SIZE['y']


class Object:
    def __init__(self, **info):
        shape = info.get('shape')
        name = info.get('name')
        if shape is not None:
            self.shape = shape
        else:
            self.shape = Shape()

        if name is not None:
            self.name = name
        else:
            self.name = 'NoName'

    def draw_rect(self, left, top, width, height, pixel_color):
        self.shape.draw_rect(left, top, width, height, pixel_color)

    def move(self, direction):
        self.shape.move(direction)


class Bullet(Object):
    def is_hit(self, other):
        if not isinstance(other, Object):
            raise TypeError('is_hit method must be done between class Object.')
        for my_pixel in self.shape.pixels:
            for other_pixel in other.shape.pixels:
                if self.shape.position['x'] + PIXEL_SIZE['x'] * my_pixel.x == other.shape.position['x'] + PIXEL_SIZE[
                    'x'] * other_pixel.x \
                        and self.shape.position['y'] + PIXEL_SIZE['y'] * my_pixel.y == other.shape.position['y'] + \
                        PIXEL_SIZE['y'] * other_pixel.y:
                    return True
        return False


class Attacker(Object):
    def __init__(self, **info):
        super().__init__(**info)
        self.bullets = []


class Player(Attacker):
    def fire(self):
        shape = Shape(position={'x': self.shape.position['x'],
                                'y': self.shape.position['y'] - 15 * PIXEL_SIZE['y']})
        shape.draw_rect(0, 0, 1, 4, COLOR['green'])
        bullet = Bullet(name='bullet',
                        shape=shape)
        self.bullets.append(bullet)


class Monster(Attacker):
    def fire(self):
        shape = Shape(position={'x': self.shape.position['x'],
                                'y': self.shape.position['y'] + 15 * PIXEL_SIZE['y']})
        shape.draw_rect(0, 0, 1, 4, COLOR['red'])
        bullet = Bullet(name='bullet',
                        shape=shape)
        self.bullets.append(bullet)

class Block(Object):
    def __init__(self, **info):
        name = info.get('name')
        shape = Shape(pixels=BlOCK_PIXEL_OFFSET,
                      position=info.get('position'))
        super().__init__(name=name, shape=shape)

class Barrier:
    def __init__(self):
        self.blocks = []

    def add_block(self, block):
        if not isinstance(block, Object):
            raise TypeError('type of block must be class Block.')
        self.blocks.append(block)


class Display:
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height))
        self.invaders = []
        self.barriers = []
        self.invader_group_boundary = {
            'left': SCREEN_SIZE['width'] / 2,
            'right': SCREEN_SIZE['width'] / 2,
            'bottom': 0
        }
        self.player = None
        self.invader_move_direction = 'right'

    def add_monster(self, monster):
        if not isinstance(monster, Object):
            raise TypeError('monster must be type as class Object.')
        self.invaders.append(monster)
        if self.invader_group_boundary['left'] > monster.shape.position['x']:
            self.invader_group_boundary['left'] = monster.shape.position['x']
        if self.invader_group_boundary['right'] < monster.shape.position['x']:
            self.invader_group_boundary['right'] = monster.shape.position['x']
        if self.invader_group_boundary['bottom'] < monster.shape.position['y']:
            self.invader_group_boundary['bottom'] = monster.shape.position['y']
    def add_barrier(self, barrier):
        if not isinstance(barrier, Barrier):
            raise TypeError('barrier must be type as class Barrier.')
        self.barriers.append(barrier)

    def set_player(self, player):
        if not isinstance(player, Object):
            raise TypeError('monster must be type as class Object.')
        self.player = player

    def update(self):
        self.screen.fill((0, 0, 0))
        for attacker in [self.player] + self.invaders:
            shape = attacker.shape
            for pixel in shape.pixels:
                pygame.draw.rect(self.screen, pixel.color,
                                 [shape.position['x'] + pixel.x * PIXEL_SIZE['x'],
                                  shape.position['y'] + pixel.y * PIXEL_SIZE['y'],
                                  PIXEL_SIZE['x'], PIXEL_SIZE['y']])

            for bullet in attacker.bullets:
                for pixel in bullet.shape.pixels:
                    pygame.draw.rect(self.screen, pixel.color,
                                     [bullet.shape.position['x'] + pixel.x * PIXEL_SIZE['x'],
                                      bullet.shape.position['y'] + pixel.y * PIXEL_SIZE['y'],
                                      PIXEL_SIZE['x'], PIXEL_SIZE['y']])

        for barrier in self.barriers:
            for block in barrier.blocks:
                for pixel in block.shape.pixels:
                    pygame.draw.rect(self.screen, pixel.color,
                                     [block.shape.position['x'] + pixel.x * PIXEL_SIZE['x'],
                                      block.shape.position['y'] + pixel.y * PIXEL_SIZE['y'],
                                      PIXEL_SIZE['x'], PIXEL_SIZE['y']])
        if len(self.invaders) == 0:
            self.display_message('win')
        pygame.display.update()

    def random_invader_fire(self):
        if len(self.invaders) > 0:
            for invader in self.invaders:
                if random.randrange(400) == 0:
                    invader.fire()

    def player_move(self, direction):
        self.player.move(direction)

    def bullet_move(self):
        for bullet in self.player.bullets:
            if bullet.shape.position['y'] < 0 or bullet.shape.position['y'] > SCREEN_SIZE['height']:
                self.player.bullets.remove(bullet)
                continue
            else:
                bullet.move('up')
            for monster in self.invaders:
                if bullet.is_hit(monster):
                    self.invaders.remove(monster)
                    self.player.bullets.remove(bullet)
                    break

        for invader in self.invaders:
            for bullet in invader.bullets:
                if bullet.shape.position['y'] < 0 or bullet.shape.position['y'] > SCREEN_SIZE['height']:
                    invader.bullets.remove(bullet)
                    continue
                else:
                    bullet.move('down')
                if bullet.is_hit(self.player):
                    del self.player
                    invader.bullets.remove(bullet)
                    return False
        return True

    def invader_move(self):
        if self.invader_group_boundary['left'] <= 30:
            self.invader_move_direction = 'right'
        if self.invader_group_boundary['right'] >= SCREEN_SIZE['width'] - 30:
            self.invader_move_direction = 'left'

        if self.invader_move_direction == 'left':
            self.invader_group_boundary['left'] -= MOVE_DISTANCE * PIXEL_SIZE['x']
            self.invader_group_boundary['right'] -= MOVE_DISTANCE * PIXEL_SIZE['x']
        if self.invader_move_direction == 'right':
            self.invader_group_boundary['left'] += MOVE_DISTANCE * PIXEL_SIZE['x']
            self.invader_group_boundary['right'] += MOVE_DISTANCE * PIXEL_SIZE['x']
        for invader in self.invaders:
            invader.move(self.invader_move_direction)

    def display_message(self, message):
        text = None
        if message == 'win':
            text = victoryText
        elif message == 'lose':
            text = gameOverText
        else:
            return

        text_rect = text.get_rect()
        text_rect.centerx = round(SCREEN_SIZE['width'] / 2)
        text_rect.y = SCREEN_SIZE['height'] / 2
        self.screen.blit(text, text_rect)

pygame.init()

font = pygame.font.SysFont("arial", 30, bold=False, italic=False)
victoryText = font.render("You Won!", True, COLOR['white'])
gameOverText = font.render("Game Over", True, COLOR['white'])

display = Display(SCREEN_SIZE['width'], SCREEN_SIZE['height'])
pygame.display.set_caption("SPACE INVADERS")

# set player object
player = Player(name='player', shape=Shape(position={'x': 300, 'y': 600}))
player.draw_rect(-7, -7, 15, 7, COLOR['green'])
player.draw_rect(-1, -10, 3, 3, COLOR['green'])
display.set_player(player)


# add invaders
def generate_invaders(left, top, row, col):
    for y in range(row):
        for x in range(col):
            invader = Monster(name='invader' + str(y * col + x),
                              shape=Shape(position={'x': (left + x * DISTANCE_BETWEEN_INVADERS['x']) * PIXEL_SIZE['x'],
                                                    'y': (top + y * DISTANCE_BETWEEN_INVADERS['y']) * PIXEL_SIZE['y']}))
            invader.draw_rect(-2, -4, 2, 2, COLOR['red'])
            invader.draw_rect(2, -4, 2, 2, COLOR['red'])
            invader.draw_rect(-4, -2, 10, 2, COLOR['red'])
            invader.draw_rect(-4, 0, 2, 2, COLOR['red'])
            invader.draw_rect(0, 0, 2, 2, COLOR['red'])
            invader.draw_rect(4, 0, 2, 2, COLOR['red'])
            invader.draw_rect(-6, 2, 14, 2, COLOR['red'])
            invader.draw_rect(-4, 4, 2, 2, COLOR['red'])
            invader.draw_rect(4, 4, 2, 2, COLOR['red'])
            yield invader

def generate_barriers(left, top, distance, number):
    for i in range(number):
        barrier = Barrier()
        for offsets in BARRIER_BLOCK_OFFSET:
            position = {
                'x': left+distance * number+offsets[0],
                'y': top+offsets[1]
            }
            block = Block(position=position)
            barrier.add_block(block)
        yield barrier


for new_invader in generate_invaders(30, 30, 5, 11):
    display.add_monster(new_invader)

for new_barrier in generate_barriers(50, 500, 70, 4):
    display.add_barrier(new_barrier)

keyPress = {
    'left': False,
    'right': False,
    'up': False,
    'down': False
}

playerMoveTime = lastPlayerMoveTime = 0
bulletMoveTime = lastBulletMoveTime = 0
invaderFireTime = lastInvaderFireTime = 0
invaderMoveTime = lastInvaderMoveTime = 0

gameOver = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            if event.key == pygame.K_LEFT:
                keyPress['left'] = True
            if event.key == pygame.K_RIGHT:
                keyPress['right'] = True
            if event.key == pygame.K_UP:
                keyPress['up'] = True
            if event.key == pygame.K_DOWN:
                keyPress['down'] = True
            if not gameOver and event.key == pygame.K_SPACE:
                display.player.fire()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                keyPress['left'] = False
            if event.key == pygame.K_RIGHT:
                keyPress['right'] = False
            if event.key == pygame.K_UP:
                keyPress['up'] = False
            if event.key == pygame.K_DOWN:
                keyPress['down'] = False

    if gameOver:
        display.display_message('lose')
        pygame.display.update()
        continue

    for key, keyIsPressed in keyPress.items():
        if keyIsPressed:
            playerMoveTime = pygame.time.get_ticks()
            if playerMoveTime - lastPlayerMoveTime >= PLAYER_MOVE_DELAY:
                display.player_move(key)
                lastPlayerMoveTime = pygame.time.get_ticks()

    bulletMoveTime = pygame.time.get_ticks()
    if bulletMoveTime - lastBulletMoveTime >= BULLET_MOVE_DELAY:
        if not display.bullet_move():
            print('game over')
            gameOver = True
            continue
        lastBulletMoveTime = bulletMoveTime

    invaderFireTime = pygame.time.get_ticks()
    if invaderFireTime - lastInvaderFireTime >= INVADER_FIRE_DELAY:
        display.random_invader_fire()
        lastInvaderFireTime = invaderFireTime

    invaderMoveTime = pygame.time.get_ticks()
    if invaderMoveTime - lastInvaderMoveTime >= INVADER_MOVE_DELAY:
        display.invader_move()
        lastInvaderMoveTime = invaderMoveTime

    display.update()
