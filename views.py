import requests
import sys
import logging
import json

from flask import Flask, render_template
app = Flask(__name__)

barturl = "http://api.bart.gov/api/{0}.aspx?cmd={1}&orig=RICH&key=MW9S-E7SL-26DU-VV8V&json=y"
arrivalurl = "http://api.bart.gov/api/sched.aspx?cmd=arrive&orig={0}&dest={1}&key=MW9S-E7SL-26DU-VV8V&json=y"
realtimeDept = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig={0}&key=MW9S-E7SL-26DU-VV8V&json=y"
stationInfo = "http://api.bart.gov/api/stn.aspx?cmd=stninfo&orig={0}&key=MW9S-E7SL-26DU-VV8V&json=y"



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

    return json.dumps(stationList)


@app.route("/trips", methods=['GET'])
def trips():
    result = {}
    try:
        res = requests.get(arrivalurl.format("12th","rock"))
        res.raise_for_status()
    except Exception as e:
        logging.ERROR("Request Failed - {0}".format(e))
    
    res = json.loads(res.text)

    destinationStation = res['root']['schedule']['request']['trip'][0]['leg'][0]['@trainHeadStation']
    print(destinationStation)

    try:
        realtimeRes = requests.get(realtimeDept.format("12th"))
        realtimeRes.raise_for_status()
    except Exception as e:
        logging.ERROR("Request Failed - {0}".format(e))
    
    realtimeRes = json.loads(realtimeRes.text)

    etdRealtime = realtimeRes['root']['station'][0]['etd']
    finaletd = []
    for val in etdRealtime:
        if val['destination'] == destinationStation:
            finaletd = val['estimate']
    # print(res['root']['schedule']['request'])
    # print(finaletd)

    result = res['root']['schedule']['request']
    result['etd'] = finaletd

    # print(result)
    return json.dumps(result)


@app.route("/station", methods=['GET'])
def station():
    try:
        res = requests.get(stationInfo.format("ssan"))
        res.raise_for_status()
    except Exception as e:
        logging.ERROR("Request Failed - {0}".format(e))

    res = json.loads(res.text)

    return json.dumps(res['root']['stations']['station'])

if __name__ == '__main__':
    app.run(debug=True)