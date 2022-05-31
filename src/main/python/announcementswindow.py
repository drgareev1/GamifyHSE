# This Python file uses the following encoding: utf-8

from fbs_runtime.application_context.PySide2 import ApplicationContext

import os
from pathlib import Path
import sys
import json

from PySide2.QtWidgets import QMainWindow, QMessageBox, QTreeWidgetItem, QHeaderView
from PySide2.QtCore import QFile
from PySide2.QtGui import QFont, QFontDatabase, QPixmap, QBrush, QColor
from PySide2.QtUiTools import QUiLoader

import ctypes.wintypes

from announcement import Announcement

class AnnouncementsWindow(QMainWindow):
    def __init__(self, username, resource_manager, app_context):
        super(AnnouncementsWindow, self).__init__()
        self.app_context = app_context
        self.username = username
        self.resource_manager = resource_manager
        
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value

        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        
        self.file_path = buf.value + "\\SmartLMS Gamification Experiment"
        
        if not os.path.exists(self.file_path):
            os.mkdir(self.file_path)

        self.file_path += "\\" + username + ".hse"

        try:
            with open(self.file_path) as f:
                data = json.load(f)
                if "announcements" in data:
                    self.read_announcements = data["announcements"]
                else:
                    self.read_announcements = []
                f.close()
        except IOError:
            self.read_announcements = []

        
        self.load_ui()

    def load_ui(self):
        loader = QUiLoader()
        ui_file = QFile(self.app_context.get_resource('announcementswindow.ui'))
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.setCentralWidget(self.ui.centralwidget)
        self.ui.announcements_widget.setColumnCount(2)
        self.ui.header_label.setFont(QFont("HSE Sans", 14, QFont.Bold))
        self.ui.announcements_widget.itemDoubleClicked.connect(self.onClicked)

        ui_file.close()
        
        self.setWindowTitle("SmartLMS | Объявления")
        

    def load_with_data(self, data):
        merged_announcements = {}
        for ann in data:
            is_read = False
            for read_an in self.read_announcements:
                if read_an["class"] == ann["class"] and read_an["subject"] == ann["subject"]:
                    is_read = True
            ann["is_read"] = is_read
            if ann["time_passed"] in merged_announcements:
                merged_announcements[ann["time_passed"]].append(ann)
            else:
                merged_announcements[ann["time_passed"]] = [ann]
                
        for time_passed, announcements in merged_announcements.items():
            parent = QTreeWidgetItem(self.ui.announcements_widget)
            parent.setText(0, time_passed)
            parent.setFont(0, QFont("HSE Sans", 10, QFont.Black))
            for annn in announcements:
                child = QTreeWidgetItem(parent)
                child.setFont(0, QFont("HSE Sans", 10, QFont.Bold))
                child.setFont(1, QFont("HSE Sans", 10))
                child.setText(0, annn["class"])
                child.setText(1, annn["subject"])
                if annn["is_read"] == False:
                    child.setForeground(0, QBrush(QColor(106,0,249)))
                    child.setForeground(1, QBrush(QColor(106,0,249)))
                
        
        header = self.ui.announcements_widget.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)
        
        self.announcements = merged_announcements

    def onClicked(self, it, col):

        for ann in self.announcements[it.parent().text(0)]:
            if ann["subject"] == it.text(1):
                self.annoucement_window = Announcement(self.resource_manager, self.app_context, self.username)
                self.annoucement_window.show()
                self.annoucement_window.load_with_data(ann)
