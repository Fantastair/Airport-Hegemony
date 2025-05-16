import sys
import random
from math import atan2, sin, cos, degrees, radians

import pygame
from pygame.locals import *

from framework import *
from mywidgets import *
import opengame


class Flash(WidgetManager):
	def __init__(self):
		super().__init__(250)
		self.flag = 0
		self.bg = BGBLUE
		icon = Ui(planeicon,(width/2,height/2+50*ration),self)
		self.alpha1 = KeyFrame(icon,2,255,60,delay=31)
		self.rotate = KeyFrame(icon,3,720,60,delay=30)
		icon.img.set_alpha(0)
		author = Ui(author_signal,(width/2,height/2+250*ration),self)
		self.up1 = KeyFrame(icon,1,-100*ration,60,absolute=False,delay=120)
		self.up2 = KeyFrame(author,1,-50*ration,60,absolute=False,delay=120)
		self.alpha2 = KeyFrame(author,2,255,60,delay=120)
		author.img.set_alpha(0)
		self.up3 = KeyFrame(icon,1,-500*ration,40,absolute=False)
		self.up4 = KeyFrame(author,1,-800*ration,40,absolute=False)

	def enter(self):
		pygame.event.set_blocked(None)
		pygame.event.set_allowed([QUIT,WINDOWFOCUSLOST,WINDOWFOCUSGAINED])
		self.rotate.connect()
		self.alpha1.connect()
		self.up1.connect()
		self.up2.connect()
		self.alpha2.connect()

	def leave(self):
		self.up3.connect()
		self.up4.connect()

	def trigger(self):
		if self.flag:
			global current
			current = prepareboard
			current.enter()
		else:
			self.leave()
			self.delay = 40
			self.flag = 1


class ChoosePlayer(Widget):
	def __init__(self, num, height, bg, master, changeable=True):
		super().__init__(master)
		self.changeable = changeable
		surface = pygame.Surface((200*ration,80*ration),flags=HWSURFACE)
		surface.fill(bg)
		number = douyu75.render(str(num),True,FAKEWHITE)
		surface.blit(number,(10*ration,0))
		surface.blit(playerhead,(90*ration,8*ration))
		self.board = Ui(surface,(-100*ration,height),self)
		self.flag = False
		if changeable:
			self.tab = SingalColorLabel(bg,(30*ration,80*ration),(-15*ration,height),self)
			o = douyu40.render('+',True,FAKEWHITE)
			self.addimg = self.tab.img.copy()
			self.addimg.blit(o,(3*ration,20*ration))
			o = douyu40.render('-',True,FAKEWHITE)
			self.minusimg = self.tab.img.copy()
			self.minusimg.blit(o,(3*ration,20*ration))
			self.tab.img = self.addimg
			self.left2 = KeyFrame(self.tab,0,170*ration,30)
			self.right2 = KeyFrame(self.tab,0,0,30)
		self.left1 = KeyFrame(self.board,0,0,30)
		self.right1 = KeyFrame(self.board,0,-170*ration,30)

	def handle(self, event):
		if self.changeable and event.type == MOUSEBUTTONDOWN and self.tab.rect.collidepoint(event.pos):
			self.flag = not self.flag
			if self.flag:
				self.left1.connect(1)
				self.left2.connect(1)
				self.tab.img = self.minusimg
			else:
				self.right1.connect(1)
				self.right2.connect(1)
				self.tab.img = self.addimg


class PlacePlane(Widget):
	def __init__(self, num, startpos, backpos, master):
		super().__init__(master)
		self.num = num
		self.chosen = self.mouseon = False
		self.mousedown = self.anchor = 0
		self.bgoffset = bgoffset[num]
		self.offset = offset[num]
		s = (50*(self.bgoffset[0][0]+1)*ration,50*(self.bgoffset[0][1]+1)*ration)
		self.board = SingalColorLabel(FAKEWHITE,s,startpos,self)
		self.bright = KeyFrame(self.board,2,150,20)
		self.dark = KeyFrame(self.board,2,25,20)
		self.board.img.set_alpha(25)
		plane = pygame.Surface(s,flags=HWSURFACE|SRCALPHA)
		block = pygame.Surface((40*ration,40*ration))
		block.fill(RED)
		head = self.offset[0][0]
		plane.blit(block,((5+50*head[0])*ration,(5+50*head[1])*ration))
		block.fill(PLANEORANGE)
		for pos in self.offset[0][1:]:
			plane.blit(block,((5+50*pos[0])*ration,(5+50*pos[1])*ration))
		self.plane = Ui(plane,startpos,self)
		self.rotate1 = KeyFrame(self.board,3,-90,20)
		self.rotate2 = KeyFrame(self.plane,3,-90,20)
		self.back1 = KeyFrame(self.board,4,backpos,20)
		self.back2 = KeyFrame(self.plane,4,backpos,20)

	def handle(self, event):
		if event.type == MOUSEMOTION:
			if self.board.rect.collidepoint(event.pos):
				if not self.mouseon:
					self.mouseon = True
					self.bright.connect(1)
			elif self.mouseon:
				self.mouseon = False
				self.dark.connect(1)
			if self.mousedown:
				self.mousedown = 2
				c = tupleadd(self.distance,event.pos)
				self.board.rect.center = self.plane.rect.center = c
		elif event.type == MOUSEBUTTONDOWN:
			if event.button == 1 and 3 not in [k.attritube for k in self.board.keyframes] and self.mouseon and not self.mousedown:
				self.mousedown = 1
				self.distance = tupleminus(self.board.rect.center,event.pos)
		elif event.type == MOUSEBUTTONUP:
			if event.button == 1:
				if self.mousedown == 1 and not self.chosen:
					self.anchor = (self.anchor+1)%4
					self.rotate1.connect(1)
					self.rotate2.connect(1)
				elif self.mousedown == 2:
					r = self.board.rect
					if prepareboard.backmap.rect.collidepoint((r.left,r.top)) and prepareboard.backmap.rect.collidepoint((r.left+r.width,r.top+r.height)):
						self.chosen = True
						left = (r.left-575*ration)//(50*ration)
						top = (r.top-5*ration)//(50*ration)
						self.center = (left,top)
						if self.crash():
							self.chosen = False
							self.back1.connect()
							self.back2.connect()
						else:
							pos = ((600+50*left)*ration+r.width/2,(30+50*top)*ration+r.height/2)
							KeyFrame(self.board,4,pos,5).connect()
							KeyFrame(self.plane,4,pos,5).connect()
					else:
						self.chosen = False
						self.back1.connect()
						self.back2.connect()
				self.mousedown = 0

	def crash(self):
		for p in prepareboard.planes:
			if p != self and p.chosen and crash(self.center+self.bgoffset[self.anchor], p.center+p.bgoffset[p.anchor]):
				return True
		return False


