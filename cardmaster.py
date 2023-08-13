import settings
import models
import mykb
import datetime
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from general_commands import send_message, nonreg_warning

class Cardmaster:
    def __init__(self, session_api_g, session_api_p):
        self.sag = session_api_g
        self.sap = session_api_p
        self.registered_users = {}
        # Чтение данных экономических карточек из специального обсуждения
        offset = 1
        while True:
            comms = self.sap.board.getComments(
                group_id=settings.group_id,
                topic_id=settings.card_board_id,
                count=100,
                offset=offset
            )['items']

            if len(comms) == 0:
                break
            else:
                for el in comms:
                    comm_text = el['text']
                    st_id = comm_text.find('[')
                    fin_id = comm_text.find('|', st_id)

                    st_nick = comm_text.find('Позывной: ')
                    fin_nick = comm_text.find('\n', st_nick)

                    st_gp = comm_text.find('Группировка: ')
                    fin_gp = comm_text.find('\n', st_gp)

                    if (st_id != -1 and fin_id != -1 and
                            st_nick != -1 and fin_nick != -1 and
                            st_gp != -1 and fin_gp != -1 and
                            comm_text[st_id + 3:fin_id].isdigit()):
                        upr = int(comm_text[st_id + 3:fin_id])
                        self.registered_users[upr] = models.PlayerData(
                            idp = int(el['id']),
                            nick = el['text'][st_nick+10:fin_nick].strip(),
                            gp = el['text'][st_gp+13:fin_gp].strip()
                        )

                    else:
                        print('ERROR: Error in player card #' +
                               str(el['id']))

                    #self.read_inventory(
                    #    eco_id=self.registered_users[upr].id,
                    #    peer_id=upr
                    #)
            offset += 100

        #wfile = open('mysite/players.txt', mode='w')
        #for peer_id in self.registered_users:
        #    self.file_write_inventory(peer_id, wfile)
        #wfile.close()

    """ Отправка данных о персонаже пользователя и клавиатуры для
    взаимодействия с профилем
    param peer: id пользователя
    param addition: фиктивный параметр
    """
    def send_personal(self, peer):
        if peer in self.registered_users:
            keyboard = VkKeyboard(one_time=False, inline=True)
            keyboard.add_openlink_button(
                label='Ссылка на вашу карточку',
                link=(settings.card_board_topic + '?post=' +
                      str(self.registered_users[peer].id))
            )

            card_text = self.sap.board.getComments(
                group_id=settings.group_id,
                topic_id=settings.card_board_id,
                start_comment_id=self.registered_users[peer].id,
                count=1
            )['items'][0]['text']

            f = card_text.find('\n') + 1
            card_text = card_text[f:]

            send_message(
                text = card_text,
                attachment = '',
                keyboard = keyboard.get_keyboard(),
                sag=self.sag,
                peer = peer
            )
        else:
            nonreg_warning(self.sag, peer)

    """ Проверка оригинальности никнейма
    param nick: текст никнейма
    """
    def nick_originality(self, nick):
        for peer in self.registered_users:
            if self.registered_users[peer].nick == nick:
                return False
        return True

    def new_eco(self, peer, addition):
        if peer in self.registered_users:
            self.send_personal(peer)############################################################
        else:
            addition = addition.split(' ')
            try:
                if not int(addition[0]) in settings.administrators:
                    send_message(
                        text=('Сейчас вам недоступна эта команда.'),
                        attachment='',
                        sag=self.sag,
                        peer=peer
                    )
                    nonreg_warning(self.sag, peer)
                    return
            except:
                send_message(
                        text=('Сейчас вам недоступна эта команда.'),
                        attachment='',
                        sag=self.sag,
                        peer=peer
                    )
                nonreg_warning(self.sag, peer)
                return

            try:
                nick_len = len(addition[1])
                if nick_len < 1:
                    send_message(
                        text=('Прозвище должно содержать минимум один символ.'),
                        peer=peer,
                        sag=self.sag,
                        without_kb=True
                    )
                    return
            except:
                send_message(
                    text=('После команды через пробелы нужно ввести прозвище и название группировки.'),
                    peer=peer,
                    sag=self.sag,
                    without_kb=True
                )
                return

            if self.nick_originality(addition[1]) == False:
                send_message(
                    text=('В ролевой уже действует персонаж с таким прозвищем.'
                          '\nУважаемый игрок, вам придётся выбрать себе '
                          'другое прозвище.'),
                    peer=peer,
                    sag=self.sag,
                    without_kb=True
                )
                return

            if len(addition) > 2 and addition[2].lower() in settings.war_groups:
                addition[2] = settings.war_groups[addition[2].lower()]
            elif len(addition) == 2:
                addition.append('Одиночки')
            else:
                addition[2] = 'Одиночки'

            status = self.sap.board.openTopic(
                group_id=settings.group_id,
                topic_id=settings.card_board_id
            )

            if status == 1:
                player_data = self.sag.users.get(
                    user_ids=peer
                )[0]
                new_card_id = self.sap.board.createComment(
                    group_id=settings.group_id,
                    topic_id=settings.card_board_id,
                    message=('Игрок: [id' + str(peer) + '|' +
                             player_data["first_name"] + ' ' +
                             player_data["last_name"] +
                             ']\nПозывной: ' + addition[1] +
                             '\nГруппировка: ' + addition[2] +
                             '\nБолезни:\nДеньги: ' + settings.start_money +
                             '\nИнформация:\nОружие:\nЗащита головы:\nБроня:' +
                             '\nРазное:\nЛичный ящик:\n'),
                    from_group=1
                )
                self.registered_users[peer] = models.PlayerData(
                    idp = new_card_id,
                    nick = addition[1],
                    gp = addition[2])
                self.registered_users[peer].money = settings.start_money

                send_message(
                    text=('Поздравляем, теперь, когда ваша анкета принята и '
                          'ваш персонаж получил эко-карточку, вы можете '
                          'принимать участие в чатах, проводимых в '
                          'комментариях под постами на стене сообщества.\n'
                          'Ваш персонаж получил стартовые 20000, на которые '
                          'теперь вы можете приобрести начальное оружие и '
                          'экипировку на Торговой площадке (тратить все 20000 '
                          'вас никто не заставляет).'),
                    attachment='',
                    keyboard=mykb.main_keyboard,
                    sag=self.sag,
                    peer=peer
                )
                self.sap.board.closeTopic(
                    group_id=settings.group_id,
                    topic_id=settings.card_board_id
                )
            else:
                send_message(
                    text=('Возникли технические неполадки.\n'
                          'Карточка не была создана, попробуйте ещё раз '
                          'спустя время.'),
                    peer=peer,
                    sag=self.sag,
                    without_kb=True
                )

    def recheck_card(self, peer, addition):
        eco_text = self.sap.board.getComments(
            group_id=settings.group_id,
            topic_id=settings.card_board_id,
            start_comment_id=addition,
            count=1
        )['items'][0]['text']

        st_id = eco_text.find('[')
        fin_id = eco_text.find('|', st_id)

        st_nick = eco_text.find('Позывной: ')
        fin_nick = eco_text.find('\n', st_nick)

        st_gp = eco_text.find('Группировка: ')
        fin_gp = eco_text.find('\n', st_gp)

        if (st_id != -1 and fin_id != -1 and
                st_nick != -1 and fin_nick != -1 and
                st_gp != -1 and fin_gp != -1 and
                eco_text[st_id + 3:fin_id].isdigit()):
            upr = int(eco_text[st_id + 3:fin_id])
            self.registered_users[upr] = models.PlayerData(
                idp = addition,
                nick = eco_text[st_nick+10:fin_nick].strip(),
                gp = eco_text[st_gp+13:fin_gp].strip()
            )
        else:
            print('ERROR: Error in rechecking player card #' +
                   str(addition))

        #send_message(
        #    text=('Данные обновлены.'),
        #    peer=peer,
        #    sag=self.sag,
        #    without_kb=True
        #)

    def delete_card(self, peer, addition):
        for user in self.registered_users:
            if self.registered_users[user].id == addition:
                del self.registered_users[user]
                break

        #send_message(
        #    text=('Данные удалены.'),
        #    peer=peer,
        #    sag=self.sag,
        #    without_kb=True
        #)

    """ Обработка полученного никнейма для смены старого никнейма

    param peer: id пользователя
    param addition: строка, введённая пользователем
    """
    """def nickname_change(self, peer, addition):
        if peer in self.registered_users:

            nick_len = len(addition)
            if nick_len < 1:
                self.send_message(
                    text=('Прозвище должно содержать минимум один символ.\n'
                          'Попробуйте подобрать себе другое.'),
                    peer=peer,
                    without_kb=True
                )
                return

            f1 = addition.find(" ")
            if f1 != -1:
                addition = addition[:f1]
            if nick_len > 16:
                addition = addition[:16]

            if not self.nick_originality(addition):
                self.send_message(
                    text=('В группе уже существует человек с такой кличкой.'
                          '\nПопробуйте подобрать себе другую.'),
                    peer=peer,
                    without_kb=True
                )
                return

            self.registered_users[peer].nick = addition

            old_text = session_api_p.board.getComments(
                group_id=settings.group_id,
                topic_id=settings.card_board_id,
                start_comment_id=self.registered_users[peer].id,
                count=1
            )['items'][0]['text']

            f1 = old_text.find('Позывной: ')
            f2 = old_text.find('\n', f1)
            if f1 == -1 or f2 == -1:
                return

            status = session_api_p.board.editComment(
                group_id=settings.group_id,
                topic_id=settings.card_board_id,
                comment_id=self.registered_users[peer].id,
                message=old_text[:f1 + 10] + addition + old_text[f2:]
            )

            if status == 1:
                self.send_message(
                    text=('Ваше прозвище успешно изменено.\nТеперь вы: ' +
                          addition + '\nЕсли вы хотите поменять его ещё '
                          'раз, снова введите команду:\n.сnick <ваше новое '
                          'прозвище>'),
                    peer=peer,
                    without_kb=True
                )
                return
            self.send_message(
                text=('Возникли технические неполадки.\nВаше прозвище не было '
                      'изменено, попробуйте ещё раз спустя время.'),
                peer=peer,
                without_kb=True
            )
        else:
            self.nonreg_warning(peer)
    """

    """ Чтение данных в программу из экономической карточки из
    специального обсуждения

    param eco_id: id сообщения с экономической карточкой в специальном
                  обсуждении
    param peer_id: id пользователя
    """
    def read_inventory(self, eco_id, peer_id=0):
        eco_text = self.sap.board.getComments(
            group_id=settings.group_id,
            topic_id=settings.card_board_id,
            start_comment_id=eco_id,
            count=1
        )['items'][0]['text']

        if peer_id == 0:
            st_peer = eco_text.find('[') + 3
            fin_peer = eco_text.find('|', st_peer)
            try:
                peer_id = int(eco_text[st_peer:fin_peer])
            except:
                return

        if not peer_id in self.registered_users:
            return

        user = self.registered_users[peer_id]
        user.refresh_inv()
        mode = 0
        eco_text = eco_text.split('\n')
        for strg in eco_text:
            if strg.startswith('Деньги:'):
                try:
                    strg = strg[7:].strip()
                    if strg[0] == '-':
                        user.money = int(strg[1:].strip()) * -1
                    else:
                        user.money = int(strg)
                except:
                    print("ERROR: Error in reading cash in player card #" +
                          str(peer_id))
                    return
            elif strg.startswith('Игрок:') or strg.startswith('Позывной:') or strg.startswith('Группировка:') or len(strg) <= 1:
                mode = 0
                continue
            elif strg.startswith('Болезни:'):
                mode = 1
            elif strg.startswith('Информация:'):
                mode = 2
            elif strg.startswith('Оружие:'):
                mode = 3
            elif strg.startswith('Защита головы:'):
                mode = 4
            elif strg.startswith('Броня:'):
                mode = 5
            elif strg.startswith('Разное:'):
                mode = 6
            elif strg.startswith('Личный ящик:'):
                mode = 7
            elif strg.startswith('-'):
                strg = strg[1:].strip()

                desc = ''
                st_desc = strg.find('{')
                end_desc = strg.find('}', st_desc)
                if st_desc != -1 and end_desc != -1:
                    desc = strg[st_desc + 1:end_desc]
                    strg = (strg[:st_desc] + strg[end_desc + 1:]).strip()

                if mode == 1:
                    dat = None
                    st_dat = strg.find('(')
                    end_dat = strg.find(')', st_dat)
                    if st_dat != -1 and end_dat != -1:
                        try:
                            dat = datetime.datetime.strptime(strg[st_dat + 1:end_dat], "%d-%m-%Y").date()
                            strg = (strg[:st_dat] + strg[end_dat + 1:]).strip()
                        except:
                            None

                    perc = 100
                    st_perc = strg.find('[')
                    end_perc = strg.find(']', st_perc)
                    if st_perc != -1 and end_perc != -1:
                        try:
                            cnt = int(strg[st_perc + 1:end_perc])
                            strg = (strg[:st_perc] + strg[end_perc + 1:]).strip()
                        except:
                            None

                    if dat:
                        if dat > datetime.date.today():
                            user.diseases[strg] = models.Disease(strg, desc, perc, dat)
                    else:
                        user.diseases[strg] = models.Disease(strg, desc, perc)
                else:
                    if mode == 2:
                        user.docs[strg] = models.Doc(strg, desc)
                    else:
                        cnt = 1
                        st_cnt = strg.find('(')
                        end_cnt = strg.find(')', st_cnt)
                        if st_cnt != -1 and end_cnt != -1:
                            try:
                                cnt = int(strg[st_cnt + 1:end_cnt])
                                strg = (strg[:st_cnt] + strg[end_cnt + 1:]).strip()
                            except:
                                None

                        if mode == 3:
                            user.weapons.setdefault(strg, models.ItemString(strg, desc, 0))
                            if user.weapons[strg].desc != desc:
                                user.weapons[strg].desc += ' | ' + desc + ' <' + str(cnt) + '>'
                            user.weapons[strg].cnt += cnt
                        elif mode == 4:
                            user.head_def.setdefault(strg, models.ItemString(strg, desc, 0))
                            if user.head_def[strg].desc != desc:
                                user.head_def[strg].desc += ' | ' + desc + ' <' + str(cnt) + '>'
                            user.head_def[strg].cnt += cnt
                        elif mode == 5:
                            user.body_def.setdefault(strg, models.ItemString(strg, desc, 0))
                            if user.body_def[strg].desc != desc:
                                user.body_def[strg].desc += ' | ' + desc + ' <' + str(cnt) + '>'
                            user.body_def[strg].cnt += cnt
                        elif mode == 6:
                            user.others.setdefault(strg, models.ItemString(strg, desc, 0))
                            user_desc = user.others[strg].desc
                            if user_desc != desc:
                                adapt = user_desc.find(' |')
                                if adapt != -1 and user_desc[:adapt] == desc:
                                    None
                                else:
                                    adapt = user_desc.find('| ' + desc + ' <')
                                    if adapt != -1:
                                        left = user_desc.find('<', adapt)
                                        right = user_desc.find('>', left)
                                        if left != -1 and right != -1 and user_desc[left + 1: right].isdigit():
                                            part_cnt = int(user_desc[left + 1: right])
                                            user.others[strg].desc = user_desc[:left + 1] + str(part_cnt + cnt) + user_desc[right:]
                                        else:
                                            user.others[strg].desc += ' | ' + desc + ' <' + str(cnt) + '>'
                                    else:
                                        user.others[strg].desc += ' | ' + desc + ' <' + str(cnt) + '>'
                            user.others[strg].cnt += cnt
                        elif mode == 7:
                            user.chest.setdefault(strg, models.ItemString(strg, desc, 0))
                            user_desc = user.chest[strg].desc
                            if user_desc != desc:
                                adapt = user_desc.find(' |')
                                if adapt != -1 and user_desc[:adapt] == desc:
                                    None
                                else:
                                    adapt = user_desc.find('| ' + desc + ' <')
                                    if adapt != -1:
                                        left = user_desc.find('<', adapt)
                                        right = user_desc.find('>', left)
                                        if left != -1 and right != -1 and user_desc[left + 1: right].isdigit():
                                            part_cnt = int(user_desc[left + 1: right])
                                            user.chest[strg].desc = user_desc[:left + 1] + str(part_cnt + cnt) + user_desc[right:]
                                        else:
                                            user.chest[strg].desc += ' | ' + desc + ' <' + str(cnt) + '>'
                                    else:
                                        user.chest[strg].desc += ' | ' + desc + ' <' + str(cnt) + '>'

                            user.chest[strg].cnt += cnt
            else:
                print("ERROR: Error is a field of player card #" +
                      str(peer_id))
                return

