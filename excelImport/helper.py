import os
import pandas as pd
import datetime

def cleanFolder(path):
    for file in get_files(path):
        c_time = os.path.getctime(f'{path}/{file}')
        dt_c = datetime.datetime.fromtimestamp(c_time)
        print(dt_c)
        if (datetime.datetime.now() - dt_c).days >= 1:
            os.remove(f'{path}/{file}')


def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def orderTypeCheck(value,error,field):

    if field in error:
        del error[field]
    if value is None or pd.isnull(value):
        return value , error
    if value == '1' or value.startswith('del') or value.startswith('DEL') or value.startswith('Del') or value.strip() == '' :
        return value , error
    elif value == '2' or value.startswith('pick') or value.startswith('PICK') or value.startswith('Pick') :
        return value , error
    else:
        error['order_type'] = 'invalid order type'
        return value , error

def orderTypeconverter(value):
    if value is None or pd.isnull(value):
        return 0
    if value == '1' or value.startswith('del') or value.startswith('DEL') or value.startswith('Del') :
        return 0 
    elif value == '2' or value.startswith('pick') or value.startswith('PICK') or value.startswith('Pick') :
        return 1 
    else:
        return 0