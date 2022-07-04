from django.conf import settings

import json
import pandas as pd
import requests


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
            'Authorization': "TOKEN "+ settings.SYNERTICS_API_KEY,
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


# send request to synertics disposition api
def disposition_request(orders, startTime , endTime , latitude , longitude ,dimensions,weight,*args,**kwargs):        
    orders = pd.DataFrame(list(orders.values()))
    orders['identification'] = orders['id']
    orders = orders[['identification','buffer','longitude','latitude','time_from','time_to','weight','depth','width','height','order_type']]

    url = "https://www.synertics.io/disposition/batch/"
    headers = {
            'Authorization': "TOKEN "+ settings.SYNERTICS_API_KEY,
            'Content-Type': 'application/json'
    }
    payload = {
        "orders" : orders.to_dict('records'),
        "driver_details" : {
            "starting_location":{
                "latitude": latitude,
                "longitude": longitude
            },
            "max_weight_per_driver":weight,
            "start_time":startTime,
            "end_time":endTime,
            "vehicle_dimensions": dimensions,
        },
    }


    r = requests.post(url, headers=headers, data=json.dumps(payload), verify=False,timeout=1000)


    return r.json()