class MessageBox(Widget):
	def __init__(self,master):
		super().__init__(master)
		self.master = master
		img = pygame.Surface((200*ration,80*ration))
		img.fill((255,255,128))
		img.blit(douyu75.render('!',True,BGBLUE),(20*ration,0))
		self.board = Ui(img,(width/2,-40*ration),self)
		self.text = TextLabel('',BGBLUE,benmo20,(width/2+30*ration,-40*ration),self)
		self.down1 = KeyFrame(self.board,1,0,30)
		self.down2 = KeyFrame(self.text,4,(width/2+30*ration,40*ration),30)
		self.up1 = KeyFrame(self.board,1,-80*ration,30)
		self.up2 = KeyFrame(self.text,4,(width/2+30*ration,-40*ration),30)
		self.alpha1 = KeyFrame(self.board,2,255,30)
		self.alpha2 = KeyFrame(self.board,2,0,30)
		self.board.img.set_alpha(0)

	def show(self, tip):
		self.text.set_text(tip,BGBLUE)
		if not self.master.flag and not self.master.delay:
			self.down1.connect(1)
			self.down2.connect(1)
			self.alpha1.connect()
		self.master.delay = 90
		self.master.flag = 0


class AiPointer(Widget):
	def __init__(self, master):
		super().__init__(master)
		self.center = (160*ration,360*ration)
		self.wheel = Ui(wheel,self.center,self)
		self.pointer = Ui(pointer,(self.center[0],self.center[1]+15*ration),self)
		self.text = TextLabel('off',FAKEWHITE,benmo20,(self.center[0],self.center[1]+1*ration),self)
		for s in self.uigroup:
			s.img.set_alpha(0)
		img = pygame.Surface((110*ration,30*ration),flags=HWSURFACE)
		img.fill(BLACK)
		img.fill(MESSAGEYELLOW,(2*ration,2*ration,106*ration,26*ration))
		t = benmo20.render('设置AI强度',True,BLACK)
		r = t.get_rect(center=(55*ration,17*ration))
		img.blit(t,r)
		self.tip = Ui(img,(0,0),self)
		self.uigroup.remove(self.tip)
		self.angle = 0
		self.changed = False
		self.time = 0

	def handle(self,event):
		if event.type == MOUSEBUTTONDOWN and event.button == 1:
			if (event.pos[0]-self.center[0])**2+(event.pos[1]-self.center[1])**2 < 1089:
				self.time = 0
				self.changed = True
				self.angle = (degrees(atan2(event.pos[1]-self.center[1],event.pos[0]-self.center[0]))-90)%360
				if self.tip in self.uigroup:
					self.uigroup.remove(self.tip)
		elif event.type == MOUSEMOTION:
			if self.tip in self.uigroup:
				self.uigroup.remove(self.tip)
			if self.changed:
				self.angle = (degrees(atan2(event.pos[1]-self.center[1],event.pos[0]-self.center[0]))-90)%360
			elif (event.pos[0]-self.center[0])**2+(event.pos[1]-self.center[1])**2 < 1089:
				self.time = 30
			else:
				self.time = 0
		elif event.type == MOUSEBUTTONUP and event.button == 1:
			self.changed = False

	def paste(self,target):
		if self.time:
			if self.time == 1:
				self.tip.rect.left, self.tip.rect.top = event.pos
				self.tip.rect.top -= 30*ration
				self.uigroup.append(self.tip)
			self.time -= 1
		if self.changed:
			global aidifficulty
			if self.angle<=22.5 or self.angle>=337.5:
				self.rotate(0)
				aidifficulty = None
				self.text.set_text('off',FAKEWHITE)
			elif self.angle>22.5 and self.angle<=45:
				self.rotate(45)
				aidifficulty = 0
				self.text.set_text('0',FAKEWHITE)
			elif self.angle <= 315:
				self.rotate(self.angle)
				aidifficulty = int((self.angle-45)/135*50)
				self.text.set_text(str(aidifficulty),FAKEWHITE)
			elif self.angle < 337.5:
				self.rotate(-45)
				aidifficulty = 100
				self.text.set_text('100',FAKEWHITE)
		super().paste(target)

	def rotate(self, angle):
		angle = radians(angle+90)
		self.pointer.rect.center = (self.center[0]+15*ration*cos(angle),self.center[1]+15*ration*sin(angle))


