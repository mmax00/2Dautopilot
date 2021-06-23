import pygame,os,math
from src.car import Car
from src.map import Map
from src.colors import Colors
import pickle
import neat

class Game:
    def __init__(self,width, height,map_height,map_width, title):
        self.colors = Colors()

        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        self.width = width
        self.height = height

        self.RAYCAST_LEN = 150

        pygame.init()
        pygame.font.init()

        self.font = pygame.font.SysFont(None, 48)

        self.screen = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption(title)

        self.max_score = 0

        self.car = Car(self.screen,self.dir_path,width//2,height-height//5)
        self.map = Map(self.screen,map_height,map_width,self.width,self.height)

        self.cars = []
        self.nets = []
        self.ge = []

        self.timer = True
        self.clock = pygame.time.Clock()

    def run(self):
        runninggame = True
        while runninggame:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    runninggame = False
                    pygame.quit()
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_LEFT]:
                self.car.steer(1)
            if pressed[pygame.K_RIGHT]:
                self.car.steer(-1)
            if pressed[pygame.K_r]:
                self.car.running = True

            if self.car.running:
                self.car.update()
                self.map.update()


            self._draw()
            self.car.draw()

            if self.checkCollision(self.car, self.map.getLines(self.map.getCurrentLines()[0])) \
                    or self.checkCollision(self.car, self.map.getLines(self.map.getCurrentLines()[1])):
                self.car.running = False

            pygame.display.update()
            self.clock.tick_busy_loop(30)

    def fitness(self,genomes,config):
        self.max_score = 0

        for _,g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g,config)
            self.nets.append(net)
            self.cars.append(Car(self.screen,self.dir_path,self.width//2,self.height-self.height//5))
            g.fitness = 0
            self.ge.append(g)

        runninggame = True
        while runninggame:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    runninggame = False
                    pygame.quit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_t:
                        self.timer = not self.timer


            if len(self.cars)==0:
                runninggame = False
                break

            self.map.update()
            self.max_score += 0.1
            self._draw()

            for i, car in enumerate(self.cars):
                car.update()
                car.draw()

                nn_inputs = self.rayCast(car, self.map.getCurrentLines())
                output = self.nets[i].activate(nn_inputs)
                #print(output)
                if output[0] > output[1]:
                    car.steer(1)
                else:
                    car.steer(-1)

                if self.checkCollision(car, self.map.getLines(self.map.getCurrentLines()[0])) \
                        or self.checkCollision(car, self.map.getLines(self.map.getCurrentLines()[1])):
                    car.running = False

                if not car.running:
                    self.ge[i].fitness-=20
                    self.cars.pop(i)
                    self.nets.pop(i)
                    self.ge.pop(i)

            for g in self.ge:
                g.fitness += 0.1

            pygame.display.update()
            if self.timer:
                self.clock.tick_busy_loop(30)


    def run_with_ai(self,config_path):
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path)

        with open("best.pkl", "rb") as f:
            genome = pickle.load(f)
        genomes = [(1, genome)]
        self.fitness(genomes, config)


    def startNeat(self,config_file):

        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_file)

        p = neat.Population(config)

        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)


        winner = p.run(self.fitness,20)
        pickle.dump(winner, open("best.pkl", "wb"))


    def checkCollision(self,car,lines):
        if lines:
            left_line = lines[0]
            right_line = lines[1]

            car_rect = car.getRect()

            clipped_line = car_rect.clipline(left_line)
            if clipped_line:
                return True

            clipped_line = car_rect.clipline(right_line)
            if clipped_line:
                return True

        return False

    def _line_intersect(self, Ax1, Ay1, Ax2, Ay2, Bx1, By1, Bx2, By2):
        d = (By2 - By1) * (Ax2 - Ax1) - (Bx2 - Bx1) * (Ay2 - Ay1)
        if d:
            uA = ((Bx2 - Bx1) * (Ay1 - By1) - (By2 - By1) * (Ax1 - Bx1)) / d
            uB = ((Ax2 - Ax1) * (Ay1 - By1) - (Ay2 - Ay1) * (Ax1 - Bx1)) / d
        else:
            return

        if not (0 <= uA <= 1 and 0 <= uB <= 1):
            return

        x = Ax1 + uA * (Ax2 - Ax1)
        y = Ay1 + uA * (Ay2 - Ay1)

        return x, y

    def _lines_intersect(self,raycastline,lines):
        x_interect, y_intersect = None,None
        for line in lines:
            start_left_x, start_left_y = line[0]
            end_left_x, end_left_y = line[1]

            if self._line_intersect(raycastline[0][0],raycastline[0][1],raycastline[1][0],raycastline[1][1],start_left_x,start_left_y,end_left_x,end_left_y):
                x_interect,y_intersect = self._line_intersect(raycastline[0][0],raycastline[0][1],raycastline[1][0],raycastline[1][1],start_left_x,start_left_y,end_left_x,end_left_y)

        return x_interect, y_intersect

    def rayCastLine(self,raycast,lines,default,car):
        x_interect, y_intersect = self._lines_intersect(raycast,lines)
        if x_interect is None or y_intersect is None:
            x_interect, y_intersect = default

        pygame.draw.line(self.screen, self.colors.RAYCAST_COLOR, (car.x, car.y), (x_interect, y_intersect), 3)
        pygame.draw.circle(self.screen, self.colors.RAYCAST_CIRCLE_COLOR, (x_interect, y_intersect), 5)

        return math.sqrt((car.x-x_interect)**2+(car.y-y_intersect)**2)/220

    def rayCast(self, car, lines):
        first_line = lines[0]
        second_line = lines[1]
        third_line = lines[2]

        first_pair_of_lines = self.map.getLines(first_line)
        second_pair_of_lines = self.map.getLines(second_line)
        third_pair_of_lines = self.map.getLines(third_line)

        first_left_line = first_pair_of_lines[0]
        first_right_line = first_pair_of_lines[1]
        second_left_line = second_pair_of_lines[0]
        second_right_line = second_pair_of_lines[1]
        third_left_line = third_pair_of_lines[0]
        third_right_line = third_pair_of_lines[1]

        # up_l
        up_len_l = self.rayCastLine(((car.x, car.y), (car.x-20, car.y - self.RAYCAST_LEN)),
                         (first_left_line, second_left_line, third_left_line,first_right_line, second_right_line,third_right_line),
                         (car.x-20, car.y - self.RAYCAST_LEN), car)

        # up_r
        up_len_r = self.rayCastLine(((car.x, car.y), (car.x + 20, car.y - self.RAYCAST_LEN)),
                                  (first_left_line, second_left_line, third_left_line, first_right_line,
                                   second_right_line, third_right_line),
                                  (car.x + 20, car.y - self.RAYCAST_LEN), car)

        # up left
        upleft_len = self.rayCastLine(((car.x, car.y), (car.x - self.RAYCAST_LEN, car.y - self.RAYCAST_LEN)),
                         (first_left_line, second_left_line, third_left_line),
                         (car.x - self.RAYCAST_LEN, car.y - self.RAYCAST_LEN), car)

        # up right
        upright_len = self.rayCastLine(((car.x, car.y), (car.x + self.RAYCAST_LEN, car.y - self.RAYCAST_LEN)),
                         (first_right_line, second_right_line,third_right_line),
                         (car.x + self.RAYCAST_LEN, car.y - self.RAYCAST_LEN), car)

        # left
        left_len = self.rayCastLine(((car.x,car.y),(car.x - self.RAYCAST_LEN, car.y)),
                         (first_left_line, second_left_line),
                         (car.x - self.RAYCAST_LEN, car.y),car)

        # right
        right_len = self.rayCastLine(((car.x, car.y), (car.x + self.RAYCAST_LEN, car.y)),
                         (first_right_line, second_right_line),
                         (car.x + self.RAYCAST_LEN, car.y), car)

        return left_len,upleft_len,up_len_l,up_len_r,upright_len,right_len


    def _draw(self):
        self.screen.fill(self.colors.BACKGROUD_COLOR)
        self.map.draw()
        img = self.font.render('SCORE: '+str(round(self.max_score,1)), True, (255,255,255))
        self.screen.blit(img, (20, 20))
