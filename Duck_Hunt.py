import pygame
import random

pygame.init()
pygame.mixer.init()

#variabile globale
WIDTH = 1280
HEIGHT = 720
FPS = 60
FramePerSec = pygame.time.Clock()

#seteaza dimensiunea ferestrei care va rula jocul
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen_rect = screen.get_rect()

running = True
game_start = False
menu = True
retry_menu = False
game_win = False
delay_completed = False
over_sound = False
win_sound = False
music_on = False
music_playing = False

current_level = 0 #level de inceput

start_time = pygame.time.get_ticks()
DIRECTIONS = ["left", "rightUpThenStraight", "rightUp", "leftThenRight", "right", "leftUpThenStraight", "rightThenLeft", "leftUp"]
spawn_time = 0
spawn_delay = 3000

#sunete
shoot_sound = pygame.mixer.Sound("sounds\gun_fire.mp3")
game_over_sound = pygame.mixer.Sound("sounds\lose.mp3")
game_win_sound = pygame.mixer.Sound("sounds\win.mp3")
level_up_sound = pygame.mixer.Sound("sounds\level_up.mp3")

#viteza ratelor dupa pixeli
bD_speed_LR = 5
bD_speed_Up_LR = (5, 2.5)

blD_speed_LR = 6
blD_speed_Up_LR = (6, 3)

rD_speed_LR = 7
rD_speed_Up_LR = (7, 3.5)

b_distance_Count = 0
bl_distance_Count = 0
r_distance_Count = 0

SPEED = 0.8

#viteza frame-urilor
FRAME_SPEED = 0.15

#denumirea aplicatiei
pygame.display.set_caption("Duck Hunt")

#setarea unei imagini de background
sky = pygame.image.load("visual\sky.png").convert_alpha()
background = pygame.image.load("visual\\background.png").convert_alpha()
tree = pygame.image.load("visual\\tree.png").convert_alpha()

#setarea imaginilor de background la dimensiunile curente
sky = pygame.transform.scale(sky, (WIDTH, HEIGHT))
blackground = pygame.transform.scale(background, (WIDTH, HEIGHT))

#setarea unui cursor customizat
custom_cursor = pygame.image.load('visual\\target.png').convert_alpha()
custom_cursor = pygame.transform.scale(custom_cursor, (40, 40)) #redimensionarea cursorului
#------------------------------------------------------------------#

