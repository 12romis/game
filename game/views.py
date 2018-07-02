import datetime

import logging
from django.contrib.auth.models import User
import json

from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.utils.crypto import get_random_string
from django.utils.decorators import decorator_from_middleware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from game.forms import LoginForm, SignUpForm, ProfileForm
from game.middleware import VerifyMobileUserMiddleware
from game.models import Profile, Codes, Results

logger = logging.getLogger('info')

@csrf_exempt
def login(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        if user is not None and user.check_password(password):
            return JsonResponse(user.profile.get_profile_dict(user),
                                content_type="application/json")
        else:
            return JsonResponse({'errors': {'email': ['Email або ж пароль не вірний!']}}, status=401)
    else:
        return JsonResponse(form.errors, content_type="application/json",
                            status=400, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def signup(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        form.cleaned_data['username'] = form.cleaned_data.get('email')
        user = User.objects.create(**form.cleaned_data)
        user.set_password(form.cleaned_data.get('password'))
        user.profile = Profile()
        user.profile.token = get_random_string(length=32)
        user.profile.save()
        user.save()
        dic = {
            'token': user.profile.token,
            'email': user.email,
        }
        return JsonResponse(dic, content_type="application/json", safe=False)
    else:
        return JsonResponse({'errors': form.errors}, content_type="application/json", status=400, safe=False)


@csrf_exempt
@decorator_from_middleware(VerifyMobileUserMiddleware)
def profile(request):
    user = request.mobile_user

    if request.method == 'POST':
        logger.info(request.FILES)
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user.last_name = form.cleaned_data.get('fullname')
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.photo = form.cleaned_data.get('photo')
            user.profile.save()
            user.save()
        else:
            return JsonResponse({'errors': form.errors}, content_type="application/json", status=400, safe=False)
    # serializers.serialize('json', [x.profile for x in users])
    return JsonResponse(user.profile.get_profile_dict(user), content_type="application/json")


@csrf_exempt
@decorator_from_middleware(VerifyMobileUserMiddleware)
def check_code(request):
    code = request.GET.get('code', '')
    if Codes.objects.filter(code=code, user=None).exists():
        db_code = Codes.objects.filter(code=code, user=None)[0]
        user = request.mobile_user
        user.profile.attempts += db_code.attempts
        user.profile.save()
        Codes.objects.filter(code=code).update(user=user)
        return JsonResponse(user.profile.get_profile_dict(user), status=200,
                            content_type="application/json")
    else:
        return JsonResponse({'errors': {'code': ['Ви ввели не вірний або уже використаний код!']}}, status=400,
                            content_type="application/json")


@csrf_exempt
@decorator_from_middleware(VerifyMobileUserMiddleware)
def set_score(request):
    try:
        score = int(request.GET.get('score', 0))
    except ValueError:
        return JsonResponse({'errors': {'score': ['Повинне бути валідне число!']}}, status=400,
                            content_type="application/json")
    user = request.mobile_user
    if user.profile.attempts > 0:
        Results.objects.create(user=user, score=score)
        user.profile.attempts -= 1
        user.profile.attempts_used += 1
        user.profile.save()
        return JsonResponse(user.profile.get_profile_dict(user), status=200,
                            content_type="application/json")
    else:
        return JsonResponse({'errors': {'attempts': ['Кількість спроб вичерпано!']}}, status=400,
                            content_type="application/json")


@csrf_exempt
@decorator_from_middleware(VerifyMobileUserMiddleware)
def get_rating(request):
    rating_count = 3
    user = request.mobile_user
    today = datetime.date.today()
    monday_date = today + datetime.timedelta(days=-today.weekday())
    sunday_date = monday_date + datetime.timedelta(days=6)

    rating = Results.objects.filter(
        created_at__gte=monday_date,
        created_at__lte=sunday_date
        ) \
        .select_related('user__profile') \
        .values('user__email', 'user__last_name', 'user__profile__photo') \
        .annotate(total=Sum('score')) \
        .order_by('-total')

    try:
        u_index = list(rating.values_list('user__email', flat=True)).index(user.email)
    except:
        u_index = 0

    if u_index >= rating_count + 2:
        # index = u_index if u_index == rating_count else u_index - 1
        r_list = Results.write_res_to_list(rating, 1, 0, 3)
        r_list += Results.write_res_to_list(rating, u_index+1, u_index-1, u_index+1)
    else:
        r_list = Results.write_res_to_list(rating, 1, 0, 6)

    return JsonResponse(r_list, status=200,
                        content_type="application/json", safe=False)


#data = serializers.serialize('json', objectQuerySet, fields=('fileName','id'))