class PrepareBoard(WidgetManager):
	def __init__(self):
		super().__init__()
		self.bg = BGBLUE
		self.flag = 0
		self.bar = SingalColorLabel(BARGOLD,(20*ration,height),(250*ration,height*1.5),self)
		self.up1 = KeyFrame(self.bar,1,-height,40,absolute=False)
		self.vs = TextLabel('VS',FAKEWHITE,douyu75,(-100*ration,360*ration),self)
		self.left = KeyFrame(self.vs,0,160*ration,40,absolute=False)
		self.startbutton = Button('开    始    游    戏',BUTTONBLUE,BGBLUE,douyu40,(1020*ration,60*ration),(770*ration,0),self)
		self.startbutton.connect(self.startgame)
		self.up2 = KeyFrame(self.startbutton.board,1,-160*ration,40,absolute=False,delay=30)
		self.up3 = KeyFrame(self.startbutton.text,1,-160*ration,40,absolute=False,delay=30)
		self.friends = []
		self.enemies = []
		for s in range(3):
			self.friends.append(ChoosePlayer(s+1,(60+s*110)*ration,FRIENDBLUE,self,changeable=s!=0))
		self.friends[0].flag = True
		for s in range(3):
			self.enemies.append(ChoosePlayer(s+4,(440+s*110)*ration,ENEMYRED,self))
		self.enemies[0].flag = True
		self.enemies[0].tab.img = self.enemies[0].minusimg
		self.lefts = []
		for s in range(4):
			p = (self.friends,self.enemies)[int(s/2)%2][s%2+1]
			self.lefts.append(KeyFrame(p.board,0,30*ration,30,absolute=False,delay=10*s))
			if p.changeable:
				self.lefts.append(KeyFrame(p.tab,0,30*ration,30,absolute=False,delay=10*s))
		img = pygame.Surface((610*ration,610*ration),flags=HWSURFACE)
		img.fill(MAPBLUE)
		rv = pygame.Rect(0,0,10*ration,610*ration)
		rh = pygame.Rect(0,0,610*ration,10*ration)
		for s in range(13):
			side = 50*ration*s
			rv.left = side
			rh.top = side
			img.fill(BGBLUE,rv)
			img.fill(BGBLUE,rh)
		self.backmap = Ui(img,(900*ration,330*ration),self)
		self.backmap.img.set_alpha(0)
		alpha = KeyFrame(self.backmap,2,255,40)
		self.plane1 = PlacePlane(0,(425*ration,1000*ration),(425*ration,155*ration),self)
		up4 = KeyFrame(self.plane1.board,1,30*ration,40)
		up5 = KeyFrame(self.plane1.plane,1,30*ration,40)
		self.plane2 = PlacePlane(1,(425*ration,1000*ration),(425*ration,400*ration),self)
		up6 = KeyFrame(self.plane2.board,1,300*ration,40)
		up7 = KeyFrame(self.plane2.plane,1,300*ration,40)
		self.plane3 = PlacePlane(2,(425*ration,1000*ration),(425*ration,580*ration),self)
		up8 = KeyFrame(self.plane3.board,1,530*ration,40)
		up9 = KeyFrame(self.plane3.plane,1,530*ration,40)
		self.ups = (up4,up5,up6,up7,up8,up9)
		self.planes = (self.plane1,self.plane2,self.plane3)
		self.messagebox = MessageBox(self)
		self.aipointer = AiPointer(self)
		alpha1 = KeyFrame(self.aipointer.wheel,2,255,60)
		alpha2 = KeyFrame(self.aipointer.pointer,2,255,60)
		alpha3 = KeyFrame(self.aipointer.text,2,255,60)
		self.alpha = [alpha,alpha1,alpha2,alpha3]

	def enter(self):
		pygame.event.set_blocked(None)
		pygame.event.set_allowed([
			QUIT,
			MOUSEMOTION,
			MOUSEBUTTONDOWN,
			MOUSEBUTTONUP,
			WINDOWFOCUSLOST,
			WINDOWFOCUSGAINED,
			])
		self.bar.rect.top = height
		self.up1.connect()
		self.startbutton.board.rect.top = 820*ration
		self.startbutton.text.rect.center = (775*ration,850*ration)
		self.up2.connect()
		self.up3.connect()
		self.friends[0].left1.connect(1)
		self.enemies[0].left1.connect(1)
		self.enemies[0].left2.connect(1)
		self.left.connect()
		for s in self.lefts:
			s.connect()
		for s in self.alpha:
			s.connect()
		for s in self.ups:
			s.connect()

	def trigger(self):
		if self.flag == 0:
			self.messagebox.up1.connect(1)
			self.messagebox.up2.connect(1)
			self.messagebox.alpha2.connect()

	def startgame(self):
		if self.equal():
			global current, planes
			planes = [p.chosen for p in self.planes]
			if True in planes:
				changepage.change(fightboard,prepare=self.getready)
				current = changepage
			else:
				self.messagebox.show('至少一架飞机')
		else:
			self.messagebox.show('人数不相等')

	def equal(self):
		friendnum = [p.flag for p in self.friends].count(True)
		enemynum = [p.flag for p in self.enemies].count(True)
		return friendnum == enemynum

	def getready(self):
		global friends, enemies, players, me, friendhead, enemyhead
		me = Me()
		friends = [me]
		enemies = []
		for s in range(1,3):
			if prepareboard.friends[s].flag:
				friends.append(Computer(s+1))
		random.shuffle(friends)
		for s in range(3):
			if prepareboard.enemies[s].flag:
				enemies.append(Computer(s+4))
		random.shuffle(enemies)
		players = [friends, enemies]
		friendhead = enemyhead = len(friends)*len(me.planes)
		if fightboard.team:
			num = enemies[0].num
		else:
			num = friends[0].num
		fightboard.number = TextLabel(str(num),FAKEWHITE,douyu75,(0,0),fightboard)
		fightboard.number.rect.left = width/2-90*ration
		fightboard.number.rect.top = 0
		fightboard.choosemap1 = ChooseMap(0,fightboard)
		fightboard.choosemap2 = ChooseMap(1,fightboard)
		fightboard.friendmap = Ui(friends[0].map,(311*ration,381*ration),fightboard)


