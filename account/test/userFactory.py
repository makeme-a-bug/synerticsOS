from faker import Faker as FakerClass
from typing import Any, Sequence
from factory import django, Faker, post_generation,PostGenerationMethodCall
from account.models import User



class UserFactory(django.DjangoModelFactory):

    def __init__(self, *args, **kwargs):
        self.password_raw = FakerClass().password()
        return super(UserFactory, self).__init__(*args, **kwargs)
    class Meta:
        model = User
    
    email = Faker('email')
    password = PostGenerationMethodCall('set_password', 'password')
    is_active = True


class AdminUserFactory(django.DjangoModelFactory):

    def __init__(self, *args, **kwargs):
        self.password_raw = FakerClass().password()
        return super(AdminUserFactory, self).__init__(*args, **kwargs)

    class Meta:
        model = User
    
    email = Faker('email')
    is_superuser = True
    is_staff = True
    is_active = True
    password = PostGenerationMethodCall('set_password', 'password')