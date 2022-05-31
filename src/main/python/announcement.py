# This Python file uses the following encoding: utf-8
import os
import json
from pathlib import Path
import sys

from PySide2.QtWidgets import QMainWindow, QMessageBox, QTreeWidgetItem
from PySide2.QtCore import QFile
from PySide2.QtGui import QFont
from PySide2.QtUiTools import QUiLoader

import ctypes.wintypes


class Announcement(QMainWindow):
    def __init__(self, resource_manager, app_context, file_name):
        super(Announcement, self).__init__()
        self.app_context = app_context
        self.resource_manager = resource_manager
        self.load_ui()
        
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value

        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        
        self.file_path = buf.value + "\\SmartLMS Gamification Experiment"
        
        if not os.path.exists(self.file_path):
            os.mkdir(self.file_path)

        self.file_path += "\\" + file_name + ".hse"

        try:
            with open(self.file_path) as f:
                data = json.load(f)
                if "announcements" in data:
                    self.read_announcements = data["announcements"]
                else:
                    self.read_announcements = []
                    self.save_read()
                f.close()
        except IOError:
            self.read_announcements = []
            self.save_read()

    def load_ui(self):
        loader = QUiLoader()
        ui_file = QFile(self.app_context.get_resource('announcement.ui'))
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        self.setCentralWidget(self.ui.centralwidget)
        
        self.ui.class_label.setFont(QFont("HSE Sans", 14, QFont.Bold))
        self.ui.subject_label.setFont(QFont("HSE Sans", 12, QFont.Bold))
        self.ui.time_passed_label.setFont(QFont("HSE Sans", 9))
        self.ui.author_label.setFont(QFont("HSE Sans", 9))
        self.ui.content_text.setFont(QFont("HSE Sans", 11))
        
        self.ui.read_button.clicked.connect(self.onClicked)
        
        ui_file.close()

    def load_with_data(self, ann):
        self.ann = ann
        self.ui.class_label.setText(ann["class"])
        self.ui.subject_label.setText(ann["subject"])
        self.ui.time_passed_label.setText(ann["time_passed"])
        self.ui.author_label.setText(ann["author"])
        self.ui.content_text.setText(ann["content"])
        self.ui.read_button.setHidden(ann["is_read"])
        

    def onClicked(self, item):
        new_ann = {}
        new_ann["class"] = self.ann["class"]
        new_ann["subject"] = self.ann["subject"]
        self.read_announcements.append(new_ann)
        self.save_read()
        self.ui.read_button.setHidden(True)
        self.resource_manager.resources["globalization"] += 1
        self.resource_manager.save_resources()

    def save_read(self):
        total_data = {}
        try:
            with open(self.file_path) as f:
                total_data = json.load(f)
                total_data["announcements"] = self.read_announcements
                f.close()
        except IOError:
            total_data["announcements"] = self.read_announcements

        with open(self.file_path, 'w+') as f:
            f.seek(0)
            json.dump(total_data, f, indent=4)
            f.truncate()
        f.close()
