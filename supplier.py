import settings
import models
import time

class Supplier:
    def __init__(self, session_api_p):
        self.sap = session_api_p

    """ Инициирует перезапись обсуждения с Торговой площадкой """
    def upload_trade_list(self, trader):
        """ Инициирует перезапись обсуждения с Торговой площадкой """
        """
        comms = self.sap.board.getComments(
            group_id=settings.group_id,
            topic_id=settings.trade_board_id,
            count=100
        )['items']
        for i in range(1, len(comms)):
            self.sap.board.deleteComment(
                group_id=settings.group_id,
                topic_id=settings.trade_board_id,
                comment_id=comms[i]['id']
            )
        """

        status = self.sap.board.openTopic(
            group_id=settings.group_id,
            topic_id=settings.trade_board_id
        )

        if status == 1:
            for page in trader.output_pages:
                if len(page[1]) > 0:
                    text = str(page[0]) + '\n\n'
                else:
                    continue

                for sec in page[1]:
                    text += str(sec) + '\n'

                    for id_slot in sec.slots:
                        text += str(id_slot) + ') - ' + sec[id_slot].name
                        #text += line.ljust(100, '_')
                        text += ' [' + str(sec[id_slot].cost) + ']'
                        if len(sec[id_slot].desc) > 0:
                            text += ' (' + sec[id_slot].desc + ')\n'
                        else:
                            text += '\n'

                    text += '\n'

                self.sap.board.createComment(
                    group_id=settings.group_id,
                    topic_id=settings.trade_board_id,
                    message=text,
                    from_group=1
                )
                time.sleep(5.0)

            #text = ""
            #for slot in trader.sell_list:
            #    text += str(slot) + ') - ' + trader[slot].name + '\n'
            #self.sap.board.createComment(
            #    group_id=settings.group_id,
            #    topic_id=settings.trade_board_id,
            #    message=text,
            #    from_group=1
            #)


        '''
        if status == 1:
            for sec in trader.sections:
                if sec.visible:
                    text = str(sec) + '\n'

                    for id_slot in sec.slots:
                        text += str(id_slot) + ') - ' sec[id_slot].name
                        #text += line.ljust(100, '_')
                        text += ' [' + str(sec[id_slot].cost) + ']'
                        if len(sec[id_slot].desc) > 0:
                            text += ' {' + sec[id_slot].desc + '}\n'
                        else:
                            text += '\n'

                    self.sap.board.createComment(
                        group_id=settings.group_id,
                        topic_id=settings.trade_board_id,
                        message=text,
                        from_group=1
                    )
        '''

        self.sap.board.closeTopic(
            group_id=settings.group_id,
            topic_id=settings.trade_board_id
        )

    def sload_trade_list(self):
        """ Инициирует чтение данных для наполнения Торговой площадки из файла
        TI.txt на сервере, вызывает перезапись обсуждения с Торговой площадкой,
        возвращает словарь с данными о Торговой площадке

        param peer: id пользователя, от которого поступила команда
        param text: текст команды
        param addition: приложение к команде
        """
        try:
            inp = open("T.txt",mode='r', encoding='utf-8')
        except Exception as exc:
            print("ERROR (sload): " + str(exc))
            return []
        text = inp.readlines()
        inp.close()

        cnt = 0
        extra = ['ОСТАЛЬНОЕ', []]
        trader = models.Trader()
        for line in text:
            if line.startswith("@@"):
                if len(trader.sections) > 0:
                    #coef_end = line.find('&')
                    #if coef_end != -1:
                    #    try:
                    #        coef = float(line[2:coef_end])
                    #        trader.sections[0].coef = coef
                    #    except Exception as exc:
                    #        print("ERROR (sload): " + str(exc))
                    #        continue
                    if (line.find('b') != -1):
                        trader.sections[0].buy = True
                    if (line.find('s') != -1):
                        trader.sections[0].sell = True
                    vis_pos = line.find('v')
                    if (vis_pos != -1):
                        trader.sections[0].visible = True
                        try:
                            num = int(line[vis_pos + 1]) - 1
                            trader.output_pages[num][1].append(trader.sections[0])
                        except:
                            extra[1].append(trader.sections[0])
                    if (line.find('d') != -1):
                        trader.sections[0].spec = 1
                    if (line.find('w') != -1):
                        trader.sections[0].spec = 2
                    if (line.find('h') != -1):
                        trader.sections[0].spec = 3
                    if (line.find('a') != -1):
                        trader.sections[0].spec = 4
                else:
                    print('ERROR (sload): Попытка настроить несуществующую '
                          'торговую секцию')
            elif line.startswith("@"):
                trader.sections.insert(0, models.TradeSection(line[1:-1], cnt))
            elif line.startswith("!"):
                if cnt > 0:
                    trader[cnt - 1].desc = line[1:-1]
                else:
                    raise Exception
            elif line.startswith("*") or len(line) < 2:
                continue
            elif line.startswith("`"):
                trader.output_pages.append([line[1:-1], []])
            else:
                f = line.find("==")
                if f != -1:
                    if len(trader.sections) > 0:
                        line = line.strip()
                        try:
                            trader.add_trade(0, cnt, line[:f], int(line[f + 2:]))
                        except Exception as exc:
                            print("ERROR (sload): " + str(exc))
                            continue
                        if trader.sections[0].buy:
                            trader.buy_list[trader[cnt].name] = int(trader[cnt].cost)
                        if trader.sections[0].sell:
                            cur = trader[cnt]
                            trader.sell_list[cnt] = models.Slot(cur.name, cur.cost, cur.spec, cur.unique)
                        cnt += 1
                    else:
                        print('ERROR (sload): Попытка настроить несуществующую '
                              'торговую секцию')
                else:
                    continue
        trader.output_pages.append(extra)
        #self.upload_trade_list(trader)
        return trader


    def sload_dop_trade_list(self, symb):
        """ Инициирует чтение данных для наполнения Торговой площадки из файла
        TI.txt на сервере, вызывает перезапись обсуждения с Торговой площадкой,
        возвращает словарь с данными о Торговой площадке

        param peer: id пользователя, от которого поступила команда
        param text: текст команды
        param addition: приложение к команде
        """
        try:
            inp = open("/home/Noknot/mysite/T" + symb + ".txt",mode='r', encoding='utf-8')
        except Exception as exc:
            print("ERROR (sload): " + str(exc))
            return []
        text = inp.readlines()
        inp.close()

        cnt = 0
        trader = models.Trader()
        for line in text:
            if line.startswith("@@"):
                if len(trader.sections) > 0:
                    #coef_end = line.find('&')
                    #if coef_end != -1:
                    #    try:
                    #        coef = float(line[2:coef_end])
                    #        trader.sections[0].coef = coef
                    #    except Exception as exc:
                    #        print("ERROR (sload): " + str(exc))
                    #        continue
                    #if (line.find('b') != -1):
                    #    trader.sections[0].buy = True
                    #if (line.find('s') != -1):
                    #    trader.sections[0].sell = True
                    if (line.find('d') != -1):
                        trader.sections[0].spec = 1
                    if (line.find('w') != -1):
                        trader.sections[0].spec = 2
                    if (line.find('h') != -1):
                        trader.sections[0].spec = 3
                    if (line.find('a') != -1):
                        trader.sections[0].spec = 4
                else:
                    print('ERROR (sload): Попытка настроить несуществующую '
                          'торговую секцию')
            elif line.startswith("@"):
                trader.sections.insert(0, models.TradeSection(line[1:-1], cnt))
            elif line.startswith("!"):
                if cnt > 0:
                    trader[cnt - 1].desc = line[1:-1]
                else:
                    raise Exception
            elif line.startswith("*") or len(line) < 2:
                continue
            else:
                f = line.find("==")
                if f != -1:
                    if len(trader.sections) > 0:
                        line = line.strip()
                        try:
                            trader.add_trade(0, cnt, line[:f], int(line[f + 2:]))
                        except Exception as exc:
                            print("ERROR (sload): " + str(exc))
                            continue
                        #if trader.sections[0].buy and trader.sections[0].visible:
                        #    trader.buy_list[trader[cnt].name] = [cnt, int(trader.sections[0].coef * trader[cnt].cost)]
                        trader.sections[0].sell = True
                        cur = trader[cnt]
                        trader.sell_list[cnt] = models.Slot(cur.name, cur.cost, cur.spec, cur.unique)
                        cnt += 1
                    else:
                        print('ERROR (sload): Попытка настроить несуществующую '
                              'торговую секцию')
                else:
                    continue
        return trader