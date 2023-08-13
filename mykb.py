from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import settings

# Клавиатура для взаимодействия с профилем с кнопками:
# купить, продать, переводы, помощь и в_начало
main_keyboard = VkKeyboard(one_time=False, inline=False)
main_keyboard.add_button(
	label='Персонаж',
	color=VkKeyboardColor.POSITIVE,
	payload={"command": "eco"}
)
main_keyboard.add_line()
main_keyboard.add_button(
	label='Купить на площадке',
	color=VkKeyboardColor.PRIMARY,
	payload={"command": "bbuy"}
)
main_keyboard.add_button(
	label='Продать на площадке',
	color=VkKeyboardColor.PRIMARY,
	payload={"command": "bsell"}
)
main_keyboard.add_line()
main_keyboard.add_button(
	label='Переноска вещей в карточке',
	color=VkKeyboardColor.PRIMARY,
	payload={"command": "brep"}
)
main_keyboard.add_line()
main_keyboard.add_button(
	label='Переводы',
	color=VkKeyboardColor.SECONDARY,
	payload={"command": "hsend"}
)
main_keyboard.add_button(
	label='Команды',
	color=VkKeyboardColor.SECONDARY,
	payload={"command": "coms"}
)
main_keyboard.add_line()
main_keyboard.add_openlink_button(
	label='Правила',
	link=settings.rules_topic
)
main_keyboard = main_keyboard.get_keyboard()

# Клавиатура для пользователей без персонажа
nonreg_keyboard = VkKeyboard(one_time=False, inline=False)
nonreg_keyboard.add_openlink_button(
	label='Анкеты игроков',
	link = settings.forms_topic
)
nonreg_keyboard.add_openlink_button(
	label='Некролог',
	link = settings.necrology_topic
)
nonreg_keyboard.add_line()
nonreg_keyboard.add_openlink_button(
	label='Узнать правила',
	link = settings.rules_topic
)
nonreg_keyboard = nonreg_keyboard.get_keyboard()

# Клавиатура для новых пользователей
ftime_keyboard = VkKeyboard(one_time=False, inline=False)
ftime_keyboard.add_openlink_button(
	label='Анкеты игроков',
	link = settings.forms_topic
)
ftime_keyboard.add_openlink_button(
	label='Узнать правила',
	link = settings.rules_topic
)
ftime_keyboard = ftime_keyboard.get_keyboard()