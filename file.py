# Реализация виджета File, который добавляется на страницу Settings при создании файла с карточками
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import sys
from images import icons
from card import Card
import sqlite3 as sq

con = sq.connect('users.db')
cur = con.cursor()

class File(QDialog):
    def __init__(self, parent=None, file_id = None):
        super(File, self).__init__(parent)
        loadUi("ui_files/file.ui", self)
        self.parent = parent  # Сохраняем ссылку на родительское окно
        self.file_id = file_id  # Сохраняем file_id для удаления из базы данных

        self.photo.setCursor(Qt.PointingHandCursor)
        self.file.setCursor(Qt.PointingHandCursor)
        self.file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.menu.clicked.connect(self.context_menu)
        self.photo.clicked.connect(self.changeAvatar)
        # self.set_image_from_bd()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Вызываем метод родительского класса для обработки действия
            self.parent.on_click(self, self.file_id)  # Передаем себя в родительский класс

    def set_title(self, title):
        self.Name.setText(title)

    def set_quality(self, id):
        cur.execute("SELECT COUNT(*) FROM terms WHERE file_id = ?", (id,))
        result = cur.fetchone()
        # Выводим количество строк
        count = result[0] if result else 0
        self.Terms.setStyleSheet('font:12pt "Comic Sans MS";')
        self.Terms.setText(f"Кол-во терминов: {count}")
        print(f"Количество строк для file_id {id}: {count}")

    def save_file_id(self, id):
        self.file_id = id

    def set_image(self, file):
        icon = QIcon(file)
        self.photo.setIcon(icon)

    def changeAvatar(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите новый аватар", "",
                                              "Image Files (*.png *.jpg *.jpeg);;All Files (*)")
        if file:
            with open(file, 'rb') as f:
                image_data = f.read()

                cur.execute("UPDATE cards SET image_data =? WHERE user_id = ?", (image_data, self.parent.user))
                con.commit()

        icon = QIcon(file)
        self.photo.setIcon(icon)

    def context_menu(self):
        self.show_custom_context_menu(self.menu,["Delete","Edit"])

    def show_custom_context_menu(self, button, menu_item):
        menu = QMenu(self)
        menu.setStyleSheet("""
                            QMenu{
                            background-color: rgb(135, 172, 255);
                            color:black;
                            }
                            QMenu:selected{
                            background-color: rgb(135, 202, 255);
                            color:black;
                            }                     
                            """)
        # Действия кнопки
        for item_text in menu_item: # Цикл, который отображает текст в эл меню
            action = QAction(item_text,self)
            # Что-то должно происходить, когда одно из действий действительно запускается
            action.triggered.connect(self.handle_menu_item_click)
            menu.addAction(action)

        menu.move(button.mapToGlobal(button.rect().topRight()))
        menu.exec()

    def handle_menu_item_click(self):
        text = self.sender().text()
        if text == "Delete":
            self.parent.delete_file(self)

        elif text == "Edit":
            print("Открывается карточка")

    def set_image_from_bd(self):
        result = cur.execute("SELECT image_data FROM cards WHERE user_id = ?", (self.parent.user,)).fetchone()
        if result is None or result[0] is None:
            return
        else:
            image_data = result[0]  # Получаем бинарные данные изображения
            temp_file_path = "images/temp_avatar.jpg"  # Создаем временный путь для файла

            with open(temp_file_path, "wb") as f:
                f.write(image_data)

            self.set_image(temp_file_path)
            cur.close()