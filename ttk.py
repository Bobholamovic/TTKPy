"""
A Python Remake of Calculator Game "The Three Kingdoms"
---------------------------------------------------------------------

@author: Bobholamovic
@date: 2018-12-19
@note:
	It is a boring afternoon off the Internet. 
	
TODO:
	1. Senario class
	2. Game class
	3. Main entrance
	4. GlobalControl class
"""
import os
import random

from abc import ABCMeta, abstractmethod, abstractproperty
from enum import Enum

MILITARY_PAY = 10
RECRUIT_BASE = 1000
FAME_BASE = 10
EARNING = 5000
GRAIN = 10000

class Mode(Enum):
	EPIC = 1
	ADVENTURE = 2

class ActionID(Enum):
	ATTACK = 1
	RECUPERATE = 2
	RECRUIT = 3
	TRAIN = 4
		
class AI(metaclass=ABCMeta):
	def __init__(self):
		super(AI, self).__init__()
	@abstractmethod
	def get_next_action(self, others):
		pass
		
class AISim(AI):
	def __init__(self, attk_idx=0.5):
		super(AISim, self).__init__()
		assert(attk_idx < 1.0)
		self.attk_idx = attk_idx
	def get_next_action(self, others):
		if random.random() < self.attk_idx:
			return ActionID.ATTACK, (others[random.randint(len(others))], )
		return random.randint(2,4)
		
		
class Senario	

class Switcher:
	def __init__(self, opt_lst, idx_lst=None):
		self.update(opt_lst, idx_lst)
	def switch(self, arg):
		return self.opt_dict.get(arg)
	def update(self, opt_lst):
		self.opt_dict = dict(enumerate(opt_lst)) if not idx_lst else dict(zip(idx_list, opt_lst))
	
class NonNegative:
		def __init__(self, init):
			super(NonNegative, self).__init__()
			self._data = init
		def __get__(self, instance, owner):
			return self._data
		def __set__(self, instance, value):
			if value < 0:
				raise ValueError("Negative Value")
			self._data = value
			
class Lord:
	r"""
	Class Lord
	
		The warlords are basic units of the game. 
		Panic in troubled times, the destruction everywhere. And the heros
		fight among rivals for the throne. 
		
		"Go and chase the deer! "
	"""
	n_lords = 0	# A counter of the total number of lords
	lord_dict = {}
	act_switcher = Switcher((attack, recuperate, recruit, train), ActionID)
	
	def __init__(self, name, coin, food, troop, charm, polit, milit, fame, troop_milit, aggr):
		super(Lord, self).__init__()
		self._name = name
		self._charm = charm
		self._polit = polit
		self._milit = milit
		self._troop_milit = troop_milit
		self._fame = fame
		self._AI = AI(aggr)
		
		self.coin = NonNegative(coin)
		self.food = NonNegative(food)
		self.troop = NonNegative(troop)
		self.active = True
		
	def __new__(cls, *args, **kwargs):
		if not cls.lord_dict.get(cls):
			cls.lord_dict[cls] = super(Lord, cls).__new__(cls, *args, **kwargs)
			cls.n_lords += 1
		return cls.lord_dict[cls]
	
	@property
	def name(self):
		return self._name
	
	@property
	def charm(self):
		return self._charm
		
	@property
	def polit(self):
		return self._polit
	
	@property
	def milit(self):
		return self._milit
	
	def recruit(self):
		try:
			raw = (self._fame*0.7 + self._charm*0.3)*random.random() * RECRUIT_BASE)
			self.coin = self.coin - raw*MILITARY_PAY
			self.troop = self.troop + raw
		except ValueError:
			self.troop = self.troop + int(self.coin/MILITARY_PAY)
			self.coin = 0
	
	def _defend(self, dmg):
		fame = FAME_BASE*max(self._troop, dmg)
		try:
			self.troop = self.troop - dmg
			self._fame = self._fame - fame
		except ValueError:
			self.die()
		return self.active
		
	def attack(self, rival):
		attk, defen = (self, rival) if (random.random()>0.6) else (rival, self)
		cs_rate = (0.001+random.random()/100) if (random.random() < 0.1) else 1
		dmg = attk.troop * (attk._milit*0.4 + attk._troop_milit*0.6) / cs_rate
		
		if defen._defend(dmg): 
			cs_rate_bk = (0.001+random.random()/100) if (random.random() < 0.2) else 1
			dmg_bk = defen.troop * (defen._milit*0.4 + defen._troop_milit*0.6) / cs_rate_bk
			attk._defend(dmg_bk)
		
	def recuperate(self):
		self.coin = self.coin + (self._polit+random.random()/3)*EARNING
		self.food = self.food + (self._polit+random.random()/3)*GRAIN
		
	def train(self):
		degree = (self._milit*0.2) if (random.random()>0.1) else (-self._milit*0.1)
		self._troop_milit = self._troop_milit + degree
		
	def die(self):
		self.coin = 0
		self.food = 0
		self.troop = 0
		self._fame = 0
		self.active = False
		self.n_lords -= 1
	
	def next_action(self, act_id, *param):
		act_func = act_switcher(act_id)
		act_func(self, *param)
		
	def AI_next_action(self, others):
		act_id, act_param = self.AI.get_next_action_par(others)
		self.next_action(act_id, *act_param)

