import urllib
from sympy.utilities.tests.diagnose_imports import relevant

try:
    import simplejson as json
except ImportError:
    import json


from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/boston')
def apiCall():
    info = "".join(urllib.urlopen("http://api.tripadvisor.com/api/partner/2.0/location" +\
                "/60745/hotels?key=SingaporeHack-CDCCADCA7505").readlines())
    jsonInfo = json.loads(info)
    return info

if __name__ == '__main__':
    app.run()

# print info