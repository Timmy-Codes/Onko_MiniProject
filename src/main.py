import sys
from Configuration import Configuration
from GraphicalUserInterface import UserInterface
from PySide6.QtWidgets import QApplication

database = Configuration("OnkoDICOM.db")

app = QApplication(sys.argv)
window = UserInterface(database)
window.show()
app.exec()
