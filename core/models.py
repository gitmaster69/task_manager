from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Count
from datetime import datetime


class UserData:
    """
    All the Queries to get data for the user
    """

    def get_team_list(self, request):
        """
        Returns list of all the teams the user belongs to
        """
        user = request.user
        return Teams.objects.filter(Q(users=user) | Q(owner=user)).values('name', 'id').annotate(count=Count('name'))\
            .filter(~Q(count__gt=1) | Q(count__gt=1))

    def get_task_list(self, request):
        """
        Returns list of all the tasks the user is assigned
        """
        user = request.user
        return Tasks.objects.filter(assignee=user).order_by('-last_modified').values('id', 'name', 'owner__first_name',
                                                                                     'owner__last_name', 'status',
                                                                                     'last_modified')

    def team_check(self, request, team_id):
        """
        Checks if team exists and the user is allowed to access it
        """
        return Teams.objects.filter(id=team_id).filter(Q(owner=request.user) | Q(users=request.user)).exists()

    def task_check(self, request, task_id):
        """
        Checks if task exists and the user is allowed to access it
        """
        return Tasks.objects.filter(id=task_id).filter(Q(owner=request.user) | Q(assignee=request.user)).exists()

    def task_owner_check(self, request, task_id):
        """
        Checks if task exists and the user is allowed to edit it
        """
        return Tasks.objects.filter(id=task_id).filter(owner=request.user).exists()

    def team_owner_check(self, request, team_id):
        """
        Checks if team exists and the user is allowed to edit it
        """
        return Teams.objects.filter(id=team_id).filter(owner=request.user).exists()

    def get_task_details(self, task_id):
        """
        Returns all details for a specific task
        """
        return Tasks.objects.filter(id=task_id).values('name', 'desc', 'owner__first_name', 'owner__last_name',
                                                       'team__name', 'assignee__first_name', 'assignee__last_name', 'status')

    def get_team_details(self, request, team_id, data):
        """
        Returns all the tasks inside a team
        """
        user = request.user

        if data is 'tasks_for_you':
            """Returns all the task assigned to the current user in a specific team"""
            return Tasks.objects.filter(team__id=team_id).filter(assignee=user)\
                .order_by('-last_modified').values('id', 'name', 'owner__first_name', 'owner__last_name',
                                                   'status', 'last_modified')

        elif data is 'tasks_by_you':
            """Returns all the task created by the current user in a specific team"""
            return Tasks.objects.filter(team__id=team_id).filter(owner=user)\
                .order_by('-last_modified').values('id', 'name', 'status', 'last_modified')

        elif data is 'all_tasks':
            """Returns all the tasks in a specific team"""
            return Tasks.objects.filter(team__id=team_id).order_by('-last_modified')\
                .values('id', 'name', 'owner__first_name', 'owner__last_name', 'status', 'last_modified')

        elif data is 'name':
            """Returns the name of the team"""
            return Teams.objects.filter(id=team_id).values('name')

    def get_comments(self, task_id):
        """
        Returns all the comments for a specific task
        """
        return Comments.objects.filter(task=task_id).order_by('-last_modified').values('author__first_name',
                                                                                       'author__last_name', 'comment',
                                                                                       'last_modified')


class Teams(models.Model):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_owner')
    users = models.ManyToManyField(User, related_name='team_user')

    def __str__(self):
        return self.name


class Tasks(models.Model):
    STATUSES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    name = models.CharField(max_length=50)
    desc = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_owner')
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name='team', null=True)
    assignee = models.ManyToManyField(User, related_name='task_assignee')
    status = models.CharField(max_length=30, choices=STATUSES, default='planned')
    last_modified = models.DateTimeField(default=datetime.now, blank=True)


class Comments(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=200)
    last_modified = models.DateTimeField(default=datetime.now, blank=True)

