# Реализация методов окон входа и регистрации
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
import sys
from tree import tree
from PyQt5.QtCore import Qt
import sqlite3 as sq

con = sq.connect('users.db')
cur = con.cursor()

class Login(QDialog):
    def __init__(self, widget):
        super(Login, self).__init__()
        loadUi("ui_files/Log.ui", self)
        self.setGeometry(0, 0,100,100)
        self.login_success = False  # Флаг успешного входа

        self.loginbutton.clicked.connect(self.loginfunc)
        self.passwordd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.createbutton.clicked.connect(self.gotocreate)

        self.current_user = None

    def loginfunc(self):
        try:
            username = self.username.text()
            passwordd = self.passwordd.text()

            cur.execute("SELECT password FROM users WHERE name = ?", (username,))
            result = cur.fetchone()

            if result:
                stored_password = result[0]
                if passwordd == stored_password:
                    self.login_success = True
                    self.current_user = username
                    self.accept()
                else:
                    self.Caution.setText(f"*Неверный пароль для пользователя {username}. Попробуйте еще раз.")
            else:
                self.Caution.setText(f"Пользователь с именем {username} не найден.")

        except Exception as e:
            print(f"Error: {e}")

    def get_user_id(self):
        query = "SELECT user_id FROM users WHERE name = ?"
        result = cur.execute(query, (self.current_user,)).fetchone()
        if result:
           return result[0]
        else:
            print("User not found.")

    def gotocreate(self):
        self.Stacked.setCurrentIndex(1)
        self.SignUp_2.clicked.connect(self.signfunc)
        self.passwordd_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordd2.setEchoMode(QtWidgets.QLineEdit.Password)

    def signfunc(self):
        username = self.username_2.text()
        password = self.passwordd_2.text()
        password2 = self.passwordd2.text()

        if password == password2:
            if len(password) > 3 and len(username) > 3:
                try:
                    # Проверяем, существует ли уже пользователь с таким именем
                    cur.execute("SELECT name FROM users WHERE name = ?", (username,))
                    existing_user = cur.fetchone()

                    if existing_user:
                        self.Caution_2.setText("Пользователь с таким именем уже существует.")
                    else:
                        cur.execute("INSERT INTO users (name, password, image_data) VALUES (?, ?, ?)",
                                    (username, password, None))
                        con.commit()
                        self.Stacked.setCurrentIndex(0)
                except Exception as e:
                    print(f"Ошибка: {e}")
            else:
                self.Caution_2.setText("Имя пользователя и пароль должны быть длиной более 3 символов.")
        else:
            self.Caution_2.setText("Пароли не совпадают.")
