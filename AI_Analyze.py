import random
import time


shape_offset = {
	# 相对坐标(x,y),(0,0)为左上角，第一个坐标都是机头
	# 包含四个方向，首个为向上，其后依次顺时针旋转90°
	# 通过外部一个绝对坐标进行偏移得到整架飞机的绝对坐标

	'big': [
		[(2,0),(0,1),(1,1),(2,1),(3,1),(4,1),(2,2),(1,3),(2,3),(3,3),(2,4)],
		[(4,2),(3,0),(3,1),(3,2),(3,3),(3,4),(2,2),(1,1),(1,2),(1,3),(0,2)],
		[(2,4),(0,3),(1,3),(2,3),(3,3),(4,3),(2,2),(1,1),(2,1),(3,1),(2,0)],
		[(0,2),(1,0),(1,1),(1,2),(1,3),(1,4),(2,2),(3,1),(3,2),(3,3),(4,2)]
		],

	'middle': [
		[(1,0),(0,1),(1,1),(2,1),(1,2),(1,3)],
		[(3,1),(2,0),(2,1),(2,2),(1,1),(0,1)],
		[(1,3),(0,2),(1,2),(2,2),(1,1),(1,0)],
		[(0,1),(1,0),(1,1),(1,2),(2,1),(3,1)]
		],

	'small': [
		[(0,0),(0,1)],
		[(1,0),(0,0)],
		[(0,1),(0,0)],
		[(0,0),(1,0)]
		],
}

rect = {
	# 包含飞机的最小矩形 [width, height]，同样是相对坐标以及包含四个方向
	# 起始坐标默认为(0,0)，这里存储的分别是长和宽
	# 与 shape_offset 一一对应

	'big': [(4,4)]*4,
	'middle': [(2,3),(3,2)]*2,
	'small': [(0,1),(1,0)]*2,
}


class Plane:
	def __init__(self, model):
		self.model = model  # model 是上面字典里的一个键
		self.shape_offset = shape_offset[model]  # 得到四个方向的相对形状

	def randomly_place(self):
		self.anchor = random.randint(0,3)  # 随机方向
		# anchor可能值为0、1、2、3，用其作为索引得到单独方向的形状和矩形
		startpos = (random.randint(0,size-1), random.randint(0,size-1))  # 随机坐标

		self.rect = startpos + rect[self.model][self.anchor]  # 得到绝对矩形
		self.poses = [
			(startpos[0]+pos[0], startpos[1]+pos[1])
			for pos in self.shape_offset[self.anchor]
			]  # 得到绝对形状(列表生成式)
		self.head = self.poses[0]

	def out_of_bound(self):
		# 判断是否出界，x、y有一个出界即为出界
		x = self.rect[0] >= size-self.rect[2]
		y = self.rect[1] >= size-self.rect[3]
		return x or y


class Airport:
	def __init__(self, models: list):
		self.planes = [Plane(m) for m in models]  # 创建飞机

	def init_game(self):
		# 初始化游戏
		self.alive_planes = []
		for plane in self.planes:
			plane.randomly_place()
			while self.overlap(plane) or plane.out_of_bound():
				plane.randomly_place()
			self.alive_planes.append(plane)

		self.attack_points = []  # 打击的点
		self.hitten_points = []  # 命中的点
		self.miss_points = []  # 未命中的点

	def overlap(self, plane):
		# 检测飞机是否重叠
		for exist in self.alive_planes:
			if collide(exist.rect, plane.rect):
				return True
		return False

	def hit(self, pos):
		# 攻击某个点
		if pos not in self.attack_points:
			self.attack_points.append(pos)
		for plane in self.alive_planes:
			if pos in plane.poses:
				if pos not in self.hitten_points:
					self.hitten_points.append(pos)
				if pos == plane.head:
					self.alive_planes.remove(plane)
				break
			elif pos not in self.miss_points:
				self.miss_points.append(pos)


def collide(r1, r2):
	# 判断两个矩形是否碰撞
	# 如果x、y方向上均重合，则为碰撞
	x = abs(r1[0]+r1[2]/2-r2[0]-r2[2]/2) <= (r1[2]+r2[2])/2
	y = abs(r1[1]+r1[3]/2-r2[1]-r2[3]/2) <= (r1[3]+r2[3])/2
	return x and y


