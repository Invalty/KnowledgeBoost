# Реализация выбора действия: Тестирование "Короткий ответ"

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import sys
import sqlite3 as sq
import random

con = sq.connect('users.db')
cur = con.cursor()

class Choose_2_logic():
    def __init__(self, page_widget: QWidget, stacked_widget, file):
        self.page_widget = page_widget
        self.stacked_widget = stacked_widget
        self.file_id = file
        self.count_correct= 0

        self.next = self.page_widget.findChild(QPushButton, 'next_2')
        self.next.clicked.connect(self.click_next)
        self.check = self.page_widget.findChild(QPushButton, 'Check')
        self.count = self.page_widget.findChild(QLabel, "count_2")
        self.pushButton = self.page_widget.findChild(QPushButton, 'back_2')
        self.pushButton.clicked.connect(self.on_button_click)

        self.repeat = self.stacked_widget.findChild(QPushButton, 'repeat')
        self.repeat.clicked.connect(self.rep)
        self.try_ =self.stacked_widget.findChild(QPushButton, "try_again")
        self.try_.clicked.connect(self.again)

        self.term_ = None
        self.definition_ = None

        self.stack = self.page_widget.findChild(QStackedWidget, 'Shorty')

        cur.execute("SELECT term, definition FROM terms WHERE file_id = ?", (self.file_id,))
        result = cur.fetchall()

        if result:
            self.terms_definitions = result
            self.count.setText(f"{self.stack.currentIndex() + 1}/{len(self.terms_definitions)}")

        random.shuffle(self.terms_definitions)
        self.create_pages()

        self.next.setEnabled(False)
        self.check.clicked.connect(self.click_check)

    def create_pages(self):
        for i, (term, definition) in enumerate(self.terms_definitions):
            page = ShortAnswer(self.page_widget, term, definition)
            self.definition_ = self.stack.findChild(QLabel, 'Definition_2')
            self.definition_.setWordWrap(True)
            self.definition_.setText(definition)
            self.stack.addWidget(page)
            print(f"Page {i} added to stackedWidget")

    def on_button_click(self):
        self.stacked_widget.setCurrentIndex(6)

    def click_next(self):
        current_index = self.stack.currentIndex()
        if current_index + 1 < len(self.terms_definitions):
            self.stack.setCurrentIndex(current_index + 1)
            self.next.setEnabled(False)
            self.check.setEnabled(True)
            self.count.setText(f"{self.stack.currentIndex() + 1}/{len(self.terms_definitions)}")
            self.term_widget.setText("")  # Берем term из введенного поля
            self.term_widget.setStyleSheet('border-radius: 15px;'
                                           'font: 18pt "Comic Sans MS";'
                                           'border: 3px solid  #9ecdff;'
                                           'background-color: rgb(255, 255, 255);')

        elif current_index + 1 == len(self.terms_definitions):
            self.stacked_widget.setCurrentIndex(4)
            self.back_5 = self.stacked_widget.findChild(QPushButton, 'back_5')
            self.back_5.clicked.connect(self.back)
            self.text_1 = self.stacked_widget.findChild(QLabel, 'text_1')
            self.text_2 = self.stacked_widget.findChild(QLabel, 'text_2')
            self.text_1.setText(f"Вы правильно ответили на {self.count_correct} из {len(self.terms_definitions)} вопросов")
            self.text_2.setText(f"Процент правильных ответов:{self.count_correct/len(self.terms_definitions)*100}%")

    def back(self):
        self.stacked_widget.setCurrentIndex(6)

    def click_check(self):
        self.check.setEnabled(False) # Отключение кнопки check, так как проверить можно только 1 раз
        current_index = self.stack.currentIndex() # Передается текущий индекс страницы StackedWidget
        page = self.stack.widget(current_index) # Инициализируем страницу
        definition_label = page.findChild(QLabel, "Definition_2") # Ищем поле определение

        self.term_widget = self.page_widget.findChild(QTextEdit, 'Term_2') # поле термина
        user_input = self.term_widget.toPlainText() # Получаем текст введенного термина

        definition = definition_label.text() # Получаем текст определения

        if not user_input: # Если не введен текст, то кнопка не сработает
            print("Пользователь не ввел текст")
            self.check.setEnabled(True)
            return

        for term, db_definition in self.terms_definitions: # Проходимся по каждому кортежу в списке терминов
            if db_definition == definition: # Если такое определение есть, проверяем правильность ответа
                self.next.setEnabled(True)
                if user_input == term: # Если совпало, то поле именяет цвет на зеленый
                    self.term_widget.setStyleSheet('border-radius: 15px;'
                                                   ' font: 18pt "Comic Sans MS";'
                                                   'border: 3px solid  #9ecdff;'
                                                   'background-color: rgb(168, 255, 160);')
                    self.count_correct += 1
                else: # Если нет, то на красный
                    self.term_widget.setStyleSheet( 'border-radius: 15px;'
                                                   ' font: 18pt "Comic Sans MS";'
                                                   'border: 3px solid  #9ecdff;'
                                                    'background-color:rgb(255, 162, 160);')
                break

    def again(self):
        self.stacked_widget.setCurrentIndex(1)
        # ПОсле того, как доходим до последней страницы нужно удалять все поля

    def rep(self):
        self.stacked_widget.setCurrentIndex(0)

class ShortAnswer(QDialog):
    def __init__(self, parent_widget, term, definition):
        super(ShortAnswer, self).__init__(parent_widget)
        loadUi("ui_files/Short_Answer.ui", self)
