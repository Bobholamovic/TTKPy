"""
A Python Remake of Calculator Game "The Three Kingdoms"
---------------------------------------------------------------------

@author: Bobholamovic
@date: 2018-12-19
@note:
	It is a boring afternoon off the Internet. 
	
TODO:
	1. More scenarios and lords
	2. Perhaps Action classes and callback functions can be used to decouple the classes
	3. Show detailed action log
	4. Every-month basis like food consumption
"""
import os
import random

from abc import ABCMeta, abstractmethod, abstractproperty

MILITARY_PAY = 1
RECRUIT_BASE = 100
EARNING = 50
GRAIN = 100
FAME_BASE = 0.01
COL_LEN = 7
	
class Enum:
	def __init__(self, **kwargs):
		self.ele_dict = kwargs
		for k, v in self.ele_dict.items():
			setattr(self, k, v)
	def __len__(self):
		return len(self.ele_dict)

mode_id = Enum(EPIC=0, ADVENTURE=1)		
senario_id = Enum(TEST_SENARIO=0, DongHanMo=1)
	
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
		return random.randint(1,3), ()

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
			
	def __init__(self, name, coin, food, troop, morale,  charm, polit, milit, fame, aggr):
		super(Lord, self).__init__()
		self._name = name
		self._charm = charm
		self._polit = polit
		self._milit = milit
		self._morale = morale
		self._AI = AISim(aggr)
		
		self.coin = coin
		self.food = food
		self.troop = troop
		self.fame = fame
		
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
	def morale(self):
		return self._morale

	def _safe_sub(self, attr, s):
		x = getattr(self, attr)
		if x > s:
			x -= s
			setattr(self, attr, x)
			return True
		else:
			setattr(self, attr, 0)
			return False
			
	def recruit(self):
		troop_old = self.troop
		coin_old = self.coin
		raw = (self.fame*0.7 + self._charm*0.3)*random.random() * RECRUIT_BASE
		if self._safe_sub('coin', raw*MILITARY_PAY):
			self.troop += raw
		else:
			self.troop = self.troop + coin_old/MILITARY_PAY
			self.coin = 0
		self._morale = self._morale*troop_old/self.troop
			
	def _defend(self, dmg):
		grain = self.troop / 10
		if not self._safe_sub('food', grain):
			self.troop *= (random.random() * 0.5 + min(0.5, self._charm))
		if not self._safe_sub('troop', dmg):
			False
		return True
	
	def _pre_attack(self):
		if not self._safe_sub('coin', self.troop/10):
			self._morale *= (random.random() * 0.1 + 0.6)
		if not self._safe_sub('food', self.troop/5):
			self._morale *= (random.random() * 0.2 + 0.6)
			self.troop *= (random.random() * 0.5 + 0.4)
			
	def attack(self, rival):
		fame = (random.random()-(self.fame-rival.fame))*FAME_BASE
		self._safe_sub('fame', fame)
		attk, defen = (self, rival) if (random.random()>0.6) else (rival, self)
		cs_rate = (0.3+random.random()*0.5) if (random.random() < 0.01) else 1.0
		attk._pre_attack()
		dmg = attk.troop/10 * (attk._milit*0.4 + attk._morale*0.3 + attk.food/(attk.troop+1e-8)*0.3) / cs_rate
		
		if defen._defend(dmg): 
			cs_rate_bk = (0.1+random.random()/10) if (random.random() < 0.02) else 1.0
			defen._pre_attack()
			dmg_bk = defen.troop/10 * (defen._milit*0.2 + defen._morale*0.3 + defen.food/(defen.troop+1e-8)*0.5) / cs_rate_bk
			attk._defend(dmg_bk)
		
		if not rival.troop:
			rival.die()
		
	def recuperate(self):
		self.coin = self.coin + (self._polit+random.random()/3)*EARNING
		self.food = self.food + (self._polit+random.random()/3)*GRAIN
		self.fame = self.fame + random.random()*FAME_BASE
		
	def train(self):
		degree = self._milit*0.2
		self._morale = min(1.0, self._morale + degree)
		
	def die(self):
		self.coin = 0
		self.food = 0
		self.troop = 0
		self.fame = 0
		self.active = False
		# self.n_lords -= 1
	
	def next_action(self, act_id, *param):
		act_func = self.actions[act_id]
		act_func(*param)
		return act_id, param
		
	def AI_next_action(self, others):
		act_id, act_param = self._AI.get_next_action_par(self, others)
		return self.next_action(act_id, *act_param)
	
# Lords
# charm, polit, milit, fame, aggr	
class LiuBei(Lord):
	def __init__(self, coin, food, troop, morale):
		super(LiuBei, self).__init__("刘备", coin, food, troop, morale, 0.99, 0.70, 0.60, 0.90, 0.50)

