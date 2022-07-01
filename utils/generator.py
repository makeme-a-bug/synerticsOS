import nanoid
import pandas as pd
import dateutil.parser as parser
import requests
from synos.settings import SYNERTICS_API_KEY,GOOGLE_API_KEY
import json
from geopy.geocoders import Nominatim,GoogleV3
from geopy.extra.rate_limiter import RateLimiter

googleGeolocator = GoogleV3(timeout=10,user_agent="Synertics",api_key = GOOGLE_API_KEY )
geolocator = Nominatim(timeout=10, user_agent = "myGeolocator")

def createNanoID():
    id = nanoid.generate('1234567890abcdef_',size=25)
    return str(id)

def NanoID():
    id = nanoid.generate('1234567890abcdef_',size=10)
    return str(id)

def read_file(file):
    try:
        df = pd.read_excel(file.file , engine='openpyxl')
    except:
        try:
            df = pd.read_csv(file.file.path)
        except:
            return True , None
    
    return False , df

def timeCorrection(value , error , field):
    if field in error:
        del error[field]
    if value == '':
        return '', error
    try:
        value = parser.parse(value).strftime('%Y-%m-%d %H:%M:%S')
    except:
        error[field] = 'invalid time formate'
    return value , error

def positiveValue(value,error,field):
    if field in error:
        del error[field]
    if value == None or value == '' or value == 'None':
        return 0, error
    try:
        value = float(value)
    except:
        error[field] = 'invalid value'
        return value , error
    if value < 0:
        error[field] = 'value must be positive'
    return value , error

# send request to synertics dispatching api
def dispatching_request(orders, drivers , constraints , indexes,*args,**kwargs):        
    orders = pd.DataFrame(list(orders.values()))
    orders['identification'] = orders['id']
    orders = orders[['identification','buffer','longitude','latitude']]

    # if the update is true it means the trip is re-calculated as the trip can have no drivers so to be on same
    # side we create a temp driver from the values in the trip such as start_latitude and start_longitude
    # if the driver is assigned we dont change anything related.
    if kwargs.get('update',None):
        drivers = [{
            "identification": 1,
            "longitude": kwargs.get('longitude',None),
            "latitude": kwargs.get('latitude',None)
        }]
        drivers = pd.DataFrame(drivers)

    else:
        drivers = pd.DataFrame(list(drivers.values()))
        drivers['identification'] = drivers['id']
        drivers=drivers[['identification','latitude','longitude']]

    url = "https://www.synertics.io/dispatching/batch/"
    headers = {
            'Authorization': "TOKEN "+SYNERTICS_API_KEY,
            'Content-Type': 'application/json'
    }
    payload = {
        "orders" : orders.to_dict('records'),
        "drivers" : drivers.to_dict('records'),
        "constraints" : constraints,
        "index": indexes
    }



    r = requests.post(url, headers=headers, data=json.dumps(payload), verify=False,timeout=1000)


    return r.json()



def geocoder(address):
    cord = googleGeolocator.geocode(address)
    if cord is None:
        cord =  geolocator.geocode(address)
    return cord



