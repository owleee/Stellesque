# Import useful modules

import pygame
import math
from random import randint, choice
from functions import sin, cos, ssqrt, m, centredRotate
from colours import GREY, WHITE, BLACK, CYAN

datatxt = open("data.txt","r")

removeNewlines = lambda l: [i.replace("\n","") for i in l]

data = removeNewlines(datatxt.readlines())
try:
    highscore = int(data[0])
except:
    highscore = 0

pygame.display.set_icon(pygame.image.load("spaceship/default/display.png"))

# Define game's tickspeed
tickspeed = 60

# Define name, with rare easter-egg variations
NAME = "STELLESQUE" if randint(1, 10) != 1 else choice(
    ["STELLÊQUE", "ESTELESQUE", "SUTERESUKU", "MUSI SELE", "SCELESKO"])

# Initiate pygame
pygame.init()

global screen
screen = pygame.display.set_mode((800, 450), pygame.RESIZABLE)
w, h = screen.get_size()
pygame.display.set_caption(NAME)
clock = pygame.time.Clock()

explosionSound = [pygame.mixer.Sound(f"sounds/explosion{i}.wav") for i in range(4)]          
laserSound = [pygame.mixer.Sound(f"sounds/laser{i}.wav") for i in range(4)]
hurtSound = pygame.mixer.Sound("sounds/hurt.wav")
clickSound = pygame.mixer.Sound("sounds/click.wav")
pygame.mixer.music.load("sounds/music.wav")
pygame.mixer.music.play(-1)

global skins, skin

skins = {
    0:"default"
}

class Game():
    def __init__(self):
        self.dt = 1
        self.score = 0
        self.schemeID = 0
        self.controlSchemes = ["default","WASD","ASPL"]

game = Game()

game.controlScheme = "default"
controls = {
    "default":{
        "fire":pygame.K_SPACE,
        "forward":pygame.K_UP,
        "back":pygame.K_DOWN,
        "cw":pygame.K_RIGHT,
        "acw":pygame.K_LEFT
    },
    "WASD":{
        "fire":pygame.K_SPACE,
        "forward":pygame.K_w,
        "back":pygame.K_s,
        "cw":pygame.K_d,
        "acw":pygame.K_a
    },
    "ASPL":{
        "fire":pygame.K_SPACE,
        "forward":pygame.K_p,
        "back":pygame.K_l,
        "cw":pygame.K_s,
        "acw":pygame.K_a
    }
}

buttons = []
deathButtons = []

class Dimensions():
    "Object that stores the screen's dimensions"

    def __init__(self):
        self.update()

    def update(self):
        w, h = screen.get_size()
        a = w / 8 if w / h < 16 / 9 else h / 4.5

        self.left = w / 2 - 4 * a
        self.right = w / 2 + 4 * a
        self.top = h / 2 - (9 * a) / 4
        self.bottom = h / 2 + (9 * a) / 4

        self.scale = a / 200

        self.width = self.right - self.left
        self.height = self.bottom - self.top

        for i in buttons:
            i.updateBox()


dim = Dimensions()

tick = 0

font = lambda a: pygame.font.Font("ChakraPetch-Bold.ttf", a)

objects = []
projectiles = []


def addObj(obj):
    objects.append(obj)


# Define various settings
settings = {
    "starfield": True,
    "engines": True,
    "fragments":True,
    "paint": False,
    "invulnerability":False,
    "realistic_friction": False,
    "fullscreen": False,
    "auto_fire": True,
    "fps":True
}

j = 1
for i in settings:
    settings[i] = (str(data[j])=="True")
    j+= 1

game.schemeID = int(data[j])
game.controlScheme = game.controlSchemes[game.schemeID]

del j

settings["paint"] = False
settings["realistic_friction"] = False

def saveData(hs=0):
    datatxt = open("data.txt","r")
    removeNewlines = lambda l: [i.replace("\n","") for i in l]
    data = removeNewlines(datatxt.readlines())
    datatxt.close()
    highscore = max(int(data[0]),hs)

    datatxt = open("data.txt","w")
    datatxt.write(f"{highscore}\n")
    for i in settings:
        datatxt.write(f"{settings[i]}\n")

    datatxt.write(f"{game.schemeID}\n")
    
    datatxt.close()

datatxt.close()

class GameObj:

    def __init__(self, src:str):
        self.x = 0
        self.y = 0
        self.xVel = 0
        self.yVel = 0
        self.r = 0
        self.rVel = 0
        self.scale = 1

        self.xOffset = 0
        self.yOffset = 0
        self.rOffset = 0
        self.scaleOffset = 1

        self.show = True

        self.z = 10
        self.image = pygame.image.load(src)
        self.children = []
        self.define()
        addObj(self)

    def move(self, x, y):
        self.xVel += x
        self.yVel += y
        self.updateChildren()

    def define(self):
        pass

    def forward(self, n):
        self.xVel -= n * sin(self.r)
        self.yVel -= n * cos(self.r)
        self.updateChildren()

    def goto(self, x, y):
        self.x = x
        self.y = y
        self.updateChildren()

    def rotate(self, angle):
        self.rVel += angle
        self.updateChildren()

    def setRotation(self, angle):
        self.r = angle % 360
        self.updateChildren()

    def velocity(self):
        self.x += self.xVel
        self.y += self.yVel
        self.r += self.rVel
        self.r = self.r % 360
        self.xVel = self.yVel = self.rVel = 0
        self.updateChildren()

    def updateChildren(self):
        for i in self.children:
            i.r = self.r + i.rOffset
            i.scale = self.scale * i.scaleOffset

            i.show = self.show

            i.x = self.x - i.yOffset * self.scale * sin(
                self.r) + i.xOffset * self.scale * cos(self.r)

            i.y = self.y - i.xOffset * self.scale * sin(
                self.r) - i.yOffset * self.scale * cos(self.r)

    def render(self):
        if not self.show:
            return
        img1 = pygame.transform.rotozoom(self.image, 0, self.scale * dim.scale)
        rotImg = centredRotate(img1, self.r, fx(self.x), fy(self.y))
        screen.blit(rotImg[0], rotImg[1])


