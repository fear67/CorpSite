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
from django.utils import timezone
# ==================== СПРАВОЧНИКИ ====================


class Post(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название должности")
    
    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
    
    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название группы")
    
    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"
    
    def __str__(self):
        return self.name


class Place(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название места")
    
    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
    
    def __str__(self):
        return self.name

class Workplace(models.Model):
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
        # validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Некорректный номер телефона")],
        verbose_name="Телефон"
    )
    address = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Адрес"
    )

    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        verbose_name="Широта"
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        verbose_name="Долгота"
    )
    
    class Meta:
        verbose_name = "Рабочее место"
        verbose_name_plural = "Рабочие места"
    
    def save(self, *args, **kwargs):
        # Автоматически заполняем name из group и place
        group_name = self.group.name if self.group else ""
        place_name = self.place.name if self.place else ""
        
        if group_name and place_name:
            self.name = f"{group_name} {place_name}"
        elif group_name:
            self.name = group_name
        elif place_name:
            self.name = place_name
        else:
            self.name = "Без названия"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name or "Без названия"


class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile', 
        verbose_name="Пользователь"
    )
    
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
    
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True, 
        verbose_name="Фото профиля"
    )
    
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

class News(models.Model):
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
        auto_now_add=True,  
        verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        Profile, 
        on_delete=models.SET_NULL,  
        null=True, 
        blank=True, 
        verbose_name="Автор"
    )
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-date'] 
    
    def __str__(self):
        return self.title


class CorpLife(models.Model):
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


class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название проекта")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects', verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_task_count(self):
        return self.tasks.count()

    def get_completed_count(self):
        return self.tasks.filter(status='done').count()

    def get_progress_percent(self):
        total = self.tasks.count()
        if total == 0:
            return 0
        done = self.tasks.filter(status='done').count()
        return int((done / total) * 100)


class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('review', 'На проверке'),
        ('done', 'Готово'),
        ('closed', 'Закрыта'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('critical', 'Критический'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название задачи")
    description = models.TextField(blank=True, verbose_name="Описание")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name="Проект")
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks', verbose_name="Исполнитель")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks', verbose_name="Создатель")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Приоритет")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Срок выполнения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return self.title

    def is_overdue(self):
        if self.due_date and self.status not in ['done', 'closed']:
            return self.due_date < timezone.now()
        return False

    def get_status_color(self):
        colors = {
            'new': '#6c757d',
            'in_progress': '#0d6efd',
            'review': '#fd7e14',
            'done': '#198754',
            'closed': '#6c757d',
        }
        return colors.get(self.status, '#6c757d')

    def get_priority_color(self):
        colors = {
            'low': '#6c757d',
            'medium': '#0d6efd',
            'high': '#fd7e14',
            'critical': '#dc3545',
        }
        return colors.get(self.priority, '#6c757d')


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments', verbose_name="Задача")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий к {self.task.title}"


class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history', verbose_name="Задача")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Пользователь")
    field = models.CharField(max_length=50, verbose_name="Поле")
    old_value = models.TextField(blank=True, verbose_name="Было")
    new_value = models.TextField(blank=True, verbose_name="Стало")
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name = "История изменения"
        verbose_name_plural = "История изменений"
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.task.title} - {self.field}: {self.old_value} -> {self.new_value}"