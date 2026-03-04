from datetime import datetime

from django import forms

from dogs.models import Dog
from users.forms import StyleFormMixin

class DogForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Dog
        # fields = '__all__'
        exclude = ('owner',)

    def clean_birth_date(self):
        cleaned_data = self.cleaned_data['birth_date']
        if cleaned_data:
            now_year = datetime.now().year
            if now_year - cleaned_data.year > 32:
                raise forms.ValidationError("Собака должна быть моложе 32 лет")
        return cleaned_data