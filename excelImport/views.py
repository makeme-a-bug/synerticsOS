import time
from django.http import JsonResponse
from django.shortcuts import render , redirect
from django.urls import reverse
from django.http import HttpResponse, Http404
from django.conf import settings

from .models import ExcelFile
from utils.helper import read_file , timeCorrection , positiveValue,geocoder , NanoID
from delivery.models import Order
from .helper import cleanFolder , orderTypeCheck , orderTypeconverter

import pandas as pd
import numpy as np
import dateutil.parser as parser
import json
import datetime
import os
import pytz



def importExcel(request):
    if request.method == 'POST':
        file = request.FILES['file']
        file = ExcelFile.objects.create(file=file)
        err , df = read_file(file)
        if err:
            return JsonResponse({'success':False},status=500)        
        request.session['fileId'] = file.id      
        return JsonResponse({'success':True},status=200)
    return render(request, 'excelImport/importExcel.html')




def fieldMapping(request,*args,**kwargs):
    if request.method == 'POST':
        geocoded = bool(request.POST.get('geocoded',None))
        data = dict( (v,k) for k , v in request.POST.items())
        file = ExcelFile.objects.get(id= request.session['fileId'])
        err , df = read_file(file)
        if not geocoded:
            df['gcode'] = df[data['address']].apply(geocoder)
            df['lat'] = [g.latitude if g != None else 0 for g in df.gcode]
            df['long'] = [g.longitude if g != None else 0 for g in df.gcode]
            data['lat'] = 'lat'
            data['lon'] = 'long'
        df['error'] = None
        orders = []
        for ID , order in df.iterrows():
            order['error'] = {}
            if order[data.get('lat','lat')] == 0:
                order['error']['address'] = 'Address could not be geocoded'

            timeFrom = str(order.get(data.get('timeFrom',None),None))
            timeTo = str(order.get(data.get('timeTo',None),None))

            if not pd.isnull(timeFrom) and timeFrom != 'NaT' and timeFrom != '':
                timeFrom , order['error'] = timeCorrection(timeFrom , order['error'] , 'timeFrom')
            else:
                timeFrom = ''
            if not pd.isnull(timeTo) and timeTo != 'NaT' and timeTo != '':
                timeTo , order['error'] = timeCorrection(timeTo,order['error'], 'timeTo')
            else:
                timeTo = ''

            weight , order['error'] = positiveValue(order.get(data.get('weight',None),None),order['error'],'weight')
            height , order['error'] = positiveValue(order.get(data.get('height',None),None),order['error'],'height')
            width , order['error'] = positiveValue(order.get(data.get('width',None),None),order['error'],'width')
            depth , order['error'] = positiveValue(order.get(data.get('depth',None),None),order['error'],'depth')
            orderType , order['error'] = orderTypeCheck(order.get(data.get('orderType',None),None),order['error'],'order_type')
            buffer , order['error'] = positiveValue(order.get(data.get('buffer',None),None),order['error'],'buffer')


            orders.append({
                'ID':ID,
                'address':order[data['address']],
                'latitude':order[data['lat']],
                'longitude':order[data['lon']],
                'buffer':buffer,
                'weight':weight,
                'depth':depth,
                'height':height,
                'width':width,
                'time_to':timeTo if timeTo else None,
                'time_from':timeFrom if timeFrom else None,
                'order_type':orderType,
                'error':json.dumps(order.get('error',None))
            })

        new_df = pd.DataFrame(orders)
        fileId = NanoID()
        new_df.to_csv(f'temp/{fileId}_orders.csv',index=False)
        request.session['csvfileId'] = fileId
        return redirect('excel:addDeliveries')
    file = ExcelFile.objects.get(id= request.session['fileId'])
    err , df = read_file(file)
    df = df[list(df.columns)].fillna('None')
    return render(request, 'excelImport/fieldMapping.html',{'columns':df.columns , 'data':df.head(5).to_dict(orient='records')})
    

def addDeliveries(request):

    df = pd.read_csv(f'temp/{request.session["csvfileId"]}_orders.csv')
    if request.method == 'POST': 
        df['error'] = df['error'].apply(json.loads)
        df['errorLen'] = df['error'].apply(len)
        if not df.loc[df['errorLen'] > 0,'error'].empty:
            return render(request, 'excelImport/deliveries.html',{'data':pd.read_csv(f'temp/{request.session["csvfileId"]}_orders.csv').to_json(orient='records'), 'error':'There are still some invalid fields please correct them'})

        df['time_from'] = df['time_from'].apply(lambda x: parser.parse(x).replace(tzinfo=pytz.utc).timestamp() if not pd.isnull(x) else 0)
        df['time_to'] = df['time_to'].apply(lambda x: parser.parse(x).replace(tzinfo=pytz.utc).timestamp() if not pd.isnull(x) else 0)
        df['order_type'] = df['order_type'].apply(orderTypeconverter)
        df = df[['time_from','time_to','address','latitude','longitude','buffer','weight','depth','height','width','order_type']]
        for _ , order in df.iterrows():
            order = Order.objects.create(user=request.user,**order)
        
        cleanFolder('temp/')
        return redirect('delivery:deliveries')

    return render(request, 'excelImport/deliveries.html',{'data':df.to_json(orient='records')})

def correctData(request):
    if request.method == 'POST':
        df = pd.read_csv(f'temp/{request.session["csvfileId"]}_orders.csv')
        value = request.POST.get('value',None)
        changed = request.POST.get('field',None)
        id = request.POST.get('id',None)
        error = json.loads(df.loc[df['ID'] == int(id),'error'].iloc[0])
        if changed == 'address':
            add = geocoder(value)
            if add:
                lat = add.latitude
                lon = add.longitude
                df.loc[df['ID'] == int(id) , 'latitude'] = lat
                df.loc[df['ID'] == int(id) , 'longitude'] = lon
                if 'address' in error:
                    del error['address']
            else:
                error['address'] =  "Address could not be geocoded"
                df.loc[df['ID'] == int(id) , 'latitude'] = 0
                df.loc[df['ID'] == int(id) , 'longitude'] = 0

        elif changed == 'time_to':
            value , error = timeCorrection(value , error , 'time_to')
            df.loc[df['ID'] == int(id) , 'timeTo'] = value

        elif changed == 'time_from':
            value , error = timeCorrection(value,error, 'time_from')
            df.loc[df['ID'] == int(id) , 'timeFrom'] = value
        
        elif changed == 'order_type':
            value , error = orderTypeCheck(value,error,changed)
            df.loc[df['ID'] == int(id) , 'order_type'] = value
        
        else:
            value , error = positiveValue(value,error,changed)
            df.loc[df['ID'] == int(id) , changed] = value               


        df.loc[df['ID'] == int(id) , changed] = value
        df.loc[df['ID'] == int(id),'error'] = json.dumps(error)
        
        df.to_csv(f'temp/{request.session["csvfileId"]}_orders.csv',index=False)
        return JsonResponse(df.loc[df['ID'] == int(id) , :].to_json(orient='records'),status=200 , safe=False)


def download_example(request):
    file_path = os.path.join(settings.BASE_DIR, 'Demo Deliveries.xlsx')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404