from django.db import models
from django.core.validators import MinValueValidator,EmailValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db.models import Min
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.conf import settings


from rest_framework.exceptions import ValidationError as VE

from utils.helper import NanoID
from utils.requests import dispatching_request
from account.models import User

class OrderStatus(models.IntegerChoices):
    UNASSIGNED = 0, 'unassigned'
    ASSIGNED = 1, 'assigned'
    DEPLOYED = 2, 'deployed'
    COMPLETED = 3 ,'completed'


#this validation makes sure the unix time provided is not less than 1900-01-01
def UnixValidator(value):
    if value != 0 and value < 631152000:
        raise ValidationError("Ensure this value is greater than or equal to 631152000.")
    else:
        return value




class Geolocation(models.Model):
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    address = models.TextField()
    class Meta:
        abstract = True



class OrderQuerySet(models.QuerySet):


    def delete(self, *args, **kwargs):
        # throw error if any of orders in the queryset is completed
        if self.filter(status=OrderStatus.COMPLETED).exists():
            raise VE("Cannot delete completed orders.")

        # we are getting trips that are related to orders in the queryset. later to be re-evaluated    
        trips = []
        for obj in self:
            if obj.trip:
                trips.append(obj.trip.id)
        super(OrderQuerySet, self).delete(*args, **kwargs)

        
        trips = set(trips) # get unique trips
        trips = Trip.objects.filter(id__in = trips)
        for t in trips:
            if len(t.order_set.all()) == 0:
                t.delete()

    def update(self, *args, **kwargs):
        trips = []
        trip_status = []

        # we are getting trips and their statuses that are related to orders in the queryset. later to be re-evaluated
        for obj in self:
            if obj.trip:
                trips.append(obj.trip.id)
                trip_status.append(obj.trip.status)
        status_changed = [ o.id for o in self.filter(status__gte = 1)]
        super(OrderQuerySet, self).update(*args, **kwargs)

        # remove the trip from the order of their status changed to unassigned
        if (self.filter(id__in=status_changed,status=0).exists()):
            self.filter(id__in=status_changed,status=0).update(distance = 0 , duration =0 , arrival_time = 0 , end_time = 0 , start_time = 0 , trip = None , stop_id = 0 )

        # get unique trips
        trips = set(trips)
        trips = Trip.objects.filter(id__in = trips)
        for i,t in enumerate(trips):
            # delete empty trips
            if len(trips[i].order_set.all()) == 0:
                t.delete()
            else:
                # send mail to drivers if the status of the trips changed to delployed
                if trip_status[i] < OrderStatus.DEPLOYED and t.status == OrderStatus.DEPLOYED:
                    if t.driver:
                        t.driver.notify("Your trip has been deployed" , "<h5> You Trip has been deployed </h5>")


class TripQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        orders = []
        # order whose status will be changed to unassigned when trip is delted
        for obj in self:
            orders.extend([o.id for o in obj.order_set.all()])
        super(TripQuerySet, self).delete(*args, **kwargs)
        # here there status is changed to unassigned on condition that the orders are not completed
        Order.objects.filter(id__in = orders).update(distance = 0 , duration =0 , arrival_time = 0 , end_time = 0 , start_time = 0 , status=0)

        


class Order(Geolocation):
    user = models.ForeignKey(User,on_delete=models.CASCADE,editable=False)
    id = models.CharField(max_length=15, primary_key=True , unique = True , editable = False , default = NanoID)
    time_from = models.FloatField(default=0 , validators=[UnixValidator])
    time_to = models.FloatField(default=0, validators=[UnixValidator])
    weight = models.FloatField(default=0, validators=[MinValueValidator(0)])
    height = models.FloatField(default=0, validators=[MinValueValidator(0)])
    width = models.FloatField(default=0, validators=[MinValueValidator(0)])
    depth = models.FloatField(default=0, validators=[MinValueValidator(0)])
    order_type = models.IntegerField(default=0,choices=((0,'Delivery'),(1,'Pick up')), validators=[MinValueValidator(0)])
    buffer = models.FloatField(default=0, validators=[MinValueValidator(0)])
    status = models.IntegerField(default= OrderStatus.UNASSIGNED,choices=OrderStatus.choices, validators=[MinValueValidator(0)])
    trip = models.ForeignKey('Trip', null=True, on_delete=models.SET_NULL)
    duration = models.FloatField(default=0, validators=[MinValueValidator(0)])
    distance = models.FloatField(default=0, validators=[MinValueValidator(0)])
    arrival_time = models.FloatField(default=0, validators=[MinValueValidator(0)])
    start_time = models.FloatField(default=0)
    end_time = models.FloatField(default=0)
    stop_id = models.IntegerField(default=0, validators=[MinValueValidator(0)])


    #over-rides the save function to perform some pre save actions
    #1. make sures that completed orders status is not changed
    #2. if the status of order is changed to UNASSIGNED it is removed from a trip
    #3. watches the trip related to order to match sure empty trips are deleted
    def save(self, *args, **kwargs):
        # no action performed on newly created order
        if kwargs.get('force_insert', False):
            super(Order, self).save(*args, **kwargs)
        else:    
            prevStatus = Order.objects.get(id=self.id).status
            t = None
            if self.trip:
                #related trip to the order that will revalueated later to make sure if it is empty it will be delted
                t = Trip.objects.get(id=self.trip.id)
            else:
                # makes sure that is the order is not assigned to a trip it remains unassigned
                self.status = OrderStatus.UNASSIGNED


            # stops updating status of completed orders
            if prevStatus == OrderStatus.COMPLETED:
                self.status = OrderStatus.COMPLETED

                
            super(Order, self).save(*args, **kwargs)

            # here we check if the status of order is changed to unassigned we remove the related trip from it
            if prevStatus != OrderStatus.UNASSIGNED and self.status == OrderStatus.UNASSIGNED:
                self.trip = None
                self.start_time = 0
                self.end_time = 0
                self.arrival_time   = 0
                self.stop_id = 0
                self.duration = 0
                self.distance = 0
                self.save()
            if t:
                # re-evaluation of the trip. if it is empty it is delted
                if len(t.order_set.all()) == 0:
                        t.delete()
    #over-rides the delete function to make sure the completed orders can't be deleted
    def delete(self, *args, **kwards):
        if self.status == OrderStatus.COMPLETED:
            raise VE("Cannot delete completed order")
        super(Order, self).delete(*args, **kwards)

    objects = OrderQuerySet.as_manager()

