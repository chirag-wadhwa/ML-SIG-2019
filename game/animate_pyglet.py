import pyglet
import time
import csv
import numpy as np
from scipy.interpolate import griddata

class car_animation(pyglet.window.Window):
    def __init__(self,acc_x,acc_y,num_cars=None,
                track_path='sample_path.csv',car_paths=None):

        pyglet.window.Window.__init__(self, width=1000, height=600, resizable = True)

        # get number of cars
        if num_cars is None:
            num_cars = np.array(acc_x).shape[0]
        self.num_cars = num_cars

        # assign lightning mcqueen for all cars if not specified
        if car_paths is None:
            car_paths = []
            for i in range(self.num_cars):
                car_paths.append('cars/car.png')

        #self.total_time = acc_x.shape[0]
        self.total_time = 10
        self.fps = 100
        self.time = 0
        self.width = 1000
        self.height = 600

        self.drawableObjects = []
        self.track = None
        self.carSprite = []
        self.vel_x = []
        self.vel_y = []
        self.max_vel_x = 7.3
        self.max_vel_y = 4
        self.get_accel(acc_x,acc_y)
        self.createDrawableObjects(car_paths,track_path)

    # interpolate given acceleration to get proper fps
    def get_accel(self, acc_x1, acc_y1):
        self.accel_x = np.zeros((self.num_cars,self.total_time*self.fps))
        self.accel_y = np.zeros((self.num_cars,self.total_time*self.fps))
        for i in range(self.num_cars):
            acc_x = np.array(acc_x1[i])
            acc_y = np.array(acc_y1[i])

            self.accel_x[i] = griddata(np.linspace(1,acc_x.shape[0],acc_x.shape[0]),
                                    acc_x,
                                    np.linspace(1,acc_x.shape[0],self.total_time*self.fps),
                                    method='linear')

            self.accel_y[i] = griddata(np.linspace(1,acc_y.shape[0],acc_y.shape[0]),
                                    acc_y,
                                    np.linspace(1,acc_y.shape[0],self.total_time*self.fps),
                                    method='linear')

            self.vel_x.append(0)
            self.vel_y.append(0)
            #self.accel_x[i][np.where(self.accel_x[i] > self.max_acc_x)] = self.max_acc_x
            #self.accel_y[i][np.where(self.accel_y[i] > self.max_acc_y)] = self.max_acc_y

    # utility to read csv track files into numpy arrays
    def read_track(self,in_file='sample_path.csv'):
        x = []
        y1 = []
        y2 = []
        with open(in_file,'r') as f:
            reader = csv.reader(f)
            for row in reader:
                x.append(float(row[0]))
                y1.append(float(row[1]))
                y2.append(float(row[2]))
        return np.array(x), np.array(y1), np.array(y2)

    # create the track object in pyglet
    def get_track(self,track_path):
        x,y1,y2 = self.read_track(track_path)
        x = (1000*x).astype(int)
        y1 = (600*y1).astype(int)
        y2 = (600*y2).astype(int)
        self.track = pyglet.graphics.Batch()
        for i in range(x.shape[0]-1):
            self.track.add(2, pyglet.gl.GL_LINES, None,
                                ('v2f', (x[i],y1[i],x[i+1],y1[i+1])),
                                ('c3B', (0, 0, 0, 0, 0, 0)))
            self.track.add(2, pyglet.gl.GL_LINES, None,
                                ('v2f', (x[i],y2[i],x[i+1],y2[i+1])),
                                ('c3B', (0, 0, 0, 0, 0, 0)))

    # create the car(s) and add track to draw on every frame
    def createDrawableObjects(self,car_paths,track_path):
        """
        Create objects that will be drawn within the
        window.
        """
        # Add track
        self.get_track(track_path)
        self.drawableObjects.append(self.track)

        # Add cars
        for i in range(self.num_cars):
            car_img = pyglet.image.load(car_paths[i])
            car_img.anchor_x = car_img.width // 2
            car_img.anchor_y = car_img.height // 2
            carSprite = pyglet.sprite.Sprite(car_img)
            carSprite.scale_x = float(50/car_img.width)
            carSprite.scale_y = float(50/car_img.height)
            carSprite.position = (0,100)
            self.carSprite.append(carSprite)
            self.drawableObjects.append(carSprite)

    # draw any frame
    def on_draw(self):
        self.clear()
        for d in self.drawableObjects:
            d.draw()

    # update frames
    def update(self,dt):
        for i in range(self.num_cars):
            if i is 0:
                print(self.vel_x[i])

            if not (self.time >= self.fps * self.total_time
                or self.carSprite[i].x >= self.width
                or self.carSprite[i].x < 0
                or self.carSprite[i].y >= self.height
                or self.carSprite[i].y < 0):

                self.vel_x[i] += self.accel_x[i][self.time]
                self.vel_y[i] += self.accel_y[i][self.time]

                if self.vel_x[i] >= self.max_vel_x:
                    self.vel_x[i] = self.max_vel_x
                if self.vel_x[i] <= 0:
                    self.vel_x[i] = 0
                if self.vel_x[i] <= 0:
                    self.vel_x[i] = 0
                if self.vel_y[i] <= 0:
                    self.vel_y[i] = 0

                self.carSprite[i].x += self.vel_x[i]
                #self.carSprite[i].y += self.vel_y[i]
        self.time += 1

def animate_cars(acc_x,acc_y,num_cars=1):
    acc_x = np.array(acc_x)
    acc_y = np.array(acc_y)
    win = car_animation(acc_x=acc_x,acc_y=acc_y,num_cars=num_cars,
                        track_path='test_2.csv',
                        car_paths=['cars/car_yellow.png','cars/car_orange.png','cars/lightning_mcqueen.png',
                                    'cars/car_purple.png','cars/scooby_doo.png'])
    pyglet.gl.glClearColor(1, 1, 1, 1)

    pyglet.clock.schedule_interval(win.update, 1/win.fps)
    pyglet.app.run()

animate_cars(num_cars=5,acc_x=4*(np.random.rand(5,100)-0.5),acc_y=0.5*(np.random.rand(5,100)-0.5))