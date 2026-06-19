from django.shortcuts import render, redirect
from .models import CorpLife, Post, Group, Place, Workplace, Profile, News, Workplace, EventPhoto  
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import permission_required
from .forms import NewsForm, EventCreateForm, UserCreateForm, UserEditForm
from django.contrib.auth.decorators import login_required
from .forms import EventPhotoForm
from django.db import models
from django.views.decorators.csrf import csrf_exempt
import traceback
from django.http import JsonResponse
from django.contrib.auth.models import User

def home_output(request):
    news = News.objects.all().order_by('-date')  # все новости, свежие сверху
    return render(request, 'module_project/home.html', {'news': news})

def profile_info(request):
    if request.method == 'POST':
        profile = request.user.profile
        
        # Обновляем поля из формы
        profile.lastname = request.POST.get('lastname', '')
        profile.firstname = request.POST.get('firstname', '')
        profile.patronumic = request.POST.get('patronumic', '')
        profile.phone_number = request.POST.get('phone_number', '')
        
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('Profile')    
    return render(request, 'module_project/profile.html')

def documents_info(request):
    return render(request, 'module_project/documents.html')

def event(request):
    """Страница со списком мероприятий"""
    events = CorpLife.objects.all().order_by('-date').prefetch_related('photos')
    
    return render(request, 'module_project/event.html', {
        'events': events,
    })

def departments_info(request):
    workplaces = Workplace.objects.select_related('group', 'place').all()
    
    return render(request, 'module_project/departments.html', {
        'workplaces': workplaces,
    })
    return render(request, 'module_project/departments.html')

def event_detail(request, event_id):
    """Страница с галереей мероприятия"""
    event = get_object_or_404(CorpLife, id=event_id)
    photos = event.photos.all()  
    
    return render(request, 'module_project/eventGal.html', {
        'event': event,
        'photos': photos,
    })

@login_required
def event_photos_upload(request, event_id):
    """Обработка загрузки фото (AJAX + обычная)"""
    event = get_object_or_404(CorpLife, id=event_id)
    
    if request.method == 'POST':
        form = EventPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.event = event
            photo.order = event.photos.count() + 1
            photo.save()
            
            # Если AJAX запрос — возвращаем JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'photo': {
                        'id': photo.id,
                        'url': photo.image.url,
                        'caption': photo.caption,
                    }
                })
            
            messages.success(request, 'Фото добавлено!')
            return redirect('event', event_id=event.id)
    else:
        form = EventPhotoForm()
    
    # Если не AJAX — показываем страницу галереи с формой
    photos = event.photos.all()
    return render(request, 'module_project/eventGal.html', {
        'event': event,
        'photos': photos,
        'form': form,
    })


@login_required
def photo_delete(request, photo_id):
    """Удаление фото (AJAX)"""
    if request.method == 'POST':
        photo = get_object_or_404(EventPhoto, id=photo_id)
        photo.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)



@permission_required('module_project.add_news', raise_exception=True)
def news_create(request):
    """Создание новости - только для редакторов"""
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user.profile
            news.save()
            messages.success(request, 'Новость успешно создана!')
            return redirect('Home')  # или куда нужно
    else:
        form = NewsForm()
    
    return render(request, 'module_project/news_create.html', {
        'form': form,
        'title': 'Создание новости'
    })

@permission_required('module_project.add_corplife', raise_exception=True)
def event_create(request):
    if request.method == 'POST':
        # Ручное создание объекта из данных формы
        title = request.POST.get('title')
        text = request.POST.get('text')
        date = request.POST.get('date')
        
        if title and text and date:
            event = CorpLife.objects.create(
                title=title,
                text=text,
                date=date,
                author=request.user
            )
            
            # Сохраняем фото
            photos = request.FILES.getlist('photos')
            for photo in photos:
                EventPhoto.objects.create(event=event, image=photo)
            
            messages.success(request, 'Мероприятие создано!')
            return redirect('Events')  # или куда нужно
        else:
            messages.error(request, 'Заполните все поля')
    
    return render(request, 'module_project/event_create.html', {'title': 'Создать мероприятие'})



def Deppersonal(request, workplace_id):
    """Страница со списком сотрудников рабочего места"""
    workplace = get_object_or_404(Workplace, id=workplace_id)
    employees = Profile.objects.filter(workplace=workplace).select_related('user', 'post')
    
    return render(request, 'module_project/personal.html', {
        'workplace': workplace,
        'employees': employees,
    })



@login_required
def event_photos_upload(request, event_id):
    """Страница добавления множества фото с drag-and-drop"""
    event = get_object_or_404(CorpLife, id=event_id)
    photos = event.photos.all().order_by('order')
    
    if request.method == 'POST' and request.FILES.get('photo'):
        # Загружаем одно фото
        photo = request.FILES['photo']
        new_photo = EventPhoto.objects.create(
            event=event,
            image=photo,
            order=event.photos.count() + 1
        )
        return JsonResponse({
            'success': True,
            'photo': {
                'id': new_photo.id,
                'url': new_photo.image.url,
                'caption': new_photo.caption or '',
            }
        })
    
    return render(request, 'module_project/photos_upload.html', {
        'event': event,
        'photos': photos,
    })


@csrf_exempt  # 👈 ВРЕМЕННО для теста
@login_required
def photo_delete_ajax(request, photo_id):
    """Удаление фото через AJAX"""
    try:
        print(f"Удаление фото {photo_id}")
        photo = get_object_or_404(EventPhoto, id=photo_id)
        print(f"Найдено фото: {photo}")
        photo.delete()
        print("Фото удалено")
        return JsonResponse({'success': True})
    except Exception as e:
        print("ОШИБКА:")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def user_list(request):
    """Список пользователей (без суперпользователей)"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('home')
    
    users = User.objects.filter(is_superuser=False)
    return render(request, 'module_project/user_list.html', {'users': users})


@login_required
def user_create(request):
    """Создание пользователя"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пользователь успешно создан!')
            return redirect('user_list')
    else:
        form = UserCreateForm()
    
    return render(request, 'module_project/user_form.html', {
        'form': form,
        'title': 'Создание пользователя',
        'action': 'create'
    })


@login_required
def user_edit(request, user_id):
    """Редактирование пользователя"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пользователь обновлён!')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'module_project/user_form.html', {
        'form': form,
        'title': 'Редактирование пользователя',
        'action': 'edit',
        'user': user
    })


@login_required
def user_delete(request, user_id):
    """Удаление пользователя"""
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Пользователь удалён!')
        return redirect('user_list')
    
    return render(request, 'module_project/user_confirm_delete.html', {'user': user})