size = 12  # 机场大小


class Ai:
	description = '这是Ai基类，不用于测试'  # 你可以更改这个属性，用来简单描述你的Ai模型

	def __init__(self):
		self.totaltimes = 0
		self.totaltime = 0
		self.total_centage = 0

	def endgame(self, airport):
		self.total_centage += len(set(airport.hitten_points))/len(airport.attack_points)

	def hit(self, airport):
		ana_time = time.time()
		pos = self.analyse(airport)
		ana_time = time.time() - ana_time
		airport.hit(pos)
		self.totaltimes += 1
		self.totaltime += ana_time

	def analyse(self, airport):
		'''
		请确保你的Ai模型继承自这个Ai基类，并自定义这个 analyze 方法，
		通过分析 airport 的 attack_points、hitten_points 和 miss_points
		三个列表里的数据(具体含义见上面的注释)，返回一个点的坐标(x,y)，
		这将决定你的Ai模型的强度
		'''
		pass


class Laji(Ai):
	description = '这是最垃圾的Ai，随机的乱打(不重复)'

	def analyse(self, airport):
		pos = (random.randint(0,size-1), random.randint(0,size-1))
		while pos in airport.attack_points:
			pos = (random.randint(0,size-1), random.randint(0,size-1))
		return pos


class XiaoLaji(Ai):
	description = '有策略，但没卵用，使打击点趋于均匀化分布'
	side = 4  # 检测半径

	def analyse(self, airport):
		pos = (random.randint(0,size-1), random.randint(0,size-1))
		average = len(airport.attack_points) / size**2
		while pos in airport.attack_points or self.density(pos, airport) > average:
			pos = (random.randint(0,size-1), random.randint(0,size-1))
		return pos

	def density(self, pos, airport):
		l = int(self.side/2)
		lefttop = (max(0,pos[0]-l), max(0,pos[1]-l))
		rightbottom = (min(size-1,pos[0]+l), min(size-1,pos[0]+l))
		s = (lefttop[0]-rightbottom[0], lefttop[1]-rightbottom[1])
		self.side = (s[0]-1, s[1]-1)
		self.side = self.side[0]*self.side[1]
		count = 0
		for pos in airport.attack_points:
			if pos[0]>=lefttop[0] and pos[1]>=lefttop[1] and pos[0]<=rightbottom[0] and pos[1]<=rightbottom[1]:
				count += 1
		return count/self.side

'''
ai = Laji()
ai = XiaoLaji()
经测试，这两个Ai模型胜率一模一样，而且都很垃圾。。。
由此证明 均匀化打击 啥也不是
'''

ai = XiaoLaji()  # 将你的Ai类的实例赋值给 ai 变量

print('***-> 打飞机Ai测试开始 <-***')
print('请确保你已了解游戏规则并根据注释正确地部署了你的Ai\n')
print(f'***-> 有关本次测试模型的信息 <-***\n{ai.description}\n')

m = input('>> 输入飞机模型名称：').split(',')  # 输入示例：big,middle,small ()
t = int(input('>> 输入测试轮数：'))
airport = Airport(m)

'''
注意，下面两句带有'测试中'的print()语句含有'\r'字符，
在Python自带的idle编辑器里不起作用，建议使用Pycharm或cmd命令行运行
'''
print(f'>> 测试中：0/{t}', end='')
r = 0
for s in range(t):
	r += 1
	print(f'\r>> 测试中：{r}/{t}', end='')
	airport.init_game()
	while airport.alive_planes:
		ai.hit(airport)
	ai.endgame(airport)

print('\n\n***-> 测试已完成 <-***')
averagetimes = ai.totaltimes/t
print(f'平均次数：{averagetimes} 次')
averagetime = ai.totaltime/ai.totaltimes
print(f'平均分析一次耗时：{round(averagetime*1000,3)} ms')
averagehit = ai.total_centage/t
print(f'平均命中率：{averagehit*100} %')
print(f'平均爆头率：{len(m)*t/ai.totaltimes*100} %')