class Spaceship(GameObj):

    def __init__(self, src):
        self.x = 0
        self.y = 0
        self.xVel = 0
        self.yVel = 0
        self.r = 0
        self.rVel = 0
        self.scale = 1
        self.image = pygame.image.load(src)
        self.z = 0
        self.children = []
        self.weapon = None
        addObj(self)

        self.show = True

        self.iFrames = 0
        self.health = 100
        self.regenDelay = 100

        self.rFriction = 0.85
        self.friction = 0.97
        self.forwardVelocity = 0

    def velocity(self):
        self.x += self.xVel
        self.y += self.yVel
        self.r += self.rVel

        self.r = self.r % 360
        if not settings["realistic_friction"]:
            self.xVel = self.xVel * (self.friction)
            self.yVel = self.yVel * (self.friction)
            self.rVel *= self.rFriction

        self.xVel, self.yVel, self.rVel = m(self.xVel), m(self.yVel), m(
            self.rVel)

        self.forwardVelocity = math.sqrt(self.xVel**2 + self.yVel**2)

        self.updateChildren()


class Hitbox:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.radius = 0

        # not used but necessary for the updateChildren method
        self.scale = 0
        self.rOffset = 0
        self.scaleOffset = 0
        self.show = False
        ##

        self.xOffset = 0
        self.yOffset = 0

        hitboxes.append(self)

    def draw(self):
        "Debug function"
        pygame.draw.circle(screen, WHITE, (fx(self.x), fy(self.y)),
                           self.radius)

    def checkCollision(self):
        for i in asteroids:
            if math.dist([self.x, self.y],
                         [i.x, i.y]) < self.radius + i.radius:
                return True, i
        return False, None


hitboxes = []


class Weapon(GameObj):

    def __init__(self, src):
        self.x = 0
        self.y = 0
        self.xVel = 0
        self.yVel = 0
        self.r = 0
        self.rVel = 0
        self.scale = 1

        self.xOffset = 0
        self.yOffset = 0
        self.rOffset = 0
        self.scaleOffset = 1

        self.projectile = None
        self.cooldown = 0

        self.z = 0
        self.image = pygame.image.load(src)
        self.children = []

        addObj(self)

    def attack(self):
        pygame.mixer.Sound.play(choice(laserSound))
        pewPew = self.projectile("spaceship/laser.png")
        pewPew.x = self.x
        pewPew.y = self.y
        pewPew.r = self.r
        pewPew.scale = self.scale
        projectiles.append(pewPew)


class Projectile(GameObj):
    "Generic projectile object"

    def __init__(self, src):
        self.x = 0
        self.y = 0
        self.xVel = ship.xVel
        self.yVel = ship.yVel
        self.r = 0
        self.rVel = 0
        self.scale = 1

        self.xOffset = 0
        self.yOffset = 0
        self.rOffset = 0
        self.scaleOffset = 1

        self.show = True

        self.speed = 1
        self.lifespan = -1

        self.radius = 1

        self.z = 0
        self.image = pygame.image.load(src)
        self.children = []
        addObj(self)

        self.define()

    def velocity(self):
        pass

    def define(self):
        "Defines unique qualities"
        pass

    def tick(self):
        "Called every frame, to handle collisions and movement"
        self.x -= (self.speed * sin(self.r) - self.xVel)*game.dt
        self.y -= (self.speed * cos(self.r) - self.yVel)*game.dt
        self.target = None
        """
        for i in asteroids:
            if self.target == None:
                self.target = i
            else:
                if math.dist([self.x, self.y], [i.x, i.y]) < math.dist(
                    [self.x, self.y], [self.target.x, self.target.y]):
                    self.target = i
        if self.target != None:
          angle = math.atan2(self.target.y - i.y, self.target.x - i.x)
          #self.r -= angle * settings["homing_strength"]  
        """
        if self.lifespan > 0:
            self.lifespan -= 1
        elif self.lifespan == 0:
            objects.remove(self)
            projectiles.remove(self)
            return

        if self.x > 1600 + 10 or self.x < -10 or self.y > 900 + 10 or self.y < -10:
            try:
                objects.remove(self)
                projectiles.remove(self)
            except:
                pass


class BasicLaser(Projectile):
    "The basic laser prototype object"

    def define(self):
        "Defines unique qualities"
        self.speed = 30
        self.lifespan = -1
        self.radius = 30
        self.pierce = [2,0]


