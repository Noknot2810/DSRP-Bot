# Массив общедоступных команд
base_commands = []
# Массив команд для администраторов
adm_commands = []
# Массив игровых/сессионных команд
game_commands = []

class Command:
	""" Вспомогательный класс, для хранения команд со свойствами

    param keys: список ключевых слов, при помощи которых может быть вызвана
    			команда
    param description: описание работы команды
    param not_out: переменная-флаг для указания, что ключи выводить не нужно
    """
	def __init__(self, access_par):
		self.keys = []
		self.description = ''
		self.no_keys = False
		self.no_out = False
		if access_par == 0:
			base_commands.append(self)
		elif access_par == 1:
			adm_commands.append(self)
		elif access_par == 2:
			game_commands.append(self)
		else:
			raise Exception("Ошибка: Недопустимый параметр доступа команды.")
	def process(self):
		""" Инициация выполнения содержимого команды """
		pass