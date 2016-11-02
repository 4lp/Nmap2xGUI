import sys
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication, QPushButton, QLineEdit, QAction, qApp, QTextEdit,
                             QWidget, QActionGroup)
from PyQt5.QtCore import pyqtSlot
import xml.etree.ElementTree as ET
import os
from socket import inet_aton

class HelpPopup(QTextEdit):
    def __init__(self):
        QWidget.__init__(self)

    def helpWindow(self):
        helpText = QTextEdit("Help")

class Gui(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def showHelp(self):
        self.w = HelpPopup()
        self.w.setGeometry(200, 200, 400, 250)
        self.w.setWindowTitle("Help")
        helpText = ("Weclome to Nmap2xGUI, the Nmap XML converter!\n"
                    "\n"
                    "This tool was developed to save time when documenting new networks. For now, it's really only useful if you need to save a directory of which hostnames correspond to which"
                    "IP addresses in, for example, the company wiki."
                    "\n"
                    "Using this utility is easy - simply press the \"Find XML file...\" button to locate your Nmap-generated XML file, "
                    "then press the \"Set save target...\" button to specify the file where you would like your output saved to. "
                    "Then, select what format you would like your output saved in."
                    "Once both fields and the output format are correctly set, click the \"CONVERT!\" button and the conversion will happen."
                    "\n"
                    "\n"
                    "Important notes:\n"
                    "- If the Moinmoin table output is selected, the output of this utility is a text file containing a Moinmoin table in the form: \n"
                    "               ||Hostname||IP Address|| \n"
                    "As such it will only include devices with a hostname.\n"
                    "- This utility outputs a list sorted by IP address\n"
                    "- This utility has only been tested on /24 networks and smaller (I don't see any reason why it wouldn't work for bigger "
                    "networks but the sorting may be messed up)\n"
                    "\n"
                    "        ")
        self.w.setText(helpText)
        self.w.setReadOnly(True)
        self.w.show()

    def selectOutput(self):
        self.outputMenu = QMenu()

    def initUI(self):

        self.btn1 = QPushButton("Find XML file...", self)
        self.btn1.move(30, 50)
        
        self.btn2 = QPushButton("Set save target...", self)
        self.btn2.move(30, 100)

        self.btn3 = QPushButton("CONVERT!", self)
        self.btn3.move(150, 150)

        self.le1 = QLineEdit(self)
        self.le1.setFixedWidth(300)
        self.le1.move(150, 50)
        self.le1.setReadOnly(True)

        self.le2 = QLineEdit(self)
        self.le2.setFixedWidth(300)
        self.le2.move(150, 100)
        self.le2.setReadOnly(True)

        self.btn1.clicked.connect(self.button1)
        self.btn2.clicked.connect(self.button2)
        self.btn3.clicked.connect(self.button3)

        self.btn1.setStatusTip('Browse to your Nmap XML file')
        self.btn2.setStatusTip('Set your target output file')
        self.btn3.setStatusTip('Convert Nmap XML to Moinmoin table')

        self.statusBar()

        helpAction = QAction('&Help', self)
        helpAction.setShortcut('Ctrl+H')
        helpAction.setStatusTip('Get Help')
        helpAction.triggered.connect(self.showHelp)

        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(helpAction)
        fileMenu.addAction(exitAction)

        selectorMenu = menubar.addMenu('&Output format')
        self.selectorGroup = QActionGroup(self, exclusive=True)
        selectMoin = self.selectorGroup.addAction(QAction('Moinmoin table', self, checkable=True))
        selectorMenu.addAction(selectMoin)
        selectCSV = self.selectorGroup.addAction(QAction('CSV', self, checkable=True))
        selectorMenu.addAction(selectCSV)
        selectTSV = self.selectorGroup.addAction(QAction('TSV', self, checkable=True))
        selectorMenu.addAction(selectTSV)

        self.setGeometry(500, 500, 500, 200)
        self.setWindowTitle('Nmap2xGUI')
        self.show()

    def button1(self):

        fname = QFileDialog.getOpenFileName(self, 'Open file', '',("XML files(*.xml)"))
        file = os.path.normpath(fname[0]) #Qfiles are tuples that return a filter as well
        self.le1.setText(file)

    def button2(self):

        fname = QFileDialog.getSaveFileName(self, 'Save file', '', ("Text file(*.txt)"))
        file = os.path.normpath(fname[0])
        self.le2.setText(file)

    def button3(self):

        fileLoc = self.le1.text()
        fileTarget = self.le2.text()
        if (fileLoc == "") or (fileTarget == "") or (fileLoc == ".") or (fileTarget == "."):
            self.statusBar().showMessage("Please enter a valid filenames for the source and target.")
        else:
            root = parseXml(getXml(fileLoc))
            if self.selectorGroup.checkedAction():
                if self.selectorGroup.checkedAction().text() == "Moinmoin table":
                    makeText(formatMoin(getNameAddr(root)), fileTarget)
                    self.statusBar().showMessage("All done!")
                elif self.selectorGroup.checkedAction().text() == "CSV":
                    makeText(formatCsv(getNameAddr(root)), fileTarget)
                    self.statusBar().showMessage("All done!")
                elif self.selectorGroup.checkedAction().text() == "TSV":
                    makeText(formatTsv(getNameAddr(root)), fileTarget)
                    self.statusBar().showMessage("All done!")
                else:
                    self.statusBar().showMessage("Please select an output format")
            else:
                self.statusBar().showMessage("Please select an output format")


def getXml(xmlLoc):
    xmlFile = open(os.path.normpath(xmlLoc))
    return xmlFile

def parseXml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return root

def getNameAddr(docroot):
    nameAddr = []
    for child in docroot.iter('host'):
        if child.find(("./hostnames/hostname")) != None:
            nameAddr.append(((child.find("./address")).attrib['addr'], child.find(("./hostnames/hostname")).attrib['name']))
    return nameAddr

def formatMoin(arr):
    arr = sorted(arr,key=lambda x: inet_aton(x[0]))
    moinArray = []
    moinArray.append("||IP Address||Hostname||")
    for tup in arr:
        row = "||" + str(tup[0]) + "||" + str(tup[1]) + "||"
        moinArray.append(row)
    return moinArray

def formatCsv(arr):
    arr = sorted(arr,key=lambda x: inet_aton(x[0]))
    csvArray = []
    csvArray.append("IP Address,Hostname")
    for tup in arr:
        row = str(tup[0]) + "," + str(tup[1])
        csvArray.append(row)
    return csvArray

def formatTsv(arr):
    arr = sorted(arr,key=lambda x: inet_aton(x[0]))
    tsvArray = []
    tsvArray.append("IP address    Hostname")
    for tup in arr:
        row = str(tup[0]) + "   " + str(tup[1])
        tsvArray.append(row)
    return tsvArray

def makeText(arr, saveLoc):
    saveLoc = os.path.normpath(saveLoc)
    file = open(saveLoc,"w")
    for row in arr:
        file.write(row + "\n")
    file.close()

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Gui()
    sys.exit(app.exec_())