class Star():
    "Star object to create scrolling starfield background"

    def __init__(self, x, y, speed, radius):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = radius

    def tick(self):
        self.x += self.speed
        self.y += self.speed / 10
        pygame.draw.circle(screen, WHITE, (fx(self.x), fy(self.y)),
                           self.radius * dim.scale)
        if self.x > 1600:
            self.x = 0
        if self.y > 900:
            self.y = 0


# Defines fifty star objects (if setting is enabled)
if settings["starfield"]:
    stars = []
    for i in range(200):
        stars.append(
            Star(randint(0, 1600), randint(0, 900),
                 randint(5, 20) / 100,
                 randint(1, 10) / 5))


def background():
    "Draws the background - called every frame"
    screen.fill(GREY(0))
    if settings["starfield"]:
        for i in stars:
            i.tick()


buttons = []


def fx(x):
    return x * dim.scale + dim.left


def fy(y):
    return y * dim.scale + dim.top


class Button:
    "Generic menu button class"

    def __init__(self, src, hover=None):

        self.x = 0
        self.y = 0
        self.x = 0
        self.y = 0
        self.r = 0
        self.scale = 1

        self.text = ""
        self.textSize = 75
        self.textColour = WHITE
        self.textXOffset = 0
        self.textYOffset = 0

        self.show = True
        self.clickCooldown = False

        self.image = pygame.image.load(src)
        if hover != None:
            self.hoverImage = pygame.image.load(hover)
        else:
            self.hoverImage = None

        self.renderedImage = self.image

        self.box = self.image.get_rect(center=(fx(self.x), fy(self.y)))

        buttons.append(self)

    def goto(self, x, y):
        self.x, self.y = x, y
        self.updateBox()
    
    def updateBox(self):
        img1 = pygame.transform.rotozoom(self.renderedImage, 0,self.scale * dim.scale)
        rotImg = centredRotate(img1, self.r, self.x * dim.scale + dim.left,self.y * dim.scale + dim.top)
        self.box = rotImg[1]

    def checkClick(self):
        self.updateBox()
        if not self.show:
            return False

        pygame.event.get()

        mousePos = pygame.mouse.get_pos()

        if not pygame.mouse.get_pressed()[0]:
            self.clickCooldown = False

        if mousePos[0] < (self.box[0] + self.box[2]) and mousePos[0] > (
                self.box[0]) and mousePos[1] < (
                    self.box[1] + self.box[3]) and mousePos[1] > (self.box[1]):
            if self.hoverImage != None:
                self.renderedImage = self.hoverImage
            if pygame.mouse.get_pressed()[0] and not self.clickCooldown:
                self.clickCooldown = True
                pygame.mixer.Sound.play(clickSound)
                return True
        else:
            self.renderedImage = self.image
        return False

    def render(self):
        img1 = pygame.transform.rotozoom(self.renderedImage, 0,self.scale * dim.scale)
        rotImg = centredRotate(img1, self.r, self.x * dim.scale + dim.left,self.y * dim.scale + dim.top)
        screen.blit(rotImg[0], rotImg[1])

        displayText(self.text, self.x + self.textXOffset,self.y + self.textYOffset, self.textSize, self.textColour)

class Switch():
    def __init__(self, src, hover=None):

        self.x = 0
        self.y = 0
        self.x = 0
        self.y = 0
        self.r = 0
        self.scale = 1

        self.on = False
        self.clickCooldown = False

        self.text = ""
        self.textSize = 75
        self.textColour = WHITE
        self.textXOffset = 0
        self.textYOffset = 0

        self.show = True

        self.image = [pygame.image.load(src[0]),pygame.image.load(src[1])]
        if hover != None:
            self.hoverImage = [pygame.image.load(hover[0]),pygame.image.load(hover[1])]
        else:
            self.hoverImage = None

        self.renderedImage = self.image

        self.box = self.image[self.on].get_rect(center=(fx(self.x), fy(self.y)))

        buttons.append(self)

    def goto(self, x, y):
            self.x, self.y = x, y
            self.updateBox()
    
    def updateBox(self):
        img1 = pygame.transform.rotozoom(self.renderedImage[self.on], 0,self.scale * dim.scale)
        rotImg = centredRotate(img1, self.r, self.x * dim.scale + dim.left,self.y * dim.scale + dim.top)
        self.box = rotImg[1]

    def state(self):
        self.updateBox()
        if not self.show:
            return False

        pygame.event.get()

        mousePos = pygame.mouse.get_pos()

        if not pygame.mouse.get_pressed()[0]:
            self.clickCooldown = False

        if mousePos[0] < (self.box[0] + self.box[2]) and mousePos[0] > (
                self.box[0]) and mousePos[1] < (
                    self.box[1] + self.box[3]) and mousePos[1] > (self.box[1]):
            if self.hoverImage != None:
                self.renderedImage = self.hoverImage
            if pygame.mouse.get_pressed()[0] and not self.clickCooldown:
                self.on = False if self.on else True
                pygame.mixer.Sound.play(clickSound)
                self.clickCooldown = True
        else:
            self.renderedImage = self.image
        return self.on
        
    
    def render(self):
        img1 = pygame.transform.rotozoom(self.renderedImage[self.on], 0,self.scale * dim.scale)
        rotImg = centredRotate(img1, self.r, self.x * dim.scale + dim.left,self.y * dim.scale + dim.top)
        screen.blit(rotImg[0], rotImg[1])

        displayText(self.text, self.x + self.textXOffset,self.y + self.textYOffset, self.textSize, self.textColour)

