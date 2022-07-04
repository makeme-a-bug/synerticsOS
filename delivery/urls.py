from django.urls import path , include
from . import views
from rest_framework import routers

app_name = 'delivery'

router = routers.SimpleRouter()

urlpatterns = [
    path('orders/', views.orders , name='deliveries'),
    path('drivers/', views.drivers , name='drivers'),
    path('trips/', views.trips , name='trips'),
    path('driverTrips/<str:id>/', views.driver_trips , name='driver_trips'),
    path('driverTrips/<str:id>/<str:trip_id>/', views.driver_ind_trip , name='driver_ind_trip'),
]

router.register(r'order', views.OrderViewSet , basename = 'order')
router.register(r'driver', views.DriverViewSet, basename = 'driver')
router.register(r'trip', views.TripViewSet, basename = 'trip')


urlpatterns += router.urls

