import sys
import pygame
from framework import *
from mywidgets import *


class Welcome(WidgetManager):
	bg = (0,0,50)
	ending = False

	def __init__(self):
		super().__init__()
		self.title = TextLabel('打飞机',(80,128,200),haiwen,(250,100),self)
		self.author = TextLabel('By Fantastair @2022.12',(255,255,255),benmo,(250,393),self)
		self.startbutton = Button('开始游戏',(80,128,200),(0,0,50),douyu,(350,80),(250,300),self)
		self.startbutton.connect(self.end)

	def end(self):
		pygame.quit()
		self.ending = True


if __name__ != '__main__':
	pygame.init()
	clock = pygame.time.Clock()

	haiwen = pygame.font.Font('fonts/海纹体.ttf',140)
	benmo = pygame.font.Font('fonts/本墨竞圆.ttf',12)
	douyu = pygame.font.Font('fonts/斗鱼追光体.otf',60)

	screen = pygame.display.set_mode((500,400))
	pygame.display.set_caption('开始游戏')
	icon = pygame.image.load('images/icon.png').convert_alpha()
	pygame.display.set_icon(icon)

	current = Welcome()

	while True:
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			else:
				for w in current.widgets:
					w.handle(event)
		if current.ending:
			break
		screen.fill(current.bg)
		current.paste(screen)
		pygame.display.flip()
