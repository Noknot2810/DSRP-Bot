import models
import datetime

class InvItem:

    def __init__(self, name, desc, defined = False):
        self.name = name
        self.defined = defined
        self.desc = desc

class Disease(InvItem):

    def __init__(self, name, desc = '', percent = 100, end_date = None):
        super().__init__(name, desc)
        self.end_date = end_date
        self.percent = percent

    #def сure(self):
    #    if self.name in settings.medicine:
    #        return settings.medicine[self.name]
    #    else:
    #        return None

    #Можно ли излечить?

    #Формула расчёта последствий.

class Doc(InvItem):

    def __init__(self, name, desc = ''):
        super().__init__(name, desc)

class ItemString(InvItem):

    def __init__(self, name, desc = '', cnt = 1):
        super().__init__(name, desc)
        self.cnt = cnt

    def get_string(self):
        eco_text = '- ' + self.name
        cnt = self.cnt
        desc = self.desc

        div = desc.find('|')
        while div != -1:
            left = desc.find('<', div)
            right = desc.find('>', left)
            if left != -1 and right != -1 and desc[left + 1: right].isdigit():
                part_cnt = int(desc[left + 1: right])
                if part_cnt > cnt:
                    part_cnt = cnt

                if part_cnt < 1:
                    desc = (desc[:div] + desc[right + 1:]).strip()
                    div = desc.find('|')
                    continue
                elif part_cnt > 1:
                    eco_text += (' (' + str(part_cnt) + ')')

                part_desc = desc[div + 1:left].strip()
                if len(part_desc) > 0:
                    eco_text += (' {' + part_desc + '}')

                cnt -= part_cnt
                if cnt < 1:
                    break
                eco_text += '\n- ' + self.name
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

        if cnt > 1:
            eco_text += (' (' + str(cnt) + ')')
        elif cnt < 1:
            return ''

        if len(desc) > 0:
            eco_text += (' {' + desc + '}')

        eco_text += '\n'
        return eco_text

class PlayerData:

    def __init__(self, idp, nick, gp):
        self.id = idp
        self.nick = nick
        self.gp = gp
        self.money = 0
        self.diseases = {}
        self.docs = {}
        self.weapons = {}
        self.head_def = {}
        self.body_def = {}
        self.others = {}
        self.chest = {}
        self.all = [self.diseases, self.docs, self.weapons, self.head_def,
                    self.body_def, self.others, self.chest]

    def get_items(self):
        items = {}
        for i in range(6, 1, -1):
            for el in self.all[i]:
                items.setdefault(el, 0)
                items[el] += self.chest[el].cnt
        """
        for el in self.chest:
            items.setdefault(el, 0)
            items[el] += self.chest[el].cnt
        for el in self.others:
            items.setdefault(el, 0)
            items[el] += self.chest[el].cnt
        for el in self.body_def:
            items.setdefault(el, 0)
            items[el] += self.chest[el].cnt
        for el in self.head_def:
            items.setdefault(el, 0)
            items[el] += self.chest[el].cnt
        for el in self.weapons:
            items.setdefault(el, 0)
            items[el] += self.chest[el].cnt
        """
        return items

    def chest_add(self, slot, cnt):
        if (slot.name in self.chest) and self.chest[slot.name].desc != slot.desc:
            self.chest[(slot.name + '#')] = ItemString(slot.name, slot.desc, cnt)
        else:
            self.chest.setdefault(slot.name, ItemString(slot.name, slot.desc, 0))
            self.chest[slot.name].cnt += cnt

    def refresh_inv(self):
        for i in range(7):
            self.all[i].clear()

class Slot:

    def __init__(self, name, cost, spec, uni = False, desc = ""):
        self.name = name
        self.cost = cost
        self.unique = uni
        self.desc = desc
        self.spec = spec

class TradeSection:

    def __init__(self, name, st_id):
        self.name = name
        self.start_id = st_id
        self.slots = {}
        self.buy = False
        self.sell = False
        self.coef = 0.5
        self.visible = False
        self.spec = 0

    def __str__(self):
        return self.name + ' (' + str(len(self.slots)) + ')'

    def __len__(self):
        return len(self.slots)

    def __getitem__(self, key):
        return self.slots[key]

    def __setitem__(self, key, value):
        if key.__class__.__name__ == 'int' and key >= st_id and value.__class__.__name__ == 'TradeSection':
            self.slots[key] = value
        else:
            raise Exception

class Trader:

    def __init__(self):
        self.sections = []
        self.buy_list = {}
        self.sell_list = {}
        self.output_pages = []
        self.last_id = -1

    def __getitem__(self, key):
        for sec in self.sections:
            if key >= sec.start_id:
                #print("ATTENTION: sec=" + str(sec) + " sec_start_id=" + str(sec.start_id) + " key=" + str(key))
                return sec[key]

    def __setitem__(self, key, value):
        for sec in self.sections:
            if key >= sec.start_id:
                sec[key] = value

    def add_trade(self, sec_num, slot_num, slot_name, slot_cost):
        self.sections[sec_num].slots[slot_num] = Slot(slot_name, slot_cost, self.sections[sec_num].spec)
        #print("ATTENTION: GOOD for " + str(self.sections[sec_num]))
        self.last_id = slot_num
