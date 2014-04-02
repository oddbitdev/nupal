__author__ = 'aperion'

import sys
from PySide import QtGui, QtCore
from messages import Messages as Msg
import csv
import solution
import random


class MainApp(QtGui.QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        self.setWindowTitle(Msg.WINDOW_TITLE)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setFixedSize(1100, 700)
        self.CentralWidget = CentralWidget()
        self.setCentralWidget(self.CentralWidget)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class CentralWidget(QtGui.QWidget):
    def __init__(self):
        super(CentralWidget, self).__init__()

        self.Board = DisplayBoard(self)
        self.UI = UIWidget(self)

        self.UI.procStart.connect(self.Board.on_procStart)

        grid = QtGui.QGridLayout()

        grid.addWidget(self.Board, 0, 0, 10, 9)
        grid.addWidget(self.UI, 0, 10, 10, 3)

        self.setLayout(grid)


class DisplayBoard(QtGui.QFrame):
    def __init__(self, parent):
        super(DisplayBoard, self).__init__(parent)
        self.tilesToDraw = None
        self.setLineWidth(1)
        self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Sunken)
        self.canvasWidthRatio = 800.0 / 3600
        self.canvasHeightRatio = 680.0 / 2800


    def paintEvent(self, e):
        super(DisplayBoard, self).paintEvent(e)
        qp = QtGui.QPainter()
        if self.tilesToDraw:
            qp.begin(self)
            for tile in self.tilesToDraw:
                self.drawRectangles(qp, tile.position[0] * self.canvasWidthRatio,
                                    tile.position[1] * self.canvasHeightRatio,
                                    tile.width * self.canvasWidthRatio, tile.height * self.canvasHeightRatio)
            qp.end()

    def drawRectangles(self, qp, x, y, width, height):
        qp.setBrush(QtGui.QColor(random.randint(10, 250), random.randint(10, 250), random.randint(10, 250)))
        qp.drawRect(x, y, width, height)

    @QtCore.Slot(list)
    def on_procStart(self, solvedTiles):
        self.tilesToDraw = solvedTiles
        self.update()
        self.raise_()


