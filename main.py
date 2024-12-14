# Реализация основного окна приложения
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from card import Card
from images import icons
from tree import tree
from new import *
from file import File
import sqlite3 as sq

# Импортируем файлы с логикой для страниц
from choose1 import Choose_1_logic
from choose2 import Choose_2_logic
from choose3 import Choose_3_logic

con = sq.connect('users.db')
cur = con.cursor()

class Main(QMainWindow):
    def __init__(self, cur_user):
        super(Main, self).__init__()
        loadUi("ui_files/main_body.ui", self)
        self.user = cur_user
        current_user = cur.execute("SELECT name FROM users WHERE user_id = ?", (self.user,)).fetchone()
        name = current_user[0]  # Извлекаем имя

        self.current_file = None
        self.delete_widget = None

        self.home_text.clicked.connect(self.switch_to_Home)
        self.home_button.clicked.connect(self.switch_to_Home)

        self.files_text.clicked.connect(self.switch_to_Files)
        self.files_button.clicked.connect(self.switch_to_Files)

        self.settings_text.clicked.connect(self.switch_to_Settings)
        self.settings_button.clicked.connect(self.switch_to_Settings)

        self.label.setText(f'{name}')
        self.icon_pesh.setHidden(True)

        # Settings окно
        self.logo_2.clicked.connect(self.change_logo)
        self.change_user.clicked.connect(self.Change_2)
        self.change_pass.clicked.connect(self.Change_1)
        # Загружаем аватар пользователя
        self.load_avatar()

        # Folders окно
        self.scroll_layout = self.gridLayout_3 # Это layout, куда добавляются файлы
        self.scrollArea.setWidgetResizable(True)
        self.columns = 3  # Количество столбцов в сетке
        self.ADD.clicked.connect(self.create_card)
        self.add_files_from_db()  # Загружаем файлы при старте

        # Choosing окно
        self.choice.mousePressEvent = self.on_click_1
        self.choice_2.mousePressEvent = self.on_click_2
        self.choice_3.mousePressEvent = self.on_click_3
        self.back_3.clicked.connect(self.switch_to_Files)

    def switch_to_Home(self):
        self.stackedWidget.setCurrentIndex(8)

    def switch_to_Files(self):
        self.stackedWidget.setCurrentIndex(7)

    def switch_to_Settings(self):
        self.stackedWidget.setCurrentIndex(5)

    def get_position(self): # Метод для получения ячеек, чтобы понимать куда добавлять
        # (необходим как для загрузки старых, так и для создания новых файлов)
        total_files = self.scroll_layout.count()
        if total_files > 0:
            # Если в layout уже есть файлы, получаем последний добавленный виджет
            last_widget = self.scroll_layout.itemAt(total_files - 1).widget()

            # Вычисляем координаты последнего виджета (строку и столбец)
            last_row = self.scroll_layout.indexOf(last_widget) // self.columns  # Строка
            last_column = self.scroll_layout.indexOf(last_widget) % self.columns  # Столбец

            # Позиция для нового виджета будет следующей по порядку:
            # Если в последнем столбце, переходим на новую строку
            if last_column == self.columns - 1:
                new_row = last_row + 1
                new_column = 0
            else:
                new_row = last_row  # Оставляем строку прежней
                new_column = last_column + 1  # Переходим на следующий столбец
        else:
            # Если в layout еще нет файлов, начинаем с первой строки и первого столбца
            new_row = 0
            new_column = 0

        # Возвращаем позицию для нового виджета (строку и столбец)
        return new_row, new_column

    def add_files_from_db(self): # Загружает файлы из бд и отображает их в layout
        try:
            with sq.connect("users.db") as conn:
                cur = conn.cursor()
                cur.execute("SELECT title, id FROM cards WHERE user_id = ?", (self.user,))
                files = cur.fetchall()

                if files:
                    # Загружаем каждый файл и отображаем его
                    for file in files:
                        # Создаем файл и добавляем его в layout
                        new_file = self.create_file_from_db(file)
                        new_row, new_column = self.get_position()  # Получаем позицию для размещения
                        self.scroll_layout.addWidget(new_file, new_row, new_column)
                        conn.close()
                else:
                    print("Нет файлов для отображения.")
        except sq.Error as e:
            print(f"Ошибка при загрузке файлов: {e}")

    def create_file_from_db(self, file_data):
        file_card = File(self)
        if file_data:  # Если переданы данные о файле (title, description)
            title, id = file_data
            file_card.save_file_id(id)
            file_card.set_title(title)  # Устанавливаем заголовок
            file_card.set_quality(id)
            file_card.setMinimumSize(367, 181)
        return file_card

    def create_card(self):
        dialog = Card(self.user) # Здесь мы заполняем данные этого файла
        if dialog.exec_() == QDialog.Accepted:
            self.add_file(dialog.text)

    def add_file(self, value):
        new_file = self.create_file(value)
        new_row, new_column = self.get_position()

        self.scroll_layout.addWidget(new_file, new_row, new_column)

    def create_file(self, value):
        new_file = File(self)
        new_file.mousePressEvent = self.on_click
        new_file.setMinimumSize(367, 181)
        new_file.set_title(value)

        return new_file

    def delete_file(self, file):
        self.delete_widget = file.file_id
        try:
            with sq.connect("users.db") as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM cards WHERE id = ?", (self.delete_widget,))
                conn.commit()
                print(f"Файл с id {self.delete_widget} удален из базы данных.")

        except sq.Error as e:
            print(f"Ошибка при удалении файла из базы данных: {e}")\

    def update_grid(self, removed_widget):
        total_files = self.scroll_layout.count()
        removed_index = -1
        # Найдем индекс удаленного виджета
        for index in range(total_files):
            widget = self.scroll_layout.itemAt(index).widget()
            if widget == removed_widget:
                removed_index = index
                break

        # Удаляем виджет из layout и освобождаем память
        self.scroll_layout.removeWidget(removed_widget)
        removed_widget.deleteLater()

    def load_avatar(self):
        # Получаем путь к изображению (в бинарном формате)
        image_data = self.get_and_save_image_from_db()

        if image_data is not None:
            self.logo.setStyleSheet(f"""border-image: url({image_data});border-radius: 25px;""")
            self.logo_3.setStyleSheet(f"""border-image: url({image_data});border-radius: 25px;""")
            self.logo_2.setStyleSheet(f"""border-image: url({image_data});border-radius: 85px; icon: None;""")
        else:
            return None

    def get_and_save_image_from_db(self):
        # Извлекаем бинарные данные изображения из базы данных
        cur.execute("SELECT image_data FROM users WHERE user_id = ?", (self.user,))
        result = cur.fetchone()

        if result is None or result[0] is None:
            return None
        else:
            image_data = result[0]  # Получаем бинарные данные изображения
            temp_file_path = "images/temp_avatar.jpg"  # Создаем временный путь для файла

            with open(temp_file_path, "wb") as f:
                f.write(image_data)

            return temp_file_path

    def change_logo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите новый аватар", "",
                                              "Image Files (*.png *.jpg *.jpeg);;All Files (*)")
        if file:
            with open(file, 'rb') as f:
                image_data = f.read()

            cur.execute("UPDATE users SET image_data = ? WHERE user_id = ?", (image_data, self.user))
            con.commit()
            self.logo_2.setStyleSheet(f"""
                               border-image: url({file});
                                border-radius: 85px;
                               icon: None;
                           """)

            self.logo.setStyleSheet(f"""
                               border-image: url({file});
                               border-radius: 25px;
                           """)

            self.logo_3.setStyleSheet(f"""
                                          border-image: url({file});
                                          border-radius: 25px;
                                      """)
    def Change_1(self):
        dialog = New_pass(self.user)
        dialog.setWindowTitle("New Password")
        if dialog.exec_() == QDialog.Accepted:
            return

    def Change_2(self):
        dialog = New_user(self.user)
        dialog.setWindowTitle("New Username")
        if dialog.exec_() == QDialog.Accepted:
            return

    def on_click(self, event: QMouseEvent, file_id):
        self.current_file = file_id
        self.stackedWidget.setCurrentIndex(6)
        cur.execute("SELECT title, description FROM cards WHERE id = ?", (file_id,))
        result = cur.fetchone()

        if result:
            title, description = result
            self.tl = title
            self.dscr = description

            self.file_name.setText(self.tl)
            self.description.setText(self.dscr)

        # Choosing окно (прописываю тут, чтобы был доступ к переменной id, и в эти окна можно попасть только нажав на файл)
        self.choose1_logic = Choose_1_logic(self.FlashCards, self.stackedWidget, self.current_file)
        self.choose2_logic = Choose_2_logic(self.ShortAnswer, self.stackedWidget, self.current_file)
        self.choose3_logic = Choose_3_logic(self.True_False, self.stackedWidget, self.current_file)

    def on_click_1(self, event: QMouseEvent):
        self.stackedWidget.setCurrentIndex(0)

    def on_click_2(self, event: QMouseEvent):
        self.stackedWidget.setCurrentIndex(2)

    def on_click_3(self, event: QMouseEvent):
        self.stackedWidget.setCurrentIndex(1)

  