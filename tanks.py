import pygame
import math

def phisical_move(speed, acceleraton=[0,0], gravity=False, wind_speed=0, environment_resistance=0.00001):
	if gravity:
		g = 9.81 / 2 # подобрать оптимальный g
	else:
		g = 0
	if speed[0] > 0:
		speed[0] = round(speed[0] + acceleraton[0] - (environment_resistance*speed[0]**2), 5)
	else:
		speed[0] = round(speed[0] + acceleraton[0] + (environment_resistance*speed[0]**2), 5)
	if speed[1] > 0:
		speed[1] = round(speed[1] + acceleraton[1] - g - (environment_resistance*speed[1]**2), 5)
	else:
		speed[1] = round(speed[1] + acceleraton[1] - g + (environment_resistance*speed[1]**2), 5)
	return speed

class Game_object:
	position = [0,0]
	speed = [0,0]
	name = None
	health = 0

	def __init__(self, position = [0,0], speed = [0,0], name=None, gameplay_instance=None):
		self.position = position[:]
		self.speed = speed[:]
		self.name = name
		self.health = 100000
		self.gameplay_instance = gameplay_instance

	def move(self):
		pass

	def draw(self, surface):
		pass

	def destroy(self):
		pass


class Tank(Game_object):
	shell_count = 0
	keyleft = keyright = 0
	acceleraton_vector = 0

	def __init__(self, position=[0,0], speed=[0,0], name=None, gameplay_instance = None):
		super().__init__(position, speed, "Tank", gameplay_instance)
		self.topspeed = 0.4 * FPS
		self.acceleraton = 0.004 * FPS
		self.decceleration = 0.002 * FPS

		self.picture = pygame.image.load("tank.png").convert_alpha()
		self.picture.set_colorkey(COLOR_WHITE)
		self.rectangle = self.picture.get_rect() 
		self.rectangle.midbottom = [int(round(self.position[0])), int(round(self.position[1]))]
		self.cannon = TankCannon(self.position[:], gameplay_instance=gameplay_instance)

	def key_handler(self, key, eventtype):
		if key == pygame.K_LEFT and eventtype == pygame.KEYDOWN:
			self.keyleft = 1
		if key == pygame.K_RIGHT and eventtype == pygame.KEYDOWN:
			self.keyright = 1
		if key == pygame.K_LEFT and eventtype == pygame.KEYUP:
			self.keyleft = 0
		if key == pygame.K_RIGHT and eventtype == pygame.KEYUP:
			self.keyright = 0
		self.acceleraton_vector = self.keyright - self.keyleft


		if key == pygame.K_UP and eventtype == pygame.KEYDOWN:
			self.cannon.event(left=1)
		if key == pygame.K_DOWN and eventtype == pygame.KEYDOWN:
			self.cannon.event(right=1)
		if key == pygame.K_UP and eventtype == pygame.KEYUP:
			self.cannon.event(left=0)
		if key == pygame.K_DOWN and eventtype == pygame.KEYUP:
			self.cannon.event(right=0)

		if key == pygame.K_SPACE and eventtype == pygame.KEYDOWN:
			self.cannon.event(space=1)
			self.shot_power_amp = 10
		if key == pygame.K_SPACE and eventtype == pygame.KEYUP:
			self.cannon.event(space=0)


	def move(self):
		self.cannon.move([self.position[0] - 10, self.position[1]-self.rectangle.height/2])

		if self.speed[0] == 0 and self.acceleraton_vector == 0:
			return

		if self.speed[0] != 0 and self.acceleraton_vector == 0:
			if self.speed[0] > 0:
				self.speed[0] = self.speed[0] - self.decceleration
			if self.speed[0] < 0:
				self.speed[0] = self.speed[0] + self.decceleration

		self.speed[0] = round(self.speed[0] + self.acceleraton_vector * self.acceleraton, 4)

		# tank speed limit
		if self.speed[0] >= self.topspeed:
			self.speed[0] = self.topspeed
		if self.speed[0] <= -self.topspeed:
			self.speed[0] = -self.topspeed
		self.position[0] = self.position[0] + self.speed[0]/FPS 
		#self.position[1] = self.position[1] - self.speed[1]/FPS
		self.rectangle.midbottom = [int(round(self.position[0])), int(round(self.position[1]))]

	def draw(self, surface):
		surface.blit(self.picture, self.rectangle)
		self.cannon.draw(surface)