class SunJian(Lord):
	def __init__(self, coin, food, troop, morale):
		super(SunJian, self).__init__("孙坚", coin, food, troop, morale, 0.70, 0.40, 0.86, 0.60, 0.71)
		
class SunCe(Lord):
	def __init__(self, coin, food, troop, morale):
		super(SunCe, self).__init__("孙策", coin, food, troop, morale, 0.75, 0.42, 0.88, 0.75, 0.85)

class YuanShao(Lord):
	def __init__(self, coin, food, troop, morale):
		super(YuanShao, self).__init__("袁绍", coin, food, troop, morale, 0.80, 0.68, 0.73, 0.82, 0.70)
		
class YuanShu(Lord):
	def __init__(self, coin, food, troop, morale):
		super(YuanShu, self).__init__("袁术", coin, food, troop, morale, 0.42, 0.44, 0.51, 0.30, 0.65)
		
class LiuYao(Lord):
	def __init__(self, coin, food, troop, morale):
		super(LiuYao, self).__init__("刘繇", coin, food, troop, morale, 0.51, 0.52, 0.43, 0.71, 0.15)
		
class LiuBiao(Lord):
	def __init__(self, coin, food, troop, morale):
		super(LiuBiao, self).__init__("刘表", coin, food, troop, morale, 0.79, 0.81, 0.60, 0.81, 0.08)

class LiuYan(Lord):
	def __init__(self, coin, food, troop, morale):
		super(LiuYan, self).__init__("刘焉", coin, food, troop, morale, 0.67, 0.76, 0.57, 0.79, 0.11)

class HanFu(Lord):
	def __init__(self, coin, food, troop, morale):
		super(HanFu, self).__init__("韩馥", coin, food, troop, morale, 0.45, 0.43, 0.43, 0.50, 0.13)

class GongSunZan(Lord):
	def __init__(self, coin, food, troop, morale):
		super(GongSunZan, self).__init__("公孙瓒", coin, food, troop, morale, 0.81, 0.56, 0.70, 0.71, 0.34)

class DongZhuo(Lord):
	def __init__(self, coin, food, troop, morale):
		super(DongZhuo, self).__init__("董卓", coin, food, troop, morale, 0.12, 0.25, 0.77, 0.01, 0.6)

class MaTeng(Lord):
	def __init__(self, coin, food, troop, morale):
		super(MaTeng, self).__init__("马腾", coin, food, troop, morale, 0.76, 0.10, 0.87, 0.65, 0.6)
		
class CaoCao(Lord):
	def __init__(self, coin, food, troop, morale):
		super(CaoCao, self).__init__("曹操", coin, food, troop, morale, 0.95, 0.89, 0.92, 0.75, 0.60)

				
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
	def __init__(self, senario, player, mode=mode_id.EPIC):
		super(GlobalControl, self).__init__()
		self.senario = senario
		self.lord_lst = senario.lord_lst
		self.player = player
		self.mode = mode
		self.evt_switcher = Switcher(senario.evt_lst)
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
			dead = []
			if self.check_single(param[0]):
				log_info += "\n{} 势力被消灭了".format(param[0].name)
				dead.append(param[0])
			if self.check_single(this):
				log_info += "\n{} 势力被消灭了".format(this.name)
				dead.append(this)
			for l in dead: self.lord_lst.remove(l)
			if self.player in dead:
				self.player = None
		else:
			log_info = "{} {}".format(this.name, self.lord_act_desc[act_id])
			
		CLI.emptyln()
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
			if self.mode == mode_id.ADVENTURE and not self.player:
				return False
			self.show_states()
		return True
				
	
	def show_states(self):
			CLI.clear()
			self.senario.show_states(show_attr=False, lord_lst=self.lord_lst)
			CLI.emptyln()
	
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
					rival = CLI.safe_input_list_elem("请选择攻击对象编号：", self.lord_lst, "非法的攻击对象！")
					assert(rival is not self.player)
					act_param = act_param+(rival, )
				except AssertionError:
					CLI.print_info("不能攻击自己！")
				else:
					break
			
		return act_id, act_param
		
	def main_loop(self):
		while True:			
			self.show_states()
			self.report_event()
			self.show_states()
			stat = self.do_next_turn()

			chk_stat, chk_str = self.check()
			if not (chk_stat & stat):
				CLI.pause()
				CLI.clear()
				CLI.println(chk_str)
				return 			
			CLI.printed("本月结束")
		
	
