# Файл создания и добавления карточек в БД
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from images import icons
from PyQt5.QtGui import QIcon
import sqlite3 as sq

con = sq.connect('users.db')
cur = con.cursor()

class Card(QDialog):
    def __init__(self, user):
        super(Card, self).__init__()
        loadUi("ui_files/card.ui", self)
        self.setFixedSize(600, 770)
        self.user_id = user
        self.setWindowTitle("Cards")

        self.layout.setAlignment(Qt.AlignCenter)

        self.add_card.clicked.connect(self.add_card_to_scroll_area)
        self.Create_flashcard.clicked.connect(self.save_card)
        self.scrollArea.setWidgetResizable(True)

        self.text = None

    def add_card_to_scroll_area(self):
        new_card = self.create_card_widget()
        self.layout.addWidget(new_card, alignment=Qt.AlignCenter)

    def create_card_widget(self):
        # Создаём виджет для карточки
        card = QWidget()
        card.setStyleSheet("""
                  QWidget {
                      background-color: rgb(255, 255, 255);
                      border-radius: 10px;
                      border: 0px solid #000000;
                  }
              """)
        card.setFixedSize(440, 160)

        # Создаём макет для карточки
        slayout = QVBoxLayout(card)
        slayout.setContentsMargins(20, 20, 20, 20)
        slayout.setAlignment(Qt.AlignCenter)

        term_layout = QGridLayout()
        slayout.addLayout(term_layout)

        term_label = QLabel("Term")
        term_label.setStyleSheet("""
                    QLabel {
                        font: 11pt "Comic Sans MS";
                    }
                 """)
        term_label.setMinimumSize(363, 20)

        delete_button = QPushButton()
        delete_button.setIcon(QIcon('images/удалить.png'))
        delete_button.setIconSize(QSize(23, 23))

        term_layout.addWidget(term_label, 0, 0)
        term_layout.addWidget(delete_button, 0, 1)

        Term = QLineEdit()
        Term.setStyleSheet("""
                   QLineEdit {
                       font: 11pt "Comic Sans MS";
                       border-radius: 0px;
                       border-bottom: 2px solid black;
                   }
               """)

        definition_label = QLabel("Definition")
        definition_label.setStyleSheet("""
                           QLabel {
                               font: 11pt "Comic Sans MS";
                           }
                       """)

        Definition = QLineEdit()
        Definition.setStyleSheet("""
                           QLineEdit {
                               font: 11pt "Comic Sans MS";
                               border-radius: 0px;
                               border-bottom: 2px solid black;
                           }
                       """)

        card.setObjectName("card")
        Term.setObjectName("Term")
        Definition.setObjectName("Definition")

        # Добавляем виджеты в layout карточки
        slayout.addWidget(Term)
        slayout.addWidget(definition_label)
        slayout.addWidget(Definition)
        delete_button.clicked.connect(lambda: self.remove_layout(card))
        return card

    def save_card(self):
        title_text = self.Titlee.text()
        description_text = self.Descript.toPlainText()

        if title_text:  # Если название не пустое
            try:
                cur.execute("INSERT INTO cards (user_id, title, description) VALUES (?, ?, ?)",
                            (self.user_id, title_text, description_text))
                con.commit()
                self.text = title_text

                card_id = cur.lastrowid
                term_widgets = self.scrollArea.findChildren(QLineEdit)

                # Проходим по всем виджетам
                # Каждый виджет сохраняется в переменную term_input, а его индекс в i.
                for i, term_input in enumerate(term_widgets):
                    if term_input.objectName() == "Term":
                        term_text = term_input.text()
                        definition_input = term_input.parent().findChild(QLineEdit, "Definition")  # Ищем определение по этому же индексу
                        definition_text = definition_input.text()

                        if term_text and definition_text:  # Если оба поля не пустые (не может существовать поля без определения)
                            try:
                                # Вставляем термин и определение в таблицу terms
                                cur.execute("INSERT INTO terms (file_id, term, definition) VALUES (?, ?, ?)",
                                            (card_id, term_text, definition_text))
                                con.commit()  # Выполняем commit
                            except Exception as e:
                                print(f"Failed to insert term '{term_text}': {e}")

            except Exception as e:
                print(f"Error while inserting card or terms: {e}")
        else:
            print("Title is empty!")

        self.accept()

    def remove_layout(self, card):
        card.deleteLater()
        print("Card removed")


