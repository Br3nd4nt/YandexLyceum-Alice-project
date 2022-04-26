import os
from flask import Flask, request
import logging
import json
from cities_parser import CitiesParser

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)# filename='server.log')
logging.warning('NEW SESSION')
sessionStorage = {}
cities_parser = CitiesParser()

@app.route('/', methods=['GET'])
def get():
    return'<h1>Server is Running</h1>'


@app.route('/post', methods=['POST'])
def main():
    request.get_json(force=True)
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    try:
        high_score = req['state']
        logging.info(high_score)
        logging.info(f'User highscore: {sessionStorage[user_id]["high_score"]}')
    except Exception:
        high_score = 0
        logging.info(f'User highscore: {None}')
        
    if req['session']['new']:
            sessionStorage[user_id] = {
                'suggests': [
                    "Давай",
                    "Нет",
                ],
                'started': False,
                'difficulty': None,
                'playing': False,
                'answered_wrong': False,
                'lost': False,
                'score': 0,
                'high_score': high_score
            }
            res['response']['text'] = '''Привет! Сыграем в угадай город? 
            Я буду называть город, а ты попытаешься угадать в какой этот город находится 
            (это может оказаться непросто!)'''
            res['response']['buttons'] = get_suggests(user_id)
            return
    else:
        logging.info(f'current state: {str(sessionStorage[user_id])}')
        if sessionStorage[user_id]['playing']:
            answer = req['request']['original_utterance']
            if answer in sessionStorage[user_id]['suggests']:
                if answer == sessionStorage[user_id]['right_answer']:
                    sessionStorage[user_id]['score'] += 1
                    if sessionStorage[user_id]['difficulty'] == 'hard':
                        question = cities_parser.get_question_hard()
                    else:
                        question = cities_parser.get_question_easy()
                    text = f'''Правильно!
                    Ваш счёт: {sessionStorage[user_id]['score']}
                    Следующий город: {question[0][0]}
                    Где он находится?'''
                    sessionStorage[user_id]['answered_wrong'] = False
                    sessionStorage[user_id]['right_answer'] = question[0][1]
                    sessionStorage[user_id]['suggests'] = question[1]
                    logging.info(f'Right answer: {question[0][1]}')
                    res['response']['text'] = text
                    res['response']['buttons'] = get_suggests(user_id)
                else:
                    if not sessionStorage[user_id]['answered_wrong']:
                        text = '''К сожалению, нет.
                        Попробуй ещё раз!'''
                        sessionStorage[user_id]['answered_wrong'] = True
                        index = sessionStorage[user_id]['suggests'].index(answer)
                        sessionStorage[user_id]['suggests'].pop(index)
                        res['response']['text'] = text
                        res['response']['buttons'] = get_suggests(user_id)
                    else:
                        if sessionStorage[user_id]['score'] > sessionStorage[user_id]['high_score']:
                            res['user_state_update']['high_score'] = sessionStorage[user_id]['score']
                        hs_text = ''''''
                        text = f'''Увы, вы проиграли:(
                        {'a'}
                        хотите сыграть ещё раз?'''
                        sessionStorage[user_id]['suggests'] = [
                            'Давай',
                            'Нет'
                        ]
                        sessionStorage[user_id]['started'] = False
                        sessionStorage[user_id]['difficulty'] = None
                        sessionStorage[user_id]['playing'] = False
                        sessionStorage[user_id]['answered_wrong'] = False
                        sessionStorage[user_id]['lost'] = False
                        sessionStorage[user_id]['score'] = 0
                        res['response']['text'] = text
                        res['response']['buttons'] = get_suggests(user_id)
            else:
                res['response']['text'] = '''Я не очень поняла, повторите, пожалуйста'''
                res['response']['buttons'] = get_suggests(user_id)
        else:
            if not sessionStorage[user_id]['started']:
                if req['request']['original_utterance'].lower() in [
                    'давай',
                    'хорошо',
                    'ок'
                    ]: 
                        sessionStorage[user_id]['started'] = True
                        res['response']['text'] = '''Отлично! 
                        Какой уровень сложности ты предпочитаешь?'''
                        sessionStorage[user_id]['suggests'] = ['Сложный', 'Лёгкий']
                        res['response']['buttons'] = get_suggests(user_id)
                else:
                    res['response']['text'] = '''Ну ладно( Увидимся!'''
                    res['response']["end_session"] = True
            else:
                if sessionStorage[user_id]['difficulty'] is None:
                    if req['request']['original_utterance'].lower() in [
                        'сложный',
                        'хард',
                        'хардкор',
                        'хардкорный'
                        ]:
                        sessionStorage[user_id]['difficulty'] = 'hard'
                        sessionStorage[user_id]['playing'] = True
                        question = cities_parser.get_question_hard()
                        text = f'''Отлично! тогда начнём игру!\n
                        Ваш первый город: {question[0][0]}
                        В какой же стране он находится?'''
                        sessionStorage[user_id]['right_answer'] = question[0][1]
                        sessionStorage[user_id]['suggests'] = question[1]
                        res['response']['text'] = text
                        res['response']['buttons'] = get_suggests(user_id)
                        logging.info(f'Right answer: {question[0][1]}')

                    elif req['request']['original_utterance'].lower() in [
                        'лёгкий',
                        'легкий',
                        'изи',
                        'попроще'
                        ]:
                        sessionStorage[user_id]['playing'] = True
                        sessionStorage[user_id]['difficulty'] = 'easy'
                        question = cities_parser.get_question_easy()
                        text = f'''Отлично! тогда начнём игру!\n
                        Ваш первый город: {question[0][0]}
                        В какой же стране он находится?'''
                        sessionStorage[user_id]['right_answer'] = question[0][1]
                        sessionStorage[user_id]['suggests'] = question[1]
                        res['response']['text'] = text
                        res['response']['buttons'] = get_suggests(user_id)
                        logging.info(f'Right answer: {question[0][1]}')
                    else:
                        res['response']['text'] = '''Прости, не поняла. Можешь повторить ещё раз?'''



def get_suggests(user_id):
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]
    return suggests


if __name__ == '__main__':
    port = 6969#int(os.environ.get("PORT", 6969))
    app.run(host='0.0.0.0', port=port)