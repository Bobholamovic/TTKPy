"""
A Python Remake of Calculator Game "The Three Kingdoms"
---------------------------------------------------------------------

@author: Bobholamovic
@date: 2018-12-19
@note:
	It is a boring afternoon off the Internet. 
	
TODO:
	1. Senario class
	2. Lords
"""
import os
import random

from abc import ABCMeta, abstractmethod, abstractproperty

MILITARY_PAY = 10
RECRUIT_BASE = 1000
FAME_BASE = 10
EARNING = 5000
GRAIN = 10000
	
class Enum:
	def __init__(self, **kwargs):
		self.ele_dict = kwargs
		for k, v in self.ele_dict.items():
			setattr(self, k, v)
	def __len__(self):
		return len(self.ele_dict)

mode_id = Enum(EPIC=1, ADVENTURE=2)		
senario_id = Enum(TEST_SENARIO=1)
	
class AI(metaclass=ABCMeta):
	def __init__(self):
		super(AI, self).__init__()
	@abstractmethod
	def get_next_action(self, others):
		pass
		
class AISim(AI):
	def __init__(self, attk_rate=0.5):
		super(AISim, self).__init__()
		assert(attk_rate < 1.0)
		self.attk_rate = attk_rate
	def get_next_action(self, others):
		if random.random() < self.attk_rate:
			return Lord.actions.ATTACK, (others[random.randint(len(others))], )
		return Lord.actions[random.randint(2,4)]

class Switcher:
	def __init__(self, opt_lst, idx_lst=None):
		self.update(opt_lst, idx_lst)
	def switch(self, arg):
		return self.opt_dict.get(arg)
	def update(self, opt_lst, idx_lst):
		self.opt_dict = dict(enumerate(opt_lst)) if not idx_lst else dict(zip(idx_lst, opt_lst))
	
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
		
		self.actions = actions(self)
		
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
		
	@property
	def fame(self):
		return self._fame
	
	def recruit(self):
		try:
			raw = (self._fame*0.7 + self._charm*0.3)*random.random() * RECRUIT_BASE
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
		act_func = self.actions[act_id]
		act_func(self, *param)
		return act_id, param
		
	def AI_next_action(self, others):
		act_id, act_param = self.AI.get_next_action_par(others)
		return self.next_action(act, *act_param)

	class actions(Enum):
		def __init__(self, lord):
				_action_func = (lord.attack, lord.recuperate, lord.recruit, lord.train)
				for (i, act) in enumerate(lord.actions):
					setattr(actions, upper(act.__name__), i)
		def __len__(self):
			return len(_action_func)
		def __get_item__(self, key):
			return _action_func[key]
				
	
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
		return "发生事件：{}\t{}".format(cls.info, cls.desc)
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
	def __init__(self, lord_lst, player, mode=mode_id.EPIC, 
							evt_lst = (EvtDrought, EvtHarvest, EvtPlague)):
		super(GlobalControl, self).__init__()
		self.lord_lst = lord_lst
		self.player = player
		self.mode = mode
		self.evt_switcher = Switcher(evt_lst)
		self.lord_act_desc = ["攻击", "休养", "征募", "练兵"]
		
	def check(self):
		n_lords_cur = len(self.lord_lst)
		if n_lords_cur == 0:
			return False, "尴尬了，没有幸存者"
		elif n_lords_cur == 1:
			return False, "{}势力获得胜利".format(self.lord_lst[0].name)
			
		for l in self.lord_lst:
			if not l.active:
				if l == self.player and self.mode == mode_id.ADVENTURE:
					return False, "{}势力被消灭".format(self.player.name)
				del l
		return True, ""
	
	def report_event(self):
		idx = int(random.random()*10)
		evt = self.evt_switcher.switch(idx)
		CLI.print_ln(evt.disp_str)
		evt.global_effect()
	
	def show_action_log(self, this, act_id, param):
		if act_id == Lord.actions.ATTACK:
			log_info = "{} 向 {} 发起进攻".format(this.name, self.param[0].name)
		else:
			log_info = "{} {}".format(this.name, self.lord_act_desc[act_id])
		CLI.println(log_info)
		
	def do_next_turn(self):
		for i, l in enumerate(self.lord_lst):
			if l == self.player:
				act_id, param = self.get_commands()
				l.next_action(act, *param)
			else:
				others = self.lord_lst[:i]+self.lord_lst[(i+1):]
				act_id, param = l.AI_next_action(others)
				
			self.show_action_log(l, act_id, param)
	
	def show_states(self):
			head = "编号\t姓名\t金钱\t粮食\t士兵\t声望\t军队战斗力"
			CLI.print_info(head)
			CLI.print_info('-'*len(head))
			for i, l in enumerate(self.lord_lst):
				CLI.print_info("{no:02d}\t{name}\t{coin}\t{food}\t{troop}\t{fame}\t{troop_milit}".format(
											no=i, name=l.name, coin=l.coin, food=l.food, troop=l.troop, 
											fame=l.fame, troop_milit=l.troop_milit))
	
	def show_cmds(self):
		for i, cmd in enumerate(self.lord_act_desc):
			CLI.print_info("[{}] {}".format(i, cmd))
			
	def get_commands(self):
		self.show_cmds()
		act_id = CLI.safe_input_enum("请输入指令编号：", Lord.actions, "非法指令！")			
		if act_id == Lord.actions.ATTACK:
			while True:
				try:
					act_param = CLI.safe_input_list_elem("请选择攻击对象编号：", self.lord_lst, "非法的攻击对象！")
					assert(act_param is not self.player)
				except:
					CLI.print_info("不能攻击自己！")
				else:
					break
			
		return act_id, act_param
		
	def main_loop(self):
		while True:
			chk_stat, chk_str = self.check()
			if not chk_stat:
				CLI.pause()
				CLI.print_ln(chk_str)
				return 
			
			self.show_states()
			self.report_event()
			self.do_next_turn()
			
			CLI.printed("本月结束")
		
	
