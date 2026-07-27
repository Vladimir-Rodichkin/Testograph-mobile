from toga.style import Pack
from toga.style.pack import COLUMN, CENTER, ROW
from toga.command import Group, Command
from toga import ImageView
from functools import partial
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import pandas as pd
import json
import requests
import io
import random
import toga
import gistyc
import textwrap

AUTH_TOKEN = ''

class MyApp(toga.App):
    def tests(self):
        gist_api = gistyc.GISTyc(auth_token=AUTH_TOKEN)
        bases = gist_api.get_gists()
        for i in range(len(bases)):
            if 'tests.json' in bases[i]['files']:
                tests = json.loads(requests.get(bases[i]['files']['tests.json']['raw_url']).text)
                return tests['tests']
    def startup(self):
        self.main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()
        global user_confirmed
        try:
            gist_api = gistyc.GISTyc(auth_token=AUTH_TOKEN)
            bases = gist_api.get_gists()
            for i in range(len(bases)):
                if 'users.json' in bases[i]['files']:
                    users = json.loads(requests.get(bases[i]['files']['users.json']['raw_url']).text)
            with open(self.paths.app / 'user.json') as data:
                data_users = json.loads(data.read())
                for i in range(len(users['users'])):
                    if users['users'][i]['username'] == data_users['username'] and users['users'][i]['password'] == data_users['password']:
                        user_confirmed = True
                        self.main_panel()
                        break
                    else:
                        user_confirmed = False
                        self.create_login_interface()
        except:
            user_confirmed = False
            self.main_panel()

    def create_login_interface(self, *args, **kwargs):
        self.main_box.clear()

        username_label = toga.Label('Логин:', style=Pack(padding=(0, 5)))
        self.username_input = toga.TextInput(style=Pack(flex=1))

        password_label = toga.Label('Пароль:', style=Pack(padding=(0, 5)))
        self.password_input = toga.PasswordInput(style=Pack(flex=1))

        login_button = toga.Button('Войти',on_press = self.checking_registration, style=Pack(padding=5))
        register_button = toga.Button('Зарегистрироваться', on_press=self.create_registration_interface, style=Pack(padding=5))

        self.main_box.add(username_label)
        self.main_box.add(self.username_input)
        self.main_box.add(password_label)
        self.main_box.add(self.password_input)
        self.main_box.add(login_button)
        self.main_box.add(register_button)

    def create_registration_interface(self, *args, **kwargs):
        self.main_box.clear()
        global user_confirmed
        user_confirmed = True
        name_label = toga.Label('Имя:', style=Pack(padding=(0, 5)))
        self.name_input = toga.TextInput(style=Pack(flex=1))

        email_label = toga.Label('Почта:', style=Pack(padding=(0, 5)))
        self.email_input = toga.TextInput(style=Pack(flex=1))

        password_label = toga.Label('Пароль:', style=Pack(padding=(0, 5)))
        self.password_input = toga.PasswordInput(style=Pack(flex=1))

        register_button = toga.Button('Зарегистрироваться',on_press=self.create_new_user, style=Pack(padding=5))
        back_button = toga.Button('Обратно к Войти', on_press=self.create_login_interface, style=Pack(padding=5))

        self.main_box.add(name_label)
        self.main_box.add(self.name_input)
        self.main_box.add(email_label)
        self.main_box.add(self.email_input)
        self.main_box.add(password_label)
        self.main_box.add(self.password_input)
        self.main_box.add(register_button)
        self.main_box.add(back_button)

    def create_new_user(self, *args, **kwargs):
        username = self.name_input.value
        email = self.email_input.value
        password = self.password_input.value
        gist_api = gistyc.GISTyc(auth_token=AUTH_TOKEN)
        bases = gist_api.get_gists()
        for i in range(len(bases)):
            if 'users.json' in bases[i]['files']:
                users = json.loads(requests.get(bases[i]['files']['users.json']['raw_url']).text)
        trueq = True
        for i in range(len(users['users'])):
            if users['users'][i]['username'] == username:
                self.main_box.add(toga.Label('Такой логин уже есть.', style=Pack(padding=(0, 5))))
                trueq = False
        if not('@' in email and email.rfind('.') > email.find('@')):
            trueq = False
            self.main_box.add(toga.Label('Неправильный формат почты', style=Pack(padding=(0, 5))))
        if len(username) < 5 or len(password) < 5:
            trueq = False
            self.main_box.add(toga.Label('Пароль или почта должны быть больше 5 символов.', style=Pack(padding=(0, 5))))
        if trueq == True:
            users['users'].append({'username': username, 'password': password , 'email': email})
            with open(self.paths.app / 'users.json' , 'w+') as f:
                f.write(str(json.dumps(users)))
            gist_api.update_gist(file_name='users.json')
            with open(self.paths.app / 'users.json' , 'w+') as f:
                f.write('')
            with open(self.paths.app / 'user.json', 'r+') as data:
                data_user = json.loads(data.read())
                data_user.update(username=username, password=password)
            with open(self.paths.app / 'user.json', 'w') as data:
                data.write(json.dumps(data_user))
                self.main_box.add(toga.Label('Вы успешно создали аккаунт', style=Pack(padding=(0, 5))))
            global user_confirmed
            user_confirmed = True
            self.main_panel()

    def checking_registration(self, *args, **kwargs):
        gist_api = gistyc.GISTyc(auth_token=AUTH_TOKEN)
        username = self.username_input.value
        password = self.password_input.value
        bases = gist_api.get_gists()
        for i in range(len(bases)):
            if 'users.json' in bases[i]['files']:
                users = json.loads(requests.get(bases[i]['files']['users.json']['raw_url']).text)
        for i in range(len(users['users'])):
            if users['users'][i]['username'] == username and users['users'][i]['password'] == password:
                with open(self.paths.app / 'user.json', 'r+') as data:
                    data_user = json.loads(data.read())
                    data_user.update(username=users['users'][i]['username'], password=users['users'][i]['password'])
                with open(self.paths.app / 'user.json', 'w') as data:
                    data.write(json.dumps(data_user))
                self.main_box.clear()
                self.main_box.add(toga.Label('Вы успешно вошли', style=Pack(padding=(0, 5))))
                self.main_panel()

    def wrap_text(self, text, window_width):
        chars_per_100_pixels = 15
        max_chars_per_line = (window_width // 100) * chars_per_100_pixels

        wrapped_text = ""
        current_line_length = 0

        for word in text.split():
            if current_line_length + len(word) > max_chars_per_line:
                wrapped_text += '\n' + word
                current_line_length = len(word) + 1
            else:
                if wrapped_text:
                    wrapped_text += ' '
                    current_line_length += 1
                wrapped_text += word
                current_line_length += len(word)

        return wrapped_text

    def main_panel(self, *args, **kwargs):
        self.main_box.clear()
        self.subq = []
        user_confirmed = True
        if user_confirmed == False:
            self.main_box.add(toga.Label(f'Аккаунт не проверен\nна подлиность', style=Pack(padding=(0, 5))))
        self.main_box.add(toga.Label('Выберите предмет', style=Pack(padding=(0, 5))))
        sub = ['rus' , 'mat' , 'phy']
        for i in sub:
            image_path = f'sub_{i}.png'
            icon = toga.Icon(image_path)
            button_sub = toga.Button(
                on_press=partial(self.main_panel_sub, i),
                icon=icon,
                style=Pack(padding=5)
            )

            button_sub.style.flex = 1
            self.main_box.add(button_sub)

    def main_panel_sub(self,subject_local, *args, **kwargs):
        global subject , offline
        subject = str(subject_local)
        offline = False
        self.main_box.clear()
        self.main_window.toolbar.clear()

        command1 = Command(self.command_test_users, 'Тесты пользователей')
        command3 = Command(self.base_tasks, 'База заданий')

        self.main_window.toolbar.add(command1)
        self.main_window.toolbar.add(command3)

        self.online_or_offline()

    def online_or_offline(self, *args, **kwargs):
        self.main_box.clear()
        self.main_box.add(toga.Label('Тесты пользователей', style=Pack(padding=(5))))
        global page
        page = 1
        self.explanations = []
        self.back_to_the_main = toga.Button('Вернуться на главную', on_press=self.main_panel, style=Pack(padding_top=5))
        self.main_box.add(self.back_to_the_main)
        self.main_box.add(toga.Button('Онлайн тесты',on_press=self.online_tests, style=Pack(padding=5)))
        self.main_box.add(toga.Button('Загруженные тесты',on_press=self.offline_tests, style=Pack(padding=5)))
        if user_confirmed == True:
            self.main_box.add(toga.Button('Создать тест',on_press=self.create_test, style=Pack(padding=5)))
            self.main_box.add(toga.Button('Профиль',on_press=self.edit_profile, style=Pack(padding=5)))

    def edit_profile(self, *args, **kwargs):
        self.main_box.clear()
        self.back_to_the_main = toga.Button('Вернуться на главную', on_press=self.main_panel, style=Pack(padding_top=5))
        self.main_box.add(self.back_to_the_main)
        with open(self.paths.app / 'user.json', 'r+') as data:
            data_user = json.loads(data.read())
        self.main_box.add(toga.Label(f'Имя пользователя: {data_user["username"]}', style=Pack(padding=(0, 5))))
        self.main_box.add(toga.Label(f'Пароль: {"*"*len(data_user["password"])}', style=Pack(padding=(0, 5))))
        self.main_box.add(toga.Label('Если забыли пароль, \nпишите нам на почту: volodymyr.rod@yandex.ru', style=Pack(padding=(0, 5))))

    def create_test(self, *args, **kwargs):
        self.main_box.clear()
        self.question_list = []
        self.question_data = {}

        title_label = toga.Label('Заголовок теста:', style=Pack(padding=(0, 5)))
        self.title_input = toga.TextInput(style=Pack(flex=1))
        title_image_url_label = toga.Label('URL изображения для заголовка:', style=Pack(padding=(0, 5)))
        self.title_image_url_input = toga.TextInput(placeholder='Введите URL изображения...', style=Pack(flex=1))
        title_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        title_box.add(title_label)
        title_box.add(self.title_input)
        title_box.add(title_image_url_label)
        title_box.add(self.title_image_url_input)
        self.main_box.add(title_box)

        add_question_button = toga.Button('Добавить вопрос', on_press=self.add_question, style=Pack(padding=5))
        self.main_box.add(add_question_button)

        self.questions_container = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.questions_box = toga.ScrollContainer(content=self.questions_container, style=Pack(flex=1))
        self.main_box.add(self.questions_box)

        submit_test_button = toga.Button('Отправить тест', on_press=self.submit_test, style=Pack(padding=5))
        self.main_box.add(submit_test_button)

    def add_question(self, widget):
        question_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        question_input = toga.TextInput(placeholder='Введите вопрос...', style=Pack(padding=(0, 5)))
        question_image_url_input = toga.TextInput(placeholder='Введите URL изображения для вопроса...', style=Pack(padding=(0, 5)))
        question_box.add(question_input)
        question_box.add(question_image_url_input)

        answer_type_label = toga.Label('Тип ответа:', style=Pack(padding=(5, 5)))
        answer_type_select = toga.Selection(items=['TEXT', 'CHECK'], style=Pack(padding=(0, 5)))
        answer_type_box = toga.Box(style=Pack(direction=ROW, padding=5))
        answer_type_box.add(answer_type_label)
        answer_type_box.add(answer_type_select)
        question_box.add(answer_type_box)

        question_extras_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        question_box.add(question_extras_box)

        question_id = len(self.question_list)
        self.question_list.append(question_box)
        self.question_data[question_id] = {
            "question_input": question_input,
            "question_image_url_input": question_image_url_input,
            "answer_type_select": answer_type_select,
            "extras_container": question_extras_box
        }
        answer_type_select.on_select = lambda widget: self.on_answer_type_select(widget, question_id)

        self.add_text_extras(question_extras_box)

        self.update_questions_container()

    def on_answer_type_select(self, widget, question_id):
        question_info = self.question_data[question_id]
        question_info["extras_container"].clear()
        if widget.value == 'CHECK':
            self.add_selection_extras(question_info["extras_container"], question_id)
        elif widget.value == 'TEXT':
            self.add_text_extras(question_info["extras_container"])

    def add_text_extras(self, container):
        text_input = toga.TextInput(placeholder='Текстовый ответ...', style=Pack(padding=(0, 5)))
        container.add(text_input)

    def add_selection_extras(self, container, question_id):
        add_option_button = toga.Button(
            'Добавить вариант ответа',
            on_press=lambda w: self.add_selection_option(container, question_id),
            style=Pack(padding=5)
        )
        container.add(add_option_button)
        self.add_selection_option(container, question_id)

    def add_selection_option(self, container, question_id):
        option_input = toga.TextInput(placeholder='Вариант ответа...', style=Pack(flex=1, padding=(0, 5)))
        option_checkbox = toga.Switch(text='Правильный ответ', style=Pack(padding=(0, 5)))

        option_box = toga.Box(style=Pack(direction=ROW, padding=5, alignment='center'))
        option_box.add(option_input)
        option_box.add(option_checkbox)
        container.add(option_box)

    def update_questions_container(self):
        self.questions_container.clear()
        for question_box in self.question_list:
            self.questions_container.add(question_box)

    def submit_test(self, widget):
        with open(self.paths.app / 'user.json') as data:
            data_users = json.loads(data.read())
        test_data = {
            "name": self.title_input.value,
            "image": self.title_image_url_input.value,
            "description": f"Тест сделан в мобильной версии Тестографа автором {data_users['username']}",
            "stars": 0,
            "questions": []
        }

        for question_id, question_info in self.question_data.items():
            question_type = question_info["answer_type_select"].value
            question_answers = {
                "right_answers": [],
                "wrong_answers": []
            }

            if question_type == "TEXT":
                text_answer_input = question_info["extras_container"].children[0]
                question_answers["right_answers"].append(text_answer_input.value)
            elif question_type == "CHECK":
                for option_box in question_info["extras_container"].children:
                    if isinstance(option_box, toga.Box) and len(option_box.children) == 2:
                        answer_input, answer_checkbox = option_box.children
                        if answer_checkbox.value:
                            question_answers["right_answers"].append(answer_input.value)
                        else:
                            question_answers["wrong_answers"].append(answer_input.value)

            question_data = {
                "question": question_info["question_input"].value,
                "type": question_type,
                "image": question_info["question_image_url_input"].value,
                "answers": question_answers
            }

            test_data["questions"].append(question_data)

        gist_api = gistyc.GISTyc(auth_token=AUTH_TOKEN)
        bases = gist_api.get_gists()
        for i in range(len(bases)):
            if 'checking_the_tests.json' in bases[i]['files']:
                tests = json.loads(requests.get(bases[i]['files']['checking_the_tests.json']['raw_url']).text)
                tests['tests'].append(test_data)
                with open(self.paths.app / 'checking_the_tests.json' , 'w+') as f:
                    f.write(str(json.dumps(tests)))
                gist_api.update_gist(file_name='checking_the_tests.json')
                with open(self.paths.app / 'checking_the_tests.json' , 'w+') as f:
                    f.write('')
        self.main_box.clear()
        self.main_box.add(toga.Label(f'Тест отправлен на модерацию', style=Pack(padding=(0, 5))))
        back_btn = toga.Button('Вернуться', on_press=partial(self.main_panel_sub , subject))
        self.main_box.add(back_btn)


    def offline_tests(self, *args, **kwargs):
        self.test_list = []
        self.main_box.clear()
        global offline
        offline = True
        self.base_users_tasks()

    def online_tests(self, *args, **kwargs):
        self.test_list = []
        global offline
        offline = False
        self.base_users_tasks()


    def base_users_tasks(self, *args, **kwargs):
        if offline == False:
            tests_temp = self.tests()
        else:
            with open(self.paths.app / 'save_test.json', 'r+') as text:
                tests_temp = json.loads(text.read())['tests']
        self.num_buttons = len(tests_temp)
        self.button_container = toga.Box(style=Pack(direction=COLUMN, padding=5, alignment=CENTER))
        self.scroll_container = toga.ScrollContainer(horizontal=False, content=self.button_container)
        self.main_window.content = self.scroll_container
        self.main_window.show()
        self.main_box.clear()
        start_index = (page - 1) * 10
        end_index = min(start_index + 10, self.num_buttons)
        item_box = toga.Box(
            style=Pack(direction=COLUMN, padding=5, alignment=CENTER)
        )
        for i in range(start_index, end_index):
            if offline == False:
                try:
                    response = requests.get(tests_temp[i]['image'])
                    response.raise_for_status()
                    image_data = response.content
                    image = Image.open(io.BytesIO(image_data))
                    image.thumbnail((200, 200))
                    item_box.add(toga.ImageView(image=image))
                except Exception as e:
                    image = toga.Image('1.png')
                    image_view = toga.ImageView(
                        image=image,
                        style=Pack(width=200, height=200, padding_bottom=5)
                    )
                    item_box.add(image_view)

            label = toga.Label(tests_temp[i]['name'], style=Pack(padding=5, text_align=CENTER))
            self.num_question = 0
            start_button = toga.Button('Приступить', on_press=lambda widget, button_number=i: self.start_test(widget, button_number, None), style=Pack(padding=5))
            item_box.add(label)
            item_box.add(start_button)
            if offline == False:
                save_test = toga.Button('Сохранить тест', on_press=lambda widget, button_number=i: self.save_test(widget, button_number), style=Pack(padding=5))
                item_box.add(save_test)
            else:
                delete_save_test = toga.Button('Удалить тест', on_press=lambda widget, button_number=i: self.delete_save_test(widget, button_number), style=Pack(padding=5))
                item_box.add(delete_save_test)

            self.button_container.add(item_box)

            self.button_container.add(toga.Label(text='', style=Pack(width=self.main_window.content.style.width, height=1, background_color='#DCDCDC')))  # Пустой текст

        nav_buttons = toga.Box(style=Pack(direction=ROW, padding=5, alignment=CENTER))
        if page > 1:
            back_button = toga.Button('Назад', on_press=lambda widget: self.change_page(page - 1))
            nav_buttons.add(back_button)
        if end_index < self.num_buttons:
            next_button = toga.Button('Дальше', on_press=lambda widget: self.change_page(page + 1))
            nav_buttons.add(next_button)
        self.button_container.add(nav_buttons)

    def delete_save_test(self, widget , button_number):
        with open(self.paths.app / 'save_test.json' , 'br') as data:
            text = json.loads(data.read())
            text["tests"].pop(button_number)
        with open(self.paths.app / 'save_test.json' , 'w+' , encoding='utf-8') as data:
            data.write(str(json.dumps(text)))
        self.offline_tests()
    def save_test(self, widget , button_number):
        self.test = self.tests()[button_number]
        for i in range(len(self.test['questions'])):
            try:
                response = requests.get(self.test['questions'][i]['image'])
                with open(self.paths.app / f"image_save/{[button_number]}-{i}-.png", 'wb') as f:
                    f.write(response.content)
                    self.test['questions'][i]['image'] = f"image_save/{[button_number]}-{i}-.png"
            except:
                self.test['questions'][i]['image'] = 'None'
        try:
            with open(self.paths.app / 'save_test.json' , 'r', encoding='utf-8') as data:
                data_users = json.loads(data.read())
        except FileNotFoundError:
            data_users = {}
        if str(data_users) == '{}':
            with open(self.paths.app / 'save_test.json' , 'w+' , encoding='utf-8') as data:
                data_users = {'tests': [self.test]}
                data.write(str(json.dumps(data_users)))
        else:
            with open(self.paths.app / 'save_test.json' , 'w+') as data:
                data_users['tests'].append(self.test)
                data.write(str(json.dumps(data_users)))

    def start_test(self, widget, button_number , subject):
        self.user_answers = []
        self.main_box.clear()
        self.question_label = toga.Label('Вопрос появится здесь', style=Pack(padding_bottom=5))
        self.submit_button = toga.Button('Отправить ответ', on_press=partial(self.submit_answer, subject), style=Pack(padding_top=5))
        self.result_label = toga.Label('Результат появится здесь', style=Pack(padding_top=5))

        self.question_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.answers_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.result_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.chart_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        self.table_box = toga.Box(style=Pack(direction=COLUMN, padding=5))

        self.main_box = toga.Box(children=[self.question_box, self.answers_box, self.submit_button, self.result_box, self.chart_box, self.table_box], style=Pack(direction=COLUMN, padding=10))
        self.scroll_container = toga.ScrollContainer(horizontal=False, content=self.main_box)
        self.main_window.content = self.scroll_container
        if button_number != 'ege':
            if offline == False:
                self.test = self.tests()[button_number]['questions']
            else:
                with open(self.paths.app / 'save_test.json', 'r+') as text:
                    self.test = json.loads(text.read())['tests'][button_number]['questions']
        else:
            self.test = self.test_list
        self.current_question_index = 0
        self.correct_answers = 0
        self.display_question()

    def clear_box(self, box):
        while box.children:
            child = box.children[0]
            box.remove(child)

    def display_question(self):
        self.clear_box(self.question_box)
        self.clear_box(self.answers_box)
        self.clear_box(self.result_box)
        if self.current_question_index < len(self.test):
            question = self.test[self.current_question_index]
            if question.get('image'):
                image_url = question['image']
                try:
                    if offline == False:
                        if image_url[:3] != 'zad':
                            response = requests.get(image_url)
                            response.raise_for_status()
                            image_data = response.content
                            pil_image = Image.open(io.BytesIO(image_data))
                            pil_image.thumbnail((200, 200))
                            self.question_box.add(toga.ImageView(image=pil_image))
                        else:
                            image = toga.Image(f'image_sub\{question["image"]}.png')
                            image_view = toga.ImageView(
                                image=image,
                                style=Pack(width=200, height=200, padding_bottom=5)
                            )
                            self.question_box.add(image_view)
                    else:
                        image = toga.Image(question['image'])
                        image_view = toga.ImageView(
                            image=image,
                            style=Pack(width=200, height=200, padding_bottom=5)
                        )
                        self.question_box.add(image_view)
                except Exception as e:
                    pass
            wrapped_question = self.wrap_text(question['question'], self.main_window.size[0])
            question_label = toga.Label(text=wrapped_question, style=Pack(padding_bottom=5))
            self.question_box.add(question_label)

            self.setup_answer_input(question['type'], question.get('answers', {}))
        else:
            self.subq = []
            self.show_answers_table()
            self.result_label.text = f'Тест завершен. Правильных ответов: {self.correct_answers}'
            self.back_to_the_main = toga.Button('Вернуться на главную', on_press=self.main_panel, style=Pack(padding_top=5))
            self.result_box.add(self.back_to_the_main)
            self.result_box.add(self.result_label)
            self.main_box.remove(self.submit_button)
            self.show_pie_chart()
            if self.explanations != []:
                self.result_box.add(toga.Label(text='Пояснения:', style=Pack(padding_bottom=5)))
                for i in range(len(self.explanations)):
                    self.result_box.add(toga.Label(text=f'№{i}: {self.wrap_text(self.explanations[i], self.main_window.size[0])}', style=Pack(padding_bottom=5)))
            self.explanations = []

    def pil_image_to_toga_image(self, pil_image):
        image_byte_array = io.BytesIO()
        pil_image.save(image_byte_array, format='png')
        image_byte_array.seek(0)
        return toga.Image.from_bytes(image_byte_array.read())

    def setup_answer_input(self, question_type, answers):
        if question_type == 'TEXT':
            self.text_input = toga.TextInput(style=Pack(flex=1))
            self.answers_box.add(self.text_input)
        elif question_type == 'RADIO':
            options = answers['right_answers'] + answers['wrong_answers']
            self.radio_select = toga.Selection(items=options, style=Pack(flex=1))
            self.answers_box.add(self.radio_select)
        elif question_type == 'CHECK':
            self.check_inputs = []
            for option in answers['right_answers'] + answers['wrong_answers']:
                check_switch = toga.Switch(text=option, style=Pack(padding=5))
                self.check_inputs.append(check_switch)
                self.answers_box.add(check_switch)

    def submit_answer(self, subject, widget):
        question = self.test[self.current_question_index]
        self.num_question += 1
        if question['type'] == 'TEXT':
            user_answer = self.text_input.value.strip()
            if user_answer.lower() in [ans.lower() for ans in question['answers']['right_answers']]:
                self.correct_answers += 1
                if self.test == self.test_list:
                    with open(self.paths.app / 'ircorrect.json', 'r+') as text:
                        ircorrect = json.loads(text.read())
                        if self.num_question in ircorrect[subject]:
                            ircorrect[subject].remove(self.num_question)
                            with open(self.paths.app / 'ircorrect.json', 'w') as outfine:
                                json.dump(ircorrect, outfine)
                if self.subq != []:
                    with open(self.paths.app / 'ircorrect.json', 'r+') as text:
                        ircorrect = json.loads(text.read())
                        if self.subq[self.num_question-1] in ircorrect[subject]:
                            ircorrect[subject].remove(self.subq[self.num_question-1])
                            with open(self.paths.app / 'ircorrect.json', 'w') as outfine:
                                json.dump(ircorrect, outfine)
            else:
                if self.test == self.test_list:
                    with open(self.paths.app / 'ircorrect.json', 'r+') as text:
                        ircorrect = json.loads(text.read())
                        if not(self.num_question in ircorrect[subject]):
                            ircorrect[subject].append(self.num_question)
                            with open(self.paths.app / 'ircorrect.json', 'w') as outfine:
                                json.dump(ircorrect, outfine)
                if self.subq != []:
                    with open(self.paths.app / 'ircorrect.json', 'r+') as text:
                        ircorrect = json.loads(text.read())
                        if not(self.subq[self.num_question-1] in ircorrect[subject]):
                            ircorrect[subject].append(self.subq[self.num_question-1])
                            with open(self.paths.app / 'ircorrect.json', 'w') as outfine:
                                json.dump(ircorrect, outfine)
        elif question['type'] == 'RADIO':
            if self.radio_select.value in question['answers']['right_answers']:
                self.correct_answers += 1
        elif question['type'] == 'CHECK':
            user_answer = [switch.text for switch in self.check_inputs if switch.value]
            if all(answer in question['answers']['right_answers'] for answer in user_answer) and len(user_answer) == len(question['answers']['right_answers']):
                self.correct_answers += 1
        self.user_answers.append(user_answer)

        self.current_question_index += 1
        self.display_question()

    def show_pie_chart(self):
        correct = self.correct_answers
        incorrect = len(self.test) - correct
        labels = ['Правильные ответы', 'Неправильные ответы']
        sizes = [correct, incorrect]
        colors = ['#66CDAA', '#FF6347']

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')


        image_stream = io.BytesIO()
        plt.savefig(image_stream, format='png')
        image_stream.seek(0)

        pil_image = Image.open(image_stream)
        pil_image.thumbnail((400, 400))
        self.chart_box.add(toga.ImageView(image=pil_image))

    def show_answers_table(self):
        question_answers = self.test
        for item in question_answers:
            item['question'] = item['question'][:70]

        data = {
            'Вопрос': [question['question'] for question in question_answers],
            'Ответ\nпользователя': self.user_answers,
            'Правильный\nответ': [question['answers']['right_answers'] for question in question_answers]
        }

        width, height = 400, len(self.user_answers)*150
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)

        num_rows = len(data['Вопрос']) + 1
        num_cols = len(data.keys())
        cell_width = width // num_cols
        cell_height = height // num_rows

        for i in range(num_rows + 1):
            draw.line([(0, i * cell_height), (width, i * cell_height)], fill='black', width=2)

        for i in range(num_cols + 1):
            draw.line([(i * cell_width, 0), (i * cell_width, height)], fill='black', width=2)

        # Создаем шрифт yeast.otf
        font_path = str(self.paths.app/"yeast.otf")
        font = ImageFont.truetype(font_path, 15, 0 ,'utf-8')

        # Добавляем текст в ячейки
        headings = list(data.keys())

        for i, heading in enumerate(headings):
            draw.text((i * cell_width + 10, 10), heading, fill='black', font=font)

        for i, question in enumerate(data['Вопрос']):
            for j, heading in enumerate(headings):
                item = str(data[heading][i])
                y = (i + 1) * cell_height + 10
                lines = textwrap.wrap(item, width=13)
                for line in lines:
                    draw.text((j * cell_width + 10, y), line, fill='black', font=font)
                    y += font.size

        image_view = toga.ImageView(image=img)
        self.table_box.add(image_view)

    def load_questions(self, subject):
        self.main_box.clear()
        with open(self.paths.app / 'ircorrect.json', 'r+') as text:
            ircorrect = json.loads(text.read())
        self.back_to_the_main = toga.Button('Вернуться на главную', on_press=self.main_panel, style=Pack(padding_top=5))
        self.main_box.add(self.back_to_the_main)
        if subject == 'mat':
            with open(self.paths.app / 'questions_math.json', 'r', encoding='utf-8') as f:
                self.questions_data = json.load(f)
            for sub_sub in ['База' , 'Профиль']:
                btn_create_test = toga.Button(f'Тест ЕГЭ ({sub_sub})', on_press=partial(self.crate_test_ege , sub_sub , subject), style=Pack(padding_top=5))
                btn_create_wrong = toga.Button(f'Составить тест ЕГЭ ({sub_sub})', on_press=partial(self.wrong_tem , sub_sub , subject), style=Pack(padding_top=5))
                self.main_box.add(btn_create_test , btn_create_wrong)
            kol = 0
            for category in self.questions_data:
                if kol in ircorrect['mat']:
                    btn = toga.Button(
                        f"[Были ошибки] {category['title'].strip()}",
                        on_press=partial(self.show_question, category['questions']),
                        style=Pack(padding=5)
                    )
                    self.main_box.add(btn)
                else:
                    btn = toga.Button(
                        category['title'].strip(),
                        on_press=partial(self.show_question, category['questions']),
                        style=Pack(padding=5)
                    )
                    self.main_box.add(btn)
                kol +=1
            kol = 0
        if subject == 'rus':
            with open(self.paths.app / 'questions_rus.json', 'r', encoding='utf-8') as f:
                self.questions_data = json.load(f)
            sub_sub = ''
            btn_create_test = toga.Button(f'Тест ЕГЭ ', on_press=partial(self.crate_test_ege , sub_sub , subject), style=Pack(padding_top=5))
            btn_create_wrong = toga.Button(f'Составить тест ЕГЭ ', on_press=partial(self.wrong_tem , sub_sub , subject), style=Pack(padding_top=5))
            self.main_box.add(btn_create_test , btn_create_wrong)
            kol = 0
            for category in self.questions_data:
                if kol in ircorrect['rus']:
                    btn = toga.Button(
                        f"[Были ошибки] {category['title'].strip()}",
                        on_press=partial(self.show_question, category['questions']),
                        style=Pack(padding=5)
                    )
                    self.main_box.add(btn)
                else:
                    btn = toga.Button(
                        category['title'].strip(),
                        on_press=partial(self.show_question, category['questions']),
                        style=Pack(padding=5)
                    )
                    self.main_box.add(btn)
                kol +=1
            kol = 0
        if subject == 'phy':
            with open(self.paths.app / 'questions_phy.json', 'r', encoding='utf-8') as f:
                self.questions_data = json.load(f)
            sub_sub = ''
            btn_create_test = toga.Button(f'Тест ЕГЭ ', on_press=partial(self.crate_test_ege , sub_sub , subject), style=Pack(padding_top=5))
            btn_create_wrong = toga.Button(f'Составить тест ЕГЭ ', on_press=partial(self.wrong_tem , sub_sub , subject), style=Pack(padding_top=5))
            self.main_box.add(btn_create_test , btn_create_wrong)
            kol = 0
            for category in self.questions_data:
                if kol in ircorrect['phy']:
                    btn = toga.Button(
                        f"[Были ошибки] {category['title'].strip()}",
                        on_press=partial(self.show_question, category['questions']),
                        style=Pack(padding=5)
                    )
                    self.main_box.add(btn)
                else:
                    btn = toga.Button(
                        category['title'].strip(),
                        on_press=partial(self.show_question, category['questions']),
                        style=Pack(padding=5)
                    )
                    self.main_box.add(btn)
                kol +=1
            kol = 0

    def wrong_tem(self, sub_sub , subject, widget):
        self.main_box.clear()
        self.main_box.add(toga.Label('Составить вариант:', style=Pack(padding=(0, 5))))
        self.switches = {}
        with open(self.paths.app / 'ircorrect.json', 'r+') as text:
            ircorrect = json.loads(text.read())
            if subject == 'mat':
                if sub_sub == 'База':
                    q = range(0, 21)
                else:
                    q = range(21, 40)
                for i in q:
                    if i in ircorrect['mat']:
                        switch = toga.Switch(f'[Были ошибки] {self.questions_data[i]["title"].splitlines()[1]}')
                    else:
                        switch = toga.Switch(self.questions_data[i]["title"].splitlines()[1])
                    self.switches[switch] = i
                    self.main_box.add(switch)
            else:
                q = range(len(self.questions_data))
                for i in q:
                    if i in ircorrect[subject]:
                        switch = toga.Switch(f'[Были ошибки] {self.questions_data[i]["title"].splitlines()[1]}')
                    else:
                        switch = toga.Switch(self.questions_data[i]["title"].splitlines()[1])
                    self.switches[switch] = i
                    self.main_box.add(switch)
        proceed_button = toga.Button('Приступить', on_press=partial(self.on_proceed_pressed, subject), style=Pack(padding=(5, 5)))
        self.main_box.add(proceed_button)

    def on_proceed_pressed(self, subject ,widget):
        sub_sub = []
        for switch, index in self.switches.items():
            if switch.value:
                sub_sub.append(index)
        self.crate_test_ege(sub_sub, subject)
    def crate_test_ege(self, sub_sub, subject, *args, **kwargs):
        self.num_question = 0
        self.test_list = []
        self.explanations = []
        try:
            while True:
                if subject == 'mat':
                    if sub_sub == 'База':
                        self.subq = range(0, 22)
                    elif sub_sub == 'Профиль':
                        self.subq = range(22, 40)
                    else:
                        self.subq = sub_sub
                    for num_question in self.subq:
                        random_num = random.randint(0, len(self.questions_data[num_question]['questions']))
                        self.explanations.append(self.questions_data[num_question]['questions'][random_num]['explanation'])
                        self.test_list.append({'question': self.questions_data[num_question]['questions'][random_num]['question'] , 'type': 'TEXT' , 'image': self.questions_data[num_question]['questions'][random_num]['imageUrl'] , 'answers': {'right_answers': self.questions_data[num_question]['questions'][random_num]['answer']}})
                if subject == 'rus':
                    if sub_sub == '':
                        sub_sub = range(len(self.questions_data))
                    else:
                        self.subq = sub_sub
                    for num_question in sub_sub:
                        if not(num_question in [1,2,22,23,24,25,26]):
                            random_num = random.randint(0, len(self.questions_data[num_question]['questions']))
                        self.explanations.append(self.questions_data[num_question]['questions'][random_num]['explanation'])
                        self.test_list.append({'question': self.questions_data[num_question]['questions'][random_num]['question'] , 'type': 'TEXT' , 'image': self.questions_data[num_question]['questions'][random_num]['imageUrl'] , 'answers': {'right_answers': self.questions_data[num_question]['questions'][random_num]['answer']}})
                if subject == 'phy':
                    if sub_sub == '':
                        sub_sub = range(len(self.questions_data))
                    else:
                        self.subq = sub_sub
                    for num_question in sub_sub:
                        random_num = random.randint(0, len(self.questions_data[num_question]['questions']))
                        self.explanations.append(self.questions_data[num_question]['questions'][random_num]['explanation'])
                        self.test_list.append({'question': self.questions_data[num_question]['questions'][random_num]['question'] , 'type': 'TEXT' , 'image': self.questions_data[num_question]['questions'][random_num]['imageUrl'] , 'answers': {'right_answers': self.questions_data[num_question]['questions'][random_num]['answer']}})
                break
        except:
            pass
        self.start_test('ege', 'ege', subject)

    def show_question(self, questions, widget):
        self.main_box.clear()
        question = random.choice(questions)
        wrapped_question = self.wrap_text(question['question'], self.main_window.size[0])
        question_label = toga.Label(text=wrapped_question, style=Pack(padding_bottom=5))
        self.main_box.add(question_label)
        if question["imageUrl"] != 'empty':
            try:
                image = toga.Image(f'image_sub\{question["imageUrl"]}.png')
                image_view = toga.ImageView(
                    image=image,
                    style=Pack(width=200, height=200, padding_bottom=5)
                )
                self.main_box.add(image_view)
            except:
                pass

        answer_input = toga.TextInput()
        submit_btn = toga.Button(
            'Отправить ответ',
            on_press=partial(self.check_answer, question['answer'], answer_input, question['explanation'])
        )

        self.main_box.add(answer_input)
        self.main_box.add(submit_btn)

    def check_answer(self, correct_answer, answer_input, explanation, widget):
        user_answer = answer_input.value
        result_message = f"Правильный ответ: {correct_answer}\nПояснение: \n{self.wrap_text(explanation,self.main_window.size[0])}"
        if user_answer == correct_answer:
            dialog = 'Верно'
        else:
            dialog = 'Неверно'
        self.main_box.clear()
        self.scroll_container = toga.ScrollContainer(horizontal=False, content=self.main_box)
        self.main_window.content = self.scroll_container
        result_label = toga.Label(dialog + '\n' + result_message)
        self.main_box.add(result_label)
        back_btn = toga.Button('Вернуться', on_press=partial(self.main_panel_sub , subject))
        self.main_box.add(back_btn)

    def change_page(self):
        self.button_container.clear()
        self.base_users_tasks()

    def command_test_users(self, widget):
        try:
            self.button_container.clear()
        except:
            pass
        self.online_or_offline()


    def base_tasks(self, widget):
        try:
            self.button_container.clear()
        except:
            pass
        self.scroll_container = toga.ScrollContainer(horizontal=False, content=self.main_box)
        self.main_window.content = self.scroll_container
        self.main_window.show()
        self.load_questions(subject)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, formal_name='Тестограф', app_id='com.testograph.application', icon='resources/testograph.png', **kwargs)

def main():
    return MyApp()

if __name__ == '__main__':
    main().main_loop()
