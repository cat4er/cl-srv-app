# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'userui2.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(936, 758)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 449, 732))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.listWidget = QtWidgets.QListWidget(self.scrollAreaWidgetContents)
        self.listWidget.setGeometry(QtCore.QRect(12, 12, 421, 621))
        self.listWidget.setObjectName("listWidget")
        self.commandLinkButton_2 = QtWidgets.QCommandLinkButton(self.scrollAreaWidgetContents)
        self.commandLinkButton_2.setGeometry(QtCore.QRect(10, 640, 84, 84))
        self.commandLinkButton_2.setMaximumSize(QtCore.QSize(84, 84))
        self.commandLinkButton_2.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("update.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_2.setIcon(icon)
        self.commandLinkButton_2.setIconSize(QtCore.QSize(64, 64))
        self.commandLinkButton_2.setObjectName("commandLinkButton_2")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.scrollArea_2 = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 449, 732))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.lineEdit = QtWidgets.QLineEdit(self.scrollAreaWidgetContents_2)
        self.lineEdit.setGeometry(QtCore.QRect(12, 636, 315, 84))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy)
        self.lineEdit.setMinimumSize(QtCore.QSize(315, 84))
        self.lineEdit.setObjectName("lineEdit")
        self.listWidget_2 = QtWidgets.QListWidget(self.scrollAreaWidgetContents_2)
        self.listWidget_2.setGeometry(QtCore.QRect(12, 12, 421, 621))
        self.listWidget_2.setObjectName("listWidget_2")
        self.commandLinkButton = QtWidgets.QCommandLinkButton(self.scrollAreaWidgetContents_2)
        self.commandLinkButton.setGeometry(QtCore.QRect(345, 638, 84, 84))
        self.commandLinkButton.setMaximumSize(QtCore.QSize(84, 84))
        self.commandLinkButton.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.commandLinkButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("send.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton.setIcon(icon1)
        self.commandLinkButton.setIconSize(QtCore.QSize(64, 64))
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.horizontalLayout.addWidget(self.scrollArea_2)
        self.scrollArea_2.raise_()
        self.scrollArea.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Чат"))