# Реализация выбора действия: Изучение карточек
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import sys
import sqlite3 as sq

con = sq.connect('users.db')
cur = con.cursor()

class Choose_1_logic():
    def __init__(self, page_widget: QWidget, stacked_widget, file):
        self.page_widget = page_widget # Шаблон страницы с карточкой
        self.stacked_widget = stacked_widget
        self.file_id = file # Дает доступ к БД текущего файла

        self.pushButton = self.page_widget.findChild(QPushButton, 'back_1')
        self.pushButton.clicked.connect(self.on_button_click)

        self.next = self.page_widget.findChild(QPushButton, 'next')
        self.next.clicked.connect(self.click_next)
        self.prev = self.page_widget.findChild(QPushButton, 'Previous')
        self.prev.clicked.connect(self.click_prev)
        self.turn = self.page_widget.findChild(QPushButton, 'Turn')
        self.count = self.page_widget.findChild(QLabel, "count")
        self.replay = self.page_widget.findChild(QPushButton, "replay")
        self.replay.clicked.connect(self.click_replay)

        self.term_ = None
        self.definition_ = None

        self.stack = self.page_widget.findChild(QStackedWidget, 'CARDS')

        cur.execute("SELECT term, definition FROM terms WHERE file_id = ?", (self.file_id,))
        result = cur.fetchall() # Возвращает список всех терминов и определений в виде списка кортежей, где каждый кортеж
        # представляет собой одну строку данных.

        if result:
            self.terms_definitions = result # Сохраняем полученные карточки в список, который будет использоваться для создания карточек
            self.count.setText(f"{self.stack.currentIndex()+1}/{len(self.terms_definitions)}")

        self.create_pages()

    def create_pages(self):
        for  i, (term, definition) in enumerate(self.terms_definitions): # Проходим по всем парам термин-определение
            page = FlashCard(self.turn) # Создаем новую карточку для каждой пары
            self.term_ = self.stack.findChild(QLabel, 'Term') # Ищем виджеты определения и термина на стр
            self.definition_ = self.stack.findChild(QLabel, 'Definition')
            self.definition_.setWordWrap(True) # Перенос слов
            self.term_.setText(term) # Устанавливаем текст термина и определения
            self.definition_.setText(definition)
            self.definition_.setHidden(True)
            self.stack.addWidget(page)

    def click_next(self):
        current_index = self.stack.currentIndex()
        if current_index + 1 < len(self.terms_definitions):
            self.stack.setCurrentIndex(current_index + 1)
            self.count.setText(f"{self.stack.currentIndex() + 1}/{len(self.terms_definitions)}")
            self.term_.setHidden(False)
            self.definition_.setHidden(True)

    def click_prev(self):
        current_index = self.stack.currentIndex()
        if current_index > 0:
            self.stack.setCurrentIndex(current_index-1)
            self.count.setText(f"{current_index}/{len(self.terms_definitions)}")

    def click_replay(self):
        self.stack.setCurrentIndex(0)
        self.count.setText(f"{1}/{len(self.terms_definitions)}")

    def on_button_click(self):
        self.stacked_widget.setCurrentIndex(6)
        print(self.file_id)
        # cur.close()

class FlashCard(QDialog):
    def __init__(self,turn): # При вызове экземпляра класса передаем в параметре ссылку на кнопку для переворота карточки
        super(FlashCard, self).__init__()
        loadUi("ui_files/Flashcards.ui", self) # Загрузка интерфейса карточек

        self.turn = turn
        self.Definition.setHidden(True) # В начале прячем определение
        self.turn.clicked.connect(self.toggle_visibility) # Подкл кнопку к "перевороту"

    def toggle_visibility(self):
        if self.Term.isVisible(): # Если термин видно, то прячем его и показываем определение
            self.Term.setHidden(True)
            self.Definition.setHidden(False)
        else:
            self.Term.setHidden(False)
            self.Definition.setHidden(True)