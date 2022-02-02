# This is a sample Python script.
import sys
import requests as rq

from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QListWidget, QGridLayout, QLabel, QLineEdit, QMessageBox
from PyQt5.QtCore import QTimer

from smtplib import SMTP
from pymongo import MongoClient


class TimerUtility(QWidget):
    def __init__(self, parent=None):
        super(TimerUtility, self).__init__(parent)
        self.setWindowTitle("test test")
        self.timer = QTimer()
        self.timer.timeout.connect(self.DoRequest)

        self.s = rq.session()
        self.db_client = MongoClient('localhost', 27017)
        self.db = self.db_client.statuses
        self.coll = self.db.collection1
        self.ids = []
        layout = QGridLayout()
        self.lineEdit1 = QLineEdit()
        self.infoText1 = QLabel()

        self.buttonStart = QPushButton()
        self.buttonStart.setText("Start")

        self.buttonStop = QPushButton()
        self.buttonStop.setText("Stop")

        self.buttonStart.clicked.connect(self.start)
        self.buttonStop.clicked.connect(self.stop)

        layout.addWidget(self.lineEdit1)
        layout.addWidget(self.buttonStart)
        layout.addWidget(self.buttonStop)
        layout.addWidget(self.infoText1)
        self.setLayout(layout)

    def start(self):
        self.url = self.lineEdit1.text()
        if self.lineEdit1.text() == '':
            QMessageBox.about(self, "Ooops", "Вы не указали ссылку на сервис")
        else:
            self.timer.start(1000)

    def stop(self):
        self.timer.stop()

    def DoRequest(self):
        resp = self.s.get(self.url)
        record = {"url": self.url, "status": resp.status_code}
        self.ids.append(self.coll.insert_one(record))

    def get_site_status(self):
        try:
            response = self.s.get(self.url)
            if getattr(response, 'status') == 200:
                return 'ok'
        except AttributeError:
            pass
        return 'smth else'

    def email_alert(message, status):
        fromaddr = 'you@gmail.com'
        toaddrs = 'yourphone@txt.att.net'

        server = SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login('you', 'password')
        server.sendmail(fromaddr, toaddrs, 'Subject: %s\r\n%s' % (status, message))
        server.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    daemon = TimerUtility()
    daemon.show()
    sys.exit(app.exec_())