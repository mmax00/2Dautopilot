import pygame
import random
from src.colors import Colors

class Map:
    def __init__(self,screen, num_lines, road_width,width,height,road_wave=90):
        self.colors = Colors()

        self.screen = screen
        self.num_lines = num_lines

        self.width = width
        self.height = height

        self.road_wave = road_wave

        self.x_center = width//2
        self.y_line_height = height//num_lines+1
        self.road_width = road_width
        
        #Generisanje prvih X linija puta
        self.num_lines+=3
        self.points = []
        start_pos = (self.x_center, self.height)

        for i in range(self.num_lines):
            end_pos = self.getEndPoint(start_pos)
            self.points.append({'start':start_pos,'end':end_pos})
            start_pos = end_pos



    def draw(self):
        for point in self.points:
            lines = self.getLines(point)
            start1,end1 = lines[0]
            start2, end2= lines[1]

            pygame.draw.polygon(self.screen, self.colors.ROAD_COLOR, [start1, end1, end2, start2])
            pygame.draw.line(self.screen, self.colors.CENTER_LINE_COLOR, point['start'], point['end'], 5)
            pygame.draw.line(self.screen, self.colors.LINE_COLOR, start1, end1, 8)
            pygame.draw.line(self.screen, self.colors.LINE_COLOR, start2, end2, 8)


    def getLines(self, point):
        if point:
            right_line = ((point['start'][0] +self.road_width, point['start'][1] ), (point['end'][0] +self.road_width, point['end'][1] ))
            left_line = ((point['start'][0] -self.road_width, point['start'][1] ), (point['end'][0] -self.road_width, point['end'][1] ))

            return (left_line,right_line)
            
    def getEndPoint(self, start_pos):
        # Da ne bi stvaralo prevelike krivine
        if start_pos[0] - self.x_center < 0:
            end_pos = (self.x_center - random.randint(-self.road_wave, 0), start_pos[1] - self.y_line_height)
        else:
            end_pos = (self.x_center - random.randint(0, self.road_wave), start_pos[1] - self.y_line_height)

        return end_pos

    def update(self):
        if self.points[0]['end'][1]>self.height:
            for i in range(self.num_lines):
                if i < self.num_lines-1:
                    self.points[i]=self.points[i+1]

            self.points[self.num_lines-1]={'start':self.points[self.num_lines-2]['end'],'end':self.getEndPoint(self.points[self.num_lines - 2]['end'])}

        self.points = [{'start':(point['start'][0],point['start'][1]+10),'end':(point['end'][0],point['end'][1]+10)} for point in self.points]

    def getCurrentLines(self,car_height=0):
        return self.points[1],self.points[2],self.points[3]