from django import forms
from .models import Order , Driver
from django.forms import BoundField


class FieldSet(object):
    def __init__(self,form,fields,id,legend='',cls=None):
        self.form = form
        self.id = id
        self.legend = legend
        self.fields = fields
        self.cls = cls

    def __iter__(self):
        for name in self.fields:
            field = self.form.fields[name]
            yield BoundField(self.form, field, name)



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ["latitude",'longitude','status']
        widgets = {'address': forms.TextInput(attrs={
            'class': 'form-control',
            'autoComplete': True,
            }),
            'time_from':forms.TextInput(attrs={
            'type': 'datetime-local',
            'value':''
            }),
            'time_to':forms.TextInput(attrs={
            'type': 'datetime-local',
            }),
        }

class DriverForm(forms.ModelForm):
    class Meta:
        model =Driver
        exclude = ["latitude",'longitude']
        widgets = {'address': forms.TextInput(attrs={
            'class': 'form-control',
            'autoComplete': True,
            }),
        }




