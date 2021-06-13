# -*- coding: utf-8 -*-
"""
Created on Tue June 12 09:30:19 2021

@author: Faruk.Buldur
"""

# import numpy as np
from flask import Flask, request, render_template
import datetime
from dateutil import tz
import os
import pymongo

app = Flask(__name__,template_folder='')

class MongoCredential(Exception):
    pass

mongo_pass = os.environ.get('MONGO_MEMENTO_SECRET')
if mongo_pass == None:
    # self.logger.error(f'Mongo Memento Secret Not Properly Passed')
    raise MongoCredential
try:
    client = pymongo.MongoClient("mongodb+srv://mementoUser:"+mongo_pass+"@mementocluster.tnxf8.mongodb.net/", 
                                maxPoolSize=100, 
                                waitQueueTimeoutMS=1, 
                                waitQueueMultiple=1)
except:
    pass


@app.route('/', methods=['GET'])
def home():
    if request.method == "GET":  
        return render_template('index.html')

@app.route('/',methods=['POST'])
def save():
    def get_sequence(name, collectionObj):
        document = collectionObj.find_one_and_update({"_id": name}, {"$inc": {"value": 1}}, return_document=True)
        return document["value"]

    magicWord = os.environ.get("MAGIC_WORD")
    if request.form['magicWord'] != magicWord:
        return render_template('mischief.html')
    memoryDict = {}
    formValues = request.form
    for key in formValues.keys():
        if key != "magicWord":
            for value in formValues.getlist(key):
                memoryDict[key] = value

    # timeNow = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    utcTime = datetime.datetime.utcnow()
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Europe/Istanbul')
    utc = utcTime.replace(tzinfo=from_zone)
    localTime = utc.astimezone(to_zone)

    memoryDict['timestamp'] = localTime.timestamp()
    memoryDict['date'] = localTime.date().strftime('%d/%m/%Y, %A')
    memoryDict['time'] = localTime.time().strftime('%H:%M:%S')

    try:
        database_name = "Memento"
        collection_name_archive = "Memories"
        database = client[database_name]
        prefArchive = database[collection_name_archive]
        memoryDict["_id"] = get_sequence("memories", prefArchive)
        prefArchive.insert_one(memoryDict)
    except:
        pass
    
    return render_template('result.html')

if __name__ == "__main__":
    app.run(debug=True)