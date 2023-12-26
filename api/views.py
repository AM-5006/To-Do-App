from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404

from rest_framework_simplejwt.tokens import RefreshToken

import jwt

from .models import User, Task
from .serializers import UserSerializers, EmailVerificationSerializer, UserLoginSerializer, TaskSerializer
from .utils import Utils

# Create your views here.

class Register(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializers

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(username=user_data['username'])
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        data = {
            'email_body': render_to_string('extras/confirmation_email.html', {'user': user.username, 'absurl': absurl}),
            'to_email': user.email,
            'email_subject': 'Verify your email',
            'token': token,
        }
        Utils.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)


class GenerateActivationLinkView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')  
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response({'error': 'User is already verified.'}, status=400)
            token = RefreshToken.for_user(user).access_token
            current_site = get_current_site(request).domain
            relative_link = reverse('email-verify') 
            abs_url = f'http://{current_site}{relative_link}?token={token}'

            email_body = render_to_string('extras/confirmation_email.html', {'user': user.username, 'absurl': abs_url})
            data = {
                'email_body': email_body,
                'to_email': user.email,
                'email_subject': 'Verify your email',
                'token': token,
            }
            Utils.send_email(data)
            return Response({'email': user.email}, status=200)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)


class VerifyEmail(View):
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], type=jwt)
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return HttpResponseRedirect(reverse('signin'))
        except jwt.ExpiredSignatureError as identifier:
            return HttpResponseRedirect(reverse('activation-expired'))
        except jwt.exceptions.DecodeError as identifier:
            return render(request, 'invalid_token.html')

class Login(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        login(request, serializer.validated_data['user'])
        return Response(serializer.data, status=status.HTTP_200_OK)


class Profile(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializers

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.request.user,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class TaskView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def post(self, request):
        request.data['user'] = request.user.id
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        filter_by = request.GET.get('filter', '')
        order = request.GET.get('order', '')
        tasks = None
        if filter_by=='':
            tasks = self.queryset.filter(user=request.user, complete=False)
        elif filter_by=='HP':
            tasks = self.queryset.filter(user=request.user, priority=True, complete=False)
        elif filter_by=='LP':
            tasks = self.queryset.filter(user=request.user, priority=False, complete=False)
        elif filter_by=='CT':
            tasks = self.queryset.filter(user=request.user, complete=True)
        elif filter_by=='ALL':
            tasks = self.queryset.filter(user=request.user)

        if (tasks is not None) and (order=='' or order=='LST'):
            tasks = tasks.order_by('timestamp')
        elif (tasks is not None) and order=='OLD':
            tasks = tasks.order_by('-timestamp')
        elif (tasks is not None) and order=='REC':
            tasks = self.queryset.filter(user=request.user, complete=True).order_by('completed_on')[:3]

        serializer = self.serializer_class(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        task = self.queryset.get(id=pk)
        request.data['complete'] = True
        serailizer = self.serializer_class(task, data=request.data, partial=True)
        serailizer.is_valid()
        serailizer.save()
        return Response(serailizer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            task = self.queryset.get(id=pk)
            if not task.complete:
                return Response({"detail": "Need to complete the task before deleting"}, status=status.HTTP_404_NOT_FOUND)
        except Task.DoesNotExist:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        task.delete()
        return Response({"detail": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT)