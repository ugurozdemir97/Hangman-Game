from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt, QTimer
from pandas import read_csv
from random import choice
from hm import Screen
import sys
import source


class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()
        self.ui = Screen()
        self.ui.setupUi(self)

        self.level = "EASY"

        self.word = ""  # This variable will hold one single word
        self.words = []  # This will hold all words to choose from

        self.chars = []  # This will hold underscores as much as the letters
        self.underscore = ""  # This will be what player sees, converted from self.chars
        self.used = ""  # This will hold used letters

        self.ui.input.setMaxLength(1)  # User can only enter one letter
        self.ui.label.hide()  # This is a label that covers entire window to warn if Words.csv file not found
        # Also for the feedback, You win, you lost etc.

        self.lives = 5

        # ----------------- CONNECTIONS ----------------- #

        self.ui.send.clicked.connect(self.send)
        self.ui.input.textChanged.connect(self.uc)  # Change letters in QLineEdit into upper case just for visuals
        self.ui.easy.toggled.connect(self.difficulty)
        self.ui.medium.toggled.connect(self.difficulty)
        self.ui.difficult.toggled.connect(self.difficulty)
        self.ui.character.toggled.connect(self.enter)
        self.ui.whole.toggled.connect(self.enter)

        # -------------- TO ADJUST FONT SIZE ---------------- #

        self.font = self.ui.known.font()  # Get font and its size
        self.font.pointSize = 12

        self.font.setPointSize(self.font.pointSize)  # Set size

        self.metrics = QFontMetrics(self.font)
        self.width = self.metrics.width(" T H O U G H T - P R O V ")  # This is from the longest word. Maximum width
        # it can take to fit in group box. If the text is wider the font size will decrease

        self.ui.known.setFont(self.font)  # Set font

        # ---------------- GET WORDS ---------------- #

        try:
            data = read_csv("Words.csv")
            self.words = data["a"].tolist()
        except FileNotFoundError:
            self.ui.label.show()  # This will show a warning label
        else:
            self.get_word()

    # --------------------------- CONNECT KEYBOARD ENTER KEY ------------------------------ #

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.ui.send.click()

    # ---------------------------- GET DIFFICULTY LEVEL ------------------------------- #

    def difficulty(self):
        sender = self.sender()
        if sender.isChecked():
            self.level = sender.text()
            self.clear()

    # ------------------------- TURN LINE EDIT TEXT INTO UPPER ------------------------- #

    def uc(self):
        if self.ui.input.text().isupper():
            pass
        else:
            self.ui.input.setText(self.ui.input.text().upper())

    # ---------------------------- CHANGE INPUT SETTING -------------------------------- #

    def enter(self):
        sender = self.sender()
        if sender.isChecked():
            if sender.objectName() == "character":
                self.ui.input.setMaxLength(1)
                self.ui.input.setPlaceholderText("Text Letter")
            else:
                self.ui.input.setMaxLength(17)  # This is the length of the longest word in the list
                self.ui.input.setPlaceholderText("Text Word")

    # ------------------------------ CLEAR PREVIOUS GAME ------------------------------ #

    def clear(self):

        # ------------------ Clear the previous game if exist --------------------- #

        self.ui.label.setText("Words.csv File Not Found :(")
        self.ui.label.setStyleSheet("background-color: rgba(0, 0, 0, 170); color: white;")
        self.ui.label.hide()  # This will hide "You Win", "You Died!" texts.

        self.ui.input.setText("")  # Clear text
        self.ui.man.setStyleSheet("")
        self.ui.input.setEnabled(True)

        self.lives = 5
        self.ui.tries.setText(f"Tries Left: {self.lives}")

        self.underscore = " "
        self.chars = []

        self.used = ""
        self.ui.used.setText(f"Used Letters: {self.used}")

        self.get_word()

    # -------------------------- GET ONE SINGLE WORD ------------------------------ #

    def get_word(self):

        words = []

        # Length of words will change according to difficulty level

        if self.level == "EASY":
            for i in self.words:
                if len(i) <= 5:
                    words.append(i)
        elif self.level == "MEDIUM":
            for i in self.words:
                if 5 < len(i) < 9:
                    words.append(i)
        else:
            for i in self.words:
                if 9 <= len(i):
                    words.append(i)

        self.word = choice(words).upper()  # Pick a random word

        # For each letter in the word add underscore to chars list
        for _ in self.word:
            self.chars.append("_")

        # This is what user will see
        for i in self.chars:
            self.underscore += i + " "

        print(self.word)

        self.ui.known.setText(self.underscore)
        self.adjust_font_size()

    # -------------------------------- SHOW LETTERS  ----------------------------------- #

    def underscores(self):

        # ---------- CHANGE WHAT USER SEES ------------ #
        self.underscore = " "
        for i in self.chars:
            self.underscore += i + " "

        self.ui.known.setText(self.underscore)
        self.adjust_font_size()

        if "_" not in self.chars:  # If there is no underscore then it means player won.
            self.feedback(f'You Win!')

    # ----------------------- ADJUST THE FONT SIZE IF NECESSARY ------------------------ #

    def adjust_font_size(self):
        if len(self.ui.known.text()) == 0:  # If there is no letters set font size 12
            self.font.setPointSize(12)

        width = self.metrics.width(self.ui.known.text())

        if width < self.width:  # If the width is less than the maximum
            self.font.setPointSize(12)
        else:
            rate = self.width / width  # If not, the new font size is = font size * old width / new width
            self.font.setPointSize(int(self.font.pointSize * rate))

        self.ui.known.setFont(self.font)
        self.ui.known.setText(self.ui.known.text())
        self.ui.input.setText("")

    # --------------------------------- CHECK LETTERS ---------------------------------- #

    def send(self):

        if self.ui.character.isChecked():  # If input mode is character check if the input is in the word
            if self.ui.input.text() in self.word:  # If guessed letter exist

                for i in range(len(self.word)):
                    if self.word[i] == self.ui.input.text():
                        self.chars[i] = self.ui.input.text()

                self.underscores()  # Show new underscores

            else:  # If guess was wrong

                if self.used != "":
                    if self.ui.input.text() not in self.used:  # Change Guessed Letters section
                        self.used += self.ui.input.text()
                        self.ui.used.setText(f"Used Letters: {self.used}")
                else:
                    self.used += self.ui.input.text()
                    self.ui.used.setText(f"Used Letters: {self.used}")

                self.ui.input.setText("")
                self.lives -= 1
                self.ui.man.setStyleSheet(f"image: url(:/Images/Images/{self.lives + 1}.png);")
                self.ui.tries.setText(f"Tries Left: {self.lives}")
                if self.lives == 0:
                    self.feedback(f'You Died!\n\nThe Word Was: \n"{self.word}"')

        else:  # If the input mode is writing whole word then check if the word is the same as input
            if self.ui.input.text() == self.word:
                self.feedback(f'You Win!')
            else:
                self.ui.input.setText("")
                self.lives -= 1
                self.ui.man.setStyleSheet(f"image: url(:/Images/Images/{self.lives + 1}.png);")
                self.ui.tries.setText(f"Tries Left: {self.lives}")
                if self.lives == 0:
                    self.feedback(f'You Died!\n\nThe Word Was: \n"{self.word}"')

    # --------------------------------- END OF THE GAME ---------------------------------- #

    def feedback(self, fb):
        self.ui.label.show()
        self.ui.label.setStyleSheet("background-color: rgba(0, 0, 0, 50); color: white;")
        self.ui.label.setText(fb)
        self.ui.input.setEnabled(False)

        QTimer.singleShot(2000, self.clear)


def application():
    window = QApplication(sys.argv)
    win = App()
    win.show()
    sys.exit(window.exec_())


application()
