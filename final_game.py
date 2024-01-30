import pygame
from tools import *
import random

# cls: Gift Item Class withn earth acceleration
class Gift(Item):
  def __init__(self, game, pos, vel):
    Item.__init__(self)
    self.game = game
    self.pos = pos
    self.vel = vel
    self.acc = pygame.Vector2(0,0.0005)
    self.image = game.gift
    self.mode = 'center-center'
    self.timeout = 5000

  def update(self, delta):
    # basic update
    Item.update(self, delta)

    # check target to shifted pos
    pos = self.pos - self.game.fg.pos
    pos.x = pos.x % self.game.width
    for target in self.game.targets:
      if target.collidepoint(pos):
        self.active = False
        self.game.bling.play()
        self.game.counter += 1

# cls: Gift Item Class withn earth acceleration
class Twinkle(Item):
  def __init__(self, game, pos, vel):
    Item.__init__(self, timeout=4000)
    self.game = game
    self.pos = pos
    self.vel = vel
    self.image = game.twinkle
    self.mode = 'center-center'
    self.timeout = 4000

# cls: Player class with steering and dropping interaction
class Player(Item):
  def __init__(self, game, pos):
    Item.__init__(self)
    self.game = game
    self.pos = pos
    self.image = game.sledge
    self.mode = 'center-center'

    self.maxspeed = 0.08
    self.cooldown = 0
    self.froozen = 0
    self.fuel = 100
  
  def update(self, delta):
    if self.fuel > 0 and self.game.time > 0:
      # decrease fuel
      self.fuel -= 0.003*delta

      # steering player with cursor keys
      self.acc = pygame.Vector2(0, 0)
      self.vel.x = self.vel.y = 0
      if self.game.keys[pygame.K_LEFT] and self.pos.x > 1/8*self.game.width:
        self.vel.x -= self.maxspeed
      if self.game.keys[pygame.K_RIGHT] and self.pos.x < 7/8*self.game.width:
        self.vel.x += self.maxspeed
      if self.game.keys[pygame.K_UP] and self.pos.y > 1/8*self.game.height:
        self.vel.y -= self.maxspeed
      if self.game.keys[pygame.K_DOWN] and self.pos.y < 5/8*self.game.height:
        self.vel.y += self.maxspeed

      # twinkle generation
      self.add(Twinkle(self.game, self.pos+(-100,80), self.game.fg.vel + (0.05*(random.random()-0.5), 0.05*(random.random()-0.5))))

    else:
      # falling down, no steering
      self.acc = pygame.Vector2(0, 0.00005)

      # game over, if on ground
      if self.pos.y > 1.25*self.game.height:
        self.acc = pygame.Vector2(0, 0)
        self.game.time = 0

    # dropping gifts with space key and cooldown
    if self.cooldown > 0:
      self.cooldown -= delta

    if self.froozen > 0:
      self.froozen -= delta
    
    if self.game.keys[pygame.K_SPACE] and self.game.time > 0 and self.cooldown <= 0 and self.froozen <= 0:
      self.cooldown = 1000
      self.game.drop.play()
      self.game.gifts.add(Gift(self.game, pygame.Vector2(self.pos), self.vel+(0.2,-0.3)))

    # basic update
    Item.update(self, delta)


# cls: Moving Scenery class with double image draw
class Scenery(Item):
  def __init__(self, game, pos, vel, image):
    Item.__init__(self)
    self.game = game
    self.pos = pos
    self.vel = vel
    self.image = image
    self.mode = 'left-top'

  def update(self, delta):
    Item.update(self, delta)

    if self.pos.x < 0:
      self.pos.x += self.game.width
    if self.pos.x >= self.game.width:
      self.pos.x -= self.game.width
  
  def draw(self, screen):
    # basic draw
    Item.draw(self, screen)
    # second draw at the left side
    drawImage(screen, self.image, self.pos - pygame.Vector2(self.game.width,0), mode=self.mode)

# cls: Star Class
class Star(Item):
  def __init__(self, game, pos, vel):
    Item.__init__(self)
    self.game = game
    self.pos = pos
    self.vel = vel
    self.image = game.star
    self.mode = 'center-center'
    self.timeout = 10000

  def update(self, delta):
    Item.update(self, delta)

    # check collecting by player
    target = pygame.Rect(self.game.player.pos.x-self.game.width/8, self.game.player.pos.y-self.game.height/8, self.game.width/4, self.game.height/4)
    if target.collidepoint(self.pos):
      self.active = False
      self.game.bling.play()
      self.game.player.fuel = min(self.game.player.fuel+25, 100)

# cls: Star Class
class Flake(Item):
  def __init__(self, game, pos, vel):
    Item.__init__(self)
    self.game = game
    self.pos = pos
    self.vel = vel
    self.image = game.flake
    self.mode = 'center-center'
    self.timeout = 10000

  def update(self, delta):
    Item.update(self, delta)

    # check collecting by player
    target = pygame.Rect(self.game.player.pos.x-self.game.width/16, self.game.player.pos.y-self.game.height/16, self.game.width/8, self.game.height/8)
    if target.collidepoint(self.pos):
      self.active = False
      self.game.player.froozen = 5000

