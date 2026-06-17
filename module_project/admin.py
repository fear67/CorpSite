from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  
from django.contrib.auth.models import User  
from django import forms
from django_admin_multiupload import MultipleUploadAdminMixin, MultipleUploadInlineMixin
from django.utils.safestring import mark_safe 
from galleryfield.mixins import GalleryFormMediaMixin
from .models import CorpLife, Post, Group, Place, Workplace, Profile, News  , EventPhoto
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
# ==================== СПРАВОЧНИКИ ====================

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'group', 'place', 'phone_number']
    list_filter = ['group', 'place']
    search_fields = ['name', 'address']


# ==================== ПРОФИЛИ ====================

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ['firstname', 'lastname', 'patronumic', 'phone_number', 'avatar', 'workplace', 'post']


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_roles', 'is_staff']
    list_filter = ['groups', 'is_staff', 'is_superuser']
    
    def get_roles(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_roles.short_description = "Роли (группы)"


# ==================== НОВОСТИ ====================

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'author', 'image_preview']
    list_filter = ['date', 'author']
    search_fields = ['title', 'text']
    readonly_fields = ['date']
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />')
        return "—"
    image_preview.short_description = "Превью"


# ==================== МЕРОПРИЯТИЯ (GALLERYFIELD) ====================

class CorpLifeAdminForm(GalleryFormMediaMixin, forms.ModelForm):
    class Meta:
        model = CorpLife
        fields = '__all__'


class EventPhotoInline(MultipleUploadInlineMixin, admin.TabularInline):
    """Inline для загрузки нескольких фото с drag-and-drop"""
    model = EventPhoto
    extra = 1
    upload_field_name = "image"  # поле в модели EventPhoto для фото
    fields = ['image', 'caption', 'order', 'preview']
    readonly_fields = ['preview']
    
    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80" style="object-fit: cover; border-radius: 4px;" />')
        return "—"
    preview.short_description = "Превью"

@admin.register(CorpLife)
class CorpLifeAdmin(MultipleUploadAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'date', 'created_at', 'author', 'photos_count']
    list_filter = ['date', 'author']
    search_fields = ['title', 'text']
    readonly_fields = ['created_at']
    inlines = [EventPhotoInline]
    
    def photos_count(self, obj):
        count = obj.photos.count()
        return f"{count}" if count else "Нет фото"
    photos_count.short_description = "Фотографии"


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=True, label='Email')
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


# ==================== INLINE ДЛЯ ПРОФИЛЯ ====================

class ProfileInline(admin.StackedInline):
    """Профиль пользователя - отображается внутри редактирования пользователя"""
    model = Profile
    can_delete = False
    verbose_name = "Профиль"
    verbose_name_plural = "Профиль пользователя"
    
    # Поля, которые показываем в админке
    fields = (
        'avatar_preview',
        'avatar',
        'firstname',
        'lastname',
        'patronumic',
        'phone_number',
        'workplace',
        'post',
        'create_date',
    )
    
    readonly_fields = ('create_date', 'avatar_preview')
    
    def avatar_preview(self, obj):
        if obj and obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" width="80" height="80" style="object-fit: cover; border-radius: 50%;" />')
        return "Нет фото"
    avatar_preview.short_description = "Текущий аватар"
    
    # Кастомизация отображения
    extra = 0  # Не добавлять пустые формы


# ==================== КАСТОМНЫЙ USER ADMIN ====================

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Поля в списке пользователей
    list_display = ('username', 'email', 'get_full_name', 'get_phone', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__phone_number')
    
    # Поля в форме редактирования
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Поля в форме создания
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    # ПОДКЛЮЧАЕМ ПРОФИЛЬ КАК INLINE
    inlines = [ProfileInline]
    
    # Дополнительные методы для отображения в списке
    def get_full_name(self, obj):
        try:
            return obj.profile.full_name
        except Profile.DoesNotExist:
            return "—"
    get_full_name.short_description = "Полное имя"
    
    def get_phone(self, obj):
        try:
            return obj.profile.phone_number or "—"
        except Profile.DoesNotExist:
            return "—"
    get_phone.short_description = "Телефон"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)