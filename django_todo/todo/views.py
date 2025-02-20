from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from .models import Task
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from datetime import datetime
from django.urls import reverse

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task_list')  # Redirect to the task list page
    else:
        form = UserCreationForm()
    return render(request, 'todo/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('task_list')  
    else:
        form = AuthenticationForm()
    return render(request, 'todo/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).order_by(
        models.Case(
            models.When(priority="High", then=models.Value(1)),
            models.When(priority="Medium", then=models.Value(2)),
            models.When(priority="Low", then=models.Value(3)),
            default=models.Value(4),
        ),
        "due_date"  # Secondary sorting by due date
    )

    form = TaskForm()
    return render(request, 'todo/task_list.html', {'tasks': tasks, 'form': form})

from django.urls import reverse
from django.db import models

@login_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.completed = True  # Ensure it's always pending
            
            due_date = request.POST.get("due_date")
            priority = request.POST.get("priority", "Medium")  # Default to Medium
            
            if due_date:
                task.due_date = datetime.strptime(due_date, "%Y-%m-%d")
            
            task.priority = priority
            task.save()

            return redirect('task_list')  # Redirect to refresh the page
    return redirect('task_list')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == "POST":
        task.delete()
    return redirect(reverse('task_list'))  # Redirect instead of returning JSON


@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.completed = not task.completed
        task.save()
    return redirect(reverse('task_list'))  # Redirect after updating task
