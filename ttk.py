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
	3. Perhaps Action classes and callback functions can be used to decouple the classes
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

mode_id = Enum(EPIC=0, ADVENTURE=1)		
senario_id = Enum(TEST_SENARIO=0)
	
class AI(metaclass=ABCMeta):
	def __init__(self):
		super(AI, self).__init__()
	@abstractmethod
	def get_next_action_par(self, others):
		pass
		
class AISim(AI):
	def __init__(self, attk_rate=0.5):
		super(AISim, self).__init__()
		assert(attk_rate < 1.0)
		self.attk_rate = attk_rate
	def get_next_action_par(self, this, others):
		if random.random() < self.attk_rate:
			return this.actions.ATTACK, (others[random.randint(0, len(others)-1)], )
		return this.actions[random.randint(2,4)]

class Switcher:
	def __init__(self, opt_lst, idx_lst=None):
		self.update(opt_lst, idx_lst)
	def switch(self, arg):
		return self.opt_dict.get(arg)
	def rand_switch(self):
		return self.opt_dict.get(self.idx_lst[random.randint(0, len(self.idx_lst)-1)]) 
	def update(self, opt_lst, idx_lst):
		if not idx_lst:
			self.opt_dict = dict(enumerate(opt_lst))
			self.idx_lst = list(range(len(opt_lst)))
		else:
			self.opt_dict = dict(zip(idx_lst, opt_lst))
			self.idx_lst = idx_lst
			
class Lord:
	r"""
	Class Lord
	
		The warlords are basic units of the game. 
		Panic in troubled times, the destruction everywhere. And the heros
		fight among rivals for the throne. 
		
		"Go and chase the deer! "
	"""
	# n_lords = 0	# A counter of the total number of lords
	# lord_dict = {}
	
	class actions(Enum):
		def __init__(self, lord):
				self._action_func = (lord.attack, lord.recuperate, lord.recruit, lord.train)
				for (i, act) in enumerate(self._action_func):
					setattr(self, act.__name__.upper(), i)
		def __len__(self):
			return len(self._action_func)
		def __getitem__(self, key):
			return self._action_func[key]
			
	def __init__(self, name, coin, food, troop, charm, polit, milit, fame, troop_milit, aggr):
		super(Lord, self).__init__()
		self._name = name
		self._charm = charm
		self._polit = polit
		self._milit = milit
		self._troop_milit = troop_milit
		self._fame = fame
		self._AI = AISim(aggr)
		
		self.coin = coin
		self.food = food
		self.troop = troop
		
		self.active = True
		
		self.actions = Lord.actions(self)
		
	# def __new__(cls, *args, **kwargs):
		# if not cls.lord_dict.get(cls):
			# cls.lord_dict[cls] = super(Lord, cls).__new__(cls, *args, **kwargs)
			# cls.n_lords += 1
		# return cls.lord_dict[cls]
	
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

	@property
	def troop_milit(self):
		return self._troop_milit
		
	def recruit(self):
		troop_old = self.troop
		raw = (self._fame*0.7 + self._charm*0.3)*random.random() * RECRUIT_BASE
		if self.coin < raw*MILITARY_PAY:
			self.coin -= raw*MILITARY_PAY
			self.troop += raw
		else:
			self.troop = self.troop + int(self.coin/MILITARY_PAY)
			self.coin = 0
		self._troop_milit = self._troop_milit*troop_old/self.troop
		
	def _defend(self, dmg):
		fame = FAME_BASE*max(self.troop, dmg)
		if (self.troop > dmg) and (self._fame > fame):
			self.troop = self.troop - dmg
			self._fame = self._fame - fame
		else:
			self.die()
		return self.active
		
	def attack(self, rival):
		attk, defen = (self, rival) if (random.random()>0.6) else (rival, self)
		cs_rate = (0.001+random.random()/100) if (random.random() < 0.1) else 1
		dmg = attk.troop * (attk._milit*0.4 + attk._troop_milit*0.3 + attk.food/attk.troop*0.3) / cs_rate
		
		if defen._defend(dmg): 
			cs_rate_bk = (0.001+random.random()/100) if (random.random() < 0.2) else 1
			dmg_bk = defen.troop * (defen._milit*0.2 + defen._troop_milit*0.3 + attk.food/attk.troop*0.5) / cs_rate_bk
			attk._defend(dmg_bk)
		
	def recuperate(self):
		self.coin = self.coin + (self._polit+random.random()/3)*EARNING
		self.food = self.food + (self._polit+random.random()/3)*GRAIN
		
	def train(self):
		degree = (self._milit*0.2) if (random.random()>0.1) else (-self._milit*0.1)
		self._troop_milit = max(1.0, self._troop_milit + degree)
		
	def die(self):
		self.coin = 0
		self.food = 0
		self.troop = 0
		self._fame = 0
		self.active = False
		# self.n_lords -= 1
	
	def next_action(self, act_id, *param):
		act_func = self.actions[act_id]
		act_func(*param)
		return act_id, param
		
	def AI_next_action(self, others):
		act_id, act_param = self._AI.get_next_action_par(self, others)
		return self.next_action(act_id, *act_param)
				
class LiuBei(Lord):
	def __init__(self, coin, food, troop):
		super(LiuBei, self).__init__("刘备", coin, food, troop, 0.9, 0.7, 0.6, 0.9, 0.5, 0.4)
		
class SunCe(Lord):
	def __init__(self, coin, food, troop):
		super(SunCe, self).__init__("孙策", coin, food, troop, 0.7, 0.4, 0.8, 0.7, 0.6, 0.8)
		
class CaoCao(Lord):
	def __init__(self, coin, food, troop):
		super(CaoCao, self).__init__("曹操", coin, food, troop, 0.8, 0.8, 0.8, 0.6, 0.6, 0.9)

				
class Event(metaclass = ABCMeta):
	@abstractproperty
	def info(self):
		pass
	@abstractproperty
	def desc(self):
		pass
	def get_disp_str(self):
		return "发生事件：{}\t{}".format(self.info, self.desc)
	@abstractmethod
	def trigger(self, obj):
		pass
	def global_effect(self, obj_lst):
		for obj in obj_lst:
			self.trigger(obj)
			
class EvtDrought(Event):
	@property
	def info(self):
		return "天降大旱"
	@property
	def desc(self):
		return "粮食随机减少"
	def trigger(self, obj):
		obj.food = obj.food*(1.0-random.random()/5)
		
class EvtHarvest(Event):
	@property
	def info(self):
		return "大丰收"
	@property
	def desc(self):
		return "粮食随机增加"
	def trigger(self, obj):
		obj.food = obj.food*(1.0+random.random()/5)
		
class EvtPlague(Event):
	@property
	def info(self):
		return "瘟疫"
	@property
	def desc(self):
		return "兵士随机减员"
	def trigger(self, obj):
		obj.troop = obj.troop*(1.0-random.random()/10)
		
class GlobalControl:			
	def __init__(self, lord_lst, evt_lst, player, mode=mode_id.EPIC):
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
		
		return True, ""
		
	def check_single(self, lord):
		return not lord.active
	
	def report_event(self):
		evt = self.evt_switcher.rand_switch()
		CLI.println(evt.get_disp_str())
		evt.global_effect(self.lord_lst)
	
	def show_action_log(self, this, act_id, param):
		if act_id == this.actions.ATTACK:
			log_info = "{} 向 {} 发起进攻".format(this.name, param[0].name)
			if self.check_single(param[0]):
				log_info += "\n{}势力被消灭了".format(param[0].name)
				self.lord_lst.remove(param[0])	# Remove the dead one from the global list
			if self.check_single(this):
				log_info += "\n{}势力被消灭了".format(this.name)
				self.lord_lst.remove(this) 
		else:
			log_info = "{} {}".format(this.name, self.lord_act_desc[act_id])
		CLI.println(log_info)
		
	def do_next_turn(self):
		for i, l in enumerate(self.lord_lst):
			if l == self.player:
				act_id, param = self.get_commands()
				l.next_action(act_id, *param)
			else:
				others = self.lord_lst[:i]+self.lord_lst[(i+1):]
				act_id, param = l.AI_next_action(others)
			self.show_action_log(l, act_id, param)
	
	def show_states(self):
			CLI.clear()
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
		act_id = CLI.safe_input_enum("请输入指令编号：", self.player.actions, "非法指令！")		
		act_param = ()
		if act_id == self.player.actions.ATTACK:
			while True:
				try:
					act_param = act_param+(CLI.safe_input_list_elem("请选择攻击对象编号：", self.lord_lst, "非法的攻击对象！"), )
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
				CLI.println(chk_str)
				return 
			
			self.show_states()
			self.report_event()
			self.show_states()
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
				assert(val >=0 and val < len(enum_cls))
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
			for i, l in enumerate(self.lord_lst):
				CLI.print_info("{no:02d}\t{name}\t{coin}\t{food}\t{troop}\t{fame}\t{charm}\t{polit}\t{milit}\t{troop_milit}"
											.format(
											no=i, name=l.name, coin=l.coin, food=l.food, troop=l.troop, 
											fame=l.fame, charm=l.charm, polit=l.polit, milit=l.milit, troop_milit=l.troop_milit
														)
										)		
Senario.senarios[senario_id.TEST_SENARIO] = Senario([
																										CaoCao(100, 1000, 1000), 
																										SunCe(50, 800, 400), 
																										LiuBei(10, 1000, 100)
																									], (EvtDrought(), EvtHarvest(), EvtPlague()))

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
		CLI.print_info("选择游戏模式：[0] Epic\t[1] ADVENTURE")
		self.mode = CLI.safe_input_enum("请输入指令编号：", mode_id, "非法指令！")
		CLI.clear()
		CLI.print_info("选择剧本：[0] 测试剧本")
		sen_id = CLI.safe_input_enum("请输入指令编号：", senario_id, "非法指令！")
		CLI.clear()
		self.senario = Senario.senarios.get(sen_id)
		self.senario.show_states()
		self.player = CLI.safe_input_list_elem("请选择势力：", self.senario.lord_lst, "非法输入！")
		self.gc = GlobalControl(self.senario.lord_lst, self.senario.evt_lst, self.player, self.mode)
		
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
	