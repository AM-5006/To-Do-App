from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        # Check if the username is an email address
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}

        try:
            user = UserModel.objects.get(**kwargs)

            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
