from framework import *


class SingalColorLabel(Ui):
	def __init__(self, color, size, *args):
		img = pygame.Surface(size, flags=pygame.HWSURFACE)
		self.color = color
		img.fill(color)
		super().__init__(img, *args)

	def changecolor(self,color):
		self.color = color
		self.img.fill(color)


class TextLabel(Ui):
	def __init__(self, text, color, font, *args):
		self.font = font
		img = font.render(text,True,color)
		super().__init__(img, *args)

	def set_text(self, text, color):
		c = self.rect.center
		self.img = self.font.render(text,True,color)
		self.rect = self.img.get_rect(center = c)


class Button(Widget):
	def __init__(self,text,bg,fg,font,size,startpos,master):
		super().__init__(master)
		self.command = None
		self.mouseon = False
		self.mousedown = False
		self.board = SingalColorLabel(bg,size,startpos,self)
		self.text = TextLabel(text,fg,font,startpos,self)
		self.bright = KeyFrame(self.board,5,tupleadd(bg,(50,50,50),lim=(0,255)),10)
		self.normal = KeyFrame(self.board,5,bg,15)
		self.dark = KeyFrame(self.board,5,tupleminus(bg,(50,50,50),lim=(0,255)),5)

	def handle(self, event):
		if event.type == pygame.MOUSEMOTION:
			if self.board.rect.collidepoint(event.pos):
				if not self.mouseon:
					self.mouseon = True
					if event.buttons[0] and self.mousedown:
						self.dark.connect(1)
					else:
						self.bright.connect(1)
			else:
				if self.mouseon:
					self.mouseon = False
					self.normal.connect(1)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				if self.mouseon:
					self.mousedown = True
					self.dark.connect(1)
		elif event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1:
				if self.mousedown:
					self.mousedown = False
					if self.mouseon:
						self.bright.connect(1)
						if self.command:
							self.command(*self.args)

	def connect(self, command, *args):
		self.args = args
		self.command = command
