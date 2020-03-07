import sys, urllib2, json, pymongo, os, pprint, time
import datetime
from pymongo import MongoClient
client = MongoClient('127.0.0.1', 27017)
db = client.ACs_data
collection = db.test_collection
os.system("rm /home/lingam/pybacnet/tools/test.json")
os.system("python /home/lingam/pybacnet/tools/bacnet-scan.py")
time.sleep(60)
data = json.load(open("/home/lingam/pybacnet/tools/test.json"))
result = data[0]
objects = result["objs"]
objects = objects[1:len(objects)-4]
#pprint.pprint(objects)
collection.insert(objects)
