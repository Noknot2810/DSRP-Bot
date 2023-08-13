import command_class
import settings
import vk_api
from speaker import Speaker
from trader import Trader
from general_commands import send_message, nonreg_warning

# Авторизация при помощи токена доступа группы
vk_session_g = vk_api.VkApi(token=settings.group_token)
session_api_g = vk_session_g.get_api()
group_upload = vk_api.VkUpload(vk_session_g)

# Авторизация при помощи токена доступа от standalone приложения
vk_session_p = vk_api.VkApi(app_id=settings.app_id,
                            token=settings.access_token)
session_api_p = vk_session_p.get_api()
personal_upload = vk_api.VkUpload(vk_session_p)

class Manager:
    """ Основной класс, обрабатывающий запросы, выполняющий большую часть
    функций и при необходимости делегирующий выполнение каких-то функций
    другим классам

    param registered_users: словарь с данными о зарегистрированных
                            пользователях, т.е. имеющих экономические карточки
                            в группе
    param greeted_users: словарь с id незарегистрированных пользователей,
                         которые были поприветствованы ботом
    param administrators: список id администраторов сообщества
    param adm_helper: объект класса Adm_helper, содержащий часть функций для
                      администрирования
    param trade_list: словарь с данными о Торговой площадке
    param game_active: переменная-флаг, что инициирована игровая сессия
    """
    def __init__(self):
        self.speaker = Speaker(session_api_g)
        self.trader = Trader(session_api_g, session_api_p)
        self.greeted_users = {}

        send_message(
            text=('Успех'),
            attachment='',
            sag=session_api_g,
            peer=189432801
        )

        # Создание объектов класса Command из команд, задание им описания и
        # добавление их в массивы по критерию доступности
        # command_class.Command(0) - добавляет команду в массив общедоступных
        # command_class.Command(1) - добавляет команду в массив
        #                            администраторских
        # command_class.Command(2) - добавляет команду в массив игровых
        command = command_class.Command(0)
        command.keys = ['coms']
        command.description = 'Показать список доступных команд'
        command.process = self.info_personal

        command = command_class.Command(0)
        command.keys = ['rules']
        command.description = 'Узнать правила сообщества'
        command.process = self.speaker.send_rules

        command = command_class.Command(0)
        command.keys = ['anks']
        command.description = ('Получить ссылку на обсуждение с анкетами '
                               'игроков')
        command.process = self.speaker.send_anks

        #command = command_class.Command(0)
        #command.keys = ['main']
        #command.description = 'Получить основной набор кнопок.'
        #command.process = self.speaker.btn_at_the_begining

        command = command_class.Command(0)
        command.keys = ['coin']
        command.description = 'Получить орла или решку'
        command.process = self.speaker.get_coin

        command = command_class.Command(0)
        command.no_keys = True
        command.keys = ['rand']
        command.description = ('Получить случайное число из диапазона '
                               'двух указанных чисел (или от 1 до 100, '
                               'если ввести просто .rand)\n'
                               '.rand <нижний предел> <верхний предел>')
        command.process = self.speaker.get_rand

        command = command_class.Command(0)
        command.keys = ['eco']
        command.description = ('Создать или получить экономическую карточку')
        command.process = self.trader.cm.new_eco

        command = command_class.Command(1)
        command.keys = ['reload']
        command.description = ('Перезагрузить файл одной из торговых '
                               'площадок. Приложите к сообщению с командой соответствующий файл!')
        command.process = self.trader.reload_trade_list

        command = command_class.Command(0)
        command.no_keys = True
        command.keys = ['buy']
        command.description = ('Купить вещь на Торговой площадке.\n'
                               '.buy <количество> <id вещи>')
        command.process = self.trader.buy_inventory

        command = command_class.Command(0)
        command.keys = ['bbuy']
        command.description = ('Получить кнопки меню покупки')
        command.process = self.trader.btn_buy

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['btbuy']
        command.description = ('')
        command.process = self.trader.btn_tbuy

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['bsecbuy']
        command.description = ('')
        command.process = self.trader.btn_secbuy

        command = command_class.Command(0)
        command.keys = ['main']
        command.description = ('Получить основной набор кнопок')
        command.process = self.trader.btn_main

        command = command_class.Command(1)
        command.keys = ['lock']
        command.description = ('Открыть или закрыть торговую площадку')
        command.process = self.trader.lock_trader

        #command = command_class.Command(0)
        #command.keys = ['up']
        #command.description = ('Перенести указанные вещи вверх по карточке')
        #command.process = self.trader.cm.item_up

        command = command_class.Command(0)
        command.keys = ['brep']
        command.description = ('Получить кнопки для перестановки вещей в инвентаре')
        command.process = self.trader.cm.btn_replace

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['bfromrep']
        command.description = ('')
        command.process = self.trader.cm.btn_from_replace

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['bcntrep']
        command.description = ('')
        command.process = self.trader.cm.btn_cnt_replace

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['btorep']
        command.description = ('')
        command.process = self.trader.cm.btn_to_replace

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['rep']
        command.description = ('')
        command.process = self.trader.cm.replace_item

        command = command_class.Command(0)
        command.keys = ['bsell']
        command.description = ('Получить кнопки для продажи вещей из инвентаря')
        command.process = self.trader.btn_sell

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['bfromsell']
        command.description = ('')
        command.process = self.trader.btn_from_sell

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['bcntsell']
        command.description = ('')
        command.process = self.trader.btn_cnt_sell

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['bconfirmsell']
        command.description = ('')
        command.process = self.trader.btn_confirm_sell

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['sell']
        command.description = ('')
        command.process = self.trader.sell_item

        command = command_class.Command(0)
        command.keys = ['hsend']
        command.description = ('Получить инструкцию, как делать переводы '
                               'другим игрокам')
        command.process = self.speaker.gift_instruction

        command = command_class.Command(0)
        command.no_keys = True
        command.keys = ['send']
        command.description = ('Получить кнопки для передачи вещи игроку\n'
                               '.send <кличка сталкера>')
        command.process = self.trader.confirm_person_gift

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['binvgift']
        command.description = ('')
        command.process = self.trader.btn_inv_gift

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['bfromgift']
        command.description = ('')
        command.process = self.trader.btn_from_gift

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['bcntgift']
        command.description = ('')
        command.process = self.trader.btn_cnt_gift

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['bconfirmgift']
        command.description = ('')
        command.process = self.trader.btn_confirm_gift

        command = command_class.Command(0)
        command.no_out = True
        command.keys = ['gift']
        command.description = ('')
        command.process = self.trader.gift_item

        command = command_class.Command(1)
        command.no_out = True
        command.keys = ['recheck_card']
        command.description = ('')
        command.process = self.trader.cm.recheck_card

        command = command_class.Command(1)
        command.no_out = True
        command.keys = ['delete_card']
        command.description = ('')
        command.process = self.trader.cm.delete_card

    """ Обработчик команд

    param peer: id пользователя, от которого поступила команда
    param text: текст команды
    param addition: приложение к команде
    """
    def command_handler(self, peer, text, addition=''):
        if isinstance(text, list):
            return
        elif not peer in self.trader.cm.registered_users:
            self.greeted_users.setdefault(peer, False)
            if not self.greeted_users[peer]:
                self.speaker.greeting_message(peer)
                self.greeted_users[peer] = True
                return

        for com in command_class.base_commands:
            if text in com.keys:
                com.process(peer, addition)
                return
        for com in command_class.adm_commands:
            if text in com.keys:
                if peer in settings.administrators:
                    com.process(peer, addition)
                    return
                else:
                    send_message(
                        text=('У вас нет прав доступа к командам '
                              'администратора.'),
                        sag=session_api_g,
                        peer=peer,
                        without_kb=True
                    )
                    return
        if (text != 'first_mes'):
            send_message(
                text='Команда не распознана.',
                sag=session_api_g,
                peer=peer,
                without_kb=True
            )

    """ Отправка списка доступных команд
    param peer: id пользователя
    param addition: фиктивный параметр
    """
    def info_personal(self, peer, addition):
        com_list = ('При наборе команд скобки не указываются!\n'
                    '__________________________\nОБЩИЕ КОМАНДЫ\n')
        for com in command_class.base_commands:
            if com.no_out:
                continue
            com_list += com.description + '\n'
            if not com.no_keys:
                com_list += '.' + com.keys[0] + '\n'
            com_list += '.............................................\n'
        if peer in settings.administrators:
            com_list += ('__________________________\n'
                         'КОМАНДЫ АДМИНИСТРИРОВАНИЯ\n')
            for com in command_class.adm_commands:
                if com.no_out:
                    continue
                com_list += com.description + '\n'
                if not com.no_keys:
                    com_list += '.' + com.keys[0] + '\n'
                com_list += '.............................................\n'
        com_list += '__________________________'
        send_message(
            text=('Список доступных команд:\n' + com_list),
            sag=session_api_g,
            peer=peer,
            without_kb=True
        )