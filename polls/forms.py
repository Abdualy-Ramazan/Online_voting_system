from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import formset_factory, BaseFormSet
from django.utils import timezone
from .models import Poll, Profile, Rating


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email уже зарегистрирован.")
        return email


class PollCreateForm(forms.ModelForm):
    allow_multiple_choices = forms.BooleanField(
        label='Разрешить выбор нескольких вариантов?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Poll
        fields = ['question', 'end_date', 'allow_multiple_choices', 'image']
        widgets = {
            'question': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите вопрос опроса'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if end_date and end_date <= timezone.now():
            raise forms.ValidationError("Дата окончания должна быть позже текущего времени.")
        return end_date


class ChoiceForm(forms.Form):
    choice_text = forms.CharField(
        label='Вариант ответа',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите вариант ответа'
        }),
        required=False
    )

    def clean_choice_text(self):
        text = self.cleaned_data.get('choice_text', '').strip()
        if text.lower() in ['да', 'нет']:
            return text
        if text and len(text) < 3:
            raise forms.ValidationError("Вариант ответа должен содержать минимум 3 символа.")
        return text


ChoiceFormSet = formset_factory(
    ChoiceForm,
    extra=2,
    can_delete=True,
)


class AvatarUploadForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Размер аватара не должен превышать 2MB.")
            if not avatar.content_type.startswith('image/'):
                raise forms.ValidationError("Файл должен быть изображением.")
        return avatar


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating_value', 'comment']
        widgets = {
            'rating_value': forms.Select(choices=[(i, str(i)) for i in range(1, 6)], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Комментарий (необязательно)'}),
        }