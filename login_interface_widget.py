# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from translator import Translator
import pyperclip


class LoginWindow(QWidget):
    approvalCode_entered = pyqtSignal(str)

    def __init__(self, translator: Translator, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.authorization_url = None
        self.translator = translator
        self.layout = QVBoxLayout()
        url_explanation_label = QLabel()
        url_explanation_label.setText(self.translator["authentication_url_explanation"])
        url_explanation_label.setWordWrap(True)
        self.layout.addWidget(url_explanation_label)
        self.url_widget = QTextEdit()
        self.layout.addWidget(self.url_widget)
        copy_button = QPushButton()
        copy_button.setText(self.translator["copy_to_clipboard"])
        copy_button.clicked.connect(self.copy_url_to_clipboard)
        self.layout.addWidget(copy_button)
        approval_code_explanation_label = QLabel()
        approval_code_explanation_label.setText(self.translator["approval_code_input_explanation"])
        approval_code_explanation_label.setWordWrap(True)
        self.layout.addWidget(approval_code_explanation_label)
        self.approval_code_text_edit = QTextEdit()
        self.layout.addWidget(self.approval_code_text_edit)
        submit_button = QPushButton()
        submit_button.setText(self.translator["apply"])
        submit_button.clicked.connect(self.submit_code)
        self.layout.addWidget(submit_button, alignment=Qt.AlignRight)
        self.setLayout(self.layout)
        self.show()

    def show_url(self, authorization_url):
        self.authorization_url = authorization_url
        self.url_widget.setText(authorization_url)

    def copy_url_to_clipboard(self):
        pyperclip.copy(self.authorization_url)

    def submit_code(self):
        self.approvalCode_entered.emit(self.approval_code_text_edit.toPlainText())

