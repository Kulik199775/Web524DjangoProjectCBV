from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm

from users.models import User
from users.validators import validate_password


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class UserForm(StyleFormMixin,forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')
        # exclude = ('is_active',)

class UserRegisterForm(StyleFormMixin, UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        cleaned_data = self.cleaned_data
        validate_password(cleaned_data['password1'])
        if cleaned_data['password1'] != cleaned_data['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cleaned_data['password2']

class UserLoginForm(StyleFormMixin, forms.Form):
    email = forms.EmailField(label='email')
    password = forms.CharField(label='пароль', widget=forms.PasswordInput)

class UserUpdateForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'telegram', 'avatar')

class UserChangePasswordForm(StyleFormMixin, PasswordChangeForm):
    pass


