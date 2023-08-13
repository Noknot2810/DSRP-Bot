import random
import mykb
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

""" Отправка сообщения пользователю

    param peer: id пользователя
    param text: текст сообщения
    param attachment: приложение к сообщению
    param keyboard: клавиатура для сообщения (форматированная строка)
    param without_kb: True - не менять клавиатуру пользователю,
                      False - менять
"""
def send_message(sag, peer, text, attachment='',
                 keyboard=VkKeyboard().get_empty_keyboard(),
                 without_kb=False):
    text = ('Бот ДСР\n*******************\n' +
            text + '\n*******************')
    if without_kb:
        sag.messages.send(
            message=text,
            random_id=random.getrandbits(64),
            peer_id=peer,
            attachment=attachment
        )
    else:
        sag.messages.send(
            message=text,
            random_id=random.getrandbits(64),
            peer_id=peer,
            attachment=attachment,
            keyboard=keyboard
        )

""" Отправка сообщения незарегистрированному пользователю

    param peer: id пользователя
"""
def nonreg_warning(sag, peer):
    send_message(
        text=('Вы не создали персонажа для role play или ваш прежний '
              'персонаж умер.\nЧтобы иметь возможность принимать участие '
              'в чатах, отправьте анкету для нового персонажа в '
              'обсуждение <<Анкеты игроков>>.\nЕсли у вас был живой '
              'персонаж и вы не понимаете, почему вам всё это выводится, '
              'проверьте обсуждение <<Некролог>> или спросите '
              'администрацию, может, быть он просто временно заморожен.'),
        attachment='',
        keyboard=mykb.nonreg_keyboard,
        peer=peer,
        sag=sag
    )