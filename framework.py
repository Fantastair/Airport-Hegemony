import sys
import pygame
from pygame.locals import *
from math import sin


class Ui:
	def __init__(self, img, startpos, master):
		self.keyframes = []
		master.uigroup.append(self)
		self.img = img.copy()
		self.rect = self.img.get_rect(center = startpos)

	def paste(self, target):
		for k in self.keyframes:
			k.transform()
		target.blit(self.img, self.rect)


class KeyFrame:
	def __init__(self, subject, attritube, target, totalframe, absolute=True, endupwith=0, delay=0):
		self.subject = subject
		self.attritube = attritube
		self.totalframe = totalframe
		self.currentframe = 0
		self.target = target
		self.absolute = absolute
		self.delay = delay
		if endupwith == 0:
			self.endupwith = self.remove
		elif endupwith == 1:
			self.endupwith = self.restart

	def connect(self, alone=0):
		if alone:
			for k in self.subject.keyframes:
				if self.attritube == k.attritube:
					k.remove()
		self.subject.keyframes.append(self)
		if self.attritube < 4:
			if self.attritube == 0:
				self.reference = self.subject.rect.left
			elif self.attritube == 1:
				self.reference = self.subject.rect.top
			elif self.attritube == 2:
				self.reference = self.subject.img.get_alpha()
			elif self.attritube == 3:
				self.referimg = self.subject.img
				self.reference = 0
			if self.absolute:
				self.offset = self.target - self.reference
			else:
				self.offset = self.target
		else:
			if self.attritube == 4:
				self.reference = self.subject.rect.center
			elif self.attritube == 5:
				self.reference = self.subject.color
			elif self.attritube == 6:
				self.referimg = self.subject.img
				self.reference = self.subject.img.get_size()
			if self.absolute:
				self.offset = tupleminus(self.target,self.reference)
			else:
				self.offset = self.target

	def transform(self):
		if self.delay:
			self.delay -= 1
		else:
			self.currentframe += 1
			ration = (sin((self.currentframe/self.totalframe-0.5)*pi)+1)/2
			if self.attritube < 4:
				value = self.reference + self.offset*ration
				if self.attritube == 0:
					self.subject.rect.left = value
				elif self.attritube == 1:
					self.subject.rect.top = value
				elif self.attritube == 2:
					self.subject.img.set_alpha(int(value))
				elif self.attritube == 3:
					c = self.subject.rect.center
					self.subject.img = pygame.transform.rotate(self.referimg,value)
					self.subject.rect = self.subject.img.get_rect(center = c)
			else:
				value = [int(self.reference[i]+ration*self.offset[i]) for i in range(len(self.offset))]
				if self.attritube == 4:
					self.subject.rect.center = value
				elif self.attritube == 5:
					self.subject.color = value
					self.subject.img.fill(value)
				elif self.attritube == 6:
					c = self.subject.rect.center
					self.subject.img = pygame.transform.smoothscale(self.referimg,value)
					self.subject.rect = self.subject.img.get_rect(center = c)
			if self.currentframe == self.totalframe:
				self.endupwith()

	def remove(self):
		self.currentframe = 0
		self.subject.keyframes.remove(self)

	def restart(self):
		self.currentframe = 0


class Widget:
	def __init__(self,master):
		self.uigroup = []
		self.widgets = []
		master.widgets.append(self)

	def paste(self, target):
		for ui in self.uigroup:
			ui.paste(target)
		for w in self.widgets:
			w.paste(target)

	def handle(self, event):
		pass


class WidgetManager:
	def __init__(self, delay=0):
		self.uigroup = []
		self.widgets = []
		self.delay = delay

	def paste(self, target):
		if self.bg:
			target.fill(self.bg)
		for ui in self.uigroup:
			ui.paste(target)
		for w in self.widgets:
			w.paste(target)

	def handle(self,event):
		for w in self.widgets:
			w.handle(event)

	def enter(self):
		pass

	def trigger(self):
		pass


def tupleadd(t1, t2, minimum=None, maximum=None, lim=0):
	if lim:
		minimum, maximum = lim
	return [limit(t1[i]+t2[i],minimum,maximum) for i in range(len(t1))]


def tupleminus(t1, t2, minimum=None, maximum=None, lim=0):
	if lim:
		minimum, maximum = lim
	return [limit(t1[i]-t2[i],minimum,maximum) for i in range(len(t1))]


def limit(item, minimum=None, maximum=None):
	if isinstance(item,int) or isinstance(item,float):
		if minimum != None and item < minimum:
			return minimum
		elif maximum != None and item > maximum:
			return maximum
		else:
			return item
	else:
		return [limit(i,minimum,maximum) for i in range(int(item))]


pi = 3.141592653589793
