# This Python file uses the following encoding: utf-8

from fbs_runtime.application_context.PySide2 import ApplicationContext

import os
from pathlib import Path
import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QMessageBox
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QFont, QFontDatabase, QPixmap, QBrush, QColor

import pygame as pg
from game.game import Game
import game.settings as st

from classwindow import ClassWindow
from announcementswindow import AnnouncementsWindow

from scraping import Scraper
from game.resource_manager import ResourceManager


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.username = ""
        self.load_ui()
        self.scraper = Scraper(display_head = False, debug_mode = False, app_context = appctxt)
        
        self.fundamentals = []
        with open(appctxt.get_resource('fundamentals.cl')) as my_file:
            for line in my_file:
                self.fundamentals.append(int(line))
            my_file.close()
        
    def set_fonts(self):
        QFontDatabase.addApplicationFont(appctxt.get_resource('HSESans-Regular.otf'))
        QFontDatabase.addApplicationFont(appctxt.get_resource('HSESans-Bold.otf'))
        QFontDatabase.addApplicationFont(appctxt.get_resource('HSESans-Black.otf'))
        QFontDatabase.addApplicationFont(appctxt.get_resource('HSESans-Italic.otf'))
        QFontDatabase.addApplicationFont(appctxt.get_resource('HSESans-SemiBold.otf'))
        QFontDatabase.addApplicationFont(appctxt.get_resource('HSESans-Thin.otf'))

        self.ui.loginLabel.setFont(QFont("HSE Sans", 16, QFont.Bold))
        self.ui.loginButton.setFont(QFont("HSE Sans", 12, QFont.Bold))
        self.ui.emailLabel.setFont(QFont("HSE Sans", 9))
        self.ui.passwordLabel.setFont(QFont("HSE Sans", 9))

        self.ui.username_field.setFont(QFont("HSE Sans", 10))
        self.ui.password_field.setFont(QFont("HSE Sans", 10))

        self.ui.game_button.setFont(QFont("HSE Sans", 12, QFont.Bold))
        self.ui.deadlines_button.setFont(QFont("HSE Sans", 12, QFont.Bold))
        self.ui.announcements_button.setFont(QFont("HSE Sans", 12, QFont.Bold))

        self.ui.title_label.setFont(QFont("HSE Sans", 24, QFont.Bold))
        self.ui.courses_label.setFont(QFont("HSE Sans", 16, QFont.Bold))
        self.ui.email_label.setFont(QFont("HSE Sans", 11))
        self.ui.email_label.setStyleSheet('color: rgb(96, 96, 96);')


    def load_ui(self):
        loader = QUiLoader()

        ui_file = QFile(appctxt.get_resource('mainwindow.ui'))
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)

        self.setCentralWidget(self.ui.stack)

        ui_file.close()
        self.ui.stack.setCurrentIndex(0)
        self.ui.loginButton.clicked.connect(self.login_button)
        self.ui.game_button.clicked.connect(self.launch_game)
        self.ui.deadlines_button.clicked.connect(self.open_deadlines)
        self.ui.announcements_button.clicked.connect(self.open_announcements)
        
        self.ui.classes_widget.setColumnCount(1)
        self.ui.classes_widget.itemDoubleClicked.connect(self.onClicked)

        self.set_fonts()

        self.setWindowTitle("SmartLMS | Gamification Experiment")
        
        pixmap = QPixmap(appctxt.get_resource('logo.png'))
        self.ui.label_3.setPixmap(pixmap)
        
        self.ui.game_button.setStyleSheet(str("border-radius: 12px; background-image: url(\"" + appctxt.get_resource('world.png') + "\");").replace("\\", '/'))
        self.ui.announcements_button.setStyleSheet(str("border-radius: 12px; background-image: url(\"" + appctxt.get_resource('announcements.png') + "\");").replace("\\", '/'))
        self.ui.deadlines_button.setStyleSheet(str("border-radius: 12px; background-image: url(\"" + appctxt.get_resource('deadlines.png') + "\");").replace("\\", '/'))


    def onClicked(self, it, col):

        for user_class in self.user_classes[it.parent().text(col)]:
            if user_class["name"] == it.text(col):
            
                tasks = self.scraper.class_tasks(str(user_class["id"]))
                self.class_window = ClassWindow(self.username, self.resource_manager, appctxt)
                self.class_window.class_id = user_class["id"]
                self.class_window.show()
                self.class_window.load_with_data(str(user_class["name"]), tasks)
        
    def login_button(self):
        self.ui.stack.setCurrentIndex(1)
        username = self.ui.username_field.text()
        password = self.ui.password_field.text()
        if password == "debugmode=True":
            self.scraper.debug_mode = True
        auth_code = self.scraper.auth(username, password)
        if auth_code == 0:
            self.user_classes = self.scraper.classes()
            
            for key, class_list in self.user_classes.items():
                parent = QTreeWidgetItem(self.ui.classes_widget)
                parent.setText(0, key)
                parent.setFont(0, QFont("HSE Sans", 12, QFont.Bold))
                for user_class in class_list:
                    print(user_class["name"] + ": " + user_class["id"])
                    child = QTreeWidgetItem(parent)
                    child.setFont(0, QFont("HSE Sans", 10))
                    child.setText(0, user_class["name"])
                    if int(user_class["id"]) in self.fundamentals:
                        child.setForeground(0, QBrush(QColor(106,0,249)))
                    
            self.ui.stack.setCurrentIndex(2)
            self.username = username.split("@")[0]
            self.resource_manager = ResourceManager(self.username.split("@")[0], self.username.split("@")[0])
            
            self.ui.email_label.setText("Ваш профиль: " + username)
            
            print("Authorized")
        else:
            print("Auth failed.")
            self.ui.stack.setCurrentIndex(0)

    def launch_game(self):
        running = True
        playing = True
        pg.init()
        pg.mixer.init()
        screen = pg.display.set_mode([st.WINDOW_WIDTH, st.WINDOW_HEIGHT])
        clock = pg.time.Clock()
        game = Game(screen, clock, self.username, self.resource_manager, appctxt)
        while running:
            while playing:
                game.run()

    def closeEvent(self, event):
        self.scraper.driver.close()

    def open_announcements(self):
        announcements = self.scraper.announcements()
        self.announcements_window = AnnouncementsWindow(self.username, self.resource_manager, appctxt)
        self.announcements_window.show()
        self.announcements_window.load_with_data(announcements)


    def open_deadlines(self):
        print("Deadlines")
        tasks = self.scraper.deadlines()
        for task in tasks:
            print(task["date"])
        QMessageBox.about(self, "Congratulations", "All deadlines have already been closed!")


if __name__ == "__main__":
    appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    widget = MainWindow()
    widget.show()
    exit_code = appctxt.app.exec_()      # 2. Invoke appctxt.app.exec_()
    sys.exit(exit_code)