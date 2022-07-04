from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from account.test.userFactory import AdminUserFactory
from delivery.models import Order
from .factory import createOrder

from faker import Faker

#needs invalid tests
class OrderViewSetTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = createOrder()
        cls.admin_user = AdminUserFactory.create()
        cls.client = APIClient()
        cls.list_url = reverse('delivery:order-list')
        cls.get_url = 'delivery:order-detail'
        cls.faker_obj = Faker()


    def test_order_list(self):
        user = self.user
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(Order.objects.filter(user = user)))

    def test_order_list_invalid(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_order(self):
        user = self.user
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        data = {
            "address":"berlin , germany",
        }
        response = self.client.post(self.list_url,data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['address'], data['address'])

    def test_create_order_invalid(self):
        user = self.user
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        data = {
            "weight": 10,
        }
        response = self.client.post(self.list_url,data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_get(self):
        user = self.user
        order = Order.objects.filter(user = user)[0]
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(reverse(self.get_url, kwargs={'pk': order.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)

    def test_order_get_invalid(self):
        user = self.user
        order = Order.objects.filter(user = user)[0]
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(reverse(self.get_url, kwargs={'pk': order.id+'j'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_update(self):
        user = self.user
        order = Order.objects.filter(user = user)[0]
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        update_dict = {
            'address': 'berlin , germany',
            'width': 0.5,
            'height': 0.2,
            'depth': 1.2,
            'weight': 10,
        }

        response = self.client.put(reverse(self.get_url, kwargs={'pk': order.id}),update_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], update_dict['address'])
        self.assertEqual(response.data['width'], update_dict['width'])
        self.assertEqual(response.data['height'], update_dict['height'])
        self.assertEqual(response.data['depth'], update_dict['depth'])
        self.assertEqual(response.data['weight'], update_dict['weight'])

    def test_order_parital_update(self):
        user = self.user
        order = Order.objects.filter(user = user)[0]
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        update_dict = {
            'address':order.address,
            'width': 0.5,
            'height': 0.2,
            'depth': 1.2,
            'weight': 10,
        }

        response = self.client.patch(reverse(self.get_url, kwargs={'pk': order.id}),update_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['width'], update_dict['width'])
        self.assertEqual(response.data['height'], update_dict['height'])
        self.assertEqual(response.data['depth'], update_dict['depth'])
        self.assertEqual(response.data['weight'], update_dict['weight'])

    def test_order_update_invalid(self):
        user = self.user
        order = Order.objects.filter(user = user)[0]
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        update_dict = {
            'width': 0.5,
            'height': 0.2,
            'depth': 1.2,
            'max_weight': 10,
        }

        response = self.client.put(reverse(self.get_url, kwargs={'pk': order.id}),update_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
       
    def test_order_partial_update_invalid(self):
        user = self.user
        order = Order.objects.filter(user = user)[0]
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        update_dict = {
            'address':"it should thorw an error",
            'width': 0.5,
            'height': 0.2,
            'depth': 1.2,
            'weight': 10,
        }

        response = self.client.patch(reverse(self.get_url, kwargs={'pk': order.id}),update_dict)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_order_destroy(self):
        user = self.user
        order = Order.objects.create(user = user,address = "berlin , germany")
        count = Order.objects.filter(user = user).count()
        token,created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.delete(reverse(self.get_url, kwargs={'pk': order.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.filter(user = user).count(),count -1)
