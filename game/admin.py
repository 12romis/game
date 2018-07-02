import csv
import datetime
import os

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile
from django.db.models import Sum
from django import forms
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.urls import path
from game.forms import AddGameCodesForm
from spila import settings
from .models import Profile, Codes, Results
from django.core.files.storage import default_storage


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    exclude = ['birth_date', 'token', 'attempts', 'attempts_used']


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('avatar',
                    'username',
                    'email',
                    'last_name',
                    'is_staff',
                    'attempts',
                    'attempts_used',
                    'get_birth_date',)
    list_select_related = ('profile',)
    list_display_links = ('username',)
    fieldsets = (
        ('Personal info', {'fields': ('username', 'email', 'password', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    def get_birth_date(self, instance):
        date = datetime.datetime.fromtimestamp(instance.profile.birth_date)
        return date
    get_birth_date.short_description = 'Дата народження'

    def avatar(self, instance):
        return mark_safe('<img src="/media/%s" width="100" height="100" />' % str(instance.profile.photo))
    avatar.short_description = 'Фото профілю'

    def attempts(self, instance):
        return instance.profile.attempts
    attempts.short_description = 'Залишилось спроб'

    def attempts_used(self, instance):
        return instance.profile.attempts_used
    attempts_used.short_description = 'Використано спроб'


class GameCodesAdmin(admin.ModelAdmin):
    list_display = ('code', 'attempts', 'created_at', 'updated_at', 'user')
    list_select_related = ('user',)
    exclude = ('user', 'code')
    form = AddGameCodesForm
    list_display_links = None

    def save_model(self, request, obj, form, change):
        data = form.cleaned_data.get('file')
        path = default_storage.save('tmp/' + str(data), ContentFile(data.read()))
        tmp_file_path = os.path.join(settings.MEDIA_ROOT, path)

        with open(tmp_file_path) as f:
            reader = csv.reader(f)
            created_num = 0
            for row in reader:
                try:
                    obj, created = Codes.objects.get_or_create(code=row[0],
                                                               defaults={
                                                                   'attempts': form.cleaned_data.get('attempts', 0)
                                                               })
                    if created:
                        created_num += 1
                except:
                    pass
            messages.success(request, 'Успішно добавлено {} унікальних коди.'.format(created_num))

        super(GameCodesAdmin, self).save_model(request, obj, form, change)

    # def has_change_permission(self, request, obj=None):
    #     return False


class GameResultsAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'created_at')
    list_display_links = None

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urlpatterns = [
            path('ratings', self.rating_view, name='rating_view'),
        ]
        return urlpatterns + super(GameResultsAdmin, self).get_urls()

    def rating_view(self, request):

        today = datetime.date.today()
        monday_date = today + datetime.timedelta(days=-today.weekday())
        sunday_date = monday_date + datetime.timedelta(days=6)
        try:
            start_date = Results.objects.order_by('created_at').values('created_at')[0]['created_at'] \
                .replace(hour=0, minute=0, second=0, microsecond=0)
            last_date = Results.objects.order_by('-created_at').values('created_at')[0]['created_at'] \
                .replace(hour=0, minute=0, second=0, microsecond=0)
            first_monday = start_date + datetime.timedelta(days=-start_date.weekday())
            last_sunday = last_date + datetime.timedelta(days=last_date.weekday() + 6)
        except:
            first_monday = monday_date
            last_sunday = sunday_date

        delta = last_sunday - first_monday
        game_dates = []
        try:
            week = int(request.GET.get('week', None))
        except TypeError:
            week = None
        for i in range(0, delta.days, 7):
            game_dates.append([
                first_monday + datetime.timedelta(days=i),
                first_monday + datetime.timedelta(days=i+6)
            ])
            if week == i/7:
                monday_date = first_monday + datetime.timedelta(days=i)
                sunday_date = first_monday + datetime.timedelta(days=i+6)

        results = Results.objects.filter(
                    created_at__gte=monday_date,
                    created_at__lte=sunday_date
                ) \
            .values('user__email') \
            .annotate(total=Sum('score'))\
            .order_by('-total')[:20]
        return render_to_response('admin/game/results/rating.html', {
            'items': results,
            'opts': self.model._meta,
            'game_dates': game_dates,
            'selected': week if week else len(game_dates) - 1
        })

    def total(self, instance):
        return instance.total


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Codes, GameCodesAdmin)
admin.site.register(Results, GameResultsAdmin)