class CLI:
	@staticmethod
	def print_info(info, *args, **kwargs):
		print(info, *args, **kwargs)
	@staticmethod
	def emptyln():
		CLI.print_info("")
	@staticmethod
	def pause():
		CLI.emptyln()
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
	def printcn(info):
		CLI.print_info(info, end='')
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
	@staticmethod
	def unicode_left_align(obj, fmt, l):
		# Note that this function only works when the length 
		# of a uchar doubles the ascii char
		sa = ("{"+fmt+"}").format(obj)
		# Check for Unicode
		cnt = 0
		for c in sa:
			if ord(c) > 127:
				cnt += 1
		sa += " " * (l-(len(sa)+cnt))
		return sa
		
class Senario:
	senarios = [None]*len(senario_id)
	@classmethod
	def show_senarios(cls):
		for i, s in enumerate(cls.senarios):
			CLI.print_info("[{}] {}".format(i, s.desc))
			
	def __init__(self, lord_lst, evt_lst, desc):
		self.lord_lst = lord_lst
		self.evt_lst = evt_lst
		self.desc = desc
	def show_states(self, show_attr=False, lord_lst=None):
			if not lord_lst: lord_lst = self.lord_lst
			
			CLI.printcn(CLI.unicode_left_align("编号", "", COL_LEN))
			CLI.printcn(CLI.unicode_left_align("姓名", "", COL_LEN))
			CLI.printcn(CLI.unicode_left_align("金钱", "", COL_LEN))
			CLI.printcn(CLI.unicode_left_align("粮食", "", COL_LEN))
			CLI.printcn(CLI.unicode_left_align("士兵", "", COL_LEN))
			CLI.printcn(CLI.unicode_left_align("士气", "", COL_LEN))
			if show_attr:
				CLI.printcn(CLI.unicode_left_align("声望", "", COL_LEN))
				CLI.printcn(CLI.unicode_left_align("魅力", "", COL_LEN))
				CLI.printcn(CLI.unicode_left_align("政治", "", COL_LEN))
				CLI.print_info(CLI.unicode_left_align("兵法", "", COL_LEN))
			else:
				CLI.print_info(CLI.unicode_left_align("声望", "", COL_LEN))
			
			for i, l in enumerate(lord_lst):
				CLI.printcn(CLI.unicode_left_align(i, ":d", COL_LEN))
				CLI.printcn(CLI.unicode_left_align(l.name, ":s", COL_LEN))
				CLI.printcn(CLI.unicode_left_align(l.coin, ":.0f", COL_LEN))
				CLI.printcn(CLI.unicode_left_align(l.food, ":.0f", COL_LEN))
				CLI.printcn(CLI.unicode_left_align(l.troop, ":.0f", COL_LEN))
				CLI.printcn(CLI.unicode_left_align(l.morale, ":.2f", COL_LEN))
				if show_attr:
					CLI.printcn(CLI.unicode_left_align(l.fame, ":.2f", COL_LEN))
					CLI.printcn(CLI.unicode_left_align(l.charm, ":.2f", COL_LEN))
					CLI.printcn(CLI.unicode_left_align(l.polit, ":.2f", COL_LEN))
					CLI.print_info(CLI.unicode_left_align(l.milit, ":.2f", COL_LEN))
				else:
					CLI.print_info(CLI.unicode_left_align(l.fame, ":.2f", COL_LEN))
				
Senario.senarios[senario_id.TEST_SENARIO] = Senario([
																										CaoCao(100, 100, 100, 0.5), 
																										SunCe(100, 100, 100, 0.5), 
																										LiuBei(100, 100, 100, 0.5)
																									], (EvtDrought(), EvtHarvest(), EvtPlague()), "测试剧本")
Senario.senarios[senario_id.DongHanMo] = Senario([
																										CaoCao(2000, 2000, 300, 0.8), 
																										SunJian(1000, 2000, 500, 0.6), 
																										LiuBei(500, 500, 100, 0.6), 
																										LiuYao(1000, 1000, 300, 0.5), 
																										YuanShao(5000, 5000, 1000, 0.2), 
																										YuanShu(4000, 10000, 800, 0.4), 
																										DongZhuo(15000, 15000, 2000, 0.1), 
																										LiuBiao(8000, 8000, 800, 0.6), 
																										HanFu(300, 300, 150, 0.5), 
																										GongSunZan(3000, 3000, 600, 0.6), 
																										MaTeng(300, 300, 200, 1.0), 
																										LiuYan(5000, 5000, 600, 0.6)
																									], (EvtDrought(), EvtHarvest(), EvtPlague()), "东汉末·董卓立新主")

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
		CLI.print_info("选择剧本：")
		Senario.show_senarios()
		sen_id = CLI.safe_input_enum("请输入指令编号：", senario_id, "非法指令！")
		CLI.clear()
		self.senario = Senario.senarios[sen_id]
		self.senario.show_states(show_attr=True)
		self.player = CLI.safe_input_list_elem("请选择势力：", self.senario.lord_lst, "非法输入！")
		self.gc = GlobalControl(self.senario, self.player, self.mode)
		
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
	