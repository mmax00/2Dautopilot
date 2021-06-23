import pygame
import random
import math

from src.colors import Colors

class Car:
    def __init__(self,screen,path,x,y):
        self.colors = Colors()

        #Slike
        self.carimg = pygame.image.load(path+"/sprites/Cars-01-"+str(random.randint(1,48)).zfill(2)+".png")
        self.car_width = int(self.carimg.get_width() / 2.5)
        self.car_height = int(self.carimg.get_height()/2.5)
        self.carimg = pygame.transform.scale(self.carimg,(self.car_width,self.car_height))

        self.running = True

        self.screen = screen

        self.x = x
        self.y = y

        self.rect = pygame.Rect(x, y, self.carimg.get_width(), self.carimg.get_height())
        self.surface = pygame.Surface((self.carimg.get_width(), self.carimg.get_height()),pygame.SRCALPHA, 32)
        self.surface.blit(self.carimg, (0, 0))
        self.angle = 0
        self.angle_offset = 180
        self.speed = 10

    def getRect(self):
        return self.rect

    def draw(self):
        self.rect.center = (int(self.x), int(self.y))
        rotated = pygame.transform.rotate(self.surface, self.angle_offset + self.angle)
        surface_rect = self.surface.get_rect(center=self.rect.center)
        new_rect = rotated.get_rect(center=surface_rect.center)
        self.screen.blit(rotated, new_rect.topleft)


    def steer(self,val):
        if not self.running:
            return

        self.angle += self.speed*val

        if self.angle > 70:
            self.angle = 70
        if self.angle <-70:
            self.angle = -70

    def update(self):
        if not self.running:
            return
        self.x -= math.sin(math.radians(self.angle))*8
