from django.contrib.auth import login, logout, user_logged_in, user_logged_out
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from djoser.conf import settings


def encode_uid(pk):
    return force_text(urlsafe_base64_encode(force_bytes(pk)))


def decode_uid(pk):
    return force_text(urlsafe_base64_decode(pk))


def login_user(request, user):
    token, _ = settings.TOKEN_MODEL.objects.get_or_create(user=user)
    if settings.CREATE_SESSION_ON_LOGIN:
        login(request, user)

        # Because we've logged in the user this has now changed
        # the activation token so we need to save a new one.
        # if user.is_validated is False:
        #     token = default_token_generator.make_token(user)
        #     user.activation_token = token
        #     user.save()
    user_logged_in.send(sender=user.__class__, request=request, user=user)
    return token


def logout_user(request):
    if settings.TOKEN_MODEL:
        settings.TOKEN_MODEL.objects.filter(user=request.user).delete()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
        )
    if settings.CREATE_SESSION_ON_LOGIN:
        logout(request)


class ActionViewMixin(object):
    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)
