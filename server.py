from flask import Flask, render_template, request
from flask.ext.socketio import SocketIO, emit
from postcodes import PostCoder
from urllib2 import Request, urlopen, URLError
import json, time, csv, os, sys, datetime, sqlite3 as lite

app = Flask(__name__)
socketio = SocketIO(app)

#north: 51.963940, -3.344690
#south: 51.335114, -3.333703
#west: 51.751900, -4.413110
#east: 51.775698, -2.495996

def create_zones():
	upper_lat = 51.963940
	upper_lon = -4.413110
	for i in range(0, 10):
		latitude_zones.append()

def create_database():
	con = lite.connect("police.db")
	with con:
		cur = con.cursor()
		cur.execute("CREATE TABLE Crimes(month INTEGER, longitude REAL, latitude REAL, crime_type TEXT)")

def create_table():
	con = lite.connect("police.db")
	with con:
		cur = con.cursor()
		cur.execute("CREATE TABLE CrimeFrequency(postcode TEXT, number_of_crimes INTEGER)")

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
	crime_data = get_crime_data("2014-01-01", "2014-02-01")

	return render_template('frontend.html', latitudes=json.dumps(crime_data["latitudes"]), longitudes=json.dumps(crime_data["longitudes"]), crime_type=json.dumps(crime_data["crime"]))

def get_crime_data(startDate, endDate):
	crimeData = {"longitudes":[], "latitudes":[], "crime":[]}
	start_date = startDate
	end_date = endDate
	pattern = "%Y-%m-%d"
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

def getLatLong(pstcode):
	pc = PostCoder()
	result = pc.get(pstcode)
	return result

def populate_crime_table():
	con = lite.connect('police.db')
	pc = PostCoder()
	start_date = "01-01-2015"
	end_date = "01-02-2015"
	pattern = "%d-%m-%Y"
	epoch_start_date = (datetime.datetime.strptime(start_date, pattern) - datetime.datetime(1970,1,1)).total_seconds()
	epoch_end_date = (datetime.datetime.strptime(end_date, pattern) - datetime.datetime(1970,1,1)).total_seconds()
	postcodeFrequency = {}
	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		cur.execute("SELECT * FROM Crimes WHERE (month >= ?) AND (month <= ?)", (int(epoch_start_date), int(epoch_end_date)))        
		rows = cur.fetchall()
		for row in rows:
			postcode = pc.get_nearest(row['latitude'], row['longitude'])[u'postcode'].decode('unicode_escape').encode('ascii','ignore')
			if (not postcode in postcodeFrequency):
				postcodeFrequency[postcode] = 1
			else:
				postcodeFrequency[postcode] += 1
		try:
			for key, value in postcodeFrequency.iteritems(): 
				cur.execute("INSERT INTO CrimeFrequency VALUES(?, ?)", (key, value))
		except lite.IntegrityError:
			pass

@app.route("/updateMap", methods=["POST"])
def updateMap():
	#info = json.loads(request.form)
	print request.form
	crime_data = get_crime_data(request.form['from'], request.form['to'])
	location_data = getLatLong(request.form['postcode'])
	return json.dumps({'latitudes':crime_data["latitudes"], 'longitudes':crime_data["longitudes"], 'crime_type':crime_data["crime"], 'curLat':location_data[u'geo'][u'lat'], 'curLon':location_data[u'geo'][u'lng']})

def tryPostcodeAPI():
	request = Request('https://api.postcodes.io/postcodes?lon=-3.344690&lat=51.963940')
	try:
		response = urlopen(request)
		postcode = response.read()
		print postcode
	except URLError, e:
	    print 'No kittez. Got an error code:', e
# Config and start server
if __name__ == '__main__':
	app.debug = True
	socketio.run(app, host='0.0.0.0', port=5000)