# cls: Random Item Emitter
class Emitter(Item):
  def __init__(self, game, pos, speed, type, min, max):
    Item.__init__(self)
    self.game = game
    self.pos = pos
    self.speed = speed
    self.type = type
    self.min = min
    self.max = max
    self.cooldown = random.randint(self.min, self.max)

  def update(self, delta):
    Item.update(self, delta)

    # dropping objects after cooldown
    if self.cooldown > 0:
      self.cooldown -= delta
    else:
      self.cooldown = random.randint(self.min, self.max)
      self.add(self.type(self.game, self.pos + (0, random.randint(1/8*self.game.height,4/8*self.game.height)), self.speed + (0,0)))

# cls: User Interface
class UI(Item):
  def __init__(self, game):
    Item.__init__(self)
    self.game = game
    self.gift = pygame.transform.scale(self.game.gift, (40, 40))
    self.star = pygame.transform.scale(self.game.star, (40, 40))

  def draw(self, screen):
    white = (255, 255, 255)
    yellow = (255, 255, 0)
    red = (255, 0, 0)

    # fuel color
    if self.game.player.fuel < 10:
      color1 = red
    elif self.game.player.fuel < 25:
      color1 = yellow
    else:
      color1 = white

    # time color
    if self.game.time < 10000:
      color2 = red
    elif self.game.time < 20000:
      color2 = yellow
    else:
      color2 = white

    # gifts color
    if self.game.player.froozen > 1000:
      color3 = red
    elif self.game.player.froozen > 0:
      color3 = yellow
    else:
      color3 = white

    # time text
    if self.game.time <= 0:
      text2 = "GAME OVER - press ENTER to start"
    else:
      text2 = "{:02d}:{:02d}".format(int(self.game.time/60000), int(self.game.time/1000)%60)

    # draw texts
    drawText(screen, "{:>2d}".format(int(self.game.player.fuel/5)*5), self.game.font1, color1, int(80), int(40), anchor='left-center')
    drawText(screen, text2, self.game.font1, color2, int(self.game.width/2), int(50), anchor='center-center')
    drawText(screen, "{:>3d}".format(self.game.counter), self.game.font1, color3, int(self.game.width - 80), int(40), anchor='right-center')

    drawImage(screen, self.star, pygame.Vector2(40,40), mode='center-center')
    drawImage(screen, self.gift, pygame.Vector2(self.game.width-40,40), mode='center-center')

# cls: main app class with game logic
class SantaClaus(Game):
  def __init__(self):
    Game.__init__(self, 'Santa Claus - programmiert im Rahmen der GTA 2021/2022 am S.-v.-P. Gymnasium Flöha', 1280, 720, fps=30)

    # resources
    self.sledge = loadImage("img/sledge.png", self.width/4, self.height/4)
    self.landscape = loadImage("img/mountains.png", self.width, self.height)
    self.town = loadImage("img/houses.png", self.width, self.height)
    self.gift = loadImage("img/gift.png", 25, 25)
    self.twinkle = loadImage("img/twinkle.png", 10, 10)
    self.star = loadImage("img/star.png", 32, 32)
    self.flake = loadImage("img/flake.png", 48, 48)

    self.drop = loadSound("snd/drop.ogg", 0.25)
    self.bling = loadSound("snd/bling.flac", 0.25)
    self.music = loadSound("snd/jingle_bells.mp3", 0.1)

    self.font1 = pygame.font.SysFont('Comic Sans MS', 40)

    # game objects
    self.player = Player(self, pygame.Vector2(self.width/2, self.height/2))
    self.bg = Scenery(self, pygame.Vector2(0,0), pygame.Vector2(-0.05,0), self.landscape)
    self.fg = Scenery(self, pygame.Vector2(0,self.height/2), pygame.Vector2(-0.15,0), self.town)
    self.gifts = Item()
    self.ui = UI(self)
    self.stars = Emitter(self, pygame.Vector2(4/4*self.width, 0), pygame.Vector2(-0.13,0), Star, 4000, 10000)
    self.flakes = Emitter(self, pygame.Vector2(4/4*self.width, 0), pygame.Vector2(-0.2,0.02), Flake, 1000, 5000)

    self.add(self.bg)
    self.add(self.stars)
    self.add(self.player)
    self.add(self.flakes)
    self.add(self.fg)
    self.add(self.gifts)
    self.add(self.ui)

    # game variables
    self.time = 0
    self.counter = 0
               
    # additional data
    self.targets = [
      pygame.Rect(91, 232, 29, 33),
      pygame.Rect(314, 233, 29, 31),
      pygame.Rect(449, 227, 29, 38),
      pygame.Rect(590, 114, 28, 31),
      pygame.Rect(638, 119, 29, 24),
      pygame.Rect(689, 105, 32, 40),
      pygame.Rect(818, 135, 30, 32),
      pygame.Rect(1111, 235, 30, 31)
    ]

  def before(self):
    # start music
    self.music.play(-1)

  def after(self):
    # stop music
    self.music.stop()

  def update(self, delta):
    # update game objects
    Game.update(self, delta)

    # game data
    if self.time >= 0:
      self.time -= delta

    # restart
    if self.time < 0 and self.keys[pygame.K_RETURN]:
      self.time = 120000
      self.counter = 0
      self.player.pos = pygame.Vector2(self.width/2, self.height/2)
      self.player.vel = pygame.Vector2(0, 0)
      self.player.acc = pygame.Vector2(0, 0)
      self.player.fuel = 100

# main: create and run game
SantaClaus().run()
