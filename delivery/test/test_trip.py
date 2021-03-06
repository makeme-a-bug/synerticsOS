from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from account.test.userFactory import AdminUserFactory
from delivery.models import Order,Driver,Trip
from .factory import createOrder

from faker import Faker
import datetime
import json

class TripViewSetTestCase(APITestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = createOrder()
        cls.admin_user = AdminUserFactory.create()
        cls.client = APIClient()
        cls.list_url = reverse('delivery:trip-list')
        cls.get_url = 'delivery:trip-detail'
        cls.disposition_url = reverse('delivery:trip-create-dispostion')
        cls.faker_obj = Faker()

    def test_create_disposition_trip(self) -> None:
        user = self.user
        token, created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        orders = [o.id for o in Order.objects.filter(user=user)]
        startAddress = "berlin , germany"
        startTime = datetime.datetime.strptime("1/1/2022 7:00 AM",'%m/%d/%Y %I:%M %p')
        data = {
            "driverDetails":{
                'startTime':startTime.timestamp(),
                'endTime':(startTime + datetime.timedelta(hours=9)).timestamp(),
                'maxWeight':1600,
                'startAddress':startAddress,
                "driverDimension":{
                    "height":5,
                    "width":5,
                    "depth":5
                }
            },
            'orderIDs':orders
        }  
        response = self.client.post(self.disposition_url, json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_dispatching_trip(self) -> None:
        user = self.user
        token, created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        orders = [o.id for o in Order.objects.filter(user=user)]
        drivers = [d.id for d in Driver.objects.filter(user=user)]
        indexes = {'distance_index':0.5 , 'duration_index':0.5,'worth_index':0.3}
        maxOrdersPerDriver = 50
        data = {
            'driverIDs': drivers,
            'orderIDs': orders,
            'indexes':indexes,
            'worth':'buffer',
            'constraints':{
                'max_orders_per_driver':maxOrdersPerDriver,
                'start_time':datetime.datetime.strptime("1/1/2022 7:00 AM",'%m/%d/%Y %I:%M %p').timestamp(),
                }
            }
        response = self.client.post(self.list_url, json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Trip.objects.filter(user=user)), len(drivers))
        self.assertEqual(Trip.objects.filter(user=user).first().start_time,data['constraints']['start_time'])

