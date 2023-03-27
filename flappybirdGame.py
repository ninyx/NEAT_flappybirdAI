#Creating Flappy Bird Game with Pygame

#importing modules
import pygame
import neat
import time
import os
import random
pygame.font.init()
#Creating window
WIN_WIDTH = 500
WIN_HEIGHT = 800

#Loading images
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))), 
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))), 
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

STAT_FONT = pygame.font.SysFont("ComicSans", 30)
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

class Pipes:
    SPACE = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGE

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50,450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.SPACE

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask() 
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask,bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False
    
class Base:
    VELOCITY = 5
    WIDTH = BASE_IMAGE.get_width()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH
    
    def draw(self, window):
        window.blit(BASE_IMAGE, (self.x1, self.y))
        window.blit(BASE_IMAGE, (self.x2, self.y))


def draw_window(window, birds, pipes, base, score):
    window.blit(BG_IMAGE, (0,0))

    for pipe in pipes:
        pipe.draw(window)
    
    text = STAT_FONT.render("Score: " + str(score), 1,(255,255,255))
    
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(window)
    for flappy in birds:
        flappy.draw(window)
    pygame.display.update()

def main(genomes, config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(FlappyBird(230,350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipes(600)]
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    play = True
    while play:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
                pygame.quit()
                quit()

        pipe_indiv = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_indiv = 1
        else:
            play = False
            break
        
        for x, flappy in enumerate(birds):
            flappy.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((flappy.y, 
                                       abs(flappy.y - pipes [pipe_indiv].height),
                                       abs(flappy.y - pipes[pipe_indiv].bottom)))
            if output[0] > 0.5:
                flappy.jump()
 

        rem = []
        add_pipe = False
        for pipe in pipes:
            for x, flappy in enumerate(birds):
                if pipe.collide(flappy):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)     
                    
            
                if not pipe.passed and pipe.x < flappy.x:
                    pipe.passed = True
                    add_pipe = True
                     
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
                
            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipes(600))

        for pipe in rem:
            pipes.remove(pipe)
        
        for x,flappy in enumerate(birds):
            if flappy.y + flappy.img.get_height() >= 730 or flappy.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        
        base.move()

        draw_window(window, birds, pipes, base, score)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, 
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    winner = pop.run(main, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)