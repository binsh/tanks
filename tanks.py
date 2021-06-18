import pygame

def phisical_move(speed, acceleraton=[0,0], gravity=False, wind_speed=0, environment_resistance=0.00001):
	if gravity:
		g = 9.81
	else:
		g = 0

	speed[0] = speed[0] + acceleraton[0] - (environment_resistance*speed[0]**2)
	speed[1] = speed[1] + acceleraton[1] - (environment_resistance*speed[1]**2) - g
	#print(speed[1])
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
	shot_power = 100
	shot_power_amp = 0


	def __init__(self, position=[0,0], speed=[0,0], name=None, gameplay_instance = None):
		super().__init__(position, speed, "Tank", gameplay_instance)
		self.topspeed = 0.4 * FPS
		self.acceleraton = 0.004 * FPS
		self.decceleration = 0.002 * FPS

		self.picture = pygame.image.load("tank.png").convert_alpha()
		self.rectangle = self.picture.get_rect()
		self.rectangle.x = int(round(self.position[0]-self.rectangle.width/2))
		self.rectangle.y = int(round(self.position[1]-self.rectangle.height))
		self.cannon = TankCannon(self.position[:])

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
			#self.cannon.event("space", 1)
			self.shot_power_amp = 10
		if key == pygame.K_SPACE and eventtype == pygame.KEYUP:
			#self.cannon.event("space", 0)
			self.shot()


	def move(self):
		#self.cannon.move(self.positon[:])
		if self.shot_power < 1000 and self.shot_power_amp > 0:
			self.shot_power = self.shot_power + self.shot_power_amp


		if self.speed[0] == 0 and self.acceleraton_vector == 0:
			return

		if self.speed[0] != 0 and self.acceleraton_vector == 0:
			if self.speed[0] > 0:
				self.speed[0] = self.speed[0] - self.decceleration
			if self.speed[0] < 0:
				self.speed[0] = self.speed[0] + self.decceleration

		self.speed[0] = self.speed[0] + self.acceleraton_vector * self.acceleraton

		# tank speed limit
		if self.speed[0] >= self.topspeed:
			self.speed[0] = self.topspeed
		if self.speed[0] <= -self.topspeed:
			self.speed[0] = -self.topspeed
		self.speed[0] = round(self.speed[0], 4) # костыль с плавающей точкой
		self.position[0] = self.position[0] + self.speed[0]/FPS 
		self.position[1] = self.position[1] + self.speed[1]/FPS

		self.rectangle.x = int(round(self.position[0]-self.rectangle.width/2))
		self.rectangle.y = int(round(self.position[1]-self.rectangle.height))

		#print (self.speed[0])
		#print (self.position)
		#print (self.rectangle)


	def shot(self):
		beas_position = [self.position[0] , self.position[1] - self.rectangle.height]
		self.gameplay_instance.create_object(beas_position, speed=[self.shot_power,self.shot_power], name="shell", classname="Shell")
		self.shot_power = 100
		self.shot_power_amp = 0

	def aim(self):
		pass

	def draw(self, surface):
		surface.blit(self.picture, self.rectangle)
		return self.picture, self.rectangle


class TankCannon(Game_object):
	moveleft = 0
	moveright = 0
	shot_power_amp = 0
	shot_power_min = 200
	shot_power_max = 800
	cannon_vector = [0.5, 0.5]

	def __init__(self, position, speed=[0,0], name=None, gameplay_instance=None):
		super().__init__(position, speed, "tankcannon", gameplay_instance)

	def event(self, eventname=None, eventvalue=0):
		if eventname == "left" and eventvalue == 1:
			self.moveleft = 1
		if eventname == "left" and eventvalue == 0:
			self.moveleft = 0
		if eventname == "right" and eventvalue == 1:
			self.moveright = 1
		if eventname == "right" and eventvalue == 0:
			self.moveright = 0
		if eventname == "space" and eventvalue == 1:
			self.shot_power_amp = 10
		if eventname == "space" and eventvalue == 0:
			self.shot_power_amp = 0
			self.shot()
		self.movecannon = self.moveright - self.moveleft

	def move(self):
		pass

class Shell(Game_object):
	def __init__(self, position, speed, name=None, gameplay_instance=None):
		super().__init__(position, speed, "shell", gameplay_instance)

	def move(self):
		if self.position[1] >= (600 - 4):   #hardcode!!!!!!!!!
			self.position[1] = 600 - 4
			self.speed[1] = -(self.speed[1] - self.speed[1]*0.1)
			#return

		self.speed = phisical_move(self.speed[:], gravity=True)
		self.position[0] = self.position[0] + self.speed[0]/FPS
		self.position[1] = self.position[1] - self.speed[1]/FPS
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
		self.shells = list()

	def key_handler(self, key, eventtype):
		if key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,pygame.K_SPACE):
			self.objects[0].key_handler(key, eventtype) # Tank is firstobject in list


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


COLOR_BLACK = 0, 0, 0
COLOR_SKY = 100, 100, 255
FPS = 100

def main():
	game = GamePlay()
	game.play(FPS)


if __name__ == '__main__':
	main()