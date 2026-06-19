from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms
from django.utils.safestring import mark_safe
from django_admin_multiupload import MultipleUploadAdminMixin, MultipleUploadInlineMixin
from galleryfield.mixins import GalleryFormMediaMixin
from .models import CorpLife, Post, Group, Place, Workplace, Profile, News, EventPhoto


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


class CorpLifeAdminForm(GalleryFormMediaMixin, forms.ModelForm):
    class Meta:
        model = CorpLife
        fields = '__all__'


class EventPhotoInline(MultipleUploadInlineMixin, admin.TabularInline):
    model = EventPhoto
    extra = 1
    upload_field_name = "image"
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
    email = forms.EmailField(required=False, label='Email')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(required=False, label='Email')

    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'

    def clean_is_superuser(self):
        is_superuser = self.cleaned_data.get('is_superuser')
        if self.instance.is_superuser and not is_superuser:
            if User.objects.filter(is_superuser=True).count() <= 1:
                raise forms.ValidationError('Нельзя снять последнего суперпользователя!')
        return is_superuser


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name = "Профиль"
    verbose_name_plural = "Профиль пользователя"
    fields = ('avatar_preview', 'avatar', 'firstname', 'lastname', 'patronumic', 'phone_number', 'workplace', 'post', 'create_date')
    readonly_fields = ('create_date', 'avatar_preview')
    extra = 0

    def avatar_preview(self, obj):
        if obj and obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" width="80" height="80" style="object-fit: cover; border-radius: 50%;" />')
        return "Нет фото"
    avatar_preview.short_description = "Текущий аватар"


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'get_full_name', 'get_phone', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'profile__phone_number']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'email', 'password1', 'password2')}),
    )

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

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def delete_model(self, request, obj):
        if obj.is_superuser:
            messages.error(request, 'Нельзя удалить суперпользователя!')
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        if queryset.filter(is_superuser=True).exists():
            messages.error(request, 'Нельзя удалять суперпользователей!')
            return
        super().delete_queryset(request, queryset)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_superuser:
            return request.user.is_superuser
        return super().has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_superuser and not request.user.is_superuser:
            return [f.name for f in User._meta.fields]
        return super().get_readonly_fields(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_superuser=False)
        return qs

    def has_add_permission(self, request):
        return request.user.is_staff

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_list_display(self, request):
        list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
        if request.user.is_superuser:
            list_display.append('is_superuser')
        return list_display

    def get_fieldsets(self, request, obj=None):
        if not request.user.is_superuser and obj and not obj.is_superuser:
            return (
                (None, {'fields': ('username', 'password')}),
                ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
                ('Права доступа', {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
            )
        return super().get_fieldsets(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)