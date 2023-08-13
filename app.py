from flask import Flask, request, json
import manager
import settings
import time

# Создание экземпляра основного класса
mng = manager.Manager()

def input_agent(data):
    """ Обработка данных, полученных от Вконтакте

        param data: словарь данных, получаемый от сервера ВК
    """
    if data['type'] == 'message_reply':
        from_id = data['object']['from_id']
        if from_id < 0:
            return
        user_id = data['object']['peer_id']
        mes_text = data['object']['text']
        text_len = len(mes_text)
        f = mes_text.find(" ")
        if text_len > 1 and mes_text[0] == '.':
            if f != -1 and f < (text_len - 1):
                mng.command_handler(user_id, mes_text[1:f].lower(),
                                    str(from_id) + ' ' + mes_text[f+1:])
            else:
                mng.command_handler(user_id, mes_text[1:].lower())

    elif data['type'] == 'message_new':
        data = data['object']['message']
        user_id = data['from_id']
        atts = data['attachments']
        try:
            pload = eval(data['payload'])
            if 'addition' in pload:
                mng.command_handler(user_id, pload['command'],
                                    pload['addition'])
            else:
                mng.command_handler(user_id, pload['command'])
        except:
            mes_text = data['text']
            text_len = len(mes_text)
            f = mes_text.find(" ")
            if text_len > 1 and mes_text[0] == '.':
                if len(atts) == 1 and mes_text == '.reload' and atts[0]['type'] == 'doc' and atts[0]['doc']['ext'] == 'txt':
                    mng.command_handler(user_id, 'reload', [atts[0]['doc']['title'], atts[0]['doc']['url']])
                elif f != -1 and f < (text_len - 1):
                    mng.command_handler(user_id, mes_text[1:f].lower(),
                                        mes_text[f+1:])
                else:
                    mng.command_handler(user_id, mes_text[1:].lower())
            elif mes_text == 'Начать':
                mng.command_handler(user_id, 'first_mes')
            else:
                mng.command_handler(user_id, [mes_text])
    elif data['type'] in {'board_post_new', 'board_post_edit', 'board_post_restore'} and data['object']['topic_id'] == settings.card_board_id:
        mng.command_handler(settings.administrators[0], 'recheck_card', data['object']['id'])
    elif data['type'] == 'board_post_delete' and data['object']['topic_id'] == settings.card_board_id:
        mng.command_handler(settings.administrators[0], 'delete_card', data['object']['id'])



app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
print("_________________________")
print("Server time : ", time.strftime('%A %B, %d %Y %H:%M:%S'));
print("_________________________")

@app.route('/', methods=['GET', 'POST'])
def processing():
    if request.method == 'POST':
        # Распаковка json из пришедшего POST-запроса
        data = json.loads(request.data)
        # Проверка наличия поля type обязательного в запросах Вконтакте
        if 'type' not in data.keys():
            return 'not vk'
        # Отправка токена привязки бота к группе при поступлении запроса на привязку
        if data['type'] == 'confirmation':
            return settings.confirmation_token
        # Отправка полученных данных функции-обработчику
        else:
            input_agent(data)
            return 'ok'
    else:
        return "Hello from Dnevniki Stalkerov RP!"
    
if __name__ == "__main__":
    app.run()
    #app.run(threaded=True)