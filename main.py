from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import *
from gui_design import *
from PyQt5.QtGui import *
import pyqtgraph as pg
import numpy as np
import cv2
import imutils

face_cascade = cv2.CascadeClassifier('models/haarcascade_plate_number.xml')

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Usamos la funcion QPoint() para guardar la posicion del mouse
        self.click_position = QPoint()
        # Se configura la ventana
        self.btn_normal.hide()
        self.btn_min.clicked.connect(lambda: self.showMinimized())
        self.btn_cerrar.clicked.connect(self.control_btn_cerrar)
        self.btn_normal.clicked.connect(self.control_btn_normal)
        self.btn_max.clicked.connect(self.control_btn_maximizar)
        self.btn_menu.clicked.connect(self.mover_menu)

        #Conexion botones
        self.btn_deteccion.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_deteccion))
        self.btn_basedatos.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_base_datos))
        self.btn_ajustes.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_ajustes))

        # Se elimina la barra de titulo por default
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Size grip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        # Movimiento de la ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        self.start_video()

    def mover_menu(self):
        if True:
            width = self.frame_menu.width()
            normal = 0
            if width == 0:
                extender = 250
            else:
                extender = normal
            self.animacion = QPropertyAnimation(self.frame_menu, b'minimumWidth')
            self.animacion.setDuration(300)
            self.animacion.setStartValue(width)
            self.animacion.setEndValue(extender)
            self.animacion.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animacion.start()


    def control_btn_cerrar(self):
        self.close()
        #cap.release()
        self.label.clear()
        self.Work.stop()

    def control_btn_normal(self):
        self.showNormal()
        self.btn_normal.hide()
        self.btn_max.show()

    def control_btn_maximizar(self):
        self.showMaximized()
        self.btn_max.hide()
        self.btn_normal.show()

    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    def mousePressEvent(self, event):
        self.click_posicion = event.globalPos()

    def mover_ventana(self, event):
        if self.isMaximized() == False:
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.click_posicion)
                self.click_posicion = event.globalPos()
                event.accept()
        if event.globalPos().y() <= 5 or event.globalPos().x() <= 5:
            self.showMaximized()
            self.btn_max.hide()
            self.btn_normal.show()
        else:
            self.showNormal()
            self.btn_normal.hide()
            self.btn_max.show()

    def start_video(self):
        self.Work = Work()
        self.Work.start()
        self.Work.Imageupd.connect(self.Imageupd_slot)

    def Imageupd_slot(self, Image):
        self.label_video.setPixmap(QPixmap.fromImage(Image))


class Work(QThread):
    Imageupd = pyqtSignal(QImage)

    def run(self):
        self.hilo_corriendo = True
        self.cap = cv2.VideoCapture(0)
        while self.hilo_corriendo:
            ret, frame = self.cap.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(Image, 1.1, 4)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (236,111,84), 2)

                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                flip = cv2.flip(Image, 1)
                frameu = imutils.resize(flip, width=640, height=480)
                pic = QImage(frameu.data, frameu.shape[1], frameu.shape[0], QImage.Format_RGB888)
                #pic = convertir_QT.scaled(320, 240, Qt.KeepAspectRatio)
                self.Imageupd.emit(pic)

    def stop(self):
        self.hilo_corriendo = False
        self.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyApp()
    window.show()
    app.exec_()