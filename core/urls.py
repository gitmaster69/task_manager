from django.urls import path
from . import views

urlpatterns = [
    # Basic URLs
    path('', views.dashboard, name='dashboard'),
    path('new-team', views.CreateTeam.as_view(), name='create_team'),
    path('new-task', views.CreateTask.as_view(), name='create_task'),

    # URLs related to Team
    path('team-<str:team_id>', views.view_team, name='show_team'),
    path('team-<str:team_id>/edit', views.EditTeam.as_view(), name='edit_team'),
    path('team-<str:team_id>/delete', views.delete_team, name='delete_team'),
    path('team-<str:team_id>/new-task', views.CreateTask.as_view(), name='create_task_for_team'),

    # URLs related to Task
    path('task-<int:task_id>', views.view_task, name='show_task'),
    path('task-<int:task_id>/edit', views.EditTask.as_view(), name='edit_task'),
    path('task-<int:task_id>/delete', views.delete_task, name='delete_task'),
    path('task-<int:task_id>/comment', views.manage_comment, name='manage_comment'),
]