import urllib2, urllib, requests

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
    jsonInfo = json.load(urllib2.urlopen(url))
    
    listJson = [ {"images": jsonData["images"]}
             for jsonData in jsonInfo["data"]]
    
    return jsonify(data = listJson)

"""
meant to be used only for getting the relevant skyScannerIDs
"""
@app.route("/ssID/<city>")
def getSkyScannerId(city):
    url = "http://partners.api.skyscanner.net/apiservices/autosuggest/v1.0/SG/SGD/en-GB?query=%s&apiKey=prtl6749387986743898559646983194" %city
    req = urllib2.Request(url)
    req.add_header('Accept', 'application/json')
    
    response = urllib2.urlopen(req)
    jsonData = json.load(response)
   
    match = [cityResponse for cityResponse in jsonData["Places"] if city.lower() == cityResponse["PlaceName"].lower() 
                or city.lower() == cityResponse["CountryName"].lower()]

    if match:
        return match[0]["CityId"]
    
    match = [cityResponse for cityResponse in jsonData["Places"] if city.lower() in cityResponse["PlaceName"].lower()
                or city.lower() in cityResponse["CountryName"].lower()]

    return match[0]["CityId"]

"""
finds flights from {fromCityName} to {toCityName} from the cache.
TAKE NOTE that live prices must still be gotten once this is done
"""
@app.route('/flights/<From>/<To>')
def ssRoute(From, To):
    originPlace = getSkyScannerId(From)
    destinationPlace = getSkyScannerId(To)
    
    apiUrl = "http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/"
    market = "SG"
    currency = "SGD"
    locale = "en-GB"
    outboundPartialDate = "2015-03"
    inboundPartialDate = "2015-05"
    preApi = "?apiKey="
    api = "ah990939262788742843673151032999"
    
    url = "/".join([apiUrl, market, currency, locale, originPlace, destinationPlace, outboundPartialDate, inboundPartialDate])
    url = "".join([url, preApi, api])
    
    req = urllib2.Request(url)
    req.add_header('Accept', 'application/json')
    
    response = urllib2.urlopen(req)
    jsonData = json.load(response)
    
    rawQuotes = jsonData["Quotes"]
    
    for quote in rawQuotes:
        try :
            quote["OutboundLeg"]["Destination"] = [destination for destination in jsonData["Places"] 
                                                       if destination["PlaceId"] == quote["OutboundLeg"]["DestinationId"]][0]
            quote["OutboundLeg"]["Origin"] = [origin for origin in jsonData["Places"] 
                                                       if origin ["PlaceId"] == quote["OutboundLeg"]["OriginId"]][0]
            quote["OutboundLeg"]["Carriers"] = [carrier for carrier in jsonData["Carriers"] 
                                                       if carrier["CarrierId"] in quote["OutboundLeg"]["CarrierIds"]]   
        except:
            quote["InboundLeg"]["Destination"] = [destination for destination in jsonData["Places"] 
                                                       if destination["PlaceId"] == quote["InboundLeg"]["DestinationId"]][0]
            quote["InboundLeg"]["Origin"] = [origin for origin in jsonData["Places"] 
                                                       if origin ["PlaceId"] == quote["InboundLeg"]["OriginId"]][0]
            quote["InboundLeg"]["Carriers"] = [carrier for carrier in jsonData["Carriers"] 
                                                       if carrier["CarrierId"] in quote["InboundLeg"]["CarrierIds"]]   
   
    return jsonify(Quotes = jsonData["Quotes"])
    
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

@app.route("/book")
def book():
   
    url = "http://partners.api.skyscanner.net/apiservices/pricing/v1.0"

    values = {
              "apiKey":  "ah990939262788742843673151032999",
          "country": "SG", 
          "currency" :"SGD",
          "locale" : "en-GB",
          "originplace" :"SIN-sky",
          "destinationplace" :"EDI-sky",
          "outbounddate" :"2015-03-16",
          "adults" : "1"}

    headers = {    "Content-Type":"application/x-www-form-urlencoded",
               "Accept" :"application/json"}
    
    req = requests.post(url, params = values, headers = headers)
    print req.url
    try:
        response = urllib2.urlopen(req)
    except Exception:
        print Exception
    return "yay"
    
if __name__ == '__main__':
    app.run()

# print info