class ChangePage(WidgetManager):
	def __init__(self):
		super().__init__()
		self.bg = None
		self.screen = pygame.Surface((size),flags=HWSURFACE)
		t = jimo200.render('打飞机',True,FAKEWHITE)
		r = t.get_rect()
		board = pygame.Surface((width/2,height),flags=HWSURFACE)
		side = pygame.Rect(0,0,10*ration,height)
		board.fill(BGBLUE)
		board.fill(BARGOLD,side)
		r.center = (0,height/2)
		board.blit(t,r)
		self.rightboard = Ui(board,(0,height/2),self)
		board.fill(BGBLUE)
		side.left = width/2-10*ration
		board.fill(BARGOLD,side)
		r.center = (width/2,height/2)
		board.blit(t,r)
		self.leftboard = Ui(board,(0,height/2),self)
		self.close1 = KeyFrame(self.leftboard,0,0,60)
		self.close2 = KeyFrame(self.rightboard,0,width/2,60)
		self.open1 = KeyFrame(self.leftboard,0,-width/2,60)
		self.open2 = KeyFrame(self.rightboard,0,width,60)
		self.plane = Ui(planeicon,(105*ration,895*ration),self)
		self.fly = KeyFrame(self.plane,4,(1175*ration,-175*ration),60,delay=5)

	def change(self, page, *args, prepare=None):
		pygame.event.set_blocked(None)
		pygame.event.set_allowed([QUIT,WINDOWFOCUSLOST,WINDOWFOCUSGAINED])
		self.plane.rect.center = (105*ration,895*ration)
		self.uigroup = [self.leftboard,self.rightboard,self.plane]
		self.leftboard.rect.left = -width/2
		self.rightboard.rect.left = width
		self.delay = 61
		self.flag = 0
		self.page = page
		self.prepare = prepare
		self.args = args
		self.close1.connect()
		self.close2.connect()

	def trigger(self):
		if self.flag == 1:
			global current
			current = self.page
			current.enter()
		elif self.flag == 2:
			self.open1.connect()
			self.open2.connect()
			self.delay = 61
			self.flag = 1
		else:
			self.flag = 2
			self.delay = 70
			if self.prepare:
				self.prepare(*self.args)
			self.page.paste(self.screen)
			Ui(self.screen,(width/2,height/2),self)
			self.uigroup = self.uigroup[::-1]
			self.uigroup.remove(self.plane)
			self.uigroup.append(self.plane)
			self.fly.connect()


class Plane:
	def __init__(self, num, startpos, anchor):
		self.num = num
		self.alive = True
		self.startpos = startpos
		self.offset = offset[num][anchor]
		self.bgoffset = bgoffset[num][anchor]
		self.location = [tuple(tupleadd(startpos,pos)) for pos in self.offset]
		self.head = self.location[0]


class BrushPlane:
	def __init__(self, num):
		self.offset = offset[num]
		self.bgoffset = bgoffset[num]
		self.headdata = []
		self.num = num

	def locate(self, startpos, anchor):
		self.location = [tuple(tupleadd(startpos,pos)) for pos in self.offset[anchor]]
		self.head = self.location[0]


class Player:
	def createmap(self):
		self.location = []
		self.map = pygame.Surface((472*ration,472*ration),flags=HWSURFACE|SRCALPHA)
		r = pygame.Rect(0,0,32*ration,32*ration)
		for p in self.planes:
			point = tupleadd(p.startpos,p.offset[0])
			r.left, r.top = (point[0]*40*ration,point[1]*40*ration)
			self.map.fill(RED,r)
			for pos in p.offset[1:]:
				point = tupleadd(p.startpos,pos)
				r.left, r.top = (point[0]*40*ration,point[1]*40*ration)
				self.map.fill(PLANEORANGE,r)
			self.location += p.location

	def hit(self, pos, team):
		global friendhead, enemyhead
		fightboard.playerbox.changecolor((FRIENDBLUE,ENEMYRED)[team])
		color = (DARKFRIENDBLUE,DARKENEMYRED)[team]
		if pos not in fightboard.renderqueue[color]:
			fightboard.renderqueue[color].append(pos)
			for p in players[team]:
				if p.alive:
					for plane in p.planes:
						if plane.alive:
							if plane.head == pos:
								if team:
									enemyhead -= 1
								else:
									friendhead -= 1
								p.alive -= 1
								plane.alive = False
								minus(p.hitposes, plane.location, inplace=True)
								for x in range(plane.startpos[0], plane.startpos[0]+plane.bgoffset[0]+1):
									for y in range(plane.startpos[1], plane.startpos[1]+plane.bgoffset[1]+1):
										p.missposes.append((x,y))
								break
							elif pos in plane.location:
								p.hitposes.append(pos)
								break
					if pos not in p.location:
						p.missposes.append(pos)

	def infer(self):
		brushes = [BrushPlane(p.num) for p in self.planes if p.alive]
		possiblity = {}
		for plane in brushes:
			for anchor in range(4):
				for x in range(0-1*(plane.num==2),12-plane.bgoffset[anchor][0]+1*(plane.num==2)):
					for y in range(0-1*(plane.num==2),12-plane.bgoffset[anchor][1]+1*(plane.num==2)):
						plane.locate((x,y),anchor)
						hitten = intersect(self.hitposes, plane.location)
						length = len(hitten)+1
						if maprect.collidepoint(plane.head):
							if aidifficulty < 51:
								if hitten and plane.head not in hitten and not intersect(self.missposes,plane.location):
									plane.headdata.append((plane.head,length))
							else:
								if not intersect(self.missposes,plane.location) and (not self.hitposes or hitten and plane.head not in hitten):
									plane.headdata.append((plane.head,length))
			if plane.headdata:
				number = 1/len(plane.headdata)
				for poss in plane.headdata:
					if poss[0] in possiblity:
						possiblity[poss[0]] += number*poss[1]
					else:
						possiblity[poss[0]] = number*poss[1]
				break
		possinline = {}
		for poss in possiblity:
			if possiblity[poss] in possinline:
				possinline[possiblity[poss]].append(poss)
			else:
				possinline[possiblity[poss]] = [poss]
		l = list(possinline)
		l.sort(reverse=True)
		if aidifficulty % 50:
			which = random.randint(1,100)
			if which < aidifficulty*2:
				pos = random.choice(possinline[l[0]])
			elif which < aidifficulty*4:
				pos = random.choice(possinline[l[min(1,len(possinline)-1)]])
			else:
				pos = random.choice(possinline[l[min(2,len(possinline)-1)]])
		else:
			pos = random.choice(possinline[l[0]])
		return pos


