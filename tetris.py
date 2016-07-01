from OpenGL.GL import *
import pygame, random, time, sys
from pygame.locals import *

class Figure:

	FIGURES = [
		[0b0000011001100000], 
		[0b0000000011110000, 0b0010001000100010], 
		[0b0000011000110000, 0b0000000100110010],
		[0b0000001101100000, 0b0000001000110001],
		[0b0000010001110000, 0b0000001100100010, 0b0000000001110001, 0b0000001000100110],
		[0b0000000101110000, 0b0000001000100011, 0b0000000001110100, 0b0000011000100010],
		[0b0000001001110000, 0b0000001000110010, 0b0000000001110010, 0b0000001001100010]]

	def __init__(self, id = 0):
		self.id = id if 0 < id and id < 8 else random.randint(1,7)-1
		self.data = Figure.FIGURES[self.id][0]
		self.rotation = 0
		self.position = (6, 20)

	def __getitem__(self, key):
		x, y = key
		return (self.data >> ((y+2)*4 + x+2) & 1) == True

	def rotate(self):
		f = Figure(self.id)
		f.position = self.position
		f.rotation = (self.rotation + 1) % len(Figure.FIGURES[self.id])
		f.data = Figure.FIGURES[self.id][f.rotation]
		return f

class Playground:
	def __init__(self):
		self.dimension = (10, 20)
		self.width = self.dimension[0]
		self.height = self.dimension[1]
		self.data = [[0 for col in range(self.width)] for row in range(self.height-1)]
		self.data.insert(0, [1] * 5 + [0] + [1]*4)

	def __getitem__(self, key):
		x, y = key
		if x < 0 or self.width <= x:
			return 0
		elif y < 0 or self.height <= y:
			return 0
		else:
			return self.data[y][x]

	def __setitem__(self, key, val):
		x, y = key
		self.data[y][x] = val

	def deleteRows(self, ls):
		ls.sort()
		ls.reverse()
		for y in ls:
			del self.data[y]
		while len(self.data) < self.height:
			self.data.append([0] * self.width)

#state
gameover = False
pause = False
countdown = 0
delta = 0
active_fig = False
figPosition = (-1, -1)

nextFigure = Figure()
currentFigure = None
playground = Playground()

#
# Game
#

def checkSpawn(fig):
	for x in range(-2, 2):
		for y in range(-2, 2):
			fig_x, fig_y = fig.position
			if fig[x, y] and playground[x + fig_x, y + fig_y]:
				return False
	return True

def checkCollision(fig, delta = (0, -1)):
	fig_x = fig.position[0] + delta[0]
	fig_y = fig.position[1] + delta[1]
	for x in range(-2, 2):
		for y in range(-2, 2):
			if fig[x, y] and (x + fig_x < 0 or x + fig_x >= 10):
				return True
			elif fig[x, y] and y + fig_y < 0:
				return True
			elif fig[x, y] and playground[x + fig_x, y + fig_y]:
				return True
	return False	

def checkRow():
	pass

def spawnFigure():
	global currentFigure, nextFigure
	currentFigure = nextFigure
	nextFigure = Figure()

def moveFigure(fig, direction):
	if fig:
		if not checkCollision(fig, direction):
			x, y = direction
			fig.position = (fig.position[0] + x, fig.position[1] + y)

def moveFigureDown(fig):
	moveFigure(fig, (0, -1))

def rotateFigure():
	global currentFigure
	if not currentFigure:
		return

	rotatedFigure = currentFigure.rotate()
	if not checkCollision(rotatedFigure, (0, 0)):
		currentFigure = rotatedFigure

def mergeFigure(fig):
	for x in range(-2, 2):
		for y in range(-2, 2):
			if fig[x, y]:
				playground[x + fig.position[0], y + fig.position[1]] = fig[x, y]

def clearRows():
	delete = []
	for y in range(playground.height):
		for x in range(playground.width):
			if not playground[x, y]:
				break
			else:
				if x + 1 == 10:
					delete.append(y)
	if delete:
		playground.deleteRows(delete)


#
# Controller
#

def handleEvent(event):
	if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
		return False
	elif event.type == KEYDOWN:
		if event.key == K_LEFT:
			moveFigure(currentFigure, (-1, 0))
		elif event.key == K_RIGHT:
			moveFigure(currentFigure, (1, 0))
		elif event.key == K_DOWN:
			moveFigure(currentFigure, (0, -1))
		elif event.key == K_UP:
			rotateFigure()

	return True

#
# OpenGL
#

def drawBlock(x, y):
	glVertex3f(x, y, 0.)
	glVertex3f(x, y + 9., 0.)
	glVertex3f(x + 9., y + 9., 0.)
	glVertex3f(x + 9., y, 0.)

def draw():
	glBegin(GL_QUADS)

	# draw wall
	glColor3f(0., 0., 1.)
	for x in [-1, playground.width]:
		for y in range(playground.height + 1):
			drawBlock(x * 10., (y-1) * 10.)
	for x in range(playground.width):
		drawBlock(x * 10., -10.)

	# draw playground
	glColor3f(0., 1., 0.)
	for x in range(playground.width):
		for y in range(playground.height):
			if playground[x, y] != 0:
				drawBlock(x * 10., y * 10.)

	# draw figure
	if currentFigure:
		glColor3f(1., 0., 0.)
		for x in range(-2, 2):
			for y in range(-2, 2):
				if currentFigure[x, y]:
					drawBlock((currentFigure.position[0] + x) * 10., (currentFigure.position[1] + y) * 10.)

	glEnd()


def resize((width, height)):
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(-20., playground.width * 10. + 20., -20., playground.height * 10. + 20., -6.0, 0.0)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

def init():
	glShadeModel(GL_SMOOTH)
	glClearColor(1.0, 1.0, 1.0, 0.0)
	glClearDepth(1.0)
	glEnable(GL_DEPTH_TEST)
	glDepthFunc(GL_LEQUAL)
	glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def clearScreen():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glLoadIdentity()
	glTranslatef(0., 0., 3.)

def main():
	global gameover, currentFigure

	pygame.init()
	pygame.key.set_repeat(100, 10)
	video_flags = OPENGL | HWSURFACE | DOUBLEBUF

	screenSize = ((playground.width+2) * 30, (playground.height+2) * 30)
	pygame.display.set_mode(screenSize, video_flags)
	resize(screenSize)

	init()

	countdown = 0
	curtime = 0

	while True:
		if not handleEvent(pygame.event.poll()):
			break

		if gameover:
			continue

		if pause:
			continue

		new_time = time.time()
		countdown = countdown - (new_time - curtime)
		curtime = new_time
		if countdown < 0:
			countdown = 0.05 * 10

			if not currentFigure:
				if not checkSpawn(nextFigure):
					gameover = True
					continue
				spawnFigure()
				continue
		
			if not checkCollision(currentFigure, (0, -1)):
				moveFigureDown(currentFigure)
			else:
				mergeFigure(currentFigure)
				clearRows()
				currentFigure = None

		# draw
		clearScreen()
		draw()
		pygame.display.flip()
		pygame.time.delay(10)

if __name__ == '__main__':
	main()
