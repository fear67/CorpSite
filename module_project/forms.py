from django import forms
from .models import News
from django import forms
from .models import CorpLife, EventPhoto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'text', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введите заголовок новости...'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Введите текст новости...',
                'rows': 8
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*'
            })
        }
        labels = {
            'title': 'Заголовок',
            'text': 'Текст новости',
            'image': 'Изображение'
        }


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # Валидируем каждый загруженный файл
        if not data:
            return []
        if isinstance(data, (list, tuple)):
            return [super().clean(d, initial) for d in data]
        return [super().clean(data, initial)]


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # Ключевой флаг, который убирает ошибку

# 2. ИСПОЛЬЗУЕМ ЕГО В ФОРМЕ
class EventCreateForm(forms.ModelForm):
    class Meta:
        model = CorpLife
        fields = ['title', 'text', 'date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название мероприятия'}),
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 6, 'placeholder': 'Описание...'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
        }



