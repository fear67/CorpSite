from django.shortcuts import render, redirect
from .models import CorpLife, Post, Group, Place, Workplace, Profile, News, Workplace, EventPhoto  
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import permission_required
from .forms import NewsForm, EventCreateForm, UserCreateForm, UserEditForm, ProjectForm
from django.contrib.auth.decorators import login_required
from .forms import EventPhotoForm
from django.db import models
from django.views.decorators.csrf import csrf_exempt
import traceback
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Project
from .models import Project, Task, TaskComment

def home_output(request):
    news = News.objects.all().order_by('-date') 
    return render(request, 'module_project/home.html', {'news': news})

def profile_info(request):
    if request.method == 'POST':
        profile = request.user.profile
        
        # Обновляем поля из формы
        profile.lastname = request.POST.get('lastname', '')
        profile.firstname = request.POST.get('firstname', '')
        profile.patronumic = request.POST.get('patronumic', '')
        profile.phone_number = request.POST.get('phone_number', '')
        request.user.email = request.POST.get('email', '')
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('Profile')    
    return render(request, 'module_project/profile.html')

def documents_info(request):
    return render(request, 'module_project/documents.html')

def event(request):
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
    event = get_object_or_404(CorpLife, id=event_id)
    photos = event.photos.all()  
    
    return render(request, 'module_project/eventGal.html', {
        'event': event,
        'photos': photos,
    })

@login_required
def event_photos_upload(request, event_id):
    event = get_object_or_404(CorpLife, id=event_id)
    
    if request.method == 'POST':
        form = EventPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.event = event
            photo.order = event.photos.count() + 1
            photo.save()
            
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
    
    photos = event.photos.all()
    return render(request, 'module_project/eventGal.html', {
        'event': event,
        'photos': photos,
        'form': form,
    })

@login_required
def photo_delete(request, photo_id):
    if request.method == 'POST':
        photo = get_object_or_404(EventPhoto, id=photo_id)
        photo.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@permission_required('module_project.add_news', raise_exception=True)
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user.profile
            news.save()
            messages.success(request, 'Новость успешно создана!')
            return redirect('Home')  
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
            
            photos = request.FILES.getlist('photos')
            for photo in photos:
                EventPhoto.objects.create(event=event, image=photo)
            
            messages.success(request, 'Мероприятие создано!')
            return redirect('Events')  
        else:
            messages.error(request, 'Заполните все поля')
    
    return render(request, 'module_project/event_create.html', {'title': 'Создать мероприятие'})

def Deppersonal(request, workplace_id):
    workplace = get_object_or_404(Workplace, id=workplace_id)
    
    employees_qs = Profile.objects.filter(
        workplace=workplace
    ).select_related('user', 'post')
    
    employees_count = employees_qs.count()
    
    def sort_key(profile):
        post_name = profile.post.name if profile.post else ''
        priority = 0 if post_name == 'Руководитель' else 1
        return (priority, post_name, profile.lastname or '', profile.firstname or '')
    
    employees = sorted(employees_qs, key=sort_key)
    
    return render(request, 'module_project/personal.html', {
        'workplace': workplace,
        'employees': employees,
        'employees_count': employees_count,
    })



@login_required
def event_photos_upload(request, event_id):
    """Страница добавления множества фото с drag-and-drop"""
    event = get_object_or_404(CorpLife, id=event_id)
    photos = event.photos.all().order_by('order')
    
    if request.method == 'POST' and request.FILES.get('photo'):
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

@csrf_exempt  
@login_required
def photo_delete_ajax(request, photo_id):
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
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('home')
    
    users = User.objects.filter(is_superuser=False)
    return render(request, 'module_project/user_list.html', {'users': users})

@login_required
def user_create(request):
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
    if not request.user.is_staff:
        messages.error(request, 'У вас нет доступа к этой странице')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Пользователь удалён!')
        return redirect('user_list')
    
    return render(request, 'module_project/user_confirm_delete.html', {'user': user})

@login_required
def project_list(request):
    projects = Project.objects.filter(is_active=True)

    search = request.GET.get('search', '')
    if search:
        projects = projects.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'module_project/project_list.html', {
        'page_obj': page_obj,
        'search': search,
    })

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, 'Проект создан!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    
    return render(request, 'module_project/project_form.html', {
        'form': form,
    })

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.all()
    
    stats = {
        'total': tasks.count(),
        'new': tasks.filter(status='new').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'review': tasks.filter(status='review').count(),
        'done': tasks.filter(status='done').count(),
        'closed': tasks.filter(status='closed').count(),
        'overdue': sum(1 for t in tasks if t.is_overdue()),
    }
    
    return render(request, 'module_project/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'stats': stats,
        'users': User.objects.all().order_by('username'),
    })

@login_required
def task_create(request):
    if request.method == 'POST':
        project_id = request.POST.get('project')
        project = get_object_or_404(Project, id=project_id)
        
        task = Task(
            title=request.POST.get('title'),
            description=request.POST.get('description', ''),
            project=project,
            created_by=request.user,
        )
        
        assignee_id = request.POST.get('assignee')
        if assignee_id:
            task.assignee = get_object_or_404(User, id=assignee_id)
        
        task.priority = request.POST.get('priority', 'medium')
        task.status = request.POST.get('status', 'new')
        
        due_date = request.POST.get('due_date')
        if due_date:
            task.due_date = due_date
        
        task.save()
        messages.success(request, 'Задача создана!')
        return redirect('project_detail', project_id=project.id)
    
    return redirect('project_list')


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    project_id = task.project.id
    task.delete()
    messages.success(request, 'Задача удалена!')
    return redirect('project_detail', project_id=project_id)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all()
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            TaskComment.objects.create(
                task=task,
                author=request.user,
                text=text
            )
            messages.success(request, 'Комментарий добавлен!')
            return redirect('task_detail', task_id=task.id)
    
    return render(request, 'module_project/task_detail.html', {
        'task': task,
        'comments': comments,
    })


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description', '')
        
        assignee_id = request.POST.get('assignee')
        task.assignee = get_object_or_404(User, id=assignee_id) if assignee_id else None
        
        task.priority = request.POST.get('priority')
        task.status = request.POST.get('status')
        
        due_date = request.POST.get('due_date')
        task.due_date = due_date if due_date else None
        
        task.save()
        messages.success(request, 'Задача обновлена!')
        return redirect('task_detail', task_id=task.id)
    
    users = User.objects.filter(is_active=True)
    
    return render(request, 'module_project/task_edit.html', {
        'task': task,
        'users': users,
    })

@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.description = request.POST.get('description', '')
        project.is_active = request.POST.get('is_active') == 'on'
        project.save()
        messages.success(request, 'Проект обновлён!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'module_project/project_edit.html', {'project': project})


@login_required
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Проект удалён!')
        return redirect('project_list')
    
    return render(request, 'module_project/project_confirm_delete.html', {'project': project})

@login_required
def my_tasks(request):
    tasks = Task.objects.filter(assignee=request.user).order_by('-priority', 'due_date')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    return render(request, 'module_project/my_tasks.html', {
        'tasks': tasks,
        'status_filter': status_filter,
        'statuses': Task.STATUS_CHOICES,
    })