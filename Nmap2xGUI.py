import sys
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication, QPushButton, QLineEdit, QAction, qApp, QTextEdit,
                             QWidget, QActionGroup, QMessageBox)
from PyQt5.QtCore import pyqtSlot
import xml.etree.ElementTree as ET
import os
from socket import inet_aton

class HelpPopup(QTextEdit):
    def __init__(self):
        QWidget.__init__(self)

    def helpWindow(self):
        helpText = QTextEdit("Help")


class FileWarning(QMessageBox):
    def __init__(self):
        QWidget.__init__(self)            


class Gui(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def fileWarning(self, target):
        global fileTarget
        self.warning = FileWarning.warning(self, "File exists", "%s already exists, overwrite?" % fileTarget, QMessageBox.Ok | QMessageBox.Cancel)
        reply = self.warning
        # 1024 = 0x00000400 = PyQt Ok signal
        if reply == 1024:
            pass
        # let's only overwrite if explicitly told to do so and prompt for another name
        else:
            if self.selectorGroup.checkedAction().text() == "Moinmoin table":
                fileTarget = QFileDialog.getSaveFileName(self, 'Save file', '', ("Text file(*.txt)"))
            if self.selectorGroup.checkedAction().text() == "CSV":
                fileTarget = QFileDialog.getSaveFileName(self, 'Save file', '', ("CSV file(*.csv)"))  
            if self.selectorGroup.checkedAction().text() == "TSV":
                fileTarget = QFileDialog.getSaveFileName(self, 'Save file', '', ("TSV file(*.tsv)"))
            return fileTarget


    def showHelp(self):
        self.w = HelpPopup()
        self.w.setGeometry(200, 200, 400, 250)
        self.w.setWindowTitle("Help")
        helpText = ("Weclome to Nmap2xGUI, the Nmap XML converter!\n"
                    "\n"
                    "This tool was developed to save time when documenting new networks. For now, it's really only useful if you need to save a directory of which hostnames correspond to which"
                    "IP addresses in, for example, the company wiki."
                    "\n"
                    "Using this utility is easy - simply press the \"Find XML file(s)...\" button to locate your Nmap-generated XML file(s). "
                    "Then, select what format you would like your output saved in from the top menu."
                    "Each converted Nmap xml file will be saved as the original filename plus the proper extension in the parent folder e.g. /home/test.xml will be saved as /home/test.csv if"
                    "the CSV option is selected."
                    "Once xml file(s) and output format are correctly set, click the \"CONVERT!\" button and the conversion will happen."
                    "\n"
                    "\n"
                    "Important notes:\n"
                    "- This utility will only include devices with a hostname.\n"
                    "- This utility outputs a list sorted by IP address with column titles.\n"
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

        self.btn1 = QPushButton("Find XML file(s)...", self)
        self.btn1.move(30, 50)

        self.btn3 = QPushButton("CONVERT!", self)
        self.btn3.move(150, 150)

        self.le1 = QLineEdit(self)
        self.le1.setFixedWidth(300)
        self.le1.move(150, 50)
        self.le1.setReadOnly(True)

        self.btn1.clicked.connect(self.button1)
        self.btn3.clicked.connect(self.button3)

        self.btn1.setStatusTip('Browse to your Nmap XML file')
        self.btn3.setStatusTip('Convert Nmap XML')

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

        fname = QFileDialog.getOpenFileNames(self, 'Open file', '',("XML files(*.xml)"))
        self.le1.setText("")
        i = 0
        for name in fname[0]:
            if i != 0:
                self.le1.insert(", ")
            self.le1.insert(os.path.normpath(name))
            i = i + 1

    def button3(self):

        fileLoc = self.le1.text().split(", ")
        if (fileLoc == "") or (fileLoc == "."):
            self.statusBar().showMessage("Please enter a valid filenames for the source and target.")
        else:
            for file in fileLoc:
                root = parseXml(getXml(file))
                if self.selectorGroup.checkedAction():
                    if self.selectorGroup.checkedAction().text() == "Moinmoin table":
                        global fileTarget
                        fileTarget = os.path.splitext(file)[0] + ".txt"
                        if os.path.isfile(fileTarget):
                            self.fileWarning(fileTarget)
                            try:
                                makeText(formatMoin(getNameAddr(root)), fileTarget)
                            except AttributeError:
                                break
                        else:
                            makeText(formatMoin(getNameAddr(root)), fileTarget)
                        self.statusBar().showMessage("All done!")
                    elif self.selectorGroup.checkedAction().text() == "CSV":
                        fileTarget = os.path.splitext(file)[0] + ".csv"
                        if os.path.isfile(fileTarget):
                            self.fileWarning(fileTarget)
                            try:
                                makeText(formatCsv(getNameAddr(root)), fileTarget)
                            except AttributeError:
                                break
                        else:
                            makeText(formatCsv(getNameAddr(root)), fileTarget)
                        self.statusBar().showMessage("All done!")
                    elif self.selectorGroup.checkedAction().text() == "TSV":
                        fileTarget = os.path.splitext(file)[0] + ".tsv"
                        if os.path.isfile(fileTarget):
                            self.fileWarning(fileTarget)
                            try:
                                makeText(formatTsv(getNameAddr(root)), fileTarget)
                            except AttributeError:
                                break
                        else:
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
    csvArray.append("IP_Address,Hostname")
    for tup in arr:
        row = str(tup[0]) + "," + str(tup[1])
        csvArray.append(row)
    return csvArray

def formatTsv(arr):
    arr = sorted(arr,key=lambda x: inet_aton(x[0]))
    tsvArray = []
    tsvArray.append("IP_address    Hostname")
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