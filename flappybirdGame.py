#Creating Flappy Bird Game with Pygame

#importing modules
import pygame
import neat
import time
import os
import random

#Creating window
WIN_WIDTH = 500
WIN_HEIGHT = 800

#Loading images
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

#Creating class for bird
class FlappyBird:
    IMAGES = BIRD_IMAGES
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        #position of bird
        self.x = x
        self.y = y
        #bird tilt
        self.tilt = 0
        
        self.jump_counter = 0 #bird jump count
        self.velocity = 0 #bird velocity

        #bird height
        self.height = self.y

        #bird image index
        self.img_count = 0
        self.img = self.IMAGES[0] 

    def jump(self):
        self.velocity = -10.5
        self.jump_counter = 0
        self.height = self.y

    def move(self):
        self.jump_counter += 1

        displacement = self.velocity*self.jump_counter + 1.5*self.jump_counter**2 #displacement equation

        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, window):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMAGES[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMAGES[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMAGES[2]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMAGES[0]
            self.img_count = 0
        
        if self.tilt <= -80:
            self.img = self.IMAGES[1]
            self.img_count = self.ANIMATION_TIME*2
        
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        window.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
        

def draw_window(window, bird):
    window.blit(BG_IMAGE, (0,0))
    bird.draw(window)
    pygame.display.update()


def main():
    flappy = FlappyBird(200, 200)
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    play = True
    while play:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
        flappy.move()
        draw_window(window, flappy)
    pygame.quit()
    quit()

main()