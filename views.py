import requests
import sys
import logging
import json

from flask import Flask
from flask_restful import Resource, Api
app = Flask(__name__)
api = Api(app)

barturl = " http://api.bart.gov/api/{0}.aspx?cmd={1}&orig=RICH&key=MW9S-E7SL-26DU-VV8V&json=y"


class stations(Resource):
    def get(self):
        try:
            res = requests.get(barturl.format("stn","stns"))
            res.raise_for_status()
        except Exception as e:
            logging.ERROR("Request Failed - {0}".format(e))
        
        res = json.loads(res.text)
        stationList = res['root']['stations']['station']
        print(stationList)

        return json.dumps(stationList)

api.add_resource(stations, '/stations')
    

if __name__ == '__main__':
    app.run(debug=True)
