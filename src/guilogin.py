# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'go6login.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(711, 334)
        MainWindow.setStyleSheet("QMainWindow {\n"
"    background: qlineargradient(spread: pad, x1: 0, y1: 0, x2: 0, y2: 1, stop: 0.1 #4B0082, stop: 0.9 #000000);\n"
"}\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.frameH_4 = QtWidgets.QFrame(self.centralwidget)
        self.frameH_4.setGeometry(QtCore.QRect(20, 90, 671, 341))
        self.frameH_4.setStyleSheet("QFrame {\n"
"    background-color: #28004F; /* Use an even darker shade of purple */\n"
"    border-radius: 10px;\n"
"}")
        self.frameH_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameH_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameH_4.setObjectName("frameH_4")
        self.label_Go6LicenseKey = QtWidgets.QLabel(self.frameH_4)
        self.label_Go6LicenseKey.setGeometry(QtCore.QRect(230, 30, 211, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft Tai Le")
        font.setPointSize(21)
        font.setBold(True)
        font.setWeight(75)
        self.label_Go6LicenseKey.setFont(font)
        self.label_Go6LicenseKey.setStyleSheet("QLabel {\n"
"    background: none;\n"
"    color: #FFF; /* Transparent font color */\n"
"    border-radius: 10px; /* Adjust the radius as needed */\n"
"}")
        self.label_Go6LicenseKey.setObjectName("label_Go6LicenseKey")
        self.lineEdit_KeyInput = QtWidgets.QLineEdit(self.frameH_4)
        self.lineEdit_KeyInput.setGeometry(QtCore.QRect(200, 90, 281, 41))
        self.lineEdit_KeyInput.setStyleSheet("QLineEdit {\n"
"    border: none;\n"
"    background-color: #e0e0e0; /* Set your desired background color */\n"
"    color: #FFF;\n"
"    padding: 10px; /* Increase padding for better spacing */\n"
"    border-radius: 10px 10px 0 0; /* Set top corners to be curved */\n"
"    text-align: center; /* Center the text */\n"
"    font-size: 14px; /* Set your desired font size */\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"    border-bottom: 1px solid rgba(169, 169, 169, 0.9);\n"
"    /* Add underline effect when the line edit is in focus */\n"
"}\n"
"")
        self.lineEdit_KeyInput.setObjectName("lineEdit_KeyInput")
        self.labelH_PleaseMessage = QtWidgets.QLabel(self.frameH_4)
        self.labelH_PleaseMessage.setGeometry(QtCore.QRect(250, 50, 161, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.labelH_PleaseMessage.setFont(font)
        self.labelH_PleaseMessage.setStyleSheet("QLabel {\n"
"    background: none;\n"
"    color: #FFF; /* Transparent font color */\n"
"    border-radius: 10px; /* Adjust the radius as needed */\n"
"}")
        self.labelH_PleaseMessage.setObjectName("labelH_PleaseMessage")
        self.pushButtonConfirm = QtWidgets.QPushButton(self.frameH_4)
        self.pushButtonConfirm.setGeometry(QtCore.QRect(300, 150, 71, 41))
        self.pushButtonConfirm.setStyleSheet("QPushButton {\n"
"    background:rgba(169, 169, 169, 0.2); /* Very transparent light grey background */\n"
"    color: #FFFFFF; /* White text color */\n"
"    border: none; /* No border */\n"
"    border-radius: 6px;\n"
"px; /* Rounded corners with a 10px radius */\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FF00FF, stop:1 #9f8bd7); /* Gradient from magenta to light purple, left to right */\n"
"}\n"
"")
        self.pushButtonConfirm.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("assets/check-circle.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonConfirm.setIcon(icon)
        self.pushButtonConfirm.setIconSize(QtCore.QSize(24, 24))
        self.pushButtonConfirm.setObjectName("pushButtonConfirm")
        self.label_ToolLogo = QtWidgets.QLabel(self.centralwidget)
        self.label_ToolLogo.setGeometry(QtCore.QRect(330, 20, 51, 51))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_ToolLogo.setFont(font)
        self.label_ToolLogo.setStyleSheet("QLabel {\n"
"    background: none;\n"
"    color: #FFF; /* Transparent font color */\n"
"    border-radius: 10px; /* Adjust the radius as needed */\n"
"}")
        self.label_ToolLogo.setText("")
        self.label_ToolLogo.setPixmap(QtGui.QPixmap("assets/go6icon.ico"))
        self.label_ToolLogo.setScaledContents(True)
        self.label_ToolLogo.setObjectName("label_ToolLogo")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_Go6LicenseKey.setText(_translate("MainWindow", "Go6 License Key"))
        self.labelH_PleaseMessage.setText(_translate("MainWindow", "Please input your Go6 license "))

# temp
class DraggableLoginWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.dragging = False
        self.old_pos = None  

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False 
# 