class UIWidget(QtGui.QWidget):
    procStart = QtCore.Signal(list)

    def __init__(self, parent):
        super(UIWidget, self).__init__(parent)
        self.solvedTiles = None
        self.noOfPages = 0
        self.currentPage = None
        self.listOfRects = None

        self.pageLabel = QtGui.QLabel()
        self.pageLabel.setText(Msg.PAGES_LABEL)
        self.pageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.loadButton = QtGui.QPushButton(Msg.LOAD_BUTTON)
        self.saveButton = QtGui.QPushButton(Msg.SAVE_BUTTON)
        self.addButton = QtGui.QPushButton(Msg.ADD_BUTTON)
        self.copyButton = QtGui.QPushButton(Msg.COPY_BUTTON)
        self.delAllButton = QtGui.QPushButton(Msg.DELALL_BUTTON)
        self.delButton = QtGui.QPushButton(Msg.DEL_BUTTON)
        self.helpButton = QtGui.QPushButton("?")
        self.copyRightButton = QtGui.QPushButton(Msg.COPYRIGHT_BUTTON)
        self.optionsButton = QtGui.QPushButton(Msg.OPTIONS_BUTTON)
        self.leftButton = QtGui.QPushButton("<")
        self.rightButton = QtGui.QPushButton(">")
        self.printButton = QtGui.QPushButton(Msg.PRINT_BUTTON)

        self.listWidget = QtGui.QListWidget()

        grid = QtGui.QGridLayout()

        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        grid.addWidget(self.loadButton, 0, 0)
        grid.addWidget(self.printButton, 0, 1)
        grid.addWidget(self.saveButton, 0, 2)
        grid.addWidget(self.addButton, 1, 0)
        grid.addWidget(self.copyButton, 1, 1)
        grid.addWidget(self.delButton, 1, 2)
        grid.addWidget(self.listWidget, 2, 0, 6, 3)
        grid.addWidget(self.leftButton, 8, 0)
        grid.addWidget(self.delAllButton, 8, 1)
        grid.addWidget(self.rightButton, 8, 2)
        grid.addWidget(self.helpButton, 9, 0)
        grid.addWidget(self.pageLabel, 9, 1)
        grid.addWidget(self.optionsButton, 9, 2)

        self.loadButton.clicked.connect(self.loadFileMenu)
        self.rightButton.clicked.connect(self.nextPage)
        self.leftButton.clicked.connect(self.previousPage)
        self.delAllButton.clicked.connect(self.clearList)
        self.delButton.clicked.connect(self.deleteListItem)

        self.setLayout(grid)

    def updateStatus(self):
        self.noOfPages = self.getNoOfPages()
        if self.noOfPages:
            extraString = "/" + str(self.noOfPages)
        else:
            extraString = ""
        self.pageLabel.setText(self.getCurrentPage() + extraString)

    def deleteListItem(self):
        for item in self.listWidget.selectedItems():
            index = self.listWidget.row(item)
            self.solvedTiles[index] = None
        self.listWidget.clear()
        self.solvedTiles = [x for x in self.solvedTiles if x is not None]
        for item in self.solvedTiles:
            item.reset()
        self.generateSolution(True)

    def getCurrentPage(self):
        if self.currentPage:
            return str(self.currentPage)
        return Msg.PAGES_LABEL

    @QtCore.Slot()
    def clearList(self):
        self.currentPage = None
        self.solvedTiles = None
        listToSend = None
        self.updateStatus()
        self.listWidget.clear()
        self.procStart.emit([])

    @QtCore.Slot()
    def previousPage(self):
        if self.currentPage and self.currentPage > 1:
            self.currentPage -= 1
            listToSend = self.getRectsToDisplay()
            self.updateStatus()
            self.procStart.emit(listToSend)

    @QtCore.Slot()
    def nextPage(self):
        if self.currentPage and self.currentPage < self.noOfPages:
            self.currentPage += 1
            listToSend = self.getRectsToDisplay()
            self.updateStatus()
            self.procStart.emit(listToSend)

    def getNoOfPages(self):
        pageNo = 0
        if not self.solvedTiles:
            return ""
        for tile in self.solvedTiles:
            if tile.sheetId + 1 > pageNo:
                pageNo = tile.sheetId + 1
        return pageNo

    def getRectsToDisplay(self):
        rectsToDisplay = []
        for tile in self.solvedTiles:
            if tile.sheetId == self.currentPage - 1:
                rectsToDisplay.append(tile)
        return rectsToDisplay

    @QtCore.Slot()
    def generateSolution(self, updateSolution=False):
        if not self.listOfRects:
            return
        if not updateSolution:
            self.tileList = [solution.Tile(width, height) for width, height in self.listOfRects]
            self.workspace = solution.Workspace(self.tileList)
        else:
            self.workspace = solution.Workspace(self.solvedTiles)
        self.solvedTiles = self.workspace.generate_solution(False, True)
        self.currentPage = 1
        self.updateStatus()
        listToSend = self.getRectsToDisplay()
        self.solvedTiles.sort(key=lambda x: x.sheetId)
        for item in self.solvedTiles:
            self.listWidget.addItem('{0} x {1} :      \t pag {2}'.format(item.width, item.height, item.sheetId + 1))
        self.procStart.emit(listToSend)

    def loadFileMenu(self):
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '/home', '*.txt')

        if not fname:
            return

        self.listWidget.clear()
        self.listOfRects = []
        reader = csv.reader(open(fname, "rb"), delimiter=",", skipinitialspace=True)
        for line in reader:
            self.listOfRects.append(line)
        for item in self.listOfRects:
            item[0] = int(item[0])
            item[1] = int(item[1])
        self.generateSolution()


def main():
    app = QtGui.QApplication(sys.argv)
    appWin = MainApp()
    appWin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()