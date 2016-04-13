import time, csv, os, sys, datetime
from sets import Set
import sys

def create_arff():
	pattern = "%Y-%m"
	path = 'crimedata'
	arffFile = open("crimeNew.arff", "w")
	for filename in os.listdir(path):
		for csvFile in os.listdir(path + "/" + filename):
			if not("outcomes" in csvFile):
				with open(path+"/"+filename+"/"+csvFile, 'rb') as f:
					reader = csv.DictReader(f)
					for row in reader:
						if (str(row['Month']) != '') and (str(row['Longitude']) != '') and (str(row['LSOA code']) != '') and (str(row['Latitude']) != '') and (str(row['Crime type']) != ''):
							arffFile.write(str(row['Month'])+"," +str(row['Longitude']) +"," +str(row['LSOA code'])+ ","+ str(row['Latitude']) +",\""+ str(row['Crime type']) + "\"\n")
	arffFile.close()


def set_of_lsoa(s):
	pattern = "%Y-%m"
	path = 'crimedata'
	lsoa = Set([])
	for filename in os.listdir(path):
		for csvFile in os.listdir(path + "/" + filename):
			if not("outcomes" in csvFile):
				with open(path+"/"+filename+"/"+csvFile, 'rb') as f:
					reader = csv.DictReader(f)
					for row in reader:
						lsoa.add(str(row[s]))
	for ls in lsoa:
		sys.stdout.write(ls + ",")


create_arff()