class DeathScreenButton(Button):
    def __init__(self, src, hover=None):

        self.x = 0
        self.y = 0
        self.x = 0
        self.y = 0
        self.r = 0
        self.scale = 1

        self.text = ""
        self.textSize = 75
        self.textColour = WHITE
        self.textXOffset = 0
        self.textYOffset = 0

        self.show = True

        self.image = pygame.image.load(src)
        if hover != None:
            self.hoverImage = pygame.image.load(hover)
        else:
            self.hoverImage = None

        self.renderedImage = self.image

        self.box = self.image.get_rect(center=(fx(self.x), fy(self.y)))

        deathButtons.append(self)

def displayImage(src, x, y, scale, r):
    image = pygame.image.load(src)
    img1 = pygame.transform.rotozoom(image, 0, scale * dim.scale)
    rotImg = centredRotate(img1, r, fx(x), fy(y))
    screen.blit(rotImg[0], rotImg[1])


def textObjects(text, font, colour):
    textSurface = font.render(text, True, colour)
    return textSurface, textSurface.get_rect()


def displayText(text, x, y, size, colour):
    TextSurf, TextRect = textObjects(str(text), font(round(size * dim.scale)),
                                     colour)
    TextRect.center = (x * dim.scale + dim.left, y * dim.scale + dim.top)
    screen.blit(TextSurf, TextRect)


def displayLines(lines, x, y, size, colour, lineSpacing=20):
    for i in range(len(lines)):
        displayText(lines[i], x, y + i * size + lineSpacing, size, colour)


def displayRectangle(x1, y1, w, h, colour):
    pygame.draw.rect(screen, colour,
                     pygame.Rect(fx(x1), fy(y1), w * dim.scale, h * dim.scale))



def forceRatio():
    pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, dim.left, dim.height))
    #pygame.draw.rect(screen, CYAN, pygame.Rect(dim.left - 10, 0, 10, dim.height))
    #pygame.draw.rect(screen, CYAN, pygame.Rect(dim.left - 30, 0, 10, dim.height))
    pygame.draw.rect(screen, BLACK, pygame.Rect(dim.right, 0, dim.left, dim.height))
    #pygame.draw.rect(screen, CYAN, pygame.Rect(dim.right + 10, 0, 10, dim.height))
    #pygame.draw.rect(screen, CYAN, pygame.Rect(dim.right + 30, 0, 10, dim.height))

    pygame.draw.rect(screen, BLACK, pygame.Rect(0, 0, dim.width, dim.top))
    #pygame.draw.rect(screen, CYAN, pygame.Rect(0, dim.top - 10, dim.width, 10))
    #pygame.draw.rect(screen, CYAN, pygame.Rect(0, dim.top - 30, dim.width, 10))
    pygame.draw.rect(screen, BLACK, pygame.Rect(0, dim.bottom, dim.width, dim.top))
    #pygame.draw.rect(screen, CYAN, pygame.Rect(0, dim.bottom + 10, dim.width, 10))
    #pygame.draw.rect(screen, CYAN, pygame.Rect(0, dim.bottom + 30, dim.width, 10))

