import datetime
import socket

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from django.db.models import Count, Sum
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe

from spila import settings


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(verbose_name='Фото профілю', upload_to='avatars', default='avatars/default.jpeg')
    attempts = models.IntegerField(verbose_name='Attempts of user', default=2)
    attempts_used = models.IntegerField(verbose_name='Used attempts by user', default=0)
    phone = models.CharField(verbose_name='Phone', max_length=50, default='')
    token = models.CharField(max_length=100, default=get_random_string(length=32))
    birth_date = models.IntegerField(default=1518523227)

    def __str__(self):
        return self.user.username

    def photo_tag(self):
        return mark_safe('<img src="%s" width="150" height="150" />' % (settings.MEDIA_URL + str(self.photo.url)))
    photo_tag.allow_tags = True

    def get_profile_dict(self, user):
        today = datetime.date.today()
        monday_date = today + datetime.timedelta(days=-today.weekday())
        sunday_date = today + datetime.timedelta(days=6)
        scores = Results.objects.filter(
                    user=user,
                    created_at__gte=monday_date,
                    created_at__lte=sunday_date
                ).aggregate(Sum('score'))['score__sum']
        return {
                'fullname': user.last_name,
                'email': user.email,
                'profile__attempts': user.profile.attempts,
                'profile__attempts_used': user.profile.attempts_used,
                'profile__photo': settings.MEDIA_ABSOLUTE_URL + str(user.profile.photo),
                'profile__phone': user.profile.phone,
                'profile__token': user.profile.token,
                'profile__birth_date': user.profile.birth_date,
                'scores': scores if scores else 0
            }


class Codes(models.Model):
    code = models.CharField(verbose_name='Код', max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name='Використано користувачем')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавлення коду')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата використання коду')
    attempts = models.IntegerField(verbose_name='Кількість спроб від цього коду', default=1)

    class Meta:
        verbose_name_plural = 'Коди'
        verbose_name = 'Код'

    def __str__(self):
        return self.code


class Results(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Гравець')
    score = models.IntegerField(verbose_name='Набрані очки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата гри')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Очки'
        verbose_name = 'рейтинг'

    @staticmethod
    def write_res_to_list(items, index, start, end):
        r_list = []
        for r in items[start:end]:
            r_list.append({
                'position': index,
                'email': r['user__email'],
                'fullname': r['user__last_name'],
                'total': r['total'],
                'profile__photo': settings.MEDIA_ABSOLUTE_URL + str(r['user__profile__photo']),
            })
            index += 1
        return r_list

