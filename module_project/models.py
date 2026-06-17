# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from multiupload.fields import MultiFileField
from galleryfield.fields import GalleryField
# ==================== СПРАВОЧНИКИ ====================


class Post(models.Model):
    """Должности"""
    name = models.CharField(max_length=100, verbose_name="Название должности")
    
    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
    
    def __str__(self):
        return self.name


class Group(models.Model):
    """Группы/отделы """
    name = models.CharField(max_length=100, verbose_name="Название группы")
    
    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
    
    def __str__(self):
        return self.name


class Place(models.Model):
    """Места/локации """
    name = models.CharField(max_length=100, verbose_name="Название места")
    
    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
    
    def __str__(self):
        return self.name


# ==================== ОСНОВНЫЕ ТАБЛИЦЫ ====================

class Workplace(models.Model):
    """Рабочие места"""
    name = models.CharField(max_length=100, verbose_name="Название рабочего места", null=True, blank=True)
    group = models.ForeignKey(
        Group, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Группа"
    )
    place = models.ForeignKey(
        Place, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Место"
    )
    timework = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Рабочее время"
    )
    phone_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Некорректный номер телефона")],
        verbose_name="Телефон"
    )
    address = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Адрес"
    )
    
    class Meta:
        verbose_name = "Рабочее место"
        verbose_name_plural = "Рабочие места"
    
    def __str__(self):
        return self.name


class Profile(models.Model):
    """Расширение стандартного пользователя Django"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile', 
        verbose_name="Пользователь"
    )
    
    # Личные данные
    phone_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        verbose_name="Номер телефона"
    )
    firstname = models.CharField(max_length=100, null=True, blank=True, verbose_name="Имя")
    lastname = models.CharField(max_length=100, null=True, blank=True, verbose_name="Фамилия")
    patronumic = models.CharField(max_length=100, null=True, blank=True, verbose_name="Отчество")
    create_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    # Фото
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True, 
        verbose_name="Фото профиля"
    )
    
    # Связи (роль удалили!)
    workplace = models.ForeignKey(
        Workplace, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Рабочее место"
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Должность"
    )
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        full_name = f"{self.lastname or ''} {self.firstname or ''} {self.patronumic or ''}".strip()
        if full_name:
            return f"{full_name} ({self.user.username})"
        return self.user.username
    
    @property
    def full_name(self):
        return f"{self.lastname or ''} {self.firstname or ''} {self.patronumic or ''}".strip()
    
    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/CorpSiteProject/images/default_avatar.png'


# ==================== КОНТЕНТНЫЕ ТАБЛИЦЫ ====================

class News(models.Model):
    """Новости (таблица из диаграммы + добавлен автор)"""
    title = models.CharField(
        max_length=200, 
        verbose_name="Заголовок"
    )
    text = models.TextField(
        verbose_name="Текст новости"
    )
    image = models.ImageField(
        upload_to='news/', 
        null=True, 
        blank=True,
        verbose_name="Изображение"
    )
    date = models.DateTimeField(
        auto_now_add=True,  # Автоматическая дата создания
        verbose_name="Дата публикации"
    )
    # !!! ВАЖНО: добавил автора (это критично для сайта)
    author = models.ForeignKey(
        Profile, 
        on_delete=models.SET_NULL,  # Если автора удалят, новость останется
        null=True, 
        blank=True, 
        verbose_name="Автор"
    )
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-date']  # Сортировка от новых к старым
    
    def __str__(self):
        return self.title


class CorpLife(models.Model):
    """Мероприятие корпоративной жизни"""
    title = models.CharField(max_length=200, verbose_name="Название мероприятия")
    text = models.TextField(verbose_name="Описание")
    date = models.DateTimeField(verbose_name="Дата проведения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания записи")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='events', verbose_name="Автор")
    
    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ['-date']
    
    def __str__(self):
        return self.title

class EventPhoto(models.Model):
    """Фотографии мероприятия"""
    event = models.ForeignKey(CorpLife, on_delete=models.CASCADE, related_name='photos', verbose_name="Мероприятие")
    image = models.ImageField(upload_to='corplife/%Y/%m/', verbose_name="Фото")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Подпись")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    
    class Meta:
        verbose_name = "Фото мероприятия"
        verbose_name_plural = "Фотографии мероприятия"
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"Фото для {self.event.title}"