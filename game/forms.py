from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password = forms.CharField(required=True)

    class Meta:
        model = User


class SignUpForm(forms.Form):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password = forms.CharField(required=True, min_length=6)

    class Meta:
        model = User

    def clean_email(self):
        email = self.data.get('email')
        exist = User.objects.filter(email=email).exists()
        if exist:
            raise forms.ValidationError("Email повинен бути унікальним!")
        return email


class ProfileForm(forms.Form):
    fullname = forms.CharField(max_length=250, required=True)
    birth_date = forms.IntegerField(required=True, max_value=2147483647)
    phone = forms.CharField(max_length=50, required=True)
    photo = forms.ImageField(required=False)

    class Meta:
        model = User


class AddGameCodesForm(forms.ModelForm):
    file = forms.FileField(required=True, help_text='Виберіть файл в форматі csv')
    attempts = forms.IntegerField(required=True, help_text='Кількість спроб від одноко коду')

    def clean_file(self):
        file = self.cleaned_data.get('file')
        filename = file.name
        if not filename.endswith('.csv'):
            raise forms.ValidationError("Файл повинен бути в форматі csv!")
        return file