def menuLoop(screen):
    buttons.clear()
    tick = 0
    skin = 0
    playButton = Button("GUI/big_button.png",
                        hover="GUI/big_button_hover.png")
    playButton.goto(200, 350)
    playButton.textXOffset = -35
    playButton.textYOffset = 5
    playButton.scale = 1.5
    playButton.text = "Play"

    settingsButton = Button("GUI/big_button.png",
                        hover="GUI/big_button_hover.png")
    settingsButton.goto(200, 650)
    settingsButton.textXOffset = -35
    settingsButton.textYOffset = 5
    settingsButton.scale = 1.5
    settingsButton.text = "Settings"

    instructionsButton = Button("GUI/big_button.png",
                                hover="GUI/big_button_hover.png")
    instructionsButton.goto(200, 500)
    instructionsButton.textXOffset = -35
    instructionsButton.textYOffset = 5
    instructionsButton.scale = 1.5
    instructionsButton.textSize = 53
    instructionsButton.text = "Instructions"

    creditsButton = Button("GUI/big_button.png",
                        hover="GUI/big_button_hover.png")
    creditsButton.goto(200, 800)
    creditsButton.textXOffset = -35
    creditsButton.textYOffset = 2
    creditsButton.scale = 1.5
    creditsButton.text = "Credits"
    creditsButton.show = False

    credits = "Created in Pygame by Ben 'Owleee' Bravery,,,With help from:,Seb 'Greeen' Cornell (Maths)".split(
        ",")

    backButton = Button("GUI/big_button.png",
                        hover="GUI/big_button_hover.png")
    backButton.text = "<"
    backButton.show = False
    backButton.textXOffset = 45
    backButton.goto(0, 100)

    displaySpaceship = Button(f"spaceship/{skins[skin]}/display.png")
    displaySpaceship.scale = 0.6

    skinLeft = Button("GUI/arrow.png")
    skinLeft.goto(1400,600)

    skinRight = Button("GUI/arrow.png")
    skinRight.goto(1000,600)
    skinRight.r = 180

    skinRight.show = skinLeft.show = False

    autoFireSwitch = Switch(["GUI/switch_off.png","GUI/switch_on.png"],hover=["GUI/switch_off_hover.png","GUI/switch_on_hover.png"])
    autoFireSwitch.goto(200,250)
    autoFireSwitch.text = "Fire automatically"
    autoFireSwitch.textXOffset = 375
    autoFireSwitch.textSize= 50
    autoFireSwitch.scale= 0.75
    autoFireSwitch.show= False

    invulnerabilitySwitch = Switch(["GUI/switch_off.png","GUI/switch_on.png"],hover=["GUI/switch_off_hover.png","GUI/switch_on_hover.png"])
    invulnerabilitySwitch.goto(200,350)
    invulnerabilitySwitch.text = "Invulnerability (fun/debug - forfeits highscore)"
    invulnerabilitySwitch.textXOffset = 720
    invulnerabilitySwitch.textSize= 50
    invulnerabilitySwitch.scale= 0.75
    invulnerabilitySwitch.show= False

    fpsSwitch = Switch(["GUI/switch_off.png","GUI/switch_on.png"],hover=["GUI/switch_off_hover.png","GUI/switch_on_hover.png"])
    fpsSwitch.goto(200,450)
    fpsSwitch.text = "Display FPS"
    fpsSwitch.textXOffset = 300
    fpsSwitch.textSize= 50
    fpsSwitch.scale= 0.75
    fpsSwitch.show= False
    
    autoFireSwitch.on = settings["auto_fire"]
    invulnerabilitySwitch.on = settings["invulnerability"]
    fpsSwitch.on = settings["fps"]

    splashes = [
        "Feat. The Beauty of Mathematics", "May contain snowballs",
        "Rocks in Space", "BOTTOM TEXT", "Get it?", "Sounds like 'Celeste'",
        "With all-new* 4K* HD* raytraced* graphics", "Etymologically derived!",
        "Free-range!", "Organic!", "Gluten-free!", "Asbestos-free!",
        "Trigonometric!", "Direction and magnitude", "Episode IV: A New Hope",
        "I'm going to ] your family", "Bruhmoment24 approved"
    ]

    keysLeft = Button("GUI/arrow.png")
    keysLeft.goto(1400,750)

    keysRight = Button("GUI/arrow.png")
    keysRight.goto(200,750)
    keysRight.r = 180

    splash = choice(splashes) if randint(1, 3) == 1 else ""

    menuState = "main"

    while True:
        tick += 1

        for event in pygame.event.get():
            if event.type in [
                    pygame.WINDOWRESIZED, pygame.WINDOWSIZECHANGED,
                    pygame.WINDOWMOVED, pygame.WINDOWMAXIMIZED,
                    pygame.WINDOWMINIMIZED, pygame.WINDOWFOCUSGAINED
            ]:
                w, h = screen.get_size()
                dim.update()
                print(w, "x", h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    splash = choice(splashes)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_f:
                    if settings["fullscreen"]:
                        settings["fullscreen"] = False
                        screen = pygame.display.set_mode((1600, 900),
                                                        pygame.RESIZABLE)
                    else:
                        settings["fullscreen"] = True
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    dim.update()

        # MAIN MENU LOOP #
        background()

        if menuState == "main":
            displayText(NAME, 800, 125, 175, WHITE)
            displayText(splash, 800, 225, 25, WHITE)

            playButton.show = settingsButton.show = instructionsButton.show = displaySpaceship.show = True
            autoFireSwitch.show = invulnerabilitySwitch.show = fpsSwitch.show = False
            keysLeft.show = keysRight.show = False
            backButton.show = False


            displaySpaceship.x = cos(3 * tick / 3) * 10 + 1200
            displaySpaceship.y = sin(2 * tick / 3) * 10 + 600
            displaySpaceship.r = sin(2 * tick)
        elif menuState == "instructions":
            displayLines([
                "Welcome to Stellesque!", "Use the controls listed below to move.",
                "Dodge asteroids for as long as possible, using your laser to destroy them.",
                "Be wary of large asteroids as they split into smaller ones!", ""
            ], 800, 100, 30, WHITE)

            keysLeft.show = keysRight.show = True

            if keysLeft.checkClick():
                game.schemeID -= 1
            elif keysRight.checkClick():
                game.schemeID += 1

            if game.schemeID > len(game.controlSchemes) - 1:
                game.schemeID = 0
            elif game.schemeID < 0:
                game.schemeID = len(game.controlSchemes) - 1

            game.controlScheme = game.controlSchemes[game.schemeID]

            if game.controlScheme == "default":
                displayImage("GUI/control_schemes/default.png", 800, 700, 0.5, 0)
                displayText("Space (tap/hold) - shoot laser", 550, 650, 30, WHITE)
                displayText("Left/right arrow - rotate", 1010, 500, 30, WHITE)
                displayText("Up/down arrow - move", 1010, 450, 30, WHITE)
            elif game.controlScheme == "WASD":
                displayImage("GUI/control_schemes/WASD.png", 800, 700, 0.5, 0)
                displayText("W", 1600-1010, 620, 100, WHITE)
                displayText("S", 1600-1010, 780, 100, WHITE)
                displayText("A", 1600-1010-160, 780, 100, WHITE)
                displayText("D", 1600-1010+160, 780, 100, WHITE)

                displayText("Space (tap/hold) - shoot laser", 1600-550, 650, 30, WHITE)
                displayText("A/D - rotate", 1600-1010, 500, 30, WHITE)
                displayText("W/S - move", 1600-1010, 450, 30, WHITE)
            elif game.controlScheme == "ASPL":
                displayImage("GUI/control_schemes/ASPL.png", 800, 700, 0.5, 0)
                displayText("P", 1200-15, 620, 100, WHITE)
                displayText("L", 1200-65, 780, 100, WHITE)

                displayText("S", 1600-1010-15, 780, 100, WHITE)
                displayText("A", 1600-1010-160-15, 780, 100, WHITE)

                displayText("Space (tap/hold) - shoot laser", 1600-750, 600, 30, WHITE)
                displayText("A/S - rotate", 495, 650, 30, WHITE)
                displayText("P/L - move", 1200-(15+65)/2, 500, 30, WHITE)


        elif menuState == "settings":
            autoFireSwitch.show = invulnerabilitySwitch.show = fpsSwitch.show = True
            settings["auto_fire"] = autoFireSwitch.state()
            settings["invulnerability"] = invulnerabilitySwitch.state()
            settings["fps"] = fpsSwitch.state()
            displayText("Change controls under Instructions",800,750,40,WHITE)

        if playButton.checkClick():
            mainLoop()
        elif instructionsButton.checkClick():
            playButton.show = settingsButton.show = instructionsButton.show = displaySpaceship.show = False
            backButton.show = True
            menuState = "instructions"
        elif settingsButton.checkClick():
            menuState = "settings"
            playButton.show = settingsButton.show = instructionsButton.show = displaySpaceship.show = False
            backButton.show = True

        elif skinRight.checkClick():
            skin += 1
            if skin < 0:
                skin = len(skins)-1
            displaySpaceship.image = pygame.image.load(f"spaceship/{skins[skin]}/display_spaceship.png")

        elif skinLeft.checkClick():
            skin -= 1
            if skin > len(skins)-1:
                skin = 0
            displaySpaceship.image = pygame.image.load(f"spaceship/{skins[skin]}/display_spaceship.png")

        if backButton.checkClick():
            menuState = "main"
            saveData()

        for i in buttons:
            if i.show:
                i.render()
        

        forceRatio()
        pygame.display.flip()

asteroids = []
debrises = []


class Spawner:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.cooldown = 40
        # Debug feature
        self.image = pygame.image.load("asteroids/asteroid.png")
        self.scale = 0.3

    def spawn(self):
        asteroid = Asteroid("asteroids/asteroid.png")
        asteroid.speed = randint(10, 25) / 5 + self.cooldown / 240
        asteroid.scale = randint(10, 50) / 100
        
        asteroids.append(asteroid)

        side = randint(1, 4)
        if side == 1:  # TOP
            self.x = randint(0, 1600)
            self.y = -asteroid.scale*175
            self.r = randint(180 - 45, 180 + 45)
        elif side == 2:  # LEFT
            self.x = -asteroid.scale*175
            self.y = randint(0, 900)
            self.r = randint(-90 - 45, -90 + 45)
        elif side == 3:  # RIGHT
            self.x = 1600 + asteroid.scale*175
            self.y = randint(0, 900)
            self.r = randint(90 - 45, 90 + 45)
        else:  # BOTTOM
            self.x = randint(0, 1600)
            self.y = 900 + asteroid.scale*175
            self.r = randint(-45, 45)

        asteroid.goto(self.x, self.y)
        asteroid.setRotation(self.r)

    def spawnAt(self, x, y, r, speed, scale):
        "Debug function"
        asteroid = Asteroid("asteroids/asteroid.png")
        asteroid.goto(x, y)
        asteroid.setRotation(r)
        asteroid.speed = speed
        asteroid.scale = scale
        asteroids.append(asteroid)

    def render(self):
        img1 = pygame.transform.rotozoom(self.image, 0, self.scale * dim.scale)
        rotImg = centredRotate(img1, 0, self.x * dim.scale + dim.left,
                               self.y * dim.scale + dim.top)
        screen.blit(rotImg[0], rotImg[1])


class Asteroid(GameObj):

    def define(self):
        self.scale = 1
        self.radius = self.scale * 175
        self.iFrames = 10

    def velocity(self):
        pass

    def tick(self):
        self.iFrames = max(self.iFrames - 1, 0)
        self.x -= self.speed * sin(self.r)*game.dt
        self.y -= self.speed * cos(self.r)*game.dt
        self.radius = self.scale * 175

        if self.x < -self.radius * 2 or self.x > 1600 + self.radius * 2 or self.y < -self.radius * 2 or self.y > 900 + self.radius * 2:
            try:
                objects.remove(self)
                asteroids.remove(self)
            except:
                pass
        self.checkCollisions()

    def checkCollisions(self):
        if self.iFrames > 0:
            return
        for i in projectiles:
            if ssqrt((i.x - self.x)**2 +
                     (i.y - self.y)**2) < i.radius + self.radius:
                i.pierce[1] += 1
                if i.pierce[1] == i.pierce[0]:
                  objects.remove(i)
                  projectiles.remove(i)
                game.score += math.ceil(self.radius / 50)
                self.destroy()
                break

    def destroy(self):
        pygame.mixer.Sound.play(choice(explosionSound))
        if self.radius > 50:
            for j in range(randint(2, 3)):
                asteroid = Asteroid("asteroids/asteroid.png")
                asteroid.goto(self.x, self.y)
                asteroid.setRotation(self.r + randint(-45, 45))
                asteroid.speed = self.speed / (randint(5, 15) / 10)
                asteroid.scale = self.scale / (randint(15, 20) / 10)
                asteroid.goto(self.x + randint(-20, 20),
                              self.y + randint(-20, 20))
                asteroids.append(asteroid)
        else:
            if settings["fragments"]:
                for j in range(randint(3, 5)):
                    debris = Debris(f"asteroids/{randint(1,5)}.png")
                    debris.scale = self.scale
                    debris.goto(self.x, self.y)
                    debris.r = randint(0,360)
                    debris.xVel = randint(-10, 10) / 10
                    debris.yVel = randint(-10, 10) / 10
                    debrises.append(debris)
        try:
            objects.remove(self)
            asteroids.remove(self)
        except:
            pass


class Debris(GameObj):

    def define(self):
        self.fadeSpeed = 0.001

    def tick(self):
        self.scale -= self.fadeSpeed*game.dt
        if self.scale < 0:
            try:
                objects.remove(self)
                debrises.remove(self)
            except:
                pass

    def velocity(self):
        self.x += self.xVel*game.dt
        self.y += self.yVel*game.dt
        self.xVel *= 0.99
        self.yVel *= 0.99



def deadLoop():

    ship.show = False
    ship.updateChildren()

    restartButton = DeathScreenButton("GUI/middle_button.png",hover="GUI/middle_button_hover.png")
    restartButton.goto(800,550)
    restartButton.text = "Restart"
    restartButton.scale = 1.5

    menuButton = DeathScreenButton("GUI/middle_button.png",hover="GUI/middle_button_hover.png")
    menuButton.goto(800,750)
    menuButton.text = "Main Menu"
    menuButton.textSize = 65
    menuButton.scale = 1.5

    hs = False

    datatxt = open("data.txt","r")

    removeNewlines = lambda l: [i.replace("\n","") for i in l]

    data = removeNewlines(datatxt.readlines())

    highscore = int(data[0])

    if game.score > highscore and not settings["invulnerability"]:
        highscore = game.score
        hs= True

    saveData(hs=highscore)

    for i in range(11):
        debris = Debris(f"spaceship/shards/{i}.png")
        debris.scale = ship.scale
        debris.goto(ship.x, ship.y)
        debris.r = randint(0,360)
        debris.xVel = ship.xVel+randint(-30, 30)/5
        debris.yVel = ship.yVel+randint(-30, 30)/5
        debrises.append(debris)

    while True:
        for event in pygame.event.get():
            if event.type in [
                    pygame.WINDOWRESIZED, pygame.WINDOWSIZECHANGED,
                    pygame.WINDOWMOVED, pygame.WINDOWMAXIMIZED,
                    pygame.WINDOWMINIMIZED, pygame.WINDOWFOCUSGAINED
            ]:
                w, h = screen.get_size()
                dim.update()
                print(w, "x", h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

        if menuButton.checkClick():
            menuLoop(screen)

        if restartButton.checkClick():
            mainLoop()

        for i in asteroids:
            i.tick( )

        for i in debrises:
            i.tick()
            i.velocity()

        background()

        for i in objects[::-1]:
            i.render() 

        #displayImage("GUI/overlay.png",800,450,1,0)

        displayText("You died!",800,250,200,WHITE)
        if hs and not settings["invulnerability"]:
            displayText(f"NEW HIGHSCORE!: {game.score}",800,400,75,(255,255,0))
        else:
            displayText(f"Score: {game.score}",800,400,75,WHITE)
            displayText(f"Highscore: {highscore}",800,850,50,WHITE)

        for i in deathButtons:
            i.render()

        forceRatio()

        pygame.display.flip()
        clock.tick(tickspeed)


def mainLoop():
    objects.clear()
    asteroids.clear()
    hitboxes.clear()
    spawner = Spawner()

    skin = 0

    tick = 0

    # Define spaceship
    global ship
    ship = Spaceship(f"spaceship/{skins[skin]}/body.png")
    ship.goto(800, 450)
    ship.scale = 0.2
    game.score = 0

    mainHitbox = Hitbox()
    mainHitbox.radius = 18
    mainHitbox.yOffset = -50
    ship.children.append(mainHitbox)
    frontHitbox = Hitbox()
    frontHitbox.radius = 5
    frontHitbox.yOffset = 150
    ship.children.append(frontHitbox)

    # Engine flame objects
    bigBooster = GameObj("spaceship/big_booster.png")
    leftBooster = GameObj("spaceship/booster.png")
    rightBooster = GameObj("spaceship/booster.png")

    ship.children.append(bigBooster)
    bigBooster.yOffset = -200

    ship.children.append(leftBooster)
    leftBooster.yOffset = -220
    leftBooster.xOffset = -130

    ship.children.append(rightBooster)
    rightBooster.yOffset = -220
    rightBooster.xOffset = 130

    # Weapon(s?)
    basicBlaster = Weapon("spaceship/blaster.png")
    basicBlaster.projectile = BasicLaser
    basicBlaster.cooldown = 20
    ship.children.append(basicBlaster)
    basicBlaster.yOffset = 180
    basicBlaster.scaleOffset = 0.8
    ship.weapon = basicBlaster

    # Sight
    """
    sight = GameObj("spaceship/laser_sight.png")
    sight.yOffset = 800
    sight.scaleOffset = 0.5
    ship.children.append(sight)
    """

    shootCooldown = 0
    spawnCooldown = 0
    regenCooldown = 0

    overflowR = 60

    ship.health = 100

    while True:
        # GAME LOOP #
        game.dt = 1

        shootCooldown -= 1
        spawnCooldown -= 1

        # Window resize
        for event in pygame.event.get():
            if event.type in [pygame.WINDOWRESIZED, pygame.WINDOWSIZECHANGED]:
                w = event.x
                h = event.y
                dim.update()
                print(w, "x", h)

        # Controls
        keys = pygame.key.get_pressed()

        if keys[controls[game.controlScheme]["cw"]] and keys[controls[game.controlScheme]["acw"]]:
            pass
        elif keys[controls[game.controlScheme]["acw"]]:
            ship.rotate(0.5)
        elif keys[controls[game.controlScheme]["cw"]]:
            ship.rotate(-0.5)
        if keys[controls[game.controlScheme]["forward"]]:
            ship.forward(0.3)
        elif keys[controls[game.controlScheme]["back"]]:
            ship.forward(-0.08)
        if (keys[pygame.K_SPACE] or settings["auto_fire"]) and shootCooldown < 0:
            ship.weapon.attack()
            shootCooldown = ship.weapon.cooldown
        if keys[pygame.K_RIGHTBRACKET]:
            ship.health = 0
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            quit()

        # Screen overflowing
        if ship.y < -overflowR:
            ship.y = 900 + overflowR
        elif ship.y > 900 + overflowR:
            ship.y = -overflowR
        if ship.x < -overflowR:
            ship.x = 1600 + overflowR
        elif ship.x > 1600 + overflowR:
            ship.x = -overflowR

        # Engines react to velocity (only if setting is enabled)
        if settings["engines"]:
            bigBooster.scaleOffset = 1.2 * ssqrt(ship.forwardVelocity / 5)

            leftBooster.scaleOffset = (1.2 * ssqrt(ship.rVel / 5) if ship.rVel < 0
                                    else 0) + 0.8 * bigBooster.scaleOffset
            rightBooster.scaleOffset = (1.2 * ssqrt(ship.rVel / 5) if ship.rVel > 0
                                        else 0) + 0.8 * bigBooster.scaleOffset

        if spawnCooldown < 0:
            #spawner.spawnAt(800, 200, 0, 0, 0.25)
            spawner.spawn()
            spawnCooldown = spawner.cooldown
            spawner.cooldown = max(12,-1.3*ssqrt(game.score)+40)

        for i in projectiles:
            i.tick()

        for i in asteroids:
            i.tick()

        for i in debrises:
            i.tick()

        for i in hitboxes:
            c = i.checkCollision()
            if c[0]:
                if ship.iFrames == 0 and not settings["invulnerability"]:
                    ship.health -= c[1].radius / 2
                    pygame.mixer.Sound.play(hurtSound)

                    for i in range(randint(1,3)):
                        debris = Debris(f"spaceship/shards/{randint(0,10)}.png")
                        debris.scale = ship.scale
                        debris.goto(ship.x, ship.y)
                        debris.r = randint(0,360)
                        debris.xVel = ship.xVel+randint(-30, 30)/5
                        debris.yVel = ship.yVel+randint(-30, 30)/5
                        debrises.append(debris)

                    ship.iFrames = 30
                    regenCooldown = 120
                c[1].destroy()
                break

        # Death
        if math.floor(ship.health) <= 0:
            deadLoop()

        ship.iFrames = max(0, ship.iFrames - 1)

        # "PHYSICS" CODE #
        for i in objects:
            i.velocity()
        # RENDER CODE #
        if not settings["paint"]:
            background()

        for i in objects[::-1]:
            i.render() 

        #for i in hitboxes:
        #    i.draw()

        displayText(game.score, 100, 100, 50, WHITE)
        fps = clock.get_fps()

        if settings["fps"]:
            displayText(f"{round(fps)} FPS", 1500, 100, 50, WHITE)

        if ship.health < 15:
            healthColour = (255, 0, 0)
        elif ship.health < 50:
            healthColour = (255, 255, 0)
        else:
            healthColour = CYAN

        regenCooldown = max(regenCooldown - 1, 0)
        if regenCooldown == 0:
            ship.health = min(100, ship.health + 0.02)

        displayRectangle(570, 860, 460, 24, GREY(50))
        displayRectangle(570, 860, 460 * (ship.health / 100), 24, healthColour)
        displayImage("GUI/healthbar.png", 800, 870, 1, 0)
        displayText(round(ship.health), 800, 870, 50, BLACK)
        """
        for i in projectiles:
            try:
                pygame.draw.line(screen, WHITE, (fx(i.x), fy(i.y)),
                                (fx(i.target.x), fy(i.target.y)))
            except:
                pass
        """

        forceRatio()

        pygame.display.flip()
        clock.tick(tickspeed)
        tick += 1

menuLoop(screen)