class Event(metaclass = ABCMeta):
	@classmethod
	@abstractproperty
	def info(cls):
		pass
	@classmethod
	@abstractproperty
	def desc(cls):
		pass
	@classmethod
	def disp_str(cls):
		return f"发生事件：{}  {}".format(cls.info, cls.desc)
	@classmethod
	@abstractmethod
	def trigger(cls, obj):
		pass
	@classmethod
	def global_effect(cls, obj_lst):
		for obj in obj_lst:
			cls.trigger(obj)
			
class EvtDrought(Event):
	@classmethod
	@property
	def info(cls):
		return "天降大旱"
	@classmethod
	@property
	def desc(cls):
		return "粮食随机减少"
	@classmethod
	def trigger(cls, obj):
		obj.food = obj.food*(1.0-random.random()/5)
		
class EvtHarvest(Event):
	@classmethod
	@property
	def info(cls):
		return "大丰收"
	@classmethod
	@property
	def desc(cls):
		return "粮食随机增加"
	@classmethod
	def trigger(cls, obj):
		obj.food = obj.food*(1.0+random.random()/5)
		
class EvtPlague(Event):
	@classmethod
	@property
	def info(cls):
		return "瘟疫"
	@classmethod
	@property
	def desc(cls):
		return "兵士随机减员"
	@classmethod
	def trigger(cls, obj):
		obj.troop = obj.troop*(1.0-random.random()/10)
		
class GlobalControl:			
	class CLIGame(CLI):
		def 
	def __init__(self, data_dict, player, mode=Mode.EPIC, 
							evt_lst = (EvtDrought, EvtHarvest, EvtPlague)):
		super(GlobalControl, self).__init__()
		data_dict = self.data_dict
		self.player = player
		self.mode = mode
		self.evt_switcher = Switcher(evt_lst)
		self.cli_ctrl = CLIGame
		
	def check(self):
		len_dict = len(self.data_dict)
		if len_dict == 0:
			return False, "尴尬了，没有幸存者"
		elif len_dict == 1:
			return False, f"{}势力获得胜利".format(list(self.data_dict)[0].name)
			
		for k, v in self.data_dict.items():
			if not v.active:
				if v == self.player and self.mode == Mode.ADVENTURE:
					return False, f"{}势力被消灭".format(self.player.name)
				del v
				self.data_dict.pop(k)
		return True, ""
	
	def report_event(self):
		idx = int(random.random()*10)
		evt = self.evt_switcher.switch(idx)
		evt.global_effect()
		return evt.disp_str
		
	def next_turn(self):
		for v in self.data_dict.values():
			if v == self.player:
				act_id, param = self.cli_ctrl.get_command("请输入指令：")
				v.next_action(act_id, *param)
			else:
				others = [obj for obj in self.data_dict.values() if obj is not v]
				v.AI_next_action(others)

class CLI:
	@staticmethod
	def print_info(info):
		print(info)
	@staticmethod
	def println(info):
		print_info(info)
		os.system("pause")
	@staticmethod
	def show_help():
		pass
	@staticmethod
	def clear():
		os.system("cls")
	@staticmethod
	def show_welcome():
		pass
	@staticmethod
	def get_command(prompt):
		return input(prompt)

class Game:
	def __new__(cls, *args, **kwargs):
		# Singleton
		return (hasattr(cls, '_instance') and getattr(cls, '_instance')) \
					or (setattr(cls, '_instance', object.__new__(cls, *args, **kwargs)) or getattr(cls, '_instance'))
					