class CLI:
	@staticmethod
	def print_info(info):
		print(info)
	@staticmethod
	def pause():
		os.system("pause")
	@staticmethod
	def clear():
		os.system("cls")
	@staticmethod
	def println(info):
		CLI.print_info(info)
		CLI.pause()
	@staticmethod
	def printed(info):
		CLI.println(info)
		CLI.clear()
	@staticmethod
	def get_command(prompt):
		return input(prompt)
	@staticmethod
	def safe_input_enum(prompt, enum_cls, err_str):
		while True:
			try:
				val = int(CLI.get_command(prompt))
				assert(val >0 and val <= len(enum_cls))
			except TypeError:
				# Handling codes could and should differ for differnt error types
				CLI.print_info(err_str)
			except AssertionError:
				CLI.print_info(err_str)
			except ValueError:
				CLI.print_info(err_str)
			else:
				break			
		return val
	@staticmethod
	def safe_input_list_elem(prompt, lst, err_str):
		while True:
			try:
				idx = int(CLI.get_command(prompt))
				val = lst[idx]
			except TypeError:
				# CLI.print_info(err_str + " Type Error")
				CLI.print_info(err_str)
			except IndexError:
				CLI.print_info(err_str)
			except ValueError:
				CLI.print_info(err_str)
			else:
				break
		return val
		
class Senario:
	senarios = {}
	def __init__(self, lord_lst, evt_lst):
		self.lord_lst = lord_lst
		self.evt_lst = evt_lst
	def show_states(self):
			head = "编号\t姓名\t初始金钱\t初始粮食\t初始士兵\t初始声望\t魅力\t政治能力\t军事能力\t军队战斗力"
			CLI.print_info(head)
			CLI.print_info('-'*len(head))
			for i, l in enumerate(self.lord_lst):
				CLI.print_info("{no:02d}\t{name}\t{coin}\t{food}\t{troop}\t{fame}\t{charm}\t{polit}\t{milit}\t{troop_milit}"
											.format(
											no=i, name=l.name, coin=l.coin, food=l.food, troop=l.troop, 
											fame=l.fame, charm=l.charm, polit=self.polit, milit=self.milit, troop_milit=self.troop_milit
														)
										)		
Senario.senarios[senario_id.TEST_SENARIO] = Senario((), (EvtDrought, EvtHarvest, EvtPlague))

class Game:
	def __init__(self):
		super(Game, self).__init__()
		self.init_game()
	
	def show_welcome(self):
		pass
	def show_help(self):
		pass
	def show_settings(self):
		pass
	def set_game(self):
		CLI.print_info("选择游戏模式：[1] Epic\t[2] ADVENTURE")
		self.mode = CLI.safe_input_enum("请输入指令编号：", mode_id, "非法指令！")
		CLI.clear()
		CLI.print_info("选择剧本：[1] 测试剧本")
		sen_id = CLI.safe_input_enum("请输入指令编号：", senario_id, "非法指令！")
		CLI.clear()
		self.senario = Senario.senarios.get(sen_id)
		self.senario.show_states()
		self.player = CLI.safe_input_list_elem("请选择势力：", self.senario.lord_lst, "非法输入！")
		self.gc = GlobalControl(self.senario.lord_lst, self.player, self.mode, self.senario.evt_lst)
		
	def init_game(self):
		self.show_welcome()
		self.set_game()
		self.show_settings()
	
	def run(self):
		self.gc.main_loop()
		
	def __new__(cls, *args, **kwargs):
		# Singleton
		return (hasattr(cls, '_instance') and getattr(cls, '_instance')) \
					or (setattr(cls, '_instance', object.__new__(cls, *args, **kwargs)) or getattr(cls, '_instance'))
					
					
if __name__ == '__main__':
	new_game = Game()
	new_game.run()
	