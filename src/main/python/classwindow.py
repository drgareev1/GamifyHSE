# This Python file uses the following encoding: utf-8

from fbs_runtime.application_context.PySide2 import ApplicationContext

import os
from pathlib import Path

from PySide2.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QTableWidget, QMessageBox
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QFont, QColor, QBrush
import json

class ClassWindow(QMainWindow):

    def __init__(self, username, resource_manager, app_context):
        super(ClassWindow, self).__init__()
        self.app_context = app_context
        self.username = username
        self.resource_manager = resource_manager
        self.load_ui()

        self.fundamentals = []
        with open(self.app_context.get_resource('fundamentals.cl')) as my_file:
            for line in my_file:
                self.fundamentals.append(int(line))
            my_file.close()

    def load_ui(self):
        loader = QUiLoader()
        ui_file = QFile(self.app_context.get_resource('classwindow.ui'))
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)

        self.setCentralWidget(self.ui.centralwidget)
        self.ui.tasks_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ui.tasks_table.setFont(QFont("HSE Sans", 10))
        self.ui.name_label.setFont(QFont("HSE Sans", 14, QFont.Bold))
        self.ui.sync_button.setFont(QFont("HSE Sans", 10, QFont.Bold))
        self.ui.final_text_label.setFont(QFont("HSE Sans", 10, QFont.Bold))
        self.ui.grade_label.setFont(QFont("HSE Sans", 10, QFont.Bold))

        self.ui.progress_text_label.setFont(QFont("HSE Sans", 10, QFont.Bold))
        self.ui.progress_label.setFont(QFont("HSE Sans", 10, QFont.Bold))

        self.ui.sync_button.clicked.connect(self.sync_button)

        self.ui.tasks_table.horizontalHeader().setFont(QFont("HSE Sans", 10, QFont.Bold))

        ui_file.close()

    def sync_button(self):
        print(self.class_id)
        difference = self.sync_class(self.username)
        is_fundamental = False
        if int(self.class_id) in self.fundamentals:
            is_fundamental = True
        print(is_fundamental)
        rewards = self.resource_manager.apply_difference(difference, is_fundamental)
        text = "You have received: "
        for reward, val in rewards.items():
            text = text + str(val) + " " + reward + ", "
        text = text[:-2]
        if len(rewards) > 0:
            QMessageBox.about(self, "Congratulations!", text)
        else:
            QMessageBox.about(self, "Done", "All achievements have already been synchronized")

    def load_with_data(self, class_name, data):

        self.setWindowTitle(class_name)

        tasks = data["list"]
        self.tasks = tasks

        final_grade = 0
        max_final_grade = 0

        self.ui.tasks_table.setColumnCount(3)

        self.ui.tasks_table.setHorizontalHeaderLabels(['Элемент', 'Вес', 'Оценка'])

        self.ui.tasks_table.setRowCount(len(tasks))
        self.ui.name_label.setText(class_name)
        i = 0

        self.grades_list = {"A": 0, "B": 0, "C": 0, "D": 0}

        for task in tasks:
            self.ui.tasks_table.setItem(i, 0, QTableWidgetItem(task["name"]))
            self.ui.tasks_table.setItem(i, 1, QTableWidgetItem(task["weight"]))
            self.ui.tasks_table.setItem(i, 2, QTableWidgetItem(task["grade"]))

            grades = task["grade"].split("/")

            grade = 0
            max_grade = float(grades[1])

            if grades[0].replace('.', '', 1).isdigit():
                grade = float(grades[0])
            if max_grade == 0:
                max_grade = 1

            if grade / max_grade >= 0.76:
                self.ui.tasks_table.item(i, 2).setForeground(QBrush(QColor(0, 100, 0)))
                self.grades_list["A"] += 1
            elif grade / max_grade >= 0.56:
                self.ui.tasks_table.item(i, 2).setForeground(QBrush(QColor(0, 185, 0)))
                self.grades_list["B"] += 1
            elif grade / max_grade >= 0.36:
                self.ui.tasks_table.item(i, 2).setForeground(QBrush(QColor(236, 183, 83)))
                self.grades_list["C"] += 1
            else:
                self.ui.tasks_table.item(i, 2).setForeground(QBrush(QColor(139, 0, 0)))
                self.grades_list["D"] += 1

            final_grade += round(float(grade), 2)
            max_final_grade += float(max_grade)

            i += 1

        header = self.ui.tasks_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self.ui.progress_label.setText(str(final_grade) + "/" + str(max_final_grade))
        self.ui.grade_label.setText(data["final"])

    def sync_class(self, file_name):
        total_data = {}
        difference_data = {}
        try:
            with open(self.resource_manager.file_path) as f:
                total_data = json.load(f)
                f.close()
                if "classes" in total_data:
                    if self.class_id in total_data["classes"]:
                        for grade, val in total_data["classes"][self.class_id]["grades"].items():
                            difference_data[grade] = total_data["classes"][self.class_id]["grades"][grade] - val
                        total_data["classes"][self.class_id]["grades"] = self.grades_list
                    else:
                        difference_data = self.grades_list
                        total_data["classes"][self.class_id] = {}
                        total_data["classes"][self.class_id]["grades"] = self.grades_list
                else:
                    total_data["classes"] = {}
                    total_data["classes"][self.class_id] = {}
                    total_data["classes"][self.class_id]["grades"] = self.grades_list
                    difference_data = self.grades_list
        except IOError:
            total_data["classes"] = {}
            total_data["classes"][self.class_id] = {}
            total_data["classes"][self.class_id]["grades"] = self.grades_list
            difference_data = self.grades_list

        with open(self.resource_manager.file_path, 'w+') as f:
            f.seek(0)
            json.dump(total_data, f, indent=4)
            f.truncate()
        f.close()
        return difference_data
