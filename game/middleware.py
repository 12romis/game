from django.contrib.auth.models import User
from django.http import JsonResponse


class VerifyMobileUserMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            token = request.META['HTTP_AUTHORIZATION']
            user = User.objects.get(profile__token=token)
        except (KeyError, User.DoesNotExist):
            return JsonResponse({'errors': {'auth': ['Необхідна авторизація!']}}, status=401, safe=False)

        request.mobile_user = user
        return None
