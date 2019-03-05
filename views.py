import requests
import sys
import logging
import json

from flask import Flask, render_template, request
app = Flask(__name__)

barturl = "http://api.bart.gov/api/{0}.aspx?cmd={1}&orig=RICH&key=MW9S-E7SL-26DU-VV8V&json=y"
arrivalurl = "http://api.bart.gov/api/sched.aspx?cmd=arrive&orig={0}&dest={1}&key=MW9S-E7SL-26DU-VV8V&json=y"
realtimeDept = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig={0}&key=MW9S-E7SL-26DU-VV8V&json=y"
stationInfo = "http://api.bart.gov/api/stn.aspx?cmd=stninfo&orig={0}&key=MW9S-E7SL-26DU-VV8V&json=y"
globalStation = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/stations", methods=['GET'])
def stations():
    try:
        res = requests.get(barturl.format("stn","stns"))
        res.raise_for_status()
    except Exception as e:
        logging.ERROR("Request Failed - {0}".format(e))
    
    res = json.loads(res.text)
    stationList = res['root']['stations']['station']
    global globalStation
    globalStation = stationList

    return json.dumps(stationList)

def getAbbr(name):
    """
    get the abbr from the name of the station.
    """
    for i in globalStation:
        if i["name"] == name:
            return i["abbr"]

@app.route("/trips", methods=['GET'])
def trips():
    result = {}
    source = request.args.get('source')
    destination = request.args.get('dest')
    print(source, destination)
    try:
        res = requests.get(arrivalurl.format(source,destination))
        res.raise_for_status()
        res = json.loads(res.text)
    except Exception as e:
        print("Request Failed - {0}".format(e))
    
    destinationStation = res['root']['schedule']['request']['trip'][0]['leg'][0]['@trainHeadStation']

    try:
        realtimeRes = requests.get(realtimeDept.format(source))
        realtimeRes.raise_for_status()
    except Exception as e:
        logging.ERROR("Request Failed - {0}".format(e))
    
    realtimeRes = json.loads(realtimeRes.text)

    etdRealtime = realtimeRes['root']['station'][0]['etd']
    finaletd = []
    for val in etdRealtime:
        if val['abbreviation'] == getAbbr(destinationStation):
            finaletd = val['estimate']
    # print(res['root']['schedule']['request'])
    # print(finaletd)

    result = res['root']['schedule']['request']
    result['etd'] = finaletd

    # print(result)
    return json.dumps(result)


@app.route("/station", methods=['GET'])
def station():
    source = request.args.get('source')
    try:
        res = requests.get(stationInfo.format(source))
        res.raise_for_status()
    except Exception as e:
        logging.ERROR("Request Failed - {0}".format(e))

    res = json.loads(res.text)

    return json.dumps(res['root']['stations']['station'])

if __name__ == '__main__':
    app.run(debug=True)