##################################################################################Менять Болезни и Группировку у всех карточек местами
    """ Запись данных в экономическую карточку пользователя в специальном
    обсуждении.

    param peer_id: id пользователя
    """
    def write_inventory(self, peer_id):
        user = self.registered_users[peer_id]
        eco_text = self.sap.board.getComments(
            group_id=settings.group_id,
            topic_id=settings.card_board_id,
            start_comment_id=user.id,
            count=1
        )['items'][0]['text']

        f = eco_text.find('Болезни:')
        eco_text = eco_text[:f]

        eco_text += 'Болезни:\n'
        for el in user.diseases:
            sample = user.diseases[el]
            eco_text += '- ' + sample.name
            per = sample.percent
            if per < 100:
                eco_text += ' [' + str(per) + ']'

            dat = sample.end_date
            if dat:
                eco_text += ' (' + str(dat) + ')'

            desc = sample.desc
            if len(desc) > 0:
                eco_text += (' {' + desc + '}')

            eco_text += '\n'

        eco_text += 'Деньги: ' + str(user.money) + '\n'

        eco_text += 'Информация:\n'
        for el in user.docs:
            sample = user.docs[el]
            eco_text += '- ' + sample.name
            desc = sample.desc
            if len(desc) > 0:
                eco_text += (' {' + desc + '}')

            eco_text += '\n'

        eco_text += 'Оружие:\n'
        for el in user.weapons:
            eco_text += user.weapons[el].get_string()

        eco_text += 'Защита головы:\n'
        for el in user.head_def:
            eco_text += user.head_def[el].get_string()

        eco_text += 'Броня:\n'
        for el in user.body_def:
            eco_text += user.body_def[el].get_string()

        eco_text += 'Разное:\n'
        for el in user.others:
            eco_text += user.others[el].get_string()

        eco_text += 'Личный ящик:\n'
        for el in user.chest:
            eco_text += user.chest[el].get_string()

        if len(eco_text) > 3000:
            send_message(
                text=('Количество символов в вашей карточке превысило' +
                      ' допустимый лимит.\nК сожалению, перезапись карточки не'+
                      ' может быть завершена.\nРазгрузите карточку и повторите'+
                      ' операцию или обратитесь в администрацию за помощью.\n' +
                      'После последней операции карточка должна была принять ' +
                      'следующий вид:\n' + eco_text + '\nВНИМАНИЕ, ТО, ЧТО ' +
                      'НАПИСАНО НИЖЕ, МОЖЕТ БЫТЬ НЕ АКТУАЛЬНО!'),
                peer=peer_id,
                sag=self.sag,
                without_kb=True
            )
            return

        status = self.sap.board.editComment(
            group_id=settings.group_id,
            topic_id=settings.card_board_id,
            comment_id=user.id,
            message=eco_text
        )
        if status != 1:
            send_message(
                text=('Возникли технические неполадки.\nПроверьте состояние '
                      'вашей карточки на всякий случай.'),
                peer=peer_id,
                sag=self.sag,
                without_kb=True
            )
            return

    """ Запись данных в экономическую карточку пользователя в специальном
    обсуждении.

    param peer_id: id пользователя
    """
    def file_write_inventory(self, peer_id, out):
        user = self.registered_users[peer_id]
        eco_text = self.sap.board.getComments(
            group_id=settings.group_id,
            topic_id=settings.card_board_id,
            start_comment_id=user.id,
            count=1
        )['items'][0]['text']

        f = eco_text.find('Болезни:')
        eco_text = eco_text[:f]

        eco_text += 'Болезни:\n'
        for el in user.diseases:
            sample = user.diseases[el]
            eco_text += '- ' + sample.name
            per = sample.percent
            if per < 100:
                eco_text += ' [' + str(per) + ']'

            dat = sample.end_date
            if dat:
                eco_text += ' (' + str(dat) + ')'

            desc = sample.desc
            if len(desc) > 0:
                eco_text += (' {' + desc + '}')

            eco_text += '\n'

        eco_text += 'Информация:\n'
        for el in user.docs:
            sample = user.docs[el]
            eco_text += '- ' + sample.name
            desc = sample.desc
            if len(desc) > 0:
                eco_text += (' {' + desc + '}')

            eco_text += '\n'

        eco_text += 'Оружие:\n'
        for el in user.weapons:
            eco_text += user.weapons[el].get_string()

        eco_text += 'Броня:\n'
        for el in user.body_def:
            eco_text += user.body_def[el].get_string()

        eco_text += 'Защита головы:\n'
        for el in user.head_def:
            eco_text += user.head_def[el].get_string()

        eco_text += 'Разное:\n'
        for el in user.others:
            eco_text += user.others[el].get_string()

        eco_text += 'Личный ящик:\n'
        for el in user.chest:
            eco_text += user.chest[el].get_string()

        out.write(eco_text + "\n\n")

    def find_peer_by_nick(self, nick):
        """ Поиск id пользователя по никнейму.

        param nick: никнейм пользователя
        """
        for user in self.registered_users:
            if self.registered_users[user].nick == nick:
                return user
        for user in self.registered_users:
            if self.registered_users[user].nick.lower().startswith(nick.lower()):
                return user
        for user in self.registered_users:
            if self.registered_users[user].nick.lower().find(nick.lower()) != -1:
                return user
        return 0

    """def item_up(self, peer, addition):
        if peer in self.registered_users:
            admin = None
            item = None
            cnt = 1
            addition = addition.split(' ')
            try:
                if int(addition[0]) in settings.administrators:
                    admin = int(addition[0])
                    cnt = int(addition[1])
                    item = addition[2]
                else:
                    cnt = int(addition[0])
                    item = addition[1]
            except:
                send_message(
                    text='Вместе с командой необходимо следом указать количество и название вещи из инвентаря.',
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
                return

            user = self.registered_users[peer]
            self.read_inventory(user.id, peer)

            completed_cnt = 0
            for i in range(3, 7):
                if item in user.all[i]:
                    rem = cnt - completed_cnt
                    user_item = user.all[i][item]
                    desc = user_item.desc
                    if user_item.cnt >= rem:
                        completed_cnt = cnt
                        user_item.cnt -= rem
                        if user_item.cnt < 1:
                            del user.all[i][item]
                    else:
                        completed_cnt += user_item.cnt
                        rem = user_item.cnt
                        user_item.cnt = 0
                        del user.all[i][item]

                    user.all[i - 1].setdefault(item, models.ItemString(item, desc, 0))
                    user_desc = user.all[i - 1][item].desc
                    if user_desc != desc:
                        adapt = user_desc.find(' |')
                        if adapt != -1 and user_desc[:adapt] == desc:
                            None
                        else:
                            adapt = user_desc.find('| ' + desc + ' <')
                            if adapt != -1:
                                left = user_desc.find('<', adapt)
                                right = user_desc.find('>', left)
                                if left != -1 and right != -1 and user_desc[left + 1: right].isdigit():
                                    part_cnt = int(user_desc[left + 1: right])
                                    user.all[i - 1][item].desc = user_desc[:left + 1] + str(part_cnt + rem) + user_desc[right:]
                                else:
                                    user.all[i - 1][item].desc += ' | ' + desc + ' <' + str(rem) + '>'
                            else:
                                user.all[i - 1][item].desc += ' | ' + desc + ' <' + str(rem) + '>'
                    user.all[i - 1][item].cnt += rem


            if completed_cnt == cnt:
                self.write_inventory(peer)
                send_message(
                    text='Вы успешно переместили сместили ' + str(cnt) +' предметов ' + item + ' вверх по карточке.',
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
            elif item in user.all[2]:
                send_message(
                    text='Найденный предмет ' + item + ' уже нельзя переместить выше в вашей карточке.',
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
            elif completed_cnt == 0:
                send_message(
                    text='Не удалось найти предмет ' + item + ' в вашей карточке.',
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
            else:
                send_message(
                    text='Не удалось найти ' + str(cnt) +' предметов ' + item + ' в вашей карточке.',
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )
        else:
            nonreg_warning(self.sag, peer)"""

    def btn_replace(self, peer, addition):
        if peer in self.registered_users:
            keyboard = VkKeyboard(one_time=False, inline=False)
            keyboard.add_button(
                label='Оружие',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromrep", "addition": {"from": 2}}
            )
            keyboard.add_button(
                label='Разное',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromrep", "addition": {"from": 5}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='Защита головы',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromrep", "addition": {"from": 3}}
            )
            keyboard.add_button(
                label='Броня',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromrep", "addition": {"from": 4}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='Личный ящик',
                color=VkKeyboardColor.SECONDARY,
                payload={"command": "bfromrep", "addition": {"from": 6}}
            )

            keyboard.add_line()

            keyboard.add_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "main"}
            )

            keyboard = keyboard.get_keyboard()
            send_message(
                text=('Получение меню инвентаря для перестановки...'),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)

    def btn_from_replace(self, peer, addition):
        if peer in self.registered_users:
            user = self.registered_users[peer]
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

            self.read_inventory(user.id, peer)
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
                if len(label) > 40:
                    label = label[:40]
                if user.all[from_place][slot].cnt == 1:
                    keyboard.add_button(
                        label=label,
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "btorep", "addition": {"from": from_place, "slot": user.all[from_place][slot].name, "cnt": 1}}
                    )
                else:
                    keyboard.add_button(
                        label=label,
                        color=VkKeyboardColor.SECONDARY,
                        payload={"command": "bcntrep", "addition": {"from": from_place, "slot": user.all[from_place][slot].name}}
                    )

                nline_cntr += 1
                cntr += 1

                if nline_cntr == 3:
                    nline_cntr = 0
                    keyboard.add_line()

                if cntr == 29:
                    dop_text = ('Слишком много предметов. Может быть только '
                                '30 кнопок. Если здесь нет нужных, обратитесь'
                                ' к администраторам для перестановки вручную.')
                    break

            keyboard.add_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "brep"}
            )

            keyboard = keyboard.get_keyboard()
            send_message(
                text=('Получение меню раздела ' + settings.inventory_names[from_place] + ' для перестановки...' + dop_text),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)

    def btn_cnt_replace(self, peer, addition):
        if peer in self.registered_users:
            user = self.registered_users[peer]
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

            self.read_inventory(user.id, peer)

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
                        payload={"command": "btorep", "addition": {"from": from_place, "slot": slot, "cnt": i}}
                    )

                    nline_cntr += 1
                    if nline_cntr == 3:
                        nline_cntr = 0
                        keyboard.add_line()

                keyboard.add_button(
                    label='Назад',
                    color=VkKeyboardColor.NEGATIVE,
                    payload={"command": "bfromrep", "addition": {"from": from_place}}
                )
                keyboard = keyboard.get_keyboard()
                send_message(
                    text=('Выберите, сколько ' + slot + ' вы хотите переместить.'),
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

    def btn_to_replace(self, peer, addition):
        if peer in self.registered_users:
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

            keyboard = VkKeyboard(one_time=False, inline=False)
            if from_place != 2:
                keyboard.add_button(
                    label='Оружие',
                    color=VkKeyboardColor.SECONDARY,
                    payload={"command": "rep", "addition": {"from": from_place, "slot": slot, "cnt": cnt, "to": 2}}
                )
            if from_place != 5:
                keyboard.add_button(
                    label='Разное',
                    color=VkKeyboardColor.SECONDARY,
                    payload={"command": "rep", "addition": {"from": from_place, "slot": slot, "cnt": cnt, "to": 5}}
                )

            keyboard.add_line()

            if from_place != 3:
                keyboard.add_button(
                    label='Защита головы',
                    color=VkKeyboardColor.SECONDARY,
                    payload={"command": "rep", "addition": {"from": from_place, "slot": slot, "cnt": cnt, "to": 3}}
                )
            if from_place != 4:
                keyboard.add_button(
                    label='Броня',
                    color=VkKeyboardColor.SECONDARY,
                    payload={"command": "rep", "addition": {"from": from_place, "slot": slot, "cnt": cnt, "to": 4}}
                )

            if from_place != 6:
                keyboard.add_line()
                keyboard.add_button(
                    label='Личный ящик',
                    color=VkKeyboardColor.SECONDARY,
                    payload={"command": "rep", "addition": {"from": from_place, "slot": slot, "cnt": cnt, "to": 6}}
                )

            keyboard.add_line()

            keyboard.add_button(
                label='Назад',
                color=VkKeyboardColor.NEGATIVE,
                payload={"command": "bcntrep", "addition": {"from": from_place, "slot": slot}}
            )

            keyboard = keyboard.get_keyboard()
            send_message(
                text=('Выберите куда нужно перенести ' + str(cnt) + ' ед. ' + slot + '.'),
                attachment='',
                sag=self.sag,
                keyboard=keyboard,
                peer=peer
            )
        else:
            nonreg_warning(self.sag, peer)

    def replace_item(self, peer, addition):
        if peer in self.registered_users:
            user = self.registered_users[peer]
            from_place = None
            slot = None
            cnt = None
            to_place = None
            try:
                from_place = addition["from"]
                slot = addition["slot"]
                cnt = addition["cnt"]
                to_place = addition["to"]
            except:
                send_message(
                    text=('Неправильная команда. Не пытайтесь вызывать данную команду вручную.'),
                    attachment='',
                    sag=self.sag,
                    peer=peer,
                    without_kb=True
                )

            self.read_inventory(user.id, peer)

            if slot in user.all[from_place]:
                if user.all[from_place][slot].cnt >= cnt:
                    user.all[to_place][(slot + '#')] = models.ItemString(slot, user.all[from_place][slot].desc, cnt)
                    user.all[from_place][slot].cnt -= cnt
                    if user.all[from_place][slot].cnt < 1:
                        del user.all[from_place][slot]
                    self.write_inventory(peer)
                    send_message(
                        text='Вы успешно переместили ' + str(cnt) +' ' + slot + ' из ' + settings.inventory_names[from_place] + ' в ' + settings.inventory_names[to_place] + '.',
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