#--------------------clasa de baza--------------------#
class Sprite(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height

        self.can_move = True
        self.mouse_pressed = False
        self.last_click_time = 0
        self.position_set = False
        self.frame_set = False
        self.count = 0
        self.is_shot = False
             
    def set_position(sprite, w, h):
        sprite.rect.x = w
        sprite.rect.y = h        

    def moveLeft(self, pixels_x):
        self.rect.x -= pixels_x
        
    def moveRight(self, pixels_x):
        self.rect.x += pixels_x
        
    def moveLeftUp(self, pixels_x, pixels_y):
        self.rect.x -= pixels_x
        self.rect.y -= pixels_y
        
    def moveRightUp(self, pixels_x, pixels_y):
        self.rect.x += pixels_x
        self.rect.y -= pixels_y

    def off_screen(self):
        return self.rect.x < -self.rect.width or self.rect.y < -self.rect.height or self.rect.x > WIDTH or self.rect.y > HEIGHT
    
    def verify_off_screen(self):
        global score_value
        if self.off_screen() and not self.is_shot:
            self.can_move = False
            self.kill()
            if score_value > 1:
                score_value -= 2
            #print('DUCK IS OUT OF SCREEN')
                
    def duck_action(self, frame_list, left_x_y, right_x_y, leftUp_x_y, rightUp_x_y, first_frame, frame_limit, shot_frame, died_frame, left_speed, right_speed, lrUp_speed_x_y):
        if not self.position_set:
            if self.direction == "left" or self.direction == "leftThenRight":
                Sprite.set_position(self, WIDTH, random.randint(*left_x_y)) #seteaza pozitia de pornire
                self.current_frame = first_frame #seteaza primul frame de start
                self.position_set = True #marcheaza pozitia ca setata
            elif self.direction == "right" or self.direction == "rightThenLeft":
                Sprite.set_position(self, 0.1, random.randint(*right_x_y))
                self.current_frame = first_frame
                self.position_set = True
            elif self.direction == "leftUp" or self.direction == "leftUpThenStraight":
                Sprite.set_position(self, WIDTH, random.randint(*leftUp_x_y))
                self.current_frame = first_frame
                self.position_set = True
            elif self.direction == "rightUp" or self.direction == "rightUpThenStraight":
                Sprite.set_position(self, 0.1, random.randint(*rightUp_x_y))
                self.current_frame = first_frame
                self.position_set = True

        if self.can_move:
            self.current_frame += FRAME_SPEED
        
            if self.current_frame >= frame_limit:
                self.current_frame = first_frame
            
            self.image = frame_list[int(self.current_frame)]
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
            if self.direction == "left" or self.direction == "leftThenRight":
                self.moveLeft(left_speed)
            elif self.direction == "right" or self.direction == "rightThenLeft":
                self.moveRight(right_speed)
            elif self.direction == "leftUp" or self.direction == "leftUpThenStraight":
                self.moveLeftUp(*lrUp_speed_x_y)
            elif self.direction == "rightUp" or self.direction == "rightUpThenStraight":
                self.moveRightUp(*lrUp_speed_x_y)
        
        if self.mouse_pressed:
            current_time = pygame.time.get_ticks()
            self.image = frame_list[shot_frame]
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            if current_time - self.last_click_time > 600:
                self.image = frame_list[died_frame]
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                self.can_move = False
                self.rect.y += 8
                
    def diffDirection(self, frame_list, first_frame, frame_limit, shot_frame, died_frame, left_speed, right_speed):  
        if not self.frame_set:
           if self.direction == "leftThenRight":
                self.current_frame = first_frame
                self.frame_set = True
           elif self.direction == "rightThenLeft":
                self.current_frame = first_frame
                self.frame_set = True
           elif self.direction == "leftUpThenStraight":
                self.current_frame = first_frame
                self.frame_set = True
           elif self.direction == "rightUpThenStraight":
                self.current_frame = first_frame
                self.frame_set = True
        
        if self.can_move:   
            self.current_frame += FRAME_SPEED
            if self.current_frame >= frame_limit:
                self.current_frame = first_frame
            
            self.image = frame_list[int(self.current_frame)]
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            
            if self.direction == "leftThenRight":
                self.moveRight(right_speed)
            elif self.direction == "rightThenLeft":
                self.moveLeft(left_speed)
            elif self.direction == "leftUpThenStraight":
                self.moveLeft(left_speed)
            elif self.direction == "rightUpThenStraight":
                self.moveRight(right_speed)
                
        if self.mouse_pressed:
            current_time = pygame.time.get_ticks()
            self.image = frame_list[shot_frame]
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            if current_time - self.last_click_time > 600:
                self.image = frame_list[died_frame]
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
                self.can_move = False
                self.rect.y += 8
                
    @classmethod
    def remove_sprites(cls, game_start, sprite_list):
        if not game_start:
            for sprite in sprite_list.sprites():
                sprite.kill()
            #sprite_list.empty()

#--------------------clasele derivate--------------------#
#clasa ratelor negre
class Black_Duck(Sprite):
    def __init__(self, width, height, direction):
        super().__init__(width, height)
        self.width = width
        self.height = height
        self.direction = direction

        #frame-urile ratei negre
        self.black_duck_frames = []
        self.black_duck_frames.append(pygame.image.load("bDuck\left1.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\left2.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\left3.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\\right1.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\\right2.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\\right3.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\leftUp1.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\leftUp2.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\leftUp3.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\\rightUp1.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\\rightUp2.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\\rightUp3.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\duckDie.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\leftDeadDuck.png").convert_alpha())
        self.black_duck_frames.append(pygame.image.load("bDuck\\rightDeadDuck.png").convert_alpha())       
       
        self.current_frame = 0
        self.image = self.black_duck_frames[self.current_frame]
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()

    def update(self):
        #print(f"{self.direction}: {self.rect.x, self.rect.y}")
        Sprite.verify_off_screen(self)

        if self.direction == "left":
            self.duck_action(self.black_duck_frames, (250, 350), None, None, None, 0, 2, 12, 13, bD_speed_LR, None, None)
        elif self.direction == "right":
            self.duck_action(self.black_duck_frames, None, (320, 400), None, None, 3, 5, 12, 14, None, bD_speed_LR, None)
        elif self.direction == "leftUp":
            self.duck_action(self.black_duck_frames, None, None, (500, 670), None, 6, 8, 12, 13, None, None, bD_speed_Up_LR)
        elif self.direction == "rightUp":
            self.duck_action(self.black_duck_frames, None, None, None, (500, 670), 9, 11, 12, 14, None, None, bD_speed_Up_LR)
        elif self.direction == "leftThenRight":
            if self.count < (97 - b_distance_Count):
                self.duck_action(self.black_duck_frames, (250, 350), None, None, None, 0, 2, 12, 13, bD_speed_LR, None, None)
                self.count += 1
            else:
                self.diffDirection(self.black_duck_frames, 3, 5, 12, 14, None, bD_speed_LR)
        elif self.direction == "rightThenLeft":
            if self.count < (99 - b_distance_Count):
                self.duck_action(self.black_duck_frames, None, (320, 400), None, None, 3, 5, 12, 14, None, bD_speed_LR, None)
                self.count += 1
            else:
                self.diffDirection(self.black_duck_frames, 0, 2, 12, 13, bD_speed_LR, None)
        elif self.direction == "leftUpThenStraight":
            if self.count < (95 - b_distance_Count):
                self.duck_action(self.black_duck_frames, None, None, (500, 670), None, 6, 8, 12, 13, None, None, bD_speed_Up_LR)
                self.count += 1
            else:
                self.diffDirection(self.black_duck_frames, 0, 2, 12, 13, bD_speed_LR, None)
        elif self.direction == "rightUpThenStraight":
            if self.count < (96 - b_distance_Count):
                self.duck_action(self.black_duck_frames, None, None, None, (500, 670), 9, 11, 12, 14, None, None, bD_speed_Up_LR)
                self.count += 1
            else:
                self.diffDirection(self.black_duck_frames, 3, 5, 12, 14, None, bD_speed_LR)
    
    @classmethod
    def spawn_black_duck(cls):
        b_direction = DIRECTIONS[random.randint(0, len(DIRECTIONS) - 1)]
        #print(b_direction)
        bDuck = cls(65, 65, b_direction)
        
        black_sprites_list.add(bDuck)
        sprites_list.add(black_sprites_list)
        #print('+ rata neagra')
    
        black_sprites_list.update()
        black_sprites_list.draw(screen)   

#clasa ratelor albastre
class Blue_Duck(Sprite):
    def __init__(self, width, height, direction):
        super().__init__(width, height)
        self.width = width
        self.height = height
        self.direction = direction

        #frame-urile ratei albastre
        self.blue_duck_frames = []
        self.blue_duck_frames.append(pygame.image.load("blDuck\left1.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\left2.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\left3.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\\right1.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\\right2.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\\right3.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\leftUp1.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\leftUp2.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\leftUp3.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\\rightUp1.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\\rightUp2.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\\rightUp3.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\duckDie.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\leftDeadDuck.png").convert_alpha())
        self.blue_duck_frames.append(pygame.image.load("blDuck\\rightDeadDuck.png").convert_alpha())
        
        self.current_frame = 0
        self.image = self.blue_duck_frames[self.current_frame]
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()

    def update(self):
        #print(f"{self.direction}: {self.rect.x, self.rect.y}")
        Sprite.verify_off_screen(self)

        if self.direction == "left":
            self.duck_action(self.blue_duck_frames, (230, 310), None, None, None, 0, 2, 12, 13, blD_speed_LR, None, None)
        elif self.direction == "right":
            self.duck_action(self.blue_duck_frames, None, (250, 350), None, None, 3, 5, 12, 14, None, blD_speed_LR, None)
        elif self.direction == "leftUp":
            self.duck_action(self.blue_duck_frames, None, None, (400, 570), None, 6, 8, 12, 13, None, None,  blD_speed_Up_LR)
        elif self.direction == "rightUp":
            self.duck_action(self.blue_duck_frames, None, None, None, (400, 570), 9, 11, 12, 14, None, None, blD_speed_Up_LR)
        elif self.direction == "leftThenRight":
            if self.count < (95 - bl_distance_Count):
                self.duck_action(self.blue_duck_frames, (230, 310), None, None, None, 0, 2, 12, 13, blD_speed_LR, None, None)
                self.count += 1
            else:
                self.diffDirection(self.blue_duck_frames, 3, 5, 12, 14, None, blD_speed_LR)
        elif self.direction == "rightThenLeft":
            if self.count < (98 - bl_distance_Count):
                self.duck_action(self.blue_duck_frames, None, (250, 350), None, None, 3, 5, 12, 14, None, blD_speed_LR, None)
                self.count += 1
            else:
                self.diffDirection(self.blue_duck_frames, 0, 2, 12, 13, blD_speed_LR, None)
        elif self.direction == "leftUpThenStraight":
            if self.count < (94 - bl_distance_Count):
                self.duck_action(self.blue_duck_frames, None, None, (400, 570), None, 6, 8, 12, 13, None, None, blD_speed_Up_LR)
                self.count += 1
            else:
                self.diffDirection(self.blue_duck_frames, 0, 2, 12, 13, blD_speed_LR, None)
        elif self.direction == "rightUpThenStraight":
            if self.count < (95 - bl_distance_Count):
                self.duck_action(self.blue_duck_frames, None, None, None, (400, 570), 9, 11, 12, 14, None, None, blD_speed_Up_LR)
                self.count += 1
            else:
                self.diffDirection(self.blue_duck_frames, 3, 5, 12, 14, None, blD_speed_LR)
            
    @classmethod
    def spawn_blue_duck(cls):
        bl_direction = DIRECTIONS[random.randint(0, len(DIRECTIONS) - 1)]
        #print(bl_direction)
        blDuck = cls(65, 65, bl_direction)
        
        blue_sprites_list.add(blDuck)
        sprites_list.add(blue_sprites_list)
        #print('+ rata albastra')
    
        blue_sprites_list.update()
        blue_sprites_list.draw(screen)   

#clasa ratelor rosii    
class Red_Duck(Sprite):
    def __init__(self, width, height, direction):
        super().__init__(width, height)
        self.width = width
        self.height = height
        self.direction = direction
        
         #frame-urile ratei albastre
        self.red_duck_frames = []
        self.red_duck_frames.append(pygame.image.load("rDuck\left1.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\left2.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\left3.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\\right1.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\\right2.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\\right3.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\leftUp1.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\leftUp2.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\leftUp3.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\\rightUp1.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\\rightUp2.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\\rightUp3.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\duckDie.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\leftDeadDuck.png").convert_alpha())
        self.red_duck_frames.append(pygame.image.load("rDuck\\rightDeadDuck.png").convert_alpha())
        
        self.current_frame = 0
        self.image = self.red_duck_frames[self.current_frame]
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        
    def update(self):
        #print(f"{self.direction}: {self.rect.x, self.rect.y}")
        Sprite.verify_off_screen(self)

        if self.direction == "left":
            self.duck_action(self.red_duck_frames, (150, 230), None, None, None, 0, 2, 12, 13, rD_speed_LR, None, None)
        elif self.direction == "right":
            self.duck_action(self.red_duck_frames, None, (180, 250), None, None, 3, 5, 12, 14, None, rD_speed_LR, None)
        elif self.direction == "leftUp":
            self.duck_action(self.red_duck_frames, None, None, (400, 520), None, 6, 8, 12, 13, None, None, rD_speed_Up_LR)
        elif self.direction == "rightUp":
            self.duck_action(self.red_duck_frames, None, None, None, (400, 520), 9, 11, 12, 14, None, None, rD_speed_Up_LR)
        elif self.direction == "leftThenRight":
            if self.count < 85 - r_distance_Count:
                self.duck_action(self.red_duck_frames, (150, 230), None, None, None, 0, 2, 12, 13, rD_speed_LR, None, None)
                self.count += 1
            else:
                self.diffDirection(self.red_duck_frames, 3, 5, 12, 14, None, rD_speed_LR)
        elif self.direction == "rightThenLeft":
            if self.count < (90 - r_distance_Count):
                self.duck_action(self.red_duck_frames, None, (180, 250), None, None, 3, 5, 12, 14, None, rD_speed_LR, None)
                self.count += 1
            else:
                self.diffDirection(self.red_duck_frames, 0, 2, 12, 13, rD_speed_LR, None)
        elif self.direction == "leftUpThenStraight":
            if self.count < (90 - r_distance_Count):
                self.duck_action(self.red_duck_frames, None, None, (400, 570), None, 6, 8, 12, 13, None, None, rD_speed_Up_LR)
                self.count += 1
            else:
                self.diffDirection(self.red_duck_frames, 0, 2, 12, 13, rD_speed_LR, None)
        elif self.direction == "rightUpThenStraight":
            if self.count < (91 - r_distance_Count):
                self.duck_action(self.red_duck_frames, None, None, None, (400, 570), 9, 11, 12, 14, None, None, rD_speed_Up_LR)
                self.count += 1
            else:
                self.diffDirection(self.red_duck_frames, 3, 5, 12, 14, None, rD_speed_LR)
            
    @classmethod
    def spawn_red_duck(cls):
        r_direction = DIRECTIONS[random.randint(0, len(DIRECTIONS) - 1)]
        #print(r_direction)
        rDuck = cls(65, 65, r_direction)
        
        red_sprites_list.add(rDuck)
        sprites_list.add(red_sprites_list)
        #print('+ rata rosie')
    
        red_sprites_list.update()
        red_sprites_list.draw(screen)   
#------------------------------------------------------------#

#grupul de baza sprites
sprites_list = pygame.sprite.Group()

#grupurile pentru fiecare tip de rata
black_sprites_list = pygame.sprite.Group()
blue_sprites_list = pygame.sprite.Group()
red_sprites_list = pygame.sprite.Group()

#------------------------------------------------------------#

#clasa pentru configurarea nivelelor  
class Level:
    def __init__(self, required_count = 0):
        self.required_count = required_count
        self.current_count = 0

    def reqShots(self):
        return self.required_count

    def currShots(self):
        return self.current_count
    
    def resetCount(self):
        self.current_count = 0

    def duck_shot(self):
        self.current_count += 1

    def is_level_completed(self):
        return self.current_count >= self.required_count

    def generate_random_ducks(self, nr_of_ducks):
            duck_types = [
                Black_Duck.spawn_black_duck,
                Blue_Duck.spawn_blue_duck,
                Red_Duck.spawn_red_duck
            ]
            for _ in range(nr_of_ducks):
                selected_duck = duck_types[random.randint(0, len(duck_types) - 1)]
                selected_duck()
                       
#-------------------------------------------------------#

#numarul de levele si numarul de rate ce trebuie impuscate    
levels = [
    Level(10),
    Level(15),
    Level(20),
    Level(25)
]

#afisare level
def display_level():
    x, y = 1170, 15
    c_lvl = font.render(f"Level {current_level + 1}/{len(levels)}", True, "white")
    lvl = font.render(f"{str(levels[current_level].currShots())} / {str(levels[current_level].reqShots())}", True, "white")
    screen.blit(c_lvl, (x, y))
    screen.blit(lvl, (x + 25, y + 35))

#functie pentru schimbarea conditiilor la atingerea unui nou nivel (marirea dificultatii)
def new_conditions(speed):
    global bD_speed_LR, blD_speed_LR, rD_speed_LR, bD_speed_Up_LR, blD_speed_Up_LR, rD_speed_Up_LR, spawn_delay, b_distance_Count, bl_distance_Count, r_distance_Count
    bD_speed_LR += speed
    blD_speed_LR += speed
    rD_speed_LR += speed
    bD_speed_Up_LR = tuple(e + speed for e in bD_speed_Up_LR)
    blD_speed_Up_LR = tuple(e + speed for e in blD_speed_Up_LR)
    rD_speed_Up_LR = tuple(e + speed for e in rD_speed_Up_LR)
    spawn_delay -= 600
    b_distance_Count += 4
    bl_distance_Count += 7
    r_distance_Count += 11

#---------------afisare scor---------------#
score_value = 0
font = pygame.font.Font('TextFont\BebasNeue-Regular.ttf', 32)

def display_score():
    #x, y = 1120, 670
    x, y = 670, 670
    score = font.render(f"Score: {str(score_value)}", True, "white")
    screen.blit(score, (x, y))

#---------------afisare gloante---------------#
MAX_BULLETS = 6
BULLETS = 6
ammo_icon = pygame.image.load("visual\\bullet.png").convert_alpha()
ammo_icon = pygame.transform.scale(ammo_icon, (18, 38))

def display_ammo():
    #x, y = 50, 668
    x, y = 490, 668
    spacing = 10
    for _ in range(BULLETS):
        screen.blit(ammo_icon, (x, y))
        x += ammo_icon.get_width() + spacing

#--------------------butoane-----------------------#
start_img = pygame.image.load("visual\\start_button.png").convert_alpha()
start_img = pygame.transform.scale(start_img, (150, 70))
reset_img = pygame.image.load("visual\\reset_button.png").convert_alpha()
reset_img = pygame.transform.scale(reset_img, (150, 70))
exit_img = pygame.image.load("visual\exit_button.png").convert_alpha()
exit_img = pygame.transform.scale(exit_img, (150, 70))

start_button = start_img.get_rect()
start_button.centerx = screen_rect.centerx
start_button.y = 300

exit_button = exit_img.get_rect()
exit_button.centerx = screen_rect.centerx
exit_button.y = 400

reset_button = reset_img.get_rect()
reset_button.centerx = screen_rect.centerx
reset_button.y = 300
#---------------------------------------------------#

#imagine de fundal pentru gloante si scor
b_s_bg = pygame.image.load("visual\\bullets_bg.png").convert_alpha()
b_s_bg = pygame.transform.scale(b_s_bg, (340, 56.5))
bullets_score_bg = b_s_bg.get_rect()
bullets_score_bg.centerx = screen_rect.centerx
bullets_score_bg.y = 658

#functie pentru resetarea jocului
def reset_game():
    global delay_completed, start_time, spawn_time, spawn_delay, bD_speed_LR, bD_speed_Up_LR, blD_speed_LR, blD_speed_Up_LR, rD_speed_LR, rD_speed_Up_LR, SPEED, score_value, BULLETS, current_level, b_distance_Count, bl_distance_Count, r_distance_Count, game_win
    game_win = False
    delay_completed = False
    start_time = pygame.time.get_ticks()
    spawn_time = 0
    spawn_delay = 3000
    bD_speed_LR = 5
    bD_speed_Up_LR = (5, 2.5)
    blD_speed_LR = 6
    blD_speed_Up_LR = (6, 3)
    rD_speed_LR = 7
    rD_speed_Up_LR = (7, 3.5)
    SPEED = 0.8
    score_value = 0
    BULLETS = 6
    current_level = 0
    b_distance_Count = 0
    bl_distance_Count = 0
    r_distance_Count = 0
    i = 0
    for _ in levels:
        levels[i].resetCount()
        i += 1
    #print("GAME RESET")

#functie pentru afisarea mesajului si scorului final
def show_final_score():
    font2 = pygame.font.Font('TextFont\BebasNeue-Regular.ttf', 64)
    if not game_win:
        msg = font2.render("You Lose!", True, "red")
    else:
        msg = font2.render("You win!", True, "green")
   
    finalScore = font2.render(f"Final score: {str(score_value)}", True, "white")
    finalScore_rect = finalScore.get_rect()
    finalScore_rect.centerx = screen_rect.centerx
    finalScore_rect.y = 120
    
    msg_rect = msg.get_rect()
    msg_rect.centerx = screen_rect.centerx
    msg_rect.y = 50
    screen.blit(finalScore, finalScore_rect.topleft)
    screen.blit(msg, msg_rect.topleft)

"""def show_fps():
    cFps = font.render(f"{FramePerSec}", True, "yellow")
    screen.blit(cFps, (580, 10))"""

#bucla principala a jocului
while running:
    if menu:
        #afiseaza imaginile de background
        screen.blit(sky, (0, 0))
        screen.blit(tree, (0, 90))
        screen.blit(background, (0, 0))
        if not retry_menu:
            #afiseaza butonul de start
            screen.blit(start_img, start_button)
        else:
            if not over_sound and not game_win:
                pygame.mixer.Sound.play(game_over_sound)
                over_sound = True
            elif not win_sound and game_win:
                pygame.mixer.Sound.play(game_win_sound)
                win_sound = True
            
            #opreste muzica de fundal
            pygame.mixer.music.stop()
            music_on = False
            music_playing = False
            show_final_score()
            
            #afiseaza butonul de reset
            screen.blit(reset_img, reset_button)
        
        #afiseaza butonul de iesire
        screen.blit(exit_img, exit_button)
        
        #actualizeaza toata fereastra
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos) or reset_button.collidepoint(event.pos):
                    if retry_menu:
                        reset_game()
                        retry_menu = False
                        
                    menu = False
                    pygame.mouse.set_visible(False) #setarea cursorului default invizibil
                    game_start = True
                    music_on = True
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    exit()
    
    if game_start:
        if music_on and not music_playing:
            pygame.mixer.music.load("sounds\\background_music.mp3")
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
            music_playing = True

        #deseneaza pe ecran imaginea pentru cer si copac
        screen.blit(sky, (0,0))
        screen.blit(tree, (0, 90))
    
        #deseneaza si actualizeaza sprite-urile
        #rate negre
        black_sprites_list.update()
        black_sprites_list.draw(screen)
    
        #rate albastre
        blue_sprites_list.update()
        blue_sprites_list.draw(screen)

        #rate rosii
        red_sprites_list.update()
        red_sprites_list.draw(screen)
        
        if not delay_completed:
            cTime = pygame.time.get_ticks()
            if cTime - start_time > 1000:
                delay_completed = True
        else:
            if not levels[current_level].is_level_completed():
                #creeaza un delay inainte de a genera ratele
                current_time = pygame.time.get_ticks()
                if current_time - spawn_time > spawn_delay:
                    spawn_time = current_time
                    if current_level == 0 or current_level == 1:
                        levels[current_level].generate_random_ducks(2)
                    else:
                        levels[current_level].generate_random_ducks(current_level)
            else:
                if current_level < len(levels) - 1:
                    pygame.mixer.Sound.play(level_up_sound)
                    current_level +=1
                    SPEED += 0.2
                    new_conditions(SPEED)
                else:
                    game_start = False
                    Sprite.remove_sprites(game_start, sprites_list)
                    pygame.mouse.set_visible(True)
                    game_win = True
                    menu = True
                    retry_menu = True                   

        #deseneaza pe ecran imaginile pentru iarba si fundalul pentru gloante si scor
        screen.blit(background, (0, 0))
        screen.blit(b_s_bg, bullets_score_bg) 

        #actualizeaza scorul, gloantele si levelul
        display_ammo()
        display_score()
        display_level()

        #obtine pozitia cursorului
        pos = pygame.mouse.get_pos()
        cursor_pos = (pos[0] - custom_cursor.get_width() // 2, pos[1] - custom_cursor.get_height() // 2)

        #afiseaza imaginea pentru cursor
        screen.blit(custom_cursor, cursor_pos)
      
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #click pe mouse
                pygame.mixer.Sound.play(shoot_sound) #porneste sunetul de tragere
                clicked_inside_sprite = False
                for sprite in sprites_list:
                    if sprite.rect.collidepoint(event.pos) and not sprite.is_shot:
                        #seteaza rata ca impuscata
                        sprite.is_shot = True
                        
                        #actualizeaza numarul de rate impuscate
                        levels[current_level].duck_shot()
                        
                        #daca nu sunt destule gloante, adauga inca unul
                        if BULLETS < MAX_BULLETS:
                            BULLETS += 1
                            
                        sprite.can_move = False
                        sprite.mouse_pressed = True
                        sprite.last_click_time = pygame.time.get_ticks()
                        
                        #adauga puncte la scor pentru rata impuscata
                        if sprite in black_sprites_list:
                            score_value += 25
                        elif sprite in blue_sprites_list:
                            score_value += 50
                        elif sprite in red_sprites_list:
                            score_value += 100
                            
                        clicked_inside_sprite = True
                        #print('RATA IMPUSCATA')
            
                if not clicked_inside_sprite and BULLETS > 0:
                    BULLETS -= 1
                    if BULLETS == 0:
                        game_win = False
                        game_start = False
                        Sprite.remove_sprites(game_start, sprites_list)
                        pygame.mouse.set_visible(True)
                        menu = True
                        retry_menu = True
                    
        #actualizeaza jocul
        #show_fps()
        pygame.display.update()
        FramePerSec.tick(FPS) 
        