def toggle(team):
	fightboard.team = team
	if fightboard.flag:
		fightboard.turn = (fightboard.turn+1)%len(friends)
		fightboard.flag = 0
	else:
		fightboard.flag = 1
	p = players[team][fightboard.turn]
	if p.alive:
		fightboard.delay = 60
	else:
		fightboard.delay = 2
	fightboard.number.set_text(str(p.num),FAKEWHITE)


class Computer(Player):
	def __init__(self,num):
		self.planes = []
		self.hitposes = []
		self.missposes = []
		self.num = num
		for s in range(3):
			if planes[s]:
				self.createplanes(s)
		self.createmap()
		self.alive = len(self.planes)

	def createplanes(self, num):
		flag, startpos, anchor = self.createplane(num)
		while flag:
			flag, startpos, anchor = self.createplane(num)
		self.planes.append(Plane(num,startpos,anchor))

	def createplane(self, num):
		anchor = random.randint(0,3)
		startpos = (random.randint(0,11-bgoffset[num][anchor][0]),random.randint(0,11-bgoffset[num][anchor][1]))
		c = False
		for p in self.planes:
			if crash(p.startpos+p.bgoffset,startpos+bgoffset[num][anchor]):
				c = True
				break
		return c, startpos, anchor

	def choosepos(self, team):
		if self.alive:
			usefulplayers = [player for player in players[team] if player.hitposes and player.alive]
			if usefulplayers:
				maxl = 0
				for player in usefulplayers:
					l = len(player.hitposes)
					if l > maxl:
						maxl = l
						p = player
			else:
				p = random.choice([p for p in players[team] if p.alive])
			if aidifficulty is None or aidifficulty < 51 and not p.hitposes:
				pos = (random.randint(0,11),random.randint(0,11))
				while pos in p.missposes:
					pos = (random.randint(0,11),random.randint(0,11))
			elif aidifficulty == 0:
				p = random.choice([p for p in players[team] if p.alive])
				pos = (random.randint(0,11),random.randint(0,11))
				color = (DARKFRIENDBLUE,DARKENEMYRED)[team]
				hitten = fightboard.renderqueue[color]
				average = len(hitten)/144
				s = 5-[plane for plane in p.planes if plane.alive][0].num*2
				while pos in p.missposes or density(pos,s,hitten) > average:
					pos = (random.randint(0,11), random.randint(0,11))
			else:
				pos = p.infer()
			self.hit(pos, team)
			if friendhead and enemyhead:
				toggle(team)
			else:
				fightboard.f = 1
				fightboard.delay = 75
				if friendhead:
					fightboard.white.rect.left = width/2
				else:
					fightboard.white.rect.left = 0
				fightboard.ending = True
				for s in fightboard.flashing:
					s.connect()
		else:
			toggle(team)
			fightboard.playerbox.changecolor((FRIENDBLUE,ENEMYRED)[team])


class Me(Player):
	def __init__(self):
		self.planes = []
		self.hitposes = []
		self.missposes = []
		self.num = 1
		for s in range(3):
			p = prepareboard.planes[s]
			if p.chosen:
				self.planes.append(Plane(s,p.center,p.anchor))
		self.createmap()
		self.alive = len(self.planes)

	def choosepos(self, team):
		if self.alive == 0:
			toggle(team)
			fightboard.playerbox.changecolor((FRIENDBLUE,ENEMYRED)[team])


