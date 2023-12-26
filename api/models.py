from django.db import models
from django.contrib.auth.models import AbstractUser,PermissionsMixin
from django.utils.translation import gettext_lazy  as _
from django.contrib.auth.models import User

from rest_framework_simplejwt.tokens import RefreshToken

from .managers import CustomUserManager
# Create your models here.


AUTH_PROVIDERS = {'email': 'email', 'username':'username'}
class User(AbstractUser):
    username = models.CharField(_('username'), max_length=100, unique=True, blank=False)
    email = models.EmailField(_('email address'), unique=True, blank=True)
    phone_no = models.CharField(unique=True,  null=True,max_length=10)
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('username'))
    is_verified = models.BooleanField(default=False)
    objects = CustomUserManager() 
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=200)
    priority = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    completed_on = models.DateTimeField(null=True, blank=True)   
    timestamp =  models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title+'-'+str(self.user)