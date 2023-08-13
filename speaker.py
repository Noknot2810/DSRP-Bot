import mykb
import settings
import random
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from general_commands import send_message

class Speaker:
    def __init__(self, session_api_g):
        self.sag = session_api_g

    """ Отправка приветственного сообщения
    param peer: id пользователя
    """
    def greeting_message(self, peer):
        send_message(
            text=('Приветствую в нашей группе, посвящённой ролевому сталкеру.'
                  '\nНам не удалось обнаружить вашу регистрационную '
                  'карточку, и это означает, что либо ваша старая карточка '
                  'была удалена, либо вы здесь в первый раз.\n\n'
                  'Предлагаем вам ознакомиться с правилами группы и/или '
                  'зарегистрироваться в нашем сообществе.\nДля этого '
                  'нажмите на одну из кнопок ниже или введите одну '
                  'следующих из команд:\n\n'
                  '.rules - для получения ссылки на обсуждение с правилами '
                  'группы.\n'
                  '.anks - для получения ссылки на обсуждение с анкетами '
                  'игроков; в данном обсуждении вам необходимо составить '
                  'анкету вашего персонажа, после утверждения которой у '
                  'вас появится возможность участвовать на игровых чатах.'
                  '\n\nЕсли вы хотите задать вопрос администрации, пишите'
                  '(без точки первым символом), будем рады ответить.'),
            attachment='',
            keyboard=mykb.ftime_keyboard,
            sag=self.sag,
            peer=peer
        )

    """ Отправка сообщения с ссылочной кнопкой на обсуждение с правилами
    param peer: id пользователя
    param addition: фиктивный параметр
    """
    def send_rules(self, peer, addition):
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_openlink_button(
            label='Узнать правила',
            link=settings.rules_topic
        )
        send_message(
            text=('Нажмите для перехода в обсуждение с правилами группы:'),
            attachment='',
            keyboard=keyboard.get_keyboard(),
            sag=self.sag,
            peer=peer
        )

    """ Отправка сообщения с ссылочной кнопкой на обсуждение с анкетами игроков
    param peer: id пользователя
    param addition: фиктивный параметр
    """
    def send_anks(self, peer, addition):
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_openlink_button(
            label='Обсуждение с анкетами',
            link=settings.forms_topic
        )
        send_message(
            text=('Нажмите для перехода в обсуждение с анкетами игроков:'),
            attachment='',
            keyboard=keyboard.get_keyboard(),
            sag=self.sag,
            peer=peer
        )

    """ Отправка сообщения с инструкцией, как правильно вводить команду
    для передачи предметов другому игроку

    param peer: id пользователя
    param addition: фиктивный параметр
    """
    def gift_instruction(self, peer, addition):
        send_message(
            text=('Чтобы сделать перевод вещей или денег другому '
                  'сталкеру, необходимо ввести команду:\n.send <кличка '
                  'получателя>.'),
            attachment='',
            peer=peer,
            sag=self.sag,
            without_kb=True
        )

    def get_coin(self, peer, addition):
        send_message(
            text=('Результат: ' + random.choice(['Орёл', 'Решка'])),
            attachment='',
            peer=peer,
            sag=self.sag,
            without_kb=True
        )

    def get_rand(self, peer, addition):
        left = 1
        right = 100

        addition = addition.strip()
        if len(addition) > 0:
            f = addition.find(' ')
            if f != -1:
                addition = addition.split(' ')

                try:
                    if int(addition[0]) in settings.administrators:
                        left = int(addition[1])
                        right = int(addition[2])
                    else:
                        left = int(addition[0])
                        right = int(addition[1])
                except:
                    send_message(
                        text=('Один из пределов введён некорректно.'),
                        attachment='',
                        peer=peer,
                        sag=self.sag,
                        without_kb=True
                    )
                    return

        send_message(
            text=('Результат: ' + str(random.randint(left, right))),
            attachment='',
            peer=peer,
            sag=self.sag,
            without_kb=True
        )