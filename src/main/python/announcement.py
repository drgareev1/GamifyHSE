# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide2.QtWidgets import QMainWindow, QMessageBox, QTreeWidgetItem
from PySide2.QtCore import QFile
from PySide2.QtGui import QFont
from PySide2.QtUiTools import QUiLoader


class Announcement(QMainWindow):
    def __init__(self, resource_manager, app_context):
        super(Announcement, self).__init__()
        self.app_context = app_context
        self.resource_manager = resource_manager
        self.load_ui()

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
        self.ui.class_label.setText(ann["class"])
        self.ui.subject_label.setText(ann["subject"])
        self.ui.time_passed_label.setText(ann["time_passed"])
        self.ui.author_label.setText(ann["author"])
        self.ui.content_text.setText(ann["content"])

    def onClicked(self, item):
        print("Test")
