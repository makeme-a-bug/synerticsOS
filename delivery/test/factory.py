from faker import Faker as FakerClass
import random
import math
import pandas as pd
from random import randrange
import numpy as np
import datetime
from factory import django, Faker, post_generation,PostGenerationMethodCall

from delivery.models import Order,Driver,Trip
from account.models import User
import nanoid
from account.test.userFactory import UserFactory as UF

class OrderFactory(django.DjangoModelFactory):
    class Meta:
        model = Order


def getRandomNumber(min,max):
    return round(min + (random.random() * (max - min)),2)

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)


def randomcoordinates():
    radius = 10000                         
    radiusInDegrees=radius/111300            
    r = radiusInDegrees
    #Munich Lat Long
    # x0 = 48.137154
    # y0 = 11.576124
    x0 = 52.500314
    y0 = 13.281913
    u = float(random.uniform(0.0,1.0))
    v = float(random.uniform(0.0,1.0))
    w = r * math.sqrt(u)
    t = 2 * math.pi * v
    x = w * math.cos(t) 
    y = w * math.sin(t)
    xLat  = x + x0
    yLong = y + y0
    latlong = [xLat, yLong]
    return latlong

def randomData(orderSize=20,driverSize=2):
    df = pd.DataFrame(np.random.randint(0,100,size=(orderSize, 1)), columns=['buffer'])
    df['type'] =  'order'
    df['order_type'] =  df.apply(lambda row: np.random.randint(2),1)
    df['id'] = df.apply(lambda row: nanoid.generate(size=10),1)
    df['weight'] = df.apply(lambda row: randrange(5,25),1)
    df['depth'] = df.apply(lambda row: getRandomNumber(0.2,0.8) ,1)
    df['width'] = df.apply(lambda row: getRandomNumber(0.2,0.5),1)
    df['height'] = df.apply(lambda row: getRandomNumber(0.1,0.3),1)
    df['time_from'] = df.apply(lambda row: random_date(datetime.datetime.strptime("1/1/2022 7:00 AM",'%m/%d/%Y %I:%M %p'), datetime.datetime.strptime("1/1/2022 9:00 AM",'%m/%d/%Y %I:%M %p')).timestamp(),1)
    df['time_to'] = df.apply(lambda row: random_date(datetime.datetime.strptime("1/1/2022 3:00 PM",'%m/%d/%Y %I:%M %p'), datetime.datetime.strptime("1/1/2022 6:00 PM",'%m/%d/%Y %I:%M %p')).timestamp(),1)
    df['latlong'] = df.apply(lambda row: randomcoordinates(),1)
    drivers = []
    for j in range(0,driverSize):
        drivers.append( {'buffer':None, 'type':'driver', 'id':nanoid.generate(size=10),  'latlong':randomcoordinates()})
    df = pd.concat([df , pd.DataFrame(drivers)])
    return df


def createOrder(orderSize = 20 , driverSize = 2):
    FS = FakerClass()
    user = UF.create()
    data = randomData(orderSize,driverSize)
    orders = data[data['type'] == 'order']
    for id , order in orders.iterrows():
        Order.objects.create(user = user, order_type=order['order_type'],latitude=order['latlong'][0] , longitude =order['latlong'][1] , address="some where in berlin" , time_from = order['time_from'],  time_to = order['time_to']
        , buffer = order['buffer'] , weight = order['weight'], height =order['height'], depth=order['depth'] , width=order['width'])
    drivers = data[data['type'] == 'driver']

    for id , driver in drivers.iterrows():
        Driver.objects.create(user = user, latitude=driver['latlong'][0] , longitude =driver['latlong'][1] , address="some where in berlin",max_weight=1600 , width=5 , height=5 , depth= 5 , name=FS.name() , email = FS.email())
    return user

    