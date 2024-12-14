# Файл запуска приложения
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
import sys
from Start import *
from main import *
import sqlite3 as sq

# Подключаемся к базе данных или создаем её, если её нет
con = sq.connect('users.db')
cur = con.cursor()

# Создаём таблицу users, если она не существует
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        password TEXT,
        image_data BLOB DEFAULT NULL
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        image_data BLOB DEFAULT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS terms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER,
        term TEXT NOT NULL,
        definition TEXT NOT NULL,
        FOREIGN KEY (file_id) REFERENCES cards(id)
    )
""")

con.commit()
con.close()

def run_app():
    app = QApplication(sys.argv)

    widget = QStackedWidget()
    login_window = Login(widget)
    widget.addWidget(login_window)
    widget.show()

    login_window.exec_()  # Ждем, пока пользователь не выполнит вход
    user = login_window.get_user_id()

    if login_window.login_success:  # Если вход успешен
        main_window = Main(user)
        widget.addWidget(main_window)
        widget.setCurrentWidget(main_window)  # Переключаем на главное окно

    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()
    con.close()
    connect.close()