class ChooseMap(Widget):
	def __init__(self,team,master):
		super().__init__(master)
		self.num = 0
		length = len(friends)
		self.team = team
		boardcolor = (DARKFRIENDBLUE,DARKENEMYRED)[team]
		slidercolor = (PLANEORANGE,SLIDEPERPLE)[team]
		self.startpos = ((75*ration,75*ration),(1197*ration-length*40*ration,75*ration))[team]
		self.board = SingalColorLabel(boardcolor,(length*40*ration,40*ration),(self.startpos[0]+length*20*ration,self.startpos[1]+20*ration),self)
		self.slider = SingalColorLabel(slidercolor,(40*ration,40*ration),(self.startpos[0]+20*ration,self.startpos[1]+20*ration),self)
		self.move = []
		for s in range(length):
			self.move.append(KeyFrame(self.slider,0,self.startpos[0]+s*40*ration,15))
			num = players[team][s].num
			TextLabel(str(num),FAKEWHITE,haiwen30,(self.startpos[0]+(20+40*s)*ration,self.startpos[1]+20*ration),self)

	def handle(self,event):
		if event.type == MOUSEBUTTONDOWN and event.button == 1 and self.board.rect.collidepoint(event.pos):
			self.num = int((event.pos[0]-self.startpos[0])//(40*ration))
			if not self.team:
				fightboard.friendmap.img = friends[self.num].map
			self.move[self.num].connect(1)


class FightBoard(WidgetManager):
	def __init__(self):
		super().__init__(90)
		self.bg = None
		self.f = 0
		self.team = random.randint(0,1)
		self.flag = self.turn = 0
		self.ending = False
		img = pygame.Surface(size,flags=HWSURFACE)
		img.fill(FRIENDBLUE,(0,0,width/2,height))
		img.fill(ENEMYRED,(width/2,0,width/2,height))
		img.fill(BARGOLD,(width/2-10*ration,0,20*ration,height))
		self.maprect = pygame.Rect(67*ration,137*ration,488*ration,488*ration)
		img.fill(DARKFRIENDBLUE,self.maprect)
		self.maprect.left = 717*ration
		img.fill(DARKENEMYRED,self.maprect)
		drawmap(img,(75*ration,145*ration),32*ration,12,FRIENDBLUE)
		drawmap(img,(725*ration,145*ration),32*ration,12,ENEMYRED)
		self.background = Ui(img,(width/2,height/2),self)
		self.playerbox = SingalColorLabel([FRIENDBLUE,ENEMYRED][self.team],(200*ration,80*ration),(width/2,40*ration),self)
		Ui(playerhead,(width/2+50*ration,40*ration),self)
		self.barh = SingalColorLabel(FAKEWHITE,(488*ration,40*ration),(961*ration,0),self)
		self.barh.img.set_alpha(100)
		self.barv = SingalColorLabel(FAKEWHITE,(40*ration,488*ration),(0,381*ration),self)
		self.barv.img.set_alpha(100)
		self.mouseon = self.mousedown = False
		self.uigroup.remove(self.barh)
		self.uigroup.remove(self.barv)
		self.siderect = pygame.Rect(0,0,32*ration,32*ration)
		self.renderqueue = {
		DARKFRIENDBLUE : [],
		RED : [],
		PLANEORANGE : [],
		DARKENEMYRED : [],
		}
		self.white = SingalColorLabel(FAKEWHITE,(width/2,height),(0,height/2),self)
		self.white.img.set_alpha(0)
		self.uigroup.remove(self.white)
		self.flashing = [
		KeyFrame(self.white,2,255,10),
		KeyFrame(self.white,2,0,10,delay=10),
		KeyFrame(self.white,2,255,12,delay=20),
		KeyFrame(self.white,2,0,13,delay=32),
		KeyFrame(self.white,2,255,15,delay=45),
		KeyFrame(self.white,2,0,15,delay=60)
		]

	def handle(self,event):
		if event.type == MOUSEMOTION:
			if self.team == 0 and isinstance(friends[self.turn],Me):
				if self.maprect.collidepoint(event.pos):
					if not self.mouseon and me.alive:
						self.mouseon = True
					pos = tupleminus(event.pos,(717*ration,137*ration),lim=(0,479*ration))
					self.pos = (pos[0]//(40*ration),pos[1]//(40*ration))
					self.barv.rect.left = 721*ration+self.pos[0]*40*ration
					self.barh.rect.top = 141*ration+self.pos[1]*40*ration
				elif self.mouseon:
					self.mouseon = False
		elif event.type == MOUSEBUTTONDOWN:
			if event.button == 1 and self.mouseon:
				self.mousedown = True
		elif event.type == MOUSEBUTTONUP and event.button == 1:
				if self.mousedown and self.mouseon:
					me.hit(self.pos,1)
					if friendhead and enemyhead:
						self.team = 1
						if self.flag:
							self.turn = (self.turn+1)%len(friends)
							self.flag = 0
						else:
							self.flag = 1
						p = enemies[self.turn]
						if p.alive:
							self.delay = 60
						else:
							self.delay = 2
						num = p.num
						self.number.set_text(str(num),FAKEWHITE)
					else:
						self.f = 1
						self.delay = 75
						if friendhead:
							self.white.rect.left = width/2
						else:
							self.white.rect.left = 0
						self.ending = True
						for s in self.flashing:
							s.connect()
					self.mouseon = False
				self.mousedown = False
		super().handle(event)

	def paste(self, target):
		super().paste(target)
		for pos in self.renderqueue[DARKFRIENDBLUE]:
			self.siderect.left, self.siderect.top = 75*ration+pos[0]*40*ration, 145*ration+pos[1]*40*ration
			target.fill(DARKFRIENDBLUE,self.siderect)
		self.renderqueue[RED] = []
		self.renderqueue[PLANEORANGE] = []
		p = enemies[self.choosemap2.num]
		for plane in p.planes:
			hitten = intersect(plane.location, self.renderqueue[DARKENEMYRED])
			if plane.head in hitten:
				self.renderqueue[RED].append(plane.head)
				self.renderqueue[PLANEORANGE] += plane.location[1:]
			elif hitten:
				self.renderqueue[PLANEORANGE] += hitten
		for s in (DARKENEMYRED,PLANEORANGE,RED):
			for pos in self.renderqueue[s]:
				self.siderect.left, self.siderect.top = 725*ration+pos[0]*40*ration, 145*ration+pos[1]*40*ration
				target.fill(s,self.siderect)
		if self.mouseon:
			self.barh.paste(target)
			self.barv.paste(target)
		if self.ending:
			self.white.paste(target)

	def trigger(self):
		if self.f:
			global current
			changepage.change(endboard, prepare=endboard.showdata)
			current = changepage
		else:
			players[self.team][self.turn].choosepos((self.team+1)%2)

	def enter(self):
		pygame.event.set_blocked(None)
		pygame.event.set_allowed([
			QUIT,
			WINDOWFOCUSLOST,
			WINDOWFOCUSGAINED,
			MOUSEMOTION,
			MOUSEBUTTONDOWN,
			MOUSEBUTTONUP,
			])


class EndBoard(WidgetManager):
	def __init__(self):
		super().__init__()
		self.bg = BGBLUE
		self.flag = 0
		self.show = False
		self.restartbutton = Button('重新开始',BUTTONBLUE,BGBLUE,douyu40,(300*ration,80*ration),(width/2-170*ration,height/2+200*ration),self)
		self.restartbutton.connect(self.restartgame)
		self.long = KeyFrame(self.restartbutton.board,6,(600*ration,60*ration),60)
		self.move1 = KeyFrame(self.restartbutton.board,4,(width/2,height/2+310*ration),30)
		self.move2 = KeyFrame(self.restartbutton.text,4,(width/2,height/2+310*ration),30)
		self.checkbutton = Button('查看详情',BUTTONBLUE,BGBLUE,douyu40,(300*ration,80*ration),(width/2+170*ration,height/2+200*ration),self)
		self.checkbutton.connect(self.showdetail)
		self.checkbutton.board.img.set_alpha(255)
		self.alpha2 = KeyFrame(self.checkbutton.board,2,0,30)
		self.slider = SingalColorLabel(BUTTONBLUE,(70*ration,40*ration),(1066*ration,672*ration),self)
		self.slider.img.set_alpha(0)
		self.alpha5 = KeyFrame(self.slider,2,255,60)
		self.moveshow = KeyFrame(self.slider,0,1099*ration,30)
		self.movehide = KeyFrame(self.slider,0,1031*ration,30)
		self.showrect = pygame.Rect(1099*ration,650*ration,70*ration,40*ration)
		self.hiderect = pygame.Rect(1031*ration,650*ration,70*ration,40*ration)
		self.text = TextLabel('隐藏|显示',FAKEWHITE,haiwen30,(1100*ration,670*ration),self)
		self.text.img.set_alpha(0)
		self.alpha6 = KeyFrame(self.text,2,255,60)
		self.text1 = TextLabel('打击点：',FAKEWHITE,benmo20,(1000*ration,672*ration),self)
		self.text1.img.set_alpha(0)
		self.alpha7 = KeyFrame(self.text1,2,255,60)
		self.bgboard = SingalColorLabel(BGBLUE,(width,height),(width/2,height/2),self)
		self.bgboard.img.set_alpha(0)
		self.covereverything = KeyFrame(self.bgboard,2,255,60)
		self.uigroup.remove(self.bgboard)

	def showdata(self):
		if friendhead:
			self.tip = TextLabel('你赢了', BARGOLD, jimo200, (width/2,height/2), self)
		else:
			self.tip = TextLabel('你输了', RED, jimo200, (width/2,height/2), self)
		self.scale = KeyFrame(self.tip,6,(240*ration,80*ration),60)
		self.move = KeyFrame(self.tip,4,(170*ration,670*ration),60)
		length = len(friends)
		w = 50*ration/length
		img = pygame.Surface((width,w*12),flags=HWSURFACE|SRCALPHA)
		hitimg = pygame.Surface((width,w*12),flags=HWSURFACE|SRCALPHA)
		self.startxposes = []
		self.height = height/2-w*6
		self.numbers = []
		self.alpha4 = []
		for s in range(length*2):
			self.startxposes.append(w*12*s+200*ration/(length*2+1)*(s+1))
			drawmap(img,(self.startxposes[s],0),w*0.8,12,MAPBLUE)
			if s < length:
				p = friends[s]
				for pos in fightboard.renderqueue[DARKFRIENDBLUE]:
					hitimg.fill(BGBLUE, (self.startxposes[s]+w*pos[0],w*pos[1],w*0.8,w*0.8))
			else:
				p = enemies[s-length]
				for pos in fightboard.renderqueue[DARKENEMYRED]:
					hitimg.fill(BGBLUE, (self.startxposes[s]+w*pos[0],w*pos[1],w*0.8,w*0.8))
			for plane in p.planes:
				img.fill(RED, (self.startxposes[s]+w*plane.head[0],w*plane.head[1],w*0.8,w*0.8))
				for pos in plane.location[1:]:
					img.fill(PLANEORANGE, (self.startxposes[s]+w*pos[0],w*pos[1],w*0.8,w*0.8))
			self.numbers.append(TextLabel(str(p.num),FAKEWHITE,douyu40,(self.startxposes[s]+30*ration,self.height-30*ration),self))
			self.numbers[s].img.set_alpha(0)
			self.uigroup.remove(self.numbers[s])
			self.alpha4.append(KeyFrame(self.numbers[s],2,255,60))
		self.mapbg = Ui(img,(width/2,height/2),self)
		self.mapbg.img.set_alpha(0)
		self.alpha3 = KeyFrame(self.mapbg,2,255,60)
		self.uigroup.remove(self.mapbg)
		self.hitimg = Ui(hitimg,(width/2,height/2),self)
		self.hitimg.img.set_alpha(0)
		self.showhitten = KeyFrame(self.hitimg,2,255,30)
		self.hidehitten = KeyFrame(self.hitimg,2,0,30)
		self.uigroup.remove(self.hitimg)

	def showdetail(self):
		self.show = True
		self.scale.connect()
		self.move.connect()
		self.alpha2.connect()
		self.alpha3.connect()
		for k in self.alpha4:
			k.connect()
		self.alpha5.connect()
		self.alpha6.connect()
		self.alpha7.connect()
		self.long.connect()
		self.move1.connect()
		self.move2.connect()
		for s in self.numbers:
			self.uigroup.append(s)
		self.uigroup.append(self.mapbg)
		self.uigroup.append(self.hitimg)
		self.delay = 30

	def restartgame(self):
		global prepareboard, fightboard, endboard, aidifficulty
		self.widgets.remove(self.restartbutton)
		if not self.show:
			self.widgets.remove(self.checkbutton)
		self.uigroup.append(self.bgboard)
		self.covereverything.connect()
		self.flag = 1
		self.delay = 60
		prepareboard = PrepareBoard()
		fightboard = FightBoard()
		endboard = EndBoard()
		aidifficulty = None

	def trigger(self):
		if self.flag:
			global current
			current = prepareboard
			current.enter()
		else:
			self.widgets.remove(self.checkbutton)

	def handle(self,event):
		if self.show and event.type == MOUSEBUTTONDOWN and event.button == 1:
			if self.showrect.collidepoint(event.pos):
				self.moveshow.connect(1)
				self.showhitten.connect(1)
			elif self.hiderect.collidepoint(event.pos):
				self.movehide.connect(1)
				self.hidehitten.connect(1)
		super().handle(event)

	def enter(self):
		pygame.event.set_blocked(None)
		pygame.event.set_allowed([
			QUIT,
			WINDOWFOCUSLOST,
			WINDOWFOCUSGAINED,
			MOUSEMOTION,
			MOUSEBUTTONDOWN,
			MOUSEBUTTONUP,
			])


def crash(r1, r2):
	xcrash = abs(r1[0]+r1[2]/2-r2[0]-r2[2]/2) <= (r1[2]+r2[2])/2
	ycrash = abs(r1[1]+r1[3]/2-r2[1]-r2[3]/2) <= (r1[3]+r2[3])/2
	return xcrash and ycrash


def drawmap(target,startpos,width,side,color):
	r = pygame.Rect(0,0,width,width)
	for x in range(side):
		xpos = startpos[0]+width*1.25*x
		r.left = xpos
		for y in range(side):
			ypos = startpos[1]+width*1.25*y
			r.top = ypos
			target.fill(color,r)


def intersect(list1, list2):
	result = []
	for s in list1:
		if s in list2:
			result.append(s)
	return result


def minus(l1, l2, inplace=False):
	if inplace:
		for s in l2:
			if s in l1:
				l1.remove(s)
	else:
		result = l1.copy()
		for s in l2:
			if s in result:
				result.remove(s)
		return result


def density(pos, s, hitten):
	l = int(s/2)
	lefttop = tupleminus(pos,(l,l),minimum=0)
	rightbottom = tupleadd(pos,(l,l),maximum=11)
	s = tupleadd(tupleminus(rightbottom,lefttop),(1,1))
	s = s[0]*s[1]
	count = 0
	for pos in hitten:
		if pos[0]>=lefttop[0] and pos[1]>=lefttop[1] and pos[0]<=rightbottom[0] and pos[1]<=rightbottom[1]:
			count += 1
	return count/s


offset = [
[[(2,0),(0,1),(1,1),(2,1),(3,1),(4,1),(2,2),(1,3),(2,3),(3,3),(2,4)],
[(4,2),(3,0),(3,1),(3,2),(3,3),(3,4),(2,2),(1,1),(1,2),(1,3),(0,2)],
[(2,4),(0,3),(1,3),(2,3),(3,3),(4,3),(2,2),(1,1),(2,1),(3,1),(2,0)],
[(0,2),(1,0),(1,1),(1,2),(1,3),(1,4),(2,2),(3,1),(3,2),(3,3),(4,2)]],
[[(1,0),(0,1),(1,1),(2,1),(1,2),(1,3)],
[(3,1),(2,0),(2,1),(2,2),(1,1),(0,1)],
[(1,3),(0,2),(1,2),(2,2),(1,1),(1,0)],
[(0,1),(1,0),(1,1),(1,2),(2,1),(3,1)]],
[[(0,0),(0,1)],
[(1,0),(0,0)],
[(0,1),(0,0)],
[(0,0),(1,0)]]
]
bgoffset = [
[(4,4)]*4,
[(2,3),(3,2)]*2,
[(0,1),(1,0)]*2
]

pygame.init()
clock = pygame.time.Clock()
screeninfo = pygame.display.Info()
size = (screeninfo.current_w, screeninfo.current_h)
ration = round(size[1]*0.8/720,1)
if ration >= 1:
	ration = 1
ration = 1
width, height = size = (1280*ration, 720*ration)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('打飞机V0.7单机版')
icon = pygame.image.load('images/icon.png').convert_alpha()
pygame.display.set_icon(icon)
aidifficulty = None
maprect = pygame.Rect(0,0,12,12)

BGBLUE = (0,0,40)
BUTTONBLUE = (80,128,255)
BARGOLD = (255,200,0)
FAKEWHITE = (230,230,230)
FRIENDBLUE = (128,128,255)
ENEMYRED = (255,128,128)
RED = (255,0,0)
PLANEORANGE = (255,170,0)
MAPBLUE = (70,70,100)
MESSAGEYELLOW = (255,255,128)
DARKFRIENDBLUE = (64,64,128)
DARKENEMYRED = (128,64,64)
SLIDEPERPLE = (150,0,255)
BLACK = (0,0,0)

douyu40 = pygame.font.Font('fonts/斗鱼追光体.otf', int(40*ration))
douyu75 = pygame.font.Font('fonts/斗鱼追光体.otf', int(75*ration))
benmo20 = pygame.font.Font('fonts/本墨竞圆.ttf', int(20*ration))
haiwen30 = pygame.font.Font('fonts/海纹体.ttf', int(30*ration))
jimo200 = pygame.font.Font('fonts/即墨体.ttf', int(200*ration))

planeicon = pygame.image.load('images/planeicon.png').convert_alpha()
s = planeicon.get_size()
planeicon = pygame.transform.smoothscale(planeicon,(s[0]*ration,s[1]*ration))
author_signal = pygame.image.load('images/author_signal.png').convert_alpha()
s = author_signal.get_size()
author_signal = pygame.transform.smoothscale(author_signal,(s[0]*ration,s[1]*ration))
playerhead = pygame.image.load('images/playerhead.png').convert_alpha()
s = playerhead.get_size()
playerhead = pygame.transform.smoothscale(playerhead,(s[0]*ration,s[1]*ration))
wheel = pygame.image.load('images/wheel.png').convert_alpha()
s = wheel.get_size()
wheel = pygame.transform.smoothscale(wheel,(s[0]*ration,s[1]*ration))
pointer = pygame.image.load('images/pointer.png').convert_alpha()
s = pointer.get_size()
pointer = pygame.transform.smoothscale(pointer,(s[0]*ration,s[1]*ration))
pauseimg = pygame.Surface(size,flags=HWSURFACE|SRCALPHA)
pauseimg.fill((0,0,0,180))
pausetip = douyu40.render('游戏已暂停，单击任意位置继续...',True,FAKEWHITE)
pauserect = pausetip.get_rect(center=(width/2,height/2))
pauseimg.blit(pausetip,pauserect)

flash = Flash()
prepareboard = PrepareBoard()
changepage = ChangePage()
fightboard = FightBoard()
endboard = EndBoard()

current = flash
current.enter()
active = True
ticks = 60
while True:
	clock.tick(ticks)
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == WINDOWFOCUSLOST:
			active = False
			ticks = 10
			screen.blit(pauseimg,(0,0))
			pygame.display.flip()
		elif event.type == WINDOWFOCUSGAINED:
			active = True
			ticks = 60
			break
		elif active:
			current.handle(event)
	if active:
		if current.delay == 1:
			current.trigger()
		if current.delay:
			current.delay -= 1
		current.paste(screen)
		fps = benmo20.render('FPS:'+str(int(clock.get_fps())),True,FAKEWHITE)
		screen.blit(fps,(0,0))
		pygame.display.flip()
