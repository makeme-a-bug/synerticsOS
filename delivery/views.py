from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils import timezone

from datetime import timedelta

from .models import Order,Driver,Trip
from .serializer import OrderSerializer , DriverSerializer, TripSerializer
from .forms import OrderForm,FieldSet,DriverForm
from utils.generator import dispatching_request,geocoder,disposition_request
from .filters import OrderFilter , TripFilter

@login_required
def orders(request):
    form = OrderForm()
    fieldsets = (FieldSet(form,('address',),'address',
                        legend='Recipient details',),
                FieldSet(form, ('time_from','time_to'),'time', 
                            legend="Delivery time window"),
                FieldSet(form, ('height','width','depth'),'dimensions', 
                            legend="Delivery dimensions"),
                FieldSet(form, ('buffer','order_type','weight'),'other',
                            legend="Other detials"),
                )
    return render(request, 'delivery/deliveries.html',{'form':form,'fieldsets':fieldsets,'deliveries':True})

@login_required
def drivers(request):
    form = DriverForm()
    fieldsets = (FieldSet(form,('address','email','name'),'address',
                        legend='Driver details',),
                FieldSet(form, ('height','width','depth'),'dimensions', 
                            legend="Vehicle dimensions"),
                FieldSet(form, ('max_weight',),'other',
                            legend="Other detials"),
        )
    return render(request, 'delivery/drivers.html',{'drivers':True,'form':form,'fieldsets':fieldsets})


@login_required
def trips(request):
    return render(request, 'delivery/trips.html',{'trips':True})



def driver_trips(request,id):
    trips = []
    
    for t in Trip.objects.filter(driver__id=id):
        if t.status != 3:
            trips.append(t)

    return render(request, 'delivery/driver_trips.html',{'trips':trips,'id':id})

def driver_ind_trip(request,id,trip_id):
    trip = Trip.objects.get(driver__id=id,id=trip_id)
    if request.method == 'POST':
        order = Order.objects.get(id = request.POST.get('id'))
        order.status = int(request.POST['status'])
        order.save()
        return JsonResponse(OrderSerializer(order).data)
    return render(request, 'delivery/driver_ind_trip.html',{'trip':trip,'id':id,'trip_id':trip_id})

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    ordering_fields = "__all__"
    search_fields = ['id','address','trip__driver__name']

    def get_queryset(self):
        return Order.objects.filter(user = self.request.user).order_by('status')

    def perform_create(self, serializer):
        geocode = geocoder(serializer.validated_data['address'])
        if geocode:
            lat = geocode.latitude
            lon = geocode.longitude
            serializer.save(user=self.request.user,latitude = lat, longitude = lon)
        else:
            raise serializers.ValidationError({'address':'Address could not be geocoded'})
    
    def perform_update(self, serializer):
        id = self.request.parser_context['kwargs']['pk']
        order = Order.objects.get(id=id)
        if order.address != serializer.validated_data['address']:
            geocode = geocoder(serializer.validated_data['address'])
            if geocode:
                lat = geocode.latitude
                lon = geocode.longitude
                serializer.save(latitude = lat, longitude = lon)
            else:
                raise serializers.ValidationError({'address':'Address could not be geocoded'})
        else:
            serializer.save()

    @action(detail=False,methods=['post'])
    def bulk_delete(self, *args, **kwargs):
        ids = self.request.data.get('ids',[])
        self.get_queryset().filter(id__in=ids).delete()
        return Response({'delete': True})

    @action(detail=False,methods=['post'])
    def bulk_update(self, *args, **kwargs):
        ids = self.request.data.get('id',[])
        queryset = self.get_queryset().filter(id__in=ids)
        queryset.update(**self.request.data.get('data',{}))
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True,methods=['post'])
    def remove_trip(self, request, pk=None):
        order = Order.objects.get(id=pk)
        trip = Trip.objects.get(id=order.trip.id)
        order.trip = None
        order.save()
        trip.recalculate()
        serializer = self.serializer_class(order)
        return Response(serializer.data)

