import pygame

# fun: load image from file an rezise
def loadImage(filename, width, height):
  image = pygame.image.load(filename)
  image = pygame.transform.scale(image, (int(width), int(height)))
  return image

# fun: load sound from file an set volume
def loadSound(filename, volume):
  sound = pygame.mixer.Sound(filename)
  sound.set_volume(volume)
  return sound

# fun: function to draw text
def drawText(screen, text, font, color, x, y, anchor='center-center'):
  img = font.render(text, True, color)
  w, h = img.get_size()
  if anchor == 'left-center':
    screen.blit(img, (int(x), int(y - h/2)))
  elif anchor == 'right-center':
    screen.blit(img, (int(x - w), int(y - h/2)))
  else:
    screen.blit(img, (int(x - w/2), int(y - h/2)))

def drawImage(screen, image, pos, mode='left-top'):
  if mode == 'center-center':
    w, h = image.get_size()
    screen.blit(image, (pos.x - w/2, pos.y-h/2))
  else:
    screen.blit(image, (pos.x, pos.y))

# cls: General Item Class with visual and physical properties
class Item:
  def __init__(self, timeout=0):
    self.image = None
    self.mode = 'left-top'
    self.pos = pygame.Vector2(0,0)
    self.vel = pygame.Vector2(0,0)
    self.acc = pygame.Vector2(0,0)
    self.active = True
    self.timeout = timeout
    self.items = []

  def add(self, item):
    self.items.append(item)

  def update(self, delta):
    if self.active:
      # timeout
      if self.timeout > 0:
        self.timeout -= delta
        if self.timeout <= 0:
          self.active = False

      # update physics
      self.vel += self.acc * delta
      self.pos += self.vel * delta

      # remove inactive items
      self.items = list(filter(lambda item: item.active, self.items))

      # update items
      for item in self.items:
        item.update(delta)

  def draw(self, screen):
    if self.active:
      # draw item
      if self.image:
        drawImage(screen, self.image, self.pos, mode=self.mode)

      # draw items
      for item in self.items:
        item.draw(screen)

# cls: Basis Game Class
class Game(Item):
  def __init__(self, title, width, height, fps=30):
    Item.__init__(self)

    # pygame Initialisierungen
    pygame.init()
    pygame.mixer.init(44100, -16, 2, 512)

    # set title
    pygame.display.set_caption(title)

    # set screen size
    self.width = width
    self.height = height

    # store fps
    self.fps = fps

  def before(self):
    pass

  def after(self):
    pass

  def update(self, delta):
    Item.update(self, delta)

  def draw(self, screen):
    Item.draw(self, screen)

  def run(self):
    # define fps and clock
    clock = pygame.time.Clock()

    # create window
    screen = pygame.display.set_mode((self.width, self.height))

    self.before()

    # main loop
    running = True
    while running:
      # sync to fps
      delta = clock.tick(self.fps)

      # handle events
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False

      # update objects
      self.keys = pygame.key.get_pressed()
      self.update(delta)

      # draw graphics
      screen.fill((0,0,0))
      self.draw(screen)

      pygame.display.update()

    # after hook
    self.after()

    # quit pygame
    pygame.quit()

