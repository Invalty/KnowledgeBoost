# Реализация выбора действия: Тестирование "Множественный выбор"
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import sqlite3 as sq
import random
import sys
from functools import partial

con = sq.connect('users.db')
cur = con.cursor()

class Choose_3_logic():
    def __init__(self, page_widget: QWidget, stacked_widget, file):
        self.page_widget = page_widget
        self.stacked_widget = stacked_widget
        self.file_id = file

        self.count_correct = 0

        self.next = self.page_widget.findChild(QPushButton, 'next_4')
        self.next.clicked.connect(self.click_next)
        self.count = self.page_widget.findChild(QLabel, "count_4")
        self.pushButton = self.page_widget.findChild(QPushButton, 'back_6')
        self.pushButton.clicked.connect(self.on_button_click)

        repeat = self.stacked_widget.findChild(QPushButton, 'repeat_2')
        repeat.clicked.connect(self.rep)
        self.try_ = self.stacked_widget.findChild(QPushButton, "try_again_2")
        self.try_.clicked.connect(self.again)

        self.term_ = None
        self.definition_ = None

        self.stack = self.page_widget.findChild(QStackedWidget, 'Choose')

        cur.execute("SELECT term, definition FROM terms WHERE file_id = ?", (self.file_id,))
        self.result = cur.fetchall()

        if self.result:
            self.terms_definitions = self.result
            self.count.setText(f"{self.stack.currentIndex() + 1}/{len(self.terms_definitions)}")

        random.shuffle(self.terms_definitions)
        self.create_pages()

    def create_pages(self):
        for i, (term, definition) in enumerate(self.terms_definitions):
            self.definition_ = self.stack.findChild(QLabel, 'Definition_3') # Получаем определение, которое у нас будет в виджете
            self.definition_.setText(definition)
            self.definition_.setWordWrap(True)
            page = Multiple_choice()

            terms = [t[0] for t in self.result if t[0] != term]  # Убираем текущий термин
            random_terms = random.sample(terms, 3)# Выбираем 3 случайных термина из оставшихся

            # Перемешиваем правильный термин и случайные
            all_terms = [term] + random_terms
            random.shuffle(all_terms)

            # Список всех виджетов, куда будут помещены термины
            self.widgets = [
                self.page_widget.findChild(QPushButton, 'var_1'),
                self.page_widget.findChild(QPushButton, 'var_2'),
                self.page_widget.findChild(QPushButton, 'var_3'),
                self.page_widget.findChild(QPushButton, 'var_4')
            ]

            # Присваиваем термины виджетам
            for i, widget in enumerate(self.widgets):
                widget.setText(all_terms[i])
                widget.clicked.connect((partial(self.check_answer, widget)))

            self.stack.addWidget(page)
            print(f"Page {i} added to stackedWidget")


    def check_answer(self, text):
        self.clicked_button = text
        self.button = self.clicked_button.text() #Кнопка, которую нажимаю
        # Получаем родительский виджет кнопки
        self.parent_widget = self.clicked_button.parent()

        # Сравниваем ответ с правильным
        current_index = self.stack.currentIndex()
        correct_term = self.terms_definitions[current_index][0]

        if self.button == correct_term:
            self.parent_widget.setStyleSheet('background-color: rgb(168, 255, 160);' 'border-radius: 30px;' ' font: 12pt "Comic Sans MS;"')  # Правильный ответ
            self.count_correct += 1
        else:
            self.parent_widget.setStyleSheet('background-color: rgb(255, 162, 160);' 'border-radius: 30px;' ' font: 12pt "Comic Sans MS;"')  # Правильный ответ


    def on_button_click(self):
        self.stacked_widget.setCurrentIndex(7)

    def click_next(self):
        current_index = self.stack.currentIndex()
        if current_index + 1 < len(self.terms_definitions):
            self.stack.setCurrentIndex(current_index + 1)
            self.count.setText(f"{self.stack.currentIndex() + 1}/{len(self.terms_definitions)}")
        elif current_index + 1 == len(self.terms_definitions):
            self.stacked_widget.setCurrentIndex(3)
            self.back_5 = self.stacked_widget.findChild(QPushButton, 'back_6')
            self.back_5.clicked.connect(self.back)
            self.text_1 = self.stacked_widget.findChild(QLabel, 'text_3')
            self.text_2 = self.stacked_widget.findChild(QLabel, 'text_4')
            self.text_1.setText(f"Вы правильно ответили на {self.count_correct} из {len(self.terms_definitions)} вопросов")
            self.text_2.setText(f"Процент правильных ответов:{self.count_correct/len(self.terms_definitions)*100}%")

    def back(self):
        self.stacked_widget.setCurrentIndex(6)

    def again(self):
        self.stacked_widget.setCurrentIndex(2)
        # ПОсле того, как доходим до последней страницы нужно удалять все поля

    def rep(self):
        self.stacked_widget.setCurrentIndex(0)

class Multiple_choice(QDialog):
    def __init__(self):
        super(Multiple_choice, self).__init__()
        loadUi("ui_files/Choose_Answer.ui", self)