from django.conf import settings

import nanoid
import pandas as pd
import dateutil.parser as parser
from geopy.geocoders import Nominatim,GoogleV3
from geopy.extra.rate_limiter import RateLimiter
import pytz

googleGeolocator = GoogleV3(timeout=10,user_agent="Synertics",api_key = settings.GOOGLE_API_KEY )
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
        value = parser.parse(value).replace(tzinfo=pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
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



def geocoder(address):
    cord = googleGeolocator.geocode(address)
    if cord is None:
        cord =  geolocator.geocode(address)
    return cord



