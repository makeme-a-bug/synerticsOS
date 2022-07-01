from django.urls import path , include
from . import views as vw

app_name = "excel"

urlpatterns = [
    path("import/",vw.importExcel , name="import"),
    path("fieldMapping/",vw.fieldMapping , name="fieldMapping"),
    path("addOrders/",vw.addDeliveries , name="addDeliveries"),
    path("update/",vw.correctData , name="update"),
]