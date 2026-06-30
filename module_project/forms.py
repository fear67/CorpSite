from django import forms
from .models import News
from .models import CorpLife, EventPhoto, Project
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Workplace, Post


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
    allow_multiple_selected = True 

class EventCreateForm(forms.ModelForm):
    class Meta:
        model = CorpLife
        fields = ['title', 'text', 'date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название мероприятия'}),
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 6, 'placeholder': 'Описание...'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
        }


class EventPhotoForm(forms.ModelForm):
    class Meta:
        model = EventPhoto
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Подпись к фото (необязательно)'
            })
        }
        labels = {
            'image': 'Фото',
            'caption': 'Подпись'
        }

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=False, label='Email')
    phone_number = forms.CharField(max_length=20, required=False, label='Номер телефона')
    firstname = forms.CharField(max_length=100, required=False, label='Имя')
    lastname = forms.CharField(max_length=100, required=False, label='Фамилия')
    patronumic = forms.CharField(max_length=100, required=False, label='Отчество')
    workplace = forms.ModelChoiceField(
        queryset=Workplace.objects.all(),
        required=False,
        label='Рабочее место'
    )
    post = forms.ModelChoiceField(
        queryset=Post.objects.all(),
        required=False,
        label='Должность'
    )
    is_staff = forms.BooleanField(required=False, label='Администратор')
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'is_active' in self.fields:
            del self.fields['is_active']
        self.instance.is_active = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.email = self.cleaned_data.get('email', '')
        user.is_staff = self.cleaned_data.get('is_staff', False)
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number', ''),
                firstname=self.cleaned_data.get('firstname', ''),
                lastname=self.cleaned_data.get('lastname', ''),
                patronumic=self.cleaned_data.get('patronumic', ''),
                workplace=self.cleaned_data.get('workplace'),
                post=self.cleaned_data.get('post'),
            )
        return user


class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=False, label='Email')
    phone_number = forms.CharField(max_length=20, required=False, label='Номер телефона')
    firstname = forms.CharField(max_length=100, required=False, label='Имя')
    lastname = forms.CharField(max_length=100, required=False, label='Фамилия')
    patronumic = forms.CharField(max_length=100, required=False, label='Отчество')
    workplace = forms.ModelChoiceField(
        queryset=Workplace.objects.all(),
        required=False,
        label='Рабочее место'
    )
    post = forms.ModelChoiceField(
        queryset=Post.objects.all(),
        required=False,
        label='Должность'
    )
    is_staff = forms.BooleanField(required=False, label='Администратор')
    is_active = forms.BooleanField(required=False, label='Активен')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            try:
                profile = self.instance.profile
                self.fields['phone_number'].initial = profile.phone_number
                self.fields['firstname'].initial = profile.firstname
                self.fields['lastname'].initial = profile.lastname
                self.fields['patronumic'].initial = profile.patronumic
                self.fields['workplace'].initial = profile.workplace
                self.fields['post'].initial = profile.post
            except Profile.DoesNotExist:
                pass
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.firstname = self.cleaned_data.get('firstname', '')
            profile.lastname = self.cleaned_data.get('lastname', '')
            profile.patronumic = self.cleaned_data.get('patronumic', '')
            profile.workplace = self.cleaned_data.get('workplace')
            profile.post = self.cleaned_data.get('post')
            profile.save()
        return user


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название проекта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание проекта (необязательно)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }
        labels = {
            'name': 'Название проекта',
            'description': 'Описание',
            'is_active': 'Проект активен',
        }