import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QLabel, QStackedWidget
)
from PyQt6.QtCore import Qt


class LoginScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)  # PyQt6 enum format

        self.button = QPushButton("Submit")
        self.button.clicked.connect(self.go_to_next_screen)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter password:"))
        layout.addWidget(self.input)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def go_to_next_screen(self):
        # Here you could validate the password; for now just switch screens
        self.stacked_widget.setCurrentIndex(1)


class NextScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("✅ Logged in! You are on the next screen."))
        self.setLayout(layout)


app = QApplication(sys.argv)

stack = QStackedWidget()
login_screen = LoginScreen(stack)
second_screen = NextScreen()

stack.addWidget(login_screen)   # Index 0
stack.addWidget(second_screen)  # Index 1

stack.setCurrentIndex(0)
stack.show()

sys.exit(app.exec())
