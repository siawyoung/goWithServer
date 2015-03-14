import urllib2, urllib

try:
    import flask.json as json
except ImportError:
    import json

from bs4 import BeautifulSoup
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'   

@app.route('/flights')
def skyScanner():
    apiUrl = "http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/"
    market = "SG"
    currency = "SGD"
    locale = "en-GB"
    originPlace = "SIN-sky"
    destinationPlace = "EDI-sky"
    outboundPartialDate = "anytime"
    inboundPartialDate = "anytime"
    preApi = "?apiKey="
    api = "ah990939262788742843673151032999"
    
    url = "/".join([apiUrl, market, currency, locale, originPlace, destinationPlace, outboundPartialDate, inboundPartialDate])
    url = "".join([url, preApi, api])
    
    return "<br>".join(urllib.urlopen(url).readlines())
    
"""
Call this for attractions in a city
"""
@app.route('/attractions/<cityName>')
def attractions(cityName):
    cityID = str(wtf(cityName))
    info = urllib2.urlopen("http://api.tripadvisor.com/api/partner/2.0/location/%s/attractions?key=SingaporeHack-CDCCADCA7505" %cityID)
    jsonInfo = json.load(info) 
    
    dictJson = [ {"percent_recommended": jsonData["percent_recommended"],
                 "name" : jsonData["name"], 
                 "awards" : jsonData["awards"],
                 "rating_image_url": jsonData["rating_image_url"]} 
                 for jsonData in jsonInfo["data"]]

    return jsonify(data = dictJson)

"""
function to get IDs from trip advisor
"""
def wtf(place):
    url = 'http://www.tripadvisor.com.sg/TypeAheadJson'
 
    values = {
        'action': 'API',
        'query': place
    }
 
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = json.load(response)
 
    return the_page['results'][0]['value']

"""
Call this for city's description
"""
@app.route("/description/<place>")
def wtf2(place):
    url = 'http://www.tripadvisor.com.sg/Tourism-g' + str(wtf(place)) + '.html'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    soup = BeautifulSoup(response)
    for node in soup.select('.shortDescription'):
        return node.findAll(text=True)[0].encode('utf-8')

@app.route("/pictures/<place>")
def pics(place):
    url = "http://api.tripadvisor.com/api/partner/2.0/location/%s/photos?key=SingaporeHack-CDCCADCA7505" %str(wtf(place))
    print url
    jsonInfo = json.load(urllib2.urlopen(url))
    
    listJson = [ {"images": jsonData["images"]}
             for jsonData in jsonInfo["data"]]
    
    return jsonify(data = listJson)

if __name__ == '__main__':
    app.run()

# print info