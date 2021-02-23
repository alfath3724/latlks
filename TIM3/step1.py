from flask import Flask, render_template, request, redirect, url_for
import os
from os.path import join, dirname, realpath
import mysql.connector as db
import csv
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

mydb = db.connect(
	host="localhost",
	username="root",
	password="",
	database="lksai_tim3"
	)

kursor = mydb.cursor()

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/uploadfile", methods=["GET", "POST"])
def uploadfile():
	if request.method == "POST":
		namatabel = request.form["namatabel"]
		uploaded_file = request.files['file']

		file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
		uploaded_file.save(file_path)

		reader = open(file_path, encoding='utf-8-sig')

		header = reader.readline()

		if header.find(";") != -1:
			simbol = ";"
			header = header.split(";")

		elif header.find(",") != -1:
			simbol = ","
			header = header.split(",")

		reader = csv.reader(reader, delimiter=simbol)
		
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
		
		mydb.commit()

		return redirect(url_for('viewdata', tbl=namatabel))

	else:
		return render_template('uploadfile.html')

@app.route("/viewdata/<tbl>")
def viewdata(tbl):
	query = "SELECT * FROM "+ tbl +""
	kursor.execute(query)
	namatabel = tbl
	tbl = kursor.fetchall()

	query = "SELECT group_concat(COLUMN_NAME) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'lksai_tim3' AND TABLE_NAME = '" + namatabel + "'"
	kursor.execute(query)
	kolom = kursor.fetchall()
	kolom = [tuple(s.replace("()", "") for s in data) for data in kolom]
	kolom = [tuple(i.split(",") for i in data) for data in kolom]

	return render_template("viewdata.html", data = tbl, total = len(tbl[0]), hdr = kolom[0], ttlhd = len(kolom))

def inputdata():
	return render_template("inputdata.html")

if(__name__=="__main__"):
	app.run(port=5000, debug=True)