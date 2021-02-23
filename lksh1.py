from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from tabulate import *
import mysql.connector as db
from mysql.connector import Error
import sys
import csv

koneksi = db.connect(host="localhost", username="root", password="", database="lksai_tim3")

kursor = koneksi.cursor()

class Home(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Home")

		self.kd = KonfirmasiData()

		lyHorizontal = QHBoxLayout()
		lyVertical = QVBoxLayout()

		self.tvPilih = QLabel("File yang dipilih")
		lyHorizontal.addWidget(self.tvPilih)

		self.etFile = QLineEdit()
		lyHorizontal.addWidget(self.etFile)

		self.btnBrowse = QPushButton("Browse")
		self.btnBrowse.clicked.connect(self.browse)
		lyHorizontal.addWidget(self.btnBrowse)

		self.btnSubmit = QPushButton("Submit")
		self.btnSubmit.clicked.connect(self.submit)
		lyVertical.addLayout(lyHorizontal)
		lyVertical.addWidget(self.btnSubmit)

		self.setLayout(lyVertical)
		self.resize(700, 50)

	def browse(self):
		fileName, _ = QFileDialog.getOpenFileName(self, "Open", "", "All Files (*.*)")
		if fileName:
			self.etFile.setText(fileName)
			self.kd.etF.setText(fileName)

	def submit(self):
		file = self.etFile.text()
		if file == "":
			self.notif = Notif()
			self.notif.msg.setText("Anda Belum Memilih File")
			self.notif.resize(250,50)
			self.notif.exec_()

		else:

			if file.endswith('.txt'):
				self.close()
				self.kd.resize(300, 50)
				self.kd.exec_()

			else:
				self.notif = Notif()
				self.notif.msg.setText("Format File yang anda pilih tidak tersedia")
				self.notif.resize(250,50)
				self.notif.exec_()

class KonfirmasiData(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Konfirmasi Data")

		lyVertical = QVBoxLayout()
		lyHorizontal = QHBoxLayout()

		self.etF = QLineEdit()
		self.etF.hide()

		self.tvNama = QLabel("Masukkan Nama Tabel")
		lyHorizontal.addWidget(self.tvNama)

		self.etNama = QLineEdit()
		lyHorizontal.addWidget(self.etNama)

		lyVertical.addLayout(lyHorizontal)

		self.btnSubmit = QPushButton("Submit")
		self.btnSubmit.clicked.connect(self.submit)
		lyVertical.addWidget(self.btnSubmit)

		self.setLayout(lyVertical)

	def submit(self):
		namatabel = self.etNama.text()
		namafile = self.etF.text()

		if namatabel == "":
			self.notif = Notif()
			self.notif.msg.setText("Anda belum memasukkan Nama Tabel!")
			self.notif.exec_()

		else:

			file = open(namafile, encoding='utf-8-sig')

			header = file.readline()

			if header.find(";") != -1:
				simbol = ";"
				header = header.split(";")

			elif header.find(",") != -1:
				simbol = ","
				header = header.split(",")

			reader = csv.reader(file, delimiter=simbol)

			try:
				createtabel = "CREATE TABLE " + namatabel + " (id_" + namatabel + " INT AUTO_INCREMENT PRIMARY KEY, "
				i = 0
				while i < len(header)-1:
					createtabel = createtabel + header[i] + " TEXT NULL, "
					i = i + 1
				createtabel = createtabel + header[i] + " TEXT NULL )"

				kursor.execute(createtabel)

				for x in reader:
					x = [s.replace("?", "NULL") for s in x ]
					sql = "INSERT IGNORE INTO " + namatabel + " ( "
					j = 0
					while j < len(header)-1:
						sql = sql + header[j] + ", "
						j = j + 1
					sql = sql + header[j] + " ) VALUES {}".format(tuple(x))

					kursor.execute(sql)	
				
				koneksi.commit()

				if kursor.rowcount == 1 :
					self.close()
					self.notif = NotifBerhasil()
					self.notif.msg.setText("Berhasil Membuat dan Menambahkan Data " + namatabel)
					self.notif.exec_()

				else :
					self.notif = Notif()
					self.notif.msg.setText("Gagal Membuat dan Menambahkan Data " + namatabel)
					self.notif.exec_()

			except Error as e:
				print(e)

class Notif(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Notif")

		lyVertical = QVBoxLayout()
		self.msg = QLabel("")
		self.msg.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
		lyVertical.addWidget(self.msg)

		self.btnClose = QPushButton("Close")
		self.btnClose.clicked.connect(self.tutup)
		lyVertical.addWidget(self.btnClose)

		self.setLayout(lyVertical)

	def tutup(self):
		self.close()

class NotifBerhasil(QDialog):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Notif")

		lyVertical = QVBoxLayout()
		self.msg = QLabel("")
		self.msg.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
		lyVertical.addWidget(self.msg)

		self.btnClose = QPushButton("Close")
		self.btnClose.clicked.connect(self.tutup)
		lyVertical.addWidget(self.btnClose)

		self.setLayout(lyVertical)

	def tutup(self):
		self.close()
		home = Home()
		home.exec_()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle('Fusion')
	home = Home()
	home.show()
	sys.exit(app.exec_())