class DriverViewSet(viewsets.ModelViewSet):
    serializer_class = DriverSerializer
    filterset_fields = "__all__"
    ordering_fields = "__all__"

    def get_queryset(self):
        return Driver.objects.filter(user = self.request.user).order_by('id')

    @action(detail=False,methods=['post'])
    def bulk_delete(self, *args, **kwargs):
        ids = self.request.data.get('ids',[])
        self.get_queryset().filter(id__in=ids).delete()
        return Response({'delete': True})

    def perform_create(self, serializer):
        geocode = geocoder(serializer.validated_data['address'])
        if geocode:
            lat = geocode.latitude
            lon = geocode.longitude
            serializer.save(user=self.request.user,latitude = lat, longitude = lon)
        else:
            raise serializers.ValidationError({'address':'Address could not be geocoded'})
    
    def perform_update(self, serializer):
        id = self.request.parser_context['kwargs']['pk']
        driver = Driver.objects.get(user = self.request.user,id=id)
        if driver.address != serializer.validated_data['address']:
            geocode = geocoder(serializer.validated_data['address'])
            if geocode:
                lat = geocode.latitude
                lon = geocode.longitude
                serializer.save(latitude = lat, longitude = lon)
            else:
                raise serializers.ValidationError({'address':'Address could not be geocoded'})
        else:
            serializer.save()

    @action(detail=True,methods=['post'])
    def send_mail(self, request, pk=None):
        driver = self.get_object()
        driver.notify("Your web app Link" , '')
        return Response({"sent":True})




class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    filterset_class = TripFilter
    ordering_fields = "__all__"

    def get_queryset(self):
        return Trip.objects.filter(user = self.request.user)


    @action(detail=True,methods=['post'])
    def driver_update(self, *args, **kwargs):
        driver = self.request.data.get("driver",None)
        self.get_queryset().filter(**kwargs).update(driver = Driver.objects.get(id=driver))
        return Response({'update': True})

    @action(detail=False,methods=['post'])
    def bulk_order_update(self, *args, **kwargs):
        id = self.request.data.get('id')
        queryset = self.get_queryset().get(id=id)
        queryset.order_set.all().update(**self.request.data.get('data',{}))
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)

    def create(self, request):
        orderIDs = request.data.get("orderIDs",[])
        driverIDs = request.data.get("driverIDs",[])
        indexes = request.data.get("indexes",{'distance_index':0.4 , 'duration_index':0.4 , 'worth_index':0.2})
        constraints =request.data.get("constraints",{'max_orders_per_driver':50})
        orders = Order.objects.filter(id__in = [o for o in orderIDs],status = 0)
        drivers = Driver.objects.filter(id__in = [d for d in driverIDs])
        result = dispatching_request(orders , drivers , constraints , indexes)
        trips = result['trips']
        res = []
        for t  in trips:
            driver = Driver.objects.get(id=t['driver']['identification'])
            trip = Trip.objects.create(user=self.request.user,total_duration = t['total_duration'] , total_distance = t['total_distance'] , start_time = t['start_time']
             , end_time = t['end_time'], polyline = t['polyline'],driver = driver , start_address = driver.address ,  start_latitude = driver.latitude , start_longitude = driver.longitude)
            res.append(trip)
            for o in t['orders']:
                order = Order.objects.get(id=o['identification'])
                order.trip = trip
                order.start_time = o['start_time']
                order.end_time = o['end_time']
                order.arrival_time   = o['arrival_time']
                order.stop_id = o['stop_id']
                order.status = 1
                order.duration = o['duration']
                order.distance = o['distance']
                order.save()   

        return Response({'data':self.serializer_class(res,many=True).data,"unassigned":len(result['unassigned_orders'])},status=200)  

    @action(detail=False,methods=['post'])
    def create_dispostion(self,*args,**kwargs):
        orderIDs = self.request.data.get("orderIDs",[])
        driverDetails = self.request.data.get("driverDetails",{})
        dimensions = driverDetails.get("driverDimension",None)
        geo = geocoder(driverDetails.get("startAddress",None))
        maxWeight = driverDetails.get("maxWeight",1600)
        if geo is None:
            raise serializers.ValidationError({'startAddress':'Address could not be geocoded'})
        start_latitude = geo.latitude
        start_longitude = geo.longitude
        startTime = driverDetails.get("startTime",timezone.now().timestamp())
        endTime = driverDetails.get("endTime",(timezone.now() + timedelta(hours=5)).timestamp())
        orders = Order.objects.filter(id__in = [o for o in orderIDs],status = 0)
        result = disposition_request(orders ,startTime , endTime ,start_latitude  , start_longitude ,dimensions,maxWeight)
        trips = result['trips']
        res = []
        for t  in trips:
            trip = Trip.objects.create(user=self.request.user,total_duration = t['total_duration'] , total_distance = t['total_distance'] , start_time = t['start_time']
             , end_time = t['end_time'], polyline = t['polyline'],start_address = geo.address ,  start_latitude = start_latitude , start_longitude = start_longitude)
            res.append(trip)
            for o in t['orders']:
                order = Order.objects.get(id=o['identification'])
                order.trip = trip
                order.start_time = o['start_time']
                order.end_time = o['end_time']
                order.arrival_time   = o['arrival_time']
                order.stop_id = o['stop_id']
                order.status = 1
                order.duration = o['duration']
                order.distance = o['distance']
                order.save()   

        return Response({'data':self.serializer_class(res,many=True).data},status=200)  