class TankCannon(Game_object):
	moveleft = moveright = 0
	movecannon = 0
	shot_power_amp = 0
	shot_power = shot_power_min = 200
	shot_power_max = 800
	rot = 0

	def __init__(self, position, speed=[0,0], name=None, gameplay_instance=None):
		super().__init__(position[:], speed, "tankcannon", gameplay_instance)
		self.image_orig = pygame.Surface((30 , 4), pygame.SRCALPHA)  
		self.image_orig.fill((250,10,10))  # fill the rectangle / surface with green color
		self.image = self.image_orig.copy()  # creating a copy of orignal image for smooth rotation 
		self.image.set_colorkey(COLOR_BLACK)  
		self.rectangle = self.image.get_rect()  # define rect for placing the rectangle at the desired position
		self.rectangle.bottomleft = (self.position[0], self.position[1])
		 

	def event(self, **event):
		if "left" in event:
			self.moveleft = event['left']
		if "right" in event:
			self.moveright = event['right']
		if "space" in event:
			if event['space'] == 1:
				self.shot_power_amp = 10
			if event['space'] == 0:
				self.shot()
		self.movecannon = self.moveright - self.moveleft


	def move(self, position):
		if self.shot_power < 1000 and self.shot_power_amp > 0:
			self.shot_power = self.shot_power + self.shot_power_amp

		if self.movecannon !=0:
			self.rot = (self.rot + self.movecannon) % 360  
			if self.rot == 0 or self.rot > 270:
				self.rot = 0
			if self.rot >= 180 and self.rot < 270:
				self.rot =180
			self.image = pygame.transform.rotate(self.image_orig , self.rot) 
			self.image.set_colorkey(COLOR_BLACK)
			self.rectangle = self.image.get_rect()

		if self.movecannon !=0 or self.position != position:
			self.position = position[:] 
			if self.rot < 90: #TODO убрать перепрыгивание пушки возле 90град
				self.rectangle.bottomleft = (self.position[0]-2, self.position[1])
			else:
				self.rectangle.bottomright = (self.position[0]+2, self.position[1])


	def draw(self, surface):
		surface.blit(self.image , self.rectangle) 

	def shot(self):
		if self.rot < 90:
			x = self.position[0] + self.rectangle.width
		else:
			x = self.position[0] - self.rectangle.width
		beas_position = [x , self.position[1] - self.rectangle.height + 2 ]
		speed = [self.shot_power * math.cos(math.radians(self.rot)), self.shot_power * math.sin(math.radians(self.rot))]
		self.gameplay_instance.create_object(beas_position, speed=speed, name="shell", classname="Shell")
		self.shot_power = self.shot_power_min
		self.shot_power_amp = 0


class Shell(Game_object):
	def __init__(self, position, speed, name=None, gameplay_instance=None):
		super().__init__(position, speed, "shell", gameplay_instance)

	def move(self):
		if self.position[1] >= (600 - 4):   #hardcode!!!!!!!!!
			self.position[1] = 600 - 4
			self.speed[1] = -(self.speed[1] - self.speed[1]*0.1)
			#return

		self.speed = phisical_move(self.speed[:], gravity=True)
		self.position[0] += self.speed[0]/FPS
		self.position[1] -= self.speed[1]/FPS
		#print(self.position)

	def check_collision(self):
		pass

	def bang(self):
		#TODO вызов объекта "взрыв", взрыв, делает обратный вызов деструктора объекта
		pass

	def draw(self, surface):
		beas_position = int(round(self.position[0])), int(round(self.position[1]))
		self.rectangle = pygame.draw.circle(surface, (0,0,0), beas_position, 4)


class Airplane(Game_object):
	def __init__(self, position, speed, name=None, gameplay_instance=None):
		pass

	def move(self):
		pass

	def check_collision(self):
		pass


class Bomb(Game_object):
	def __init__(self, position, speed, name=None, gameplay_instance=None):
		super().__init__(position, speed, "Bomb", gameplay_instance) #явный вызов конструктора базового класса
		pass

	def move(self):
		pass

	def check_collision(self):
		pass

	def bang(self):
		pass


class GroundSurface():
	pass


class GamePlay():
	def __init__(self):
		self.size = width, height = 800,600
		self.screen = pygame.display.set_mode(self.size)
		self.done = False
		self.clock = pygame.time.Clock()
		pygame.init()
		pygame.display.set_caption("Object Oriented Tank")
		self.objects = []
		self.create_object(position=[width/2,height], speed=[0,0], name="Tank", classname="Tank")


	def key_handler(self, key, eventtype):
		if key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,pygame.K_SPACE):
			self.objects[0].key_handler(key, eventtype) # Tank is first object in list


	def create_object(self, position, speed, name, classname):
		TargetClass = globals()[classname]
		self.objects.append(TargetClass(position, speed, name, gameplay_instance=self))


	def objects_move(self):
		for obj in self.objects: #.values()
			obj.move()


	def objects_draw(self):
		for obj in self.objects: #.values()
			obj.draw(self.screen)


	def play(self, tick=100):
		while not self.done:
			self.clock.tick(tick)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.done = True
				if event.type in (pygame.KEYDOWN, pygame.KEYUP):
					self.key_handler(event.key, event.type)

			self.screen.fill(COLOR_SKY)
			self.objects_move()
			self.objects_draw()
			pygame.display.flip()

COLOR_WHITE = 255, 255, 255
COLOR_BLACK = 0, 0, 0
COLOR_SKY = 100, 100, 255
FPS = 100

def main():
	game = GamePlay()
	game.play(FPS)


if __name__ == '__main__':
	main()