class Driver(Geolocation):
    user = models.ForeignKey(User,on_delete=models.CASCADE,editable=False)
    id = models.CharField(max_length=15, primary_key=True , unique = True , editable = False , default = NanoID)
    max_weight = models.FloatField(default=0, validators=[MinValueValidator(0)])
    height = models.FloatField(default=0, validators=[MinValueValidator(0)])
    width = models.FloatField(default=0, validators=[MinValueValidator(0)])
    depth = models.FloatField(default=0, validators=[MinValueValidator(0)])
    email = models.EmailField(validators=[EmailValidator])
    name = models.CharField(max_length=250)

    #send email to the drivers with the link to web app
    def notify(self,subject, message , *args, **kwargs):
        driver = self
        url = settings.CURRENT_SITE+reverse("delivery:driver_trips", kwargs={'id':driver.id})
        from_email, to = settings.EMAIL_HOST_USER, driver.email
        html_content = message + "<p> Your web app link is below:</p> <a href='" + url + "'>Click here to view your trips</a>"
        msg = EmailMultiAlternatives(subject,"" , from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class Trip(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,editable=False)
    id = models.CharField(max_length=15, primary_key=True , unique = True , editable = False , default = NanoID)
    start_address  = models.TextField()
    start_latitude = models.FloatField(default=0)
    start_longitude = models.FloatField(default=0)
    driver = models.ForeignKey(Driver , on_delete=models.SET_NULL , null=True)
    total_distance = models.FloatField(default=0)
    total_duration = models.FloatField(default=0)
    start_time = models.FloatField(default=0)
    end_time = models.FloatField(default=0)
    polyline = models.TextField(default="")
    distance_index = models.FloatField(default=0.5)
    duration_index = models.FloatField(default=0.5)
    worth_index = models.FloatField(default=0)
    driver = models.ForeignKey(Driver , on_delete=models.SET_NULL , null=True)

    @property
    def status(self):
        return self.order_set.aggregate(min_status=Min('status'))['min_status']

    objects = TripQuerySet.as_manager()

    #re-calcuate the trip 
    def recalculate(self,*args,**kwargs):
        orders = self.order_set.all()
        constraints = {"max_orders_per_driver":50 , 'start_time':self.start_time}
        indexes = {"distance_index":self.distance_index, 'duration_index':self.duration_index, "worth_index":self.worth_index}
        result = dispatching_request(orders , [] , constraints , indexes,latitude = self.start_latitude, longitude = self.start_longitude , update=True)
        trips = result['trips']
        for t  in trips:
            self.total_duration,self.total_distance,self.start_time,self.end_time,self.polyline = t['total_duration'] ,t['total_distance'] ,t['start_time'],t['end_time'],t['polyline']
            for o in t['orders']:
                order = Order.objects.get(id=o['identification'])
                order.trip = self
                order.start_time = o['start_time']
                order.end_time = o['end_time']
                order.arrival_time   = o['arrival_time']
                order.stop_id = o['stop_id']
                order.status = 1
                order.duration = o['duration']
                order.distance = o['distance']
                order.save()

    #over-rides the delete function because it tries to change the status of orders related to deleted trips to UNASSIGNED
    def delete(self, *args, **kwargs):
        orders = [o.id for o in self.order_set.all()]
        super(Trip, self).delete(*args, **kwargs)
        queryset = Order.objects.filter(id__in = orders)
        if len(queryset) > 0:
            #exclude here remove the orders that are completed to be changed when deleting the trip
            queryset.exclude(status=OrderStatus.COMPLETED).update(distance = 0 , duration =0 , arrival_time = 0 , end_time = 0 , start_time = 0 , status=0 , stop_id = 0)




