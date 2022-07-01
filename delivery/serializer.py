from rest_framework import serializers
from .models import Order , Driver , Trip






class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'

class TripOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class TripSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only = True)
    orders = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = '__all__'

    def get_status(self,obj,*args,**kwargs):
        return obj.status

    def get_orders(self,obj,*args,**kwargs):
        return TripOrderSerializer(obj.order_set.all().order_by('stop_id'),many=True).data

class OrderSerializer(serializers.ModelSerializer):
    trip = TripSerializer(read_only = True)

    class Meta:
        model = Order
        fields = '__all__'

    