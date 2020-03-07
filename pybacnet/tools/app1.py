from flask import Flask, render_template, url_for, request, redirect, jsonify
import sys, urllib2, json, pymongo, os, pprint, time
from pymongo import MongoClient

#	if request.form("btn") == "ChangeStatus":
client = MongoClient('127.0.0.1', 27017)
db = client.ACs_data
objects = db.test_collection.find().sort("date_time", pymongo.DESCENDING).limit(2156)
j = 1
print(objects)
AC_status = {}
Room_temp = {}
Setpoint_temp = {}
for i in range(0, 77):
	AC_status[i] = objects[j]
	Room_temp[i] = objects[j+7]
	Setpoint_temp[i] = objects[j+8]
	j = j + 28
print(AC_status)



