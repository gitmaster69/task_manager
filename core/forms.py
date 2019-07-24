from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Teams, Tasks, Comments


class TeamCreateForm(forms.ModelForm):

    class Meta:
        model = Teams
        fields = ('name', 'users', )


class TaskCreateForm(forms.ModelForm):

    class Meta:
        model = Tasks
        fields = ('name', 'desc', 'assignee', 'status', )

    # def __init__(self, *args, **kwargs):
    #     super(TaskCreateForm, self).__init__(*args, **kwargs)
    #     self.fields['assignee'].queryset = Teams.objects.get(id=11).owner
    #     print(Teams.objects.get(id=11).owner)


class AddCommentForm(forms.ModelForm):

    class Meta:
        model = Comments
        fields = ('comment', )
