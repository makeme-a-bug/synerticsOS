import django_filters
from .models import Order, Trip , Driver

class OrderFilter(django_filters.FilterSet):

    class Meta:
        model = Order
        fields = {
            'address': ['contains','exact'],
            'time_from': ['exact', 'gte','lte'],
            'time_to': ['exact', 'gte','lte'],
            'status':['exact','contains','in'],
            'trip__id':['exact'],
        } 


class TripFilter(django_filters.FilterSet):

    class Meta:
        model = Trip
        fields = {
            'id': ['contains','exact'],
            'start_time': ['exact', 'gte','lte'],
            'end_time': ['exact', 'gte','lte'],
            'driver__id':['exact'],
            'driver__name':['exact',"contains"],
            'id':['exact'],
        } 