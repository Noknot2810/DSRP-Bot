import models
import mykb
import requests
import settings
import random
from general_commands import send_message, nonreg_warning
from cardmaster import Cardmaster
from supplier import Supplier
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

class Trader:
    def __init__(self, session_api_g, session_api_p):
        self.sag = session_api_g
        self.sap = session_api_p
        self.cm = Cardmaster(self.sag, self.sap)
        self.sup = Supplier(self.sap)
        self.trade_list = None
        self.dop_trade_lists = {'M':None, 'B':None, 'D':None, 'S':None, 'E':None}
        self.closed = False

        # Загрузка данных Торговой площадки из файла Tl.txt
        self.download_trade_list(settings.administrators[0], "0")

    def download_trade_list(self, peer, addition):
        """ Инициация загрузки данных для Торговой площадки

        param peer: id пользователя
        param addition: дополнительный параметр, определяющий способ загрузки
        """
        res = None
        if len(addition) < 1 or addition == "0":
            res = self.sup.sload_trade_list()

        if not res or res.last_id == -1:
            send_message(
                text=('Произошла ошибка.\nНе удалось загрузить данные из '
                      'файла T.txt для наполнения Торговой площадки.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
        else:
            self.trade_list = res
            send_message(
                text=('Наполнение Торговой площадки.\nданными из файла '
                      'T.txt успешно.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )

    def download_dop_trade_list(self, peer, symb):
        """ Инициация загрузки данных для Торговой площадки

        param peer: id пользователя
        param addition: дополнительный параметр, определяющий способ загрузки
        """
        res = self.sup.sload_dop_trade_list(symb)

        if not res or res.last_id == -1:
            send_message(
                text=('Произошла ошибка.\nНе удалось загрузить данные из '
                      'файла для наполнения торговой площадки ' + symb + '.\n'
                      'Обратитесь за помощью к администрации.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
            return False
        else:
            self.dop_trade_lists[symb] = res
            send_message(
                text=('!!!!!!!!!! T.txt' + symb + ' успешно.'),################################################################
                attachment='',
                sag=self.sag,
                peer=settings.administrators[0],
                without_kb=True
            )
            return True

    def reload_trade_list(self, peer, addition):
        try:
            file = requests.get(addition[1])
            open('/home/dsrpgru/dsrpg/' + addition[0], 'wb').write(file.content)
        except Exception as exc:
            send_message(
                text= ('ERROR: ' + str(exc)),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
            return

        tpos = addition[0].find('T')
        if tpos < 0:
            send_message(
                text=('На сервер загружен неизвеизвестный файл ' +
                      addition[0] + '!'),
                attachment='',
                sag=self.sag,
                peer=settings.administrators[0],
                without_kb=True
            )
            send_message(
                text=('Вы загрузили некорректный файл на сервер.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
            return

        res = None
        tpos = addition[0][tpos + 1]
        if tpos == '.':
            res = self.sup.sload_trade_list()
            if not res or res.last_id == -1:
                send_message(
                    text=('Произошла ошибка.\nНе удалось загрузить данные из '
                          'файла ' + addition[0] + ' для наполнения Торговой '
                          'площадки. На сервере сейчас некорректная версия файла!'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
            else:
                self.trade_list = res
                send_message(
                    text=('Перезаполнение Торговой площадки.\nданными из ' +
                          'загруженного вами файла ' + addition[0] + '  успешно.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
        elif tpos in self.dop_trade_lists:
            res = self.sup.sload_dop_trade_list(tpos)
            if not res or res.last_id == -1:
                send_message(
                    text=('Произошла ошибка.\nНе удалось загрузить данные из '
                          'файла ' + addition[0] + ' для наполнения Торговой '
                          'площадки. На сервере сейчас некорректная версия файла!'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
            else:
                self.dop_trade_lists[tpos] = res
                send_message(
                    text=('Перезаполнение Торговой площадки.\nданными из ' +
                          'загруженного вами файла ' + addition[0] + '  успешно.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
        else:
            send_message(
                text=('На сервер загружен неизвеизвестный файл ' +
                      addition[0] + '!'),
                attachment='',
                sag=self.sag,
                peer=settings.administrators[0],
                without_kb=True
            )
            send_message(
                text=('Вы загрузили некорректный файл на сервер.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
            return

    """ Оценивает инвентарь персонажа пользователя и возвращает словарь
    предметов, имеющих ценность

    param peer: id пользователя
    param addition: фиктивный параметр
    """
    """def assess_inventory(self, peer_id, addition):

        text = ''
        if peer_id in self.cm.registered_users:
            items = self.cm.registered_users[peer_id].get_items()
            for item in items:
                if item in self.trade_list.buy_list:
                    slot = self.trade_list.buy_list[item]
                    text += (str(slot[0]) + ') - ' +
                            item + '(в наличии: ' + str(items[item]) +
                            ') за [' + str(slot[1]) + ']\n')
        if len(text) == 0:
            send_message(
                text='У вас нет ничего, что можно было бы продать!',
                sag=self.sag,
                peer=peer_id,
                without_kb=True
            )
        else:
            send_message(
                text=('Список доступных к продаже предметов:\n' + text +
                      '___________________'),
                sag=self.sag,
                peer=peer_id,
                without_kb=True
            )
    """
    
    def success_deal(self, peer, slot_name, cnt, profit):
        self.registered_users[peer].money += profit
        self.cm.write_inventory(peer)
        send_message(
            text=('Вы успешно продали ' + slot_name + ' - ' +
                   str(cnt) + 'шт.\nНа счёт начислено: ' +
                   str(profit)),
            attachment='',
            keyboard=mykb.main_keyboard,
            sag=self.sag,
            peer=peer
        )

    
##############################################################################
# Покупка у игрока
##############################################################################

    def btn_sell(self, peer, addition):
        if peer in self.cm.registered_users:
            keyboard = VkKeyboard(one_time=False, inline=False)
            keyboard.add_button(
                label='Оружие',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromsell", "addition": {"from": 2}}
            )
            keyboard.add_button(
                label='Разное',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromsell", "addition": {"from": 5}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='Защита головы',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromsell", "addition": {"from": 3}}
            )
            keyboard.add_button(
                label='Броня',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromsell", "addition": {"from": 4}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='Личный ящик',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromsell", "addition": {"from": 6}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "main"}
            )

            keyboard = keyboard.get_keyboard()
            send_message(
                text=('Получение меню инвентаря для продажи...'),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)

    def btn_from_sell(self, peer, addition):
        if peer in self.cm.registered_users:
            user = self.cm.registered_users[peer]
            from_place = None
            try:
                from_place = addition["from"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            self.cm.read_inventory(user.id, peer)
            if len(user.all[from_place]) < 1:
                send_message(
                    text=('В разделе инвентаря ' + settings.inventory_names[from_place] + ' пусто. Возврат к основному меню...'),
                    attachment='',
                    sag=self.sag,
                    keyboard=mykb.main_keyboard,
                    peer=peer
                )
                return

            keyboard = VkKeyboard(one_time=False, inline=False)
            nline_cntr = 0
            cntr = 0
            dop_text = ""
            for slot in user.all[from_place]:
                label = user.all[from_place][slot].name
                if label in self.trade_list.buy_list:
                    if len(label) > 40:
                        label = label[:40]
                    if user.all[from_place][slot].cnt == 1:
                        keyboard.add_button(
                            label=label,
                            color=VkKeyboardColor.SECONDARY,
                            payload={"command": "bconfirmsell", "addition": {"from": from_place, "slot": user.all[from_place][slot].name, "cnt": 1}}
                        )
                    else:
                        keyboard.add_button(
                            label=label,
                            color=VkKeyboardColor.SECONDARY,
                            payload={"command": "bcntsell", "addition": {"from": from_place, "slot": user.all[from_place][slot].name}}
                        )

                    nline_cntr += 1
                    cntr += 1

                    if nline_cntr == 3:
                        nline_cntr = 0
                        keyboard.add_line()

                    if cntr == 29:
                        dop_text = ('Слишком много предметов. Может быть только '
                                    '30 кнопок. Если здесь нет нужных, предварительно '
                                    'попередвигайте предметы или обратитесь к '
                                    'администраторам для продажи вручную.')
                        break

            keyboard.add_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "bsell"}
            )

            keyboard = keyboard.get_keyboard()
            send_message(
                text=('Получение меню раздела ' + settings.inventory_names[from_place] + ' для продажи...' + dop_text),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)

    def btn_cnt_sell(self, peer, addition):
        if peer in self.cm.registered_users:
            user = self.cm.registered_users[peer]
            from_place = None
            slot = None
            try:
                from_place = addition["from"]
                slot = addition["slot"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            self.cm.read_inventory(user.id, peer)

            if slot in user.all[from_place]:
                ch_cnt = user.all[from_place][slot].cnt + 1
                if ch_cnt > 26:
                    ch_cnt = 26

                keyboard = VkKeyboard(one_time=False, inline=False)
                nline_cntr = 0
                for i in range(1, ch_cnt):
                    keyboard.add_button(
                        label=str(i),
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmsell", "addition": {"from": from_place, "slot": slot, "cnt": i}}
                    )

                    nline_cntr += 1
                    if nline_cntr == 3:
                        nline_cntr = 0
                        keyboard.add_line()

                keyboard.add_button(
                    label='Назад',
                    color=VkKeyboardColor.NEGATIVE,
                    payload={"command": "bfromsell", "addition": {"from": from_place}}
                )
                keyboard = keyboard.get_keyboard()
                send_message(
                    text=('Выберите, сколько ' + slot + ' вы хотите продать (далее вам напишут, сколько будут готовы предложить).'),
                    attachment='',
                    sag=self.sag,
                    keyboard=keyboard,
                    peer=peer
                )

            else:
                send_message(
                    text=('Предмет ' + slot + ' не был найден в разделе инвентаря ' + settings.inventory_names[from_place] + '. Возврат к основному меню...'),
                    attachment='',
                    sag=self.sag,
                    keyboard=mykb.main_keyboard,
                    peer=peer
                )
        else:
            nonreg_warning(self.sag, peer)

    def btn_confirm_sell(self, peer, addition):
        if peer in self.cm.registered_users:
            from_place = None
            slot = None
            cnt = None
            try:
                from_place = addition["from"]
                slot = addition["slot"]
                cnt = addition["cnt"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            if slot in self.trade_list.buy_list:
                cost = round(self.trade_list.buy_list[slot] * (0.93 + random.randint(0, 140) / 1000))

                keyboard = VkKeyboard(one_time=False, inline=False)
                keyboard.add_button(
                    label='Принять',
                    color=VkKeyboardColor.POSITIVE,
                    payload={"command": "sell", "addition": {"from": from_place, "slot": slot, "cnt": cnt, "cost": cost}}
                )
                keyboard.add_button(
                    label='Отказаться',
                    color=VkKeyboardColor.NEGATIVE,
                    payload={"command": "main"}
                )
                keyboard = keyboard.get_keyboard()
                send_message(
                    text=('Вам предлагается продать ' + str(cnt) + ' ед. ' +
                          slot + ' из раздела ' +
                          settings.inventory_names[from_place] + ' по ' +
                          str(cost) + ' за единицу.\nВсё в сумме за ' +
                          str(cost * cnt) + '.'),
                    attachment='',
                    sag=self.sag,
                    keyboard=keyboard,
                    peer=peer
                )
            else:
                send_message(
                    text=('Предмет ' + slot + ' на этот момент более не покупается. Возврат к основному меню...'),
                    attachment='',
                    sag=self.sag,
                    keyboard=mykb.main_keyboard,
                    peer=peer
                )
        else:
            nonreg_warning(self.sag, peer)

    def sell_item(self, peer, addition):
        if self.closed:
            send_message(
                text=('Адъмин временно закрыл возможность продавать на '
                      'Торговой площадке.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
            return

        if peer in self.cm.registered_users:
            user = self.cm.registered_users[peer]
            from_place = None
            slot = None
            cnt = None
            cost = None
            try:
                from_place = addition["from"]
                slot = addition["slot"]
                cnt = addition["cnt"]
                cost = addition["cost"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            self.cm.read_inventory(user.id, peer)

            if slot in user.all[from_place]:
                if user.all[from_place][slot].cnt >= cnt:
                    user.all[from_place][slot].cnt -= cnt
                    if user.all[from_place][slot].cnt < 1:
                        del user.all[from_place][slot]
                    profit = cnt * cost
                    user.money += profit
                    self.cm.write_inventory(peer)
                    send_message(
                        text='Вы успешно продали ' + str(cnt) +' ' + slot + ' из ' + settings.inventory_names[from_place] + ' за ' + str(profit) + '.',
                        attachment='',
                        sag=self.sag,
                        keyboard=mykb.main_keyboard,
                        peer=peer
                    )
                else:
                    send_message(
                        text=('Предмет ' + slot + ' не был найден в количестве ' + str(cnt) + ' в разделе инвентаря ' + settings.inventory_names[from_place] + '. Возврат к основному меню...'),
                        attachment='',
                        sag=self.sag,
                        keyboard=mykb.main_keyboard,
                        peer=peer
                    )
            else:
                send_message(
                    text=('Предмет ' + slot + ' не был найден в разделе инвентаря ' + settings.inventory_names[from_place] + '. Возврат к основному меню...'),
                    attachment='',
                    sag=self.sag,
                    keyboard=mykb.main_keyboard,
                    peer=peer
                )
        else:
            nonreg_warning(self.sag, peer)

##############################################################################
# Продажа игроку
##############################################################################

    def btn_buy(self, peer, addition):
        """ Отправляет клавиатуру с отделами Торговой площадки для покупки

        param peer: id пользователя
        param addition: фиктивный параметр
        """
        if peer in self.cm.registered_users:
            user = self.cm.registered_users[peer]

            keyboard = VkKeyboard(one_time=False, inline=False)
            keyboard.add_button(
                label='Общая торговая площадка',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "btbuy"}
            )

            keyboard.add_line()

            if user.gp in settings.war_groups_symbs:
                for gp_symb in settings.war_groups_symbs[user.gp]:
                    if not self.dop_trade_lists[gp_symb] is None or self.download_dop_trade_list(peer, gp_symb):
                        keyboard.add_button(
                            label='Торговая площадка ' + gp_symb,
                            color=VkKeyboardColor.SECONDARY,
                            payload={"command": "btbuy", "addition": gp_symb}
                        )
                        keyboard.add_line()

            keyboard.add_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "main"}
            )

            keyboard = keyboard.get_keyboard()
            send_message(
                text=('Получение меню покупки...'),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)

    def btn_tbuy(self, peer, addition):
        if peer in self.cm.registered_users:
            addition = addition.split(' ')
            sell_sections = None
            gp_symb = ""
            if len(addition) > 0:
                try:
                    if len(addition) > 1 and int(addition[0]) in settings.administrators:
                        gp_symb = addition[1].upper()
                    else:
                        gp_symb = addition[0].upper()
                except:
                    send_message(
                        text=('С командой должна быть указана буква нужной '
                              'торговой площадки (или не указано ничего, '
                              'если запрашивается общая ТП).'),
                        attachment='',
                        sag=self.sag,
                        peer=peer,
                        without_kb=True
                    )
                    return

                if len(gp_symb) < 1:
                    sell_sections = self.trade_list.sections
                elif gp_symb in self.dop_trade_lists and (not self.dop_trade_lists[gp_symb] is None or self.download_dop_trade_list(peer, gp_symb)):
                    sell_sections = self.dop_trade_lists[gp_symb].sections
                else:
                    send_message(
                        text=('Площадки с буквой ' + gp_symb + ' не существует или она не загружена.'),
                        attachment='',
                        sag=self.sag,
                        peer=peer,
                        without_kb=True
                    )
                    return
            else:
                sell_sections = self.trade_list.sections

            keyboard = VkKeyboard(one_time=False, inline=False)
            nline_cntr = 0
            cntr = 0
            for i in range(len(sell_sections)):
                if sell_sections[i].sell:
                    label = str(sell_sections[i])
                    if len(label) > 40:
                        label = label[:40]
                    keyboard.add_button(
                        label=label,
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bsecbuy", "addition": {"tp": gp_symb, "sec": i}}
                    )
                    nline_cntr += 1
                    cntr += 1

                if nline_cntr == 3:
                    nline_cntr = 0
                    keyboard.add_line()

            if cntr > 29:
                send_message(
                    text=('Ошибка торговой площадки. Слишком много секций (>29)'
                          '. Обратитесь в администрацию.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            keyboard.add_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "bbuy"}
            )

            keyboard = keyboard.get_keyboard()
            send_message(
                text=('Получение меню секций торговой площадки...'),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)


    def btn_secbuy(self, peer, addition):
        bratva_factor = False
        if peer in self.cm.registered_users:
            bratva_factor = self.cm.registered_users[peer].gp
            if bratva_factor in settings.war_groups_symbs and settings.war_groups_symbs[bratva_factor][0] == 'B':
                bratva_factor = True
            else:
                bratva_factor = False
        else:
            nonreg_warning(self.sag, peer)
            return

        tp = None
        section = None
        sell_sections = None
        try:
            tp = addition["tp"]
            section = addition["sec"]
        except:
            send_message(
                text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )

        if len(tp) < 1:
            sell_sections = self.trade_list.sections
        elif not self.dop_trade_lists[tp] is None or self.download_dop_trade_list(peer, tp):
            sell_sections = self.dop_trade_lists[tp].sections
        else:
            send_message(
                    text=('Площадка с буквой ' + tp + ', скорее всего, не загружена.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
            return

        if section < len(sell_sections):
            slots = sell_sections[section].slots

            keyboard = VkKeyboard(one_time=False, inline=False)
            nline_cntr = 0
            cntr = 0
            text = "Ассортимент раздела:\n"
            for key in slots:
                slot_cost = slots[key].cost
                if bratva_factor and len(tp) < 1:
                    slot_cost = round(slot_cost * 0.9)

                text += str(key) + ") - " + slots[key].name + " [" + str(slot_cost) + "]\n"
                label = slots[key].name
                if len(label) > 40:
                    label = label[:40]
                keyboard.add_button(
                    label=label,
                    color=VkKeyboardColor.SECONDARY,
                    payload={"command": "buy", "addition": "1 " + str(key) + tp}
                )
                nline_cntr += 1
                cntr += 1

                if nline_cntr == 3:
                    nline_cntr = 0
                    keyboard.add_line()

            if cntr > 29:
                send_message(
                    text=('Ошибка секции торговой площадки. Слишком много '
                          'предметов (>29). Обратитесь в администрацию.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            keyboard.add_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "btbuy", "addition": tp}
            )
            keyboard = keyboard.get_keyboard()
            send_message(
                text=(text + 'Получение меню предметов секции торговой площадки...'),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            send_message(
                text=('Секция ' + str(section) + ' на указанной площадке отсутствует. Вероятно, площадка была обновлена.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )

    def buy_inventory(self, peer, addition):
        """ Инициация покупки предмета на Торговой площадке

        param peer: id пользователя
        param addition: форматированная строка: '<количество> <id вещи>'
                        треугольные скобки не указываются
        """
        if self.closed:
            send_message(
                text=('Адъмин временно закрыл возможность покупать на '
                      'Торговой площадке.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
            return

        if peer in self.cm.registered_users:
            bratva_factor = False
            admin = None
            cnt = None
            bid = None
            addition = addition.split(' ')
            if len(addition) > 1:
                try:
                    if int(addition[0]) in settings.administrators:
                        admin = int(addition[0])
                        cnt = int(addition[1])
                    else:
                        cnt = int(addition[0])
                except:
                    send_message(
                        text='Количество покупаемых вещей введено некорректно',
                        attachment='',
                        sag=self.sag,
                        peer=peer,
                        without_kb=True
                    )
                    return
                if cnt < 1:
                    send_message(
                        text=('Количество покупаемых вещей не может быть '
                              'меньше 1.'),
                        attachment = '',
                        sag=self.sag,
                        peer = peer,
                        without_kb = True
                    )
                    return
                if cnt > 100000:
                    send_message(
                        text=('Количество покупаемых вещей не может быть '
                              'больше 100000.'),
                        attachment='',
                        sag=self.sag,
                        peer=peer,
                        without_kb=True
                    )
                    return

                if (not admin is None) and len(addition) < 3:
                    send_message(
                        text = ('Команда набрана неверно, должно быть 2 '
                                'параметра, разделённых пробелами.'),
                        attachment = '',
                        sag=self.sag,
                        peer = peer,
                        without_kb = True
                    )
                    return
                elif not admin is None:
                    bid = addition[2]
                else:
                    bid = addition[1]
            else:
                send_message(
                    text = ('Команда набрана неверно, должно быть 2 '
                            'параметра, разделённых пробелами.'),
                    attachment = '',
                    sag=self.sag,
                    peer = peer,
                    without_kb = True
                )
                return

            if len(bid) > 0 and bid[0].isdigit():
                user = self.cm.registered_users[peer]
                gp = user.gp
                sell_list = None

                lsymb = bid[-1]
                if lsymb.isalpha():
                    lsymb = lsymb.upper()
                    if (gp in settings.war_groups_symbs and lsymb in settings.war_groups_symbs[gp]) or (not admin is None):
                        if self.dop_trade_lists[lsymb] is None and not self.download_dop_trade_list(peer, lsymb):
                            return
                        sell_list = self.dop_trade_lists[lsymb].sell_list
                        bid = bid[:-1]
                    else:
                        send_message(
                            text = ('У вас нет прямого доступа к торговой площадке ' + lsymb + '.'),
                            attachment = '',
                            sag=self.sag,
                            peer = peer,
                            without_kb = True
                        )
                        return
                else:
                    sell_list = self.trade_list.sell_list

                    if gp in settings.war_groups_symbs and settings.war_groups_symbs[gp][0] == 'B':
                        bratva_factor = True

                try:
                    bid = int(bid)
                except:
                    send_message(
                        text=('Вещь с введённым id = ' + str(bid) +
                              ' отсутствует на Торговой площадке.'),
                        attachment='',
                        sag=self.sag,
                        peer=peer,
                        without_kb=True
                    )

                if bid in sell_list:
                    slot = sell_list[bid]
                    slot_cost = slot.cost

                    if bratva_factor:
                        slot_cost = round(slot_cost * 0.9)

                    total_cost = slot_cost * cnt

                    self.cm.read_inventory(user.id, peer)
                    if user.money >= total_cost:
                        if slot.spec == 1:
                            if slot.name in user.docs:
                                send_message(
                                    text=('У вас уже есть ' + slot.name +
                                          '. Покупка отменена.'),
                                    attachment='',
                                    sag=self.sag,
                                    peer=peer,
                                    without_kb=True
                                )
                                return
                            else:
                                user.docs[slot.name] = models.Doc(slot.name, slot.desc)
                        elif slot.spec == 2 and len(user.weapons) < 7:
                            if slot.name in user.weapons and slot.desc == user.weapons[slot.name].desc:
                                user.weapons[slot.name] = models.ItemString(slot.name, slot.desc, cnt + user.weapons[slot.name].cnt)
                            else:
                                user.weapons[slot.name + '#'] = models.ItemString(slot.name, slot.desc, cnt)

                        elif slot.spec == 3 and len(user.head_def) < 2 and not (slot.name in user.head_def):
                            user.head_def[slot.name] = models.ItemString(slot.name, slot.desc, 1)
                            if cnt > 1:
                                user.chest_add(slot, cnt - 1)
                        elif slot.spec == 4 and len(user.body_def) < 1 and not (slot.name in user.body_def):
                            user.body_def[slot.name] = models.ItemString(slot.name, slot.desc, 1)
                            if cnt > 1:
                                user.chest_add(slot, cnt - 1)
                        else:
                            user.chest_add(slot, cnt)

                        user.money -= total_cost
                        self.cm.write_inventory(peer)
                        send_message(
                            text=('Вы успешно приобрели ' +
                                slot.name + ' - ' +
                                str(cnt) + 'шт.\nСо счёта списано: ' +
                                str(total_cost)),
                            attachment='',
                            sag=self.sag,
                            peer=peer,
                            without_kb=True
                        )
                        return
                    else:
                        send_message(
                            text=('Вам не хватает денег (' +
                                  str(total_cost -
                                      user.money) +
                                  ') для совершения покупки.'),
                                attachment='',
                                sag=self.sag,
                                peer=peer,
                                without_kb=True
                        )
                        return
                else:
                    send_message(
                        text=('Вещь с введённым id = ' + str(bid) +
                              ' отсутствует на Торговой площадке.'),
                        attachment='',
                        sag=self.sag,
                        peer=peer,
                        without_kb=True
                    )
            else:
                send_message(
                    text=('Возможность покупать по названию предмета пока '
                          'не реализована, используйте id.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
        else:
            nonreg_warning(self.sag, peer)

##############################################################################
# Передача вещей между игроками
##############################################################################

    def confirm_person_gift(self, peer, addition):
        if peer in self.cm.registered_users:
            addressee_peer = self.cm.find_peer_by_nick(addition)
            if addressee_peer != 0:
                keyboard = VkKeyboard(one_time=False, inline=False)
                keyboard.add_button(
                    label='Да',
                    color=VkKeyboardColor.POSITIVE,
                    payload={"command": "binvgift", "addition": {"addr": addressee_peer}}
                )
                keyboard.add_button(
                    label='Нет',
                    color=VkKeyboardColor.NEGATIVE,
                    payload={"command": "main"}
                )
                keyboard = keyboard.get_keyboard()
                send_message(
                    text=('Удалось найти сталкера по прозвищу ' +
                          self.cm.registered_users[addressee_peer].nick +
                          '.\n Это тот, кому вы хотите что-то передать?'),
                    attachment='',
                    sag=self.sag,
                    keyboard=keyboard,
                    peer=peer
                )
            else:
                send_message(
                    text=('Пользователь с никнеймом, содержащим "' +
                           addition + '", не найден.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
        else:
            nonreg_warning(self.sag, peer)

    def btn_inv_gift(self, peer, addition):
        if peer in self.cm.registered_users:
            addr = None
            try:
                addr = addition["addr"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            keyboard = VkKeyboard(one_time=False, inline=False)
            keyboard.add_button(
                label='Деньги',
                color=VkKeyboardColor.POSITIVE,
                payload={"command": "bcntgift", "addition": {"addr": addr, "from": -1, "slot": '$'}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='Оружие',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromgift", "addition": {"addr": addr, "from": 2}}
            )
            keyboard.add_button(
                label='Разное',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromgift", "addition": {"addr": addr, "from": 5}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='Защита головы',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromgift", "addition": {"addr": addr, "from": 3}}
            )
            keyboard.add_button(
                label='Броня',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromgift", "addition": {"addr": addr, "from": 4}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='Личный ящик',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromgift", "addition": {"addr": addr, "from": 6}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='На главную',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "main"}
            )

            keyboard = keyboard.get_keyboard()
            send_message(
                text=('Получение меню инвентаря для передачи вещей...'),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)

    def btn_from_gift(self, peer, addition):
        if peer in self.cm.registered_users:
            user = self.cm.registered_users[peer]
            addr = None
            from_place = None
            try:
                addr = addition["addr"]
                from_place = addition["from"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            self.cm.read_inventory(user.id, peer)

            keyboard = VkKeyboard(one_time=False, inline=False)
            dop_text = ""

            if len(user.all[from_place]) < 1:
                dop_text = '\nВ разделе инвентаря ' + settings.inventory_names[from_place] + ' пусто. Выберите действие...'
                keyboard.add_button(
                    label='На главную',
                    color=VkKeyboardColor.NEGATIVE,
                    payload={"command": "main"}
                )
            else:
                nline_cntr = 0
                cntr = 0
                for slot in user.all[from_place]:
                    label = user.all[from_place][slot].name
                    if label in self.trade_list.buy_list:
                        if len(label) > 40:
                            label = label[:40]
                        if user.all[from_place][slot].cnt == 1:
                            keyboard.add_button(
                                label=label,
                                color=VkKeyboardColor.SECONDARY,
                                payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": user.all[from_place][slot].name, "cnt": 1}}
                            )
                        else:
                            keyboard.add_button(
                                label=label,
                                color=VkKeyboardColor.SECONDARY,
                                payload={"command": "bcntgift", "addition": {"addr": addr, "from": from_place, "slot": user.all[from_place][slot].name}}
                            )

                        nline_cntr += 1
                        cntr += 1

                        if nline_cntr == 3:
                            nline_cntr = 0
                            keyboard.add_line()

                        if cntr == 29:
                            dop_text = ('Слишком много предметов. Может быть только '
                                        '30 кнопок. Если здесь нет нужных, предварительно '
                                        'попередвигайте предметы или обратитесь к '
                                        'администраторам для продажи вручную.')
                            break

            keyboard.add_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "binvgift", "addition": {"addr": addr}}
            )

            keyboard = keyboard.get_keyboard()
            send_message(
                text=('Получение меню раздела ' + settings.inventory_names[from_place] + ' доступных для передачи вещей...' + dop_text),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)

    def btn_cnt_gift(self, peer, addition):
        if peer in self.cm.registered_users:
            user = self.cm.registered_users[peer]
            addr = None
            from_place = None
            slot = None
            try:
                addr = addition["addr"]
                from_place = addition["from"]
                slot = addition["slot"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            self.cm.read_inventory(user.id, peer)

            if from_place == -1:
                keyboard = VkKeyboard(one_time=False, inline=False)
                if user.money >= 10:
                    keyboard.add_button(
                        label='10',
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": '$', "cnt": 10}}
                    )
                if user.money >= 50:
                    keyboard.add_button(
                        label='50',
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": '$', "cnt": 50}}
                    )
                if user.money >= 100:
                    keyboard.add_button(
                        label='100',
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": '$', "cnt": 100}}
                    )
                    keyboard.add_line()

                if user.money >= 500:
                    keyboard.add_button(
                        label='500',
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": '$', "cnt": 500}}
                    )
                if user.money >= 1000:
                    keyboard.add_button(
                        label='1000',
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": '$', "cnt": 1000}}
                    )
                if user.money >= 2000:
                    keyboard.add_button(
                        label='2000',
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": '$', "cnt": 2000}}
                    )
                    keyboard.add_line()

                if user.money >= 5000:
                    keyboard.add_button(
                        label='5000',
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": '$', "cnt": 5000}}
                    )
                if user.money >= 10000:
                    keyboard.add_button(
                        label='10000',
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": '$', "cnt": 10000}}
                    )
                if user.money >= 20000:
                    keyboard.add_button(
                        label='20000',
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": '$', "cnt": 20000}}
                    )
                    keyboard.add_line()

                keyboard.add_button(
                    label='Назад',
                    color=VkKeyboardColor.NEGATIVE,
                    payload={"command": "binvgift", "addition": {"addr": addr}}
                )
                keyboard = keyboard.get_keyboard()
                send_message(
                    text=('Выберите, сколько денег вы хотите передать.'),
                    attachment='',
                    sag=self.sag,
                    keyboard=keyboard,
                    peer=peer
                )
            elif slot in user.all[from_place]:
                ch_cnt = user.all[from_place][slot].cnt + 1
                if ch_cnt > 26:
                    ch_cnt = 26

                keyboard = VkKeyboard(one_time=False, inline=False)
                nline_cntr = 0
                for i in range(1, ch_cnt):
                    keyboard.add_button(
                        label=str(i),
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bconfirmgift", "addition": {"addr": addr, "from": from_place, "slot": slot, "cnt": i}}
                    )

                    nline_cntr += 1
                    if nline_cntr == 3:
                        nline_cntr = 0
                        keyboard.add_line()

                keyboard.add_button(
                    label='Назад',
                    color=VkKeyboardColor.NEGATIVE,
                    payload={"command": "bfromgift", "addition": {"addr": addr, "from": from_place}}
                )
                keyboard = keyboard.get_keyboard()
                send_message(
                    text=('Выберите, сколько ' + slot + ' вы хотите передать.'),
                    attachment='',
                    sag=self.sag,
                    keyboard=keyboard,
                    peer=peer
                )
            else:
                send_message(
                    text=('Предмет ' + slot + ' не был найден в разделе инвентаря ' + settings.inventory_names[from_place] + '. Возврат к основному меню...'),
                    attachment='',
                    sag=self.sag,
                    keyboard=mykb.main_keyboard,
                    peer=peer
                )
        else:
            nonreg_warning(self.sag, peer)

    def btn_confirm_gift(self, peer, addition):
        if peer in self.cm.registered_users:
            addr = None
            from_place = None
            slot = None
            cnt = None
            try:
                addr = addition["addr"]
                from_place = addition["from"]
                slot = addition["slot"]
                cnt = addition["cnt"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            if slot == '$' or slot in self.trade_list.buy_list:
                if addr in self.cm.registered_users:
                    keyboard = VkKeyboard(one_time=False, inline=False)
                    keyboard.add_button(
                        label='Да',
                        color=VkKeyboardColor.POSITIVE,
                        payload={"command": "gift", "addition": {"addr": addr, "from": from_place, "slot": slot, "cnt": cnt}}
                    )
                    keyboard.add_button(
                        label='Отмена',
                        color=VkKeyboardColor.NEGATIVE,
                        payload={"command": "binvgift", "addition": {"addr": addr}}
                    )
                    keyboard = keyboard.get_keyboard()
                    if slot == '$':
                        send_message(
                            text=('Вы, действительно, хотите перевести ' + str(cnt) +
                                  ' у.е. на счёт сталкера ' +
                                  self.cm.registered_users[addr].nick + '?'),
                            attachment='',
                            sag=self.sag,
                            keyboard=keyboard,
                            peer=peer
                        )
                    else:
                        send_message(
                            text=('Вы, действительно, хотите передать ' + str(cnt) + ' ед. ' +
                                  slot + ' из раздела ' +
                                  settings.inventory_names[from_place] + ' сталкеру ' +
                                  self.cm.registered_users[addr].nick + '?'),
                            attachment='',
                            sag=self.sag,
                            keyboard=keyboard,
                            peer=peer
                        )

                else:
                    send_message(
                        text=('Указанный вами получатель на данный момент недоступен для передачи. Возврат к основному меню...'),
                        attachment='',
                        sag=self.sag,
                        keyboard=mykb.main_keyboard,
                        peer=peer
                    )
            else:
                send_message(
                    text=('Предмет ' + slot + ' на этот момент более не может быть передан. Возврат к основному меню...'),
                    attachment='',
                    sag=self.sag,
                    keyboard=mykb.main_keyboard,
                    peer=peer
                )
        else:
            nonreg_warning(self.sag, peer)

    def gift_item(self, peer, addition):
        if self.closed:
            send_message(
                text=('Адъмин временно закрыл возможность передавать вещи.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
            return

        if peer in self.cm.registered_users:
            user = self.cm.registered_users[peer]
            addr = None
            from_place = None
            slot = None
            cnt = None
            try:
                addr = addition["addr"]
                from_place = addition["from"]
                slot = addition["slot"]
                cnt = addition["cnt"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            if not addr in self.cm.registered_users:
                send_message(
                    text=('Указанный вами получатель на данный момент недоступен для передачи. Возврат к основному меню...'),
                    attachment='',
                    sag=self.sag,
                    keyboard=mykb.main_keyboard,
                    peer=peer
                )
                return

            addressee = self.cm.registered_users[addr]
            self.cm.read_inventory(addressee.id, addr)

            self.cm.read_inventory(user.id, peer)
            if from_place == -1:
                if user.money >= cnt:
                    addressee.money += cnt
                    self.cm.write_inventory(addr)
                    send_message(
                        text='Сталкер ' + self.cm.registered_users[peer].nick + ' перевёл вам на счёт ' + str(cnt) + ' денежных единиц.',
                        attachment='',
                        sag=self.sag,
                        keyboard=mykb.main_keyboard,
                        peer=addr
                    )
                    user.money -= cnt
                    self.cm.write_inventory(peer)
                    send_message(
                        text='Вы успешно перевели ' + str(cnt) + ' денежных единиц на счёт сталкера ' + self.cm.registered_users[addr].nick + '.',
                        attachment='',
                        sag=self.sag,
                        keyboard=mykb.main_keyboard,
                        peer=peer
                    )
                else:
                    send_message(
                        text=('Указанное число денежных средств (' + str(cnt) + ') на данный момент отсутствует. Возврат к основному меню...'),
                        attachment='',
                        sag=self.sag,
                        keyboard=mykb.main_keyboard,
                        peer=peer
                    )
            elif slot in user.all[from_place]:
                if user.all[from_place][slot].cnt >= cnt:
                    addressee.chest[(slot + '#')] = models.ItemString(slot, user.all[from_place][slot].desc, cnt)
                    self.cm.write_inventory(addr)
                    send_message(
                        text='Сталкер ' + self.cm.registered_users[peer].nick + ' прислал вам ' + str(cnt) + ' ед. ' + slot + '. Полученное добавлено в личный ящик.',
                        attachment='',
                        sag=self.sag,
                        keyboard=mykb.main_keyboard,
                        peer=addr
                    )

                    user.all[from_place][slot].cnt -= cnt
                    if user.all[from_place][slot].cnt < 1:
                        del user.all[from_place][slot]
                    self.cm.write_inventory(peer)
                    send_message(
                        text='Вы успешно передали ' + str(cnt) +' ' + slot + ' из ' + settings.inventory_names[from_place] + ' сталкеру ' + self.cm.registered_users[addr].nick + '.',
                        attachment='',
                        sag=self.sag,
                        keyboard=mykb.main_keyboard,
                        peer=peer
                    )
                else:
                    send_message(
                        text=('Предмет ' + slot + ' не был найден в количестве ' + str(cnt) + ' в разделе инвентаря ' + settings.inventory_names[from_place] + '. Возврат к основному меню...'),
                        attachment='',
                        sag=self.sag,
                        keyboard=mykb.main_keyboard,
                        peer=peer
                    )
            else:
                send_message(
                    text=('Предмет ' + slot + ' не был найден в разделе инвентаря ' + settings.inventory_names[from_place] + '. Возврат к основному меню...'),
                    attachment='',
                    sag=self.sag,
                    keyboard=mykb.main_keyboard,
                    peer=peer
                )
        else:
            nonreg_warning(self.sag, peer)

##############################################################################
# Общие
##############################################################################

    def btn_main(self, peer, addition):
        if peer in self.cm.registered_users:
            send_message(
                text=('Получение основного меню...'),
                attachment='',
                sag=self.sag,
                keyboard=mykb.main_keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)

    def lock_trader(self, peer, addition):
        if self.closed:
            self.closed = False
            send_message(
                text=('Вы открыли возможность торговать на площадке.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
        else:
            self.closed = True
            send_message(
                text=('Вы временно закрыли возможность торговать на площадке.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )

############################################################################################################send.all???????
    def gift_inventory(self, peer, addition):
        """ Инициация передачи предмета одним игроком другому

        param peer: id пользователя
        param addition: форматированная строка:
                        '<никнейм пользователя> <количество> <что нужно передать>'
                        треугольные скобки не указываются
        """
        if self.closed:
            send_message(
                text=('Адъмин временно закрыл возможность передавать что-либо.'),
                attachment='',
                sag=self.sag,
                peer=peer,
                without_kb=True
            )
            return

        if peer in self.cm.registered_users:
            cnt = 1
            f = addition.find(' ')
            if f != -1 and f != (len(addition) - 1):
                addressee = addition[:f]
                addition = addition[f + 1:]
                f = addition.find(' ')
                if f != -1 and f != (len(addition) - 1):
                    try:
                        cnt = int(addition[:f])
                    except:
                        send_message(
                            text=('Количество передаваемых вещей введено '
                                  'некорректно.'),
                            attachment='',
                            sag=self.sag,
                            peer=peer,
                            without_kb=True
                        )
                        return
                    if cnt <= 0 or cnt > 100000:
                        send_message(
                            text=('Количество передаваемых вещей введено '
                                  'некорректно. Допустимы только числа от 1 до'
                                  ' 100000'),
                            attachment='',
                            sag=self.sag,
                            peer=peer,
                            without_kb=True
                        )
                        return
                    addition = addition[f + 1:].strip()

                    addressee_id = self.cm.find_peer_by_nick(addressee)
                    if addressee_id != 0:
                        sender = self.registered_users[peer]
                        adrs = self.registered_users[addressee_id]
                        self.cm.read_inventory(sender.id, peer)

                        if addition == '$':
                            if cnt <= sender.money:
                                adrs.money += cnt
                                self.cm.write_inventory(addressee_id)
                                send_message(
                                    text=('Пользователь ' +
                                          sender.nick +
                                          ' перевёл вам на счёт деньги в ' +
                                          'количестве: ' + str(cnt) + '.'),
                                    attachment='',
                                    sag=self.sag,
                                    peer=addressee_id,
                                    without_kb=True
                                )

                                sender.money -= cnt
                                self.cm.write_inventory(peer)
                                send_message(
                                    text=('Вы успешно перевели пользователю ' +
                                          addressee + ' денежную сумму: ' +
                                          str(cnt) + '.'),
                                    attachment='',
                                    sag=self.sag,
                                    peer=peer,
                                    without_kb=True
                                )
                            else:
                                send_message(
                                    text=('У вас нет столько средств для ' +
                                          'перевода.\nУ вас в наличии только ' +
                                          str(sender.money) + '.'),
                                    attachment='',
                                    sag=self.sag,
                                    peer=peer,
                                    without_kb=True
                                )

                        else:
                            svr = cnt
                            bag = []

                            for i in range(6, 1, -1):
                                for el in self.all[i]:
                                    if el == addition:
                                        inside_cnt = self.all[i][el].cnt
                                        desc = self.all[i][el].desc
                                        cur_bag = len(bag)

                                        div = desc.find('|')
                                        while div != -1:
                                            left = desc.find('<', div)
                                            right = desc.find('>', left)
                                            if left != -1 and right != -1 and desc[left + 1: right].isdigit():
                                                part_cnt = int(desc[left + 1: right])

                                                if part_cnt < 1 or part_cnt > inside_cnt:
                                                    desc = (desc[:div] + desc[right + 1:]).strip()
                                                    div = desc.find('|')
                                                    continue

                                                part_desc = desc[div + 1:left].strip()

                                                bag.append([part_cnt, part_desc, i])

                                                inside_cnt -= part_cnt
                                                if inside_cnt < 1:
                                                    break
                                                desc = (desc[:div] + desc[right + 1:]).strip()
                                                div = desc.find('|')
                                            else:
                                                new_div = desc.find('|', div + 1)
                                                if new_div == -1:
                                                    desc = desc[:div].strip()
                                                    break
                                                else:
                                                    desc = desc[:div] + desc[new_div:]
                                                    div = desc.find('|')

                                        if inside_cnt > 0:
                                            descs = []#######################################################
                                            descs.insert(cur_bag, [inside_cnt, desc, i])

                                        del self.all[i][el]

                            res_size = len(bag)
                            if res_size < 1:
                                send_message(
                                    text='У вас нет вещей с именем ' + addition + '.',
                                    attachment='',
                                    sag=self.sag,
                                    peer=peer,
                                    without_kb=True
                                )
                                return

                            final = {}
                            for i in range(len(bag)):
                                if cnt >= bag[i][0]:
                                    final.setdefault(bag[i][1], 0)
                                    final[bag[i][1]] += bag[i][0]
                                    cnt -= bag[i][0]
                                    bag[i] = None
                                    if cnt == 0:
                                        break
                                elif cnt < bag[i][0]:
                                    final.setdefault(bag[i][1], 0)
                                    final[bag[i][1]] += cnt
                                    bag[i][0] -= cnt
                                    cnt = 0
                                    break

                            if cnt > 0:
                                send_message(
                                    text=('У вас нет столько предметов для ' +
                                          'перевода.\nУ вас в наличии только ' +
                                          str(svr - cnt) +
                                          'ед. ' + addition + '.'),
                                    attachment='',
                                    sag=self.sag,
                                    peer=peer,
                                    without_kb=True
                                )
                                return

                            i = 0
                            for des in final:
                                adrs.chest[addition + '#' + str(i)] = models.ItemString(addition, des, final[des])
                                i += 1

                            self.cm.write_inventory(addressee_id)
                            send_message(
                                text=('Пользователь ' +
                                      sender.nick +
                                      ' передал вам:\n' + addition +
                                      ' - ' + str(svr) + 'шт.'),
                                attachment='',
                                sag=self.sag,
                                peer=addressee_id,
                                without_kb=True
                            )

                            i = 0
                            for ost in bag:
                                if ost:
                                    sender.all[ost[2]][addition + '#' + str(i)] = models.ItemString(addition, ost[1], ost[0])
                                    i += 1

                            self.cm.write_inventory(peer)
                            send_message(
                                text=('Вы успешно перевели пользователю ' +
                                      addressee + ':\n' + addition +
                                      ' - ' + str(svr) + 'шт.'),
                                attachment='',
                                sag=self.sag,
                                peer=peer,
                                without_kb=True
                            )
                    else:
                        send_message(
                            text=('Пользователь с никнеймом ' +
                                   addressee + ' не найден.'),
                            attachment='',
                            sag=self.sag,
                            peer=peer,
                            without_kb=True
                        )
                else:
                    send_message(
                        text=('Команда набрана неверно, должно быть 3 '
                              'параметра, разделённых пробелами.'),
                        attachment='',
                        sag=self.sag,
                        peer=peer,
                        without_kb=True
                    )
            else:
                send_message(
                    text=('Команда набрана неверно, должно быть 3 параметра, '
                          'разделённых пробелами.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
        else:
            nonreg_warning(self.sag, peer)

    def get_dop_keyboard(self, peer, addition):
        if peer in self.registered_users:
            nonreg_warning(self.sag, peer)
        else:
            nonreg_warning(self.sag, peer)
