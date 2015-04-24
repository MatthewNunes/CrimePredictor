from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
import json, time, csv, os, sys, datetime, sqlite3 as lite

app = Flask(__name__)
socketio = SocketIO(app)

longitudes = []
latitudes = []
crime_type = []

def create_database():
	con = lite.connect("police.db")
	with con:
		cur = con.cursor()
		cur.execute("CREATE TABLE Crimes(month INTEGER, longitude REAL, latitude REAL, crime_type TEXT)")

def fill_database():
	pattern = "%Y-%m"
	con = lite.connect("police.db")
	path = 'crimedata'
	for filename in os.listdir(path):
		for csvFile in os.listdir(path + "/" + filename):
			if not("outcomes" in csvFile):
				with open(path+"/"+filename+"/"+csvFile, 'rb') as f:
					reader = csv.DictReader(f)
					for row in reader:
						string_date = row['Month']
						epoch_date = (datetime.datetime.strptime(row['Month'], pattern) - datetime.datetime(1970,1,1)).total_seconds()  
						with con:
							cur = con.cursor()
							try: 
								cur.execute("INSERT INTO Crimes VALUES(?, ?, ?, ?)", (int(epoch_date), row['Longitude'], row['Latitude'], row['Crime type']))
							except lite.IntegrityError:
								pass

@app.route("/", methods=["GET"])
def render_homepage():
	get_crime_data()

	return render_template('frontend.html', latitudes=json.dumps(latitudes), longitudes=json.dumps(longitudes), crime_type=json.dumps(crime_type))

def get_crime_data():
	path = 'crimedata'
	for filename in os.listdir(path):
		for csvFile in os.listdir(path + "/" + filename):
			if not("outcomes" in csvFile):
				with open(path+"/"+filename+"/"+csvFile, 'rb') as f:
					reader = csv.DictReader(f)
					for row in reader:
						longitudes.append(row['Longitude'])
						latitudes.append(row['Latitude'])
						crime_type.append(row['Crime type'])

# Config and start server
if __name__ == '__main__':
	app.debug = True
	socketio.run(app, host='0.0.0.0', port=5000)