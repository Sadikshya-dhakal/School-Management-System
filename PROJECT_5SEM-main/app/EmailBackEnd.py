from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            users = UserModel.objects.filter(email=username)
            for user in users:
                if user.check_password(password):
                    return user
            return None
        except UserModel.DoesNotExist:
            return None
