from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone

from .models import User, Task

import random

# register serializers

class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'phone_no', 'email', 'password', 'is_verified']
        extra_kwargs = {
            'password' :{'write_only':True},
            'username' :{'read_only':True}
        }
    
    def validate_email(self, value):
        valid_domains = ('@gmail.com')
        if not value:
            raise serializers.ValidationError("Email is required")
        if value and not value.endswith(valid_domains):
            raise serializers.ValidationError("Invalid email domain, accepted domain is gmail")
        return value

   
    def create(self, validated_data):
        email = validated_data.get('email', None)
        first_name = validated_data.get('first_name', '')
        username = f"{first_name.lower()}_{random.randint(1000, 99999)}"
        password = validated_data.pop('password',None)
        instance = self.Meta.model(username=username, **validated_data)
        if password is not None:
            instance.set_password(password)
        if len(password) <6:
            raise serializers.ValidationError("Enter a strong password, atleast 6 characters long")
        instance.save()
        return instance


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(username=obj['username'])
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'tokens']

    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        user = auth.authenticate(username=username, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'user': user,
            'username': user.username,
            'email': user.email,
            'tokens': user.tokens
        }

        return super().validate(attrs)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'user', 'title', 'description', 'priority', 'complete', 'completed_on', 'timestamp']

    def validate(self, data):
        if self.instance is None:  
            if 'title' not in data:
                raise serializers.ValidationError("Title is required when creating a task.")

        if ('user' in data):
            data['user'] = data.get('user')

        if ('title' in data) and data['title']=='':
            raise serializers.ValidationError("Title is required when creating a task.")
        elif ('title' in data):
            data['title'] = data.get('title')
            data['timestamp'] = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')

        if ('description' in data):
            data['description'] = data.get('description')
        if ('priority' in data):
            data['priority'] = data.get('priority', False)
        if ('complete' in data):
            data['complete'] = data.get('complete', False)
            data['completed_on'] = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')

        return data