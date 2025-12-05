from PyQt5.QtWidgets import QMessageBox

def showAlert(window, title, text):
    msg = QMessageBox(window)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.exec_()