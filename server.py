from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
import json, time, csv, os, sys, datetime, sqlite3 as lite

app = Flask(__name__)
socketio = SocketIO(app)


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
	crime_data = get_crime_data("01-01-2014", "02-01-2014")

	return render_template('frontend.html', latitudes=json.dumps(crime_data["latitudes"]), longitudes=json.dumps(crime_data["longitudes"]), crime_type=json.dumps(crime_data["crime"]))

def get_crime_data(startDate, endDate):
	crimeData = {"longitudes":[], "latitudes":[], "crime":[]}
	start_date = startDate
	end_date = endDate
	pattern = "%d-%m-%Y"
	epoch_start_date = (datetime.datetime.strptime(start_date, pattern) - datetime.datetime(1970,1,1)).total_seconds()
	epoch_end_date = (datetime.datetime.strptime(end_date, pattern) - datetime.datetime(1970,1,1)).total_seconds()
	con = lite.connect('police.db')

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute("SELECT * FROM Crimes WHERE (month >= ?) AND (month <= ?)", (int(epoch_start_date), int(epoch_end_date)))        
		rows = cur.fetchall()
		for row in rows:
			crimeData["longitudes"].append(row['longitude'])
			crimeData["latitudes"].append(row['latitude'])
			crimeData["crime"].append(row['crime_type'])
	return crimeData

@socketio.on('update map')
def updateMap(msg):
	info = json.loads(msg)
	crime_data = get_crime_data(info['from'], info['to'])
	emit('map update', {'latitudes':crime_data["latitudes"], 'longitudes':crime_data["longitudes"], 'crime_type':crime_data["crime"]}, broadcast=True)

# Config and start server
if __name__ == '__main__':
	app.debug = True
	socketio.run(app, host='0.0.0.0', port=5000)