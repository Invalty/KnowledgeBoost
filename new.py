# Диалоговый окна смены пароля и имени пользователя
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
import sys
import sqlite3 as sq

con = sq.connect('users.db')
cur = con.cursor()

class New_pass(QDialog):
    def __init__(self,user):
        super(New_pass, self).__init__()
        loadUi("ui_files/Change_Password.ui", self)
        self.cur_name = user
        self.Ok_butt.clicked.connect(self.OKey)

    def OKey(self):
        text = self.NewPass.text()
        cur.execute("UPDATE users SET password = ? WHERE user_id = ?", (text, self.cur_name))
        con.commit()

        print(f"Пароль для пользователя {self.cur_name} успешно обновлен.")
        self.accept()

class New_user(QDialog):
    name_updated = pyqtSignal(str)

    def __init__(self,user):
        super(New_user, self).__init__()
        loadUi("ui_files/Change_Username.ui", self)
        self.cur_name = user
        self.OK_butt.clicked.connect(self.OK)

    def OK(self):
        text = self.NewUser.text()
        cur.execute("UPDATE users SET name = ? WHERE user_id = ?", (text, self.cur_name))
        con.commit()

        # Отправляем сигнал с новым именем
        self.name_updated.emit(text)

        print(f"Имя пользователя {self.cur_name} успешно обновлено.")
        self.accept()


