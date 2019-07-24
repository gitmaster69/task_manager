from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import TeamCreateForm, TaskCreateForm, AddCommentForm
from .models import UserData, Teams, Tasks


@login_required
def dashboard(request):
    """
    Displays the homepage to the logged in user
    """
    user_data = UserData()  # Creating UserData object

    # Get fullname of the user
    fullname = request.user.get_full_name()

    # Get list of tasks assigned to the user from all teams
    tasks_for_you = user_data.get_task_list(request)

    # Get list of teams, for the sidebar
    side_teams = user_data.get_team_list(request)

    args = {'fullname': fullname, 'sidebar_teams': side_teams, 'tasks_for_you': tasks_for_you}
    return render(request, 'core/dashboard.html', args)


@login_required
def view_team(request, team_id):
    """
    Displays the team page with all the tasks in it
    """
    user_data = UserData()  # Creating UserData object

    # Checking if the user is authorised to access the specific Team
    # If not authorised then redirect to dashboard
    if not user_data.team_check(request, team_id):
        messages.error(request, 'You are not Authorised to access this Team')
        return redirect(reverse('dashboard'))

    # Getting the list of Tasks in different sections
    tasks_for_you = user_data.get_team_details(request, team_id, 'tasks_for_you')
    tasks_by_you = user_data.get_team_details(request, team_id, 'tasks_by_you')
    tasks_all = user_data.get_team_details(request, team_id, 'all_tasks')

    # Getting the name of the Team
    team_name = user_data.get_team_details(request, team_id, 'name')[0]

    # Get list of teams, for the sidebar
    side_teams = user_data.get_team_list(request)

    args = {'heading': (team_name['name'], team_id), 'tasks_for_you': tasks_for_you, 'tasks_by_you': tasks_by_you,
            'tasks_all': tasks_all, 'sidebar_teams': side_teams}
    return render(request, 'core/team.html', args)


@login_required
def delete_team(request, team_id):
    """
    Delete a specific team and all its tasks
    """

    # Checking if the user is the creator of the Team
    # If not then redirect to dashboard
    if not UserData().team_owner_check(request, team_id):
        messages.error(request, 'You are not Authorised to delete this team')
        return redirect(reverse('dashboard'))

    # Delete the Team
    Teams.objects.get(id=team_id).delete()

    return redirect(reverse('dashboard'))


@login_required
def view_task(request, task_id):
    """
    Displays the task page with option to add comments
    """
    user_data = UserData()  # Creating UserData object

    # Checking if the user is the member of the Team
    # If not authorised then redirect to dashboard
    if not user_data.team_check(request, Tasks.objects.filter(id=task_id).values('team')[0]['team']):
        messages.error(request, 'You are not Authorised to access this Task')
        return redirect(reverse('dashboard'))

    # Create ModelForm object
    form = AddCommentForm()

    # TODO delete comment
    # Show all comments for this task
    comments = user_data.get_comments(task_id)

    # Get details of a specific task
    task_data = user_data.get_task_details(task_id)

    # Get list of teams, for the sidebar
    side_teams = user_data.get_team_list(request)

    args = {'form': form, 'comments': comments, 'task_id': task_id, 'task_data': task_data, 'sidebar_teams': side_teams}
    return render(request, 'core/task.html', args)


@login_required
def delete_task(request, task_id):
    """
    Delete a specific task and all its comments
    """

    # Checking if the user is the creator of the Task
    # If not then redirect to dashboard
    if not UserData().task_owner_check(request, task_id):
        messages.error(request, 'You are not Authorised to delete this task')
        return redirect(reverse('dashboard'))

    # Delete the Task
    instance = Tasks.objects.get(id=task_id)
    instance.delete()

    # Redirect to the team's page or to the dashboard
    if instance.team is not None:
        return redirect(reverse('show_team', kwargs={'team_id': instance.team.id}))
    else:
        return redirect(reverse('dashboard'))


@login_required
def manage_comment(request, task_id):
    """
    Function to insert comment
    """
    user_data = UserData()  # Creating UserData object

    # Checking if the user is the member of the Team
    # If not authorised then redirect to dashboard
    if not user_data.team_check(request, Tasks.objects.filter(id=task_id).values('team')[0]['team']):
        messages.error(request, 'You are not Authorised to access this Task')
        return redirect(reverse('dashboard'))

    # Check if a comment is submitted
    if request.method == 'POST':
        form = AddCommentForm(request.POST)  # Creating ModelForm object
        if form.is_valid():
            post = form.save(commit=False)
            post.task = Tasks.objects.get(id=task_id)
            post.author = request.user
            post.save()

    return redirect(reverse('show_task', kwargs={'task_id': task_id}) + "#comments")


class CreateTeam(TemplateView):
    """
    Class to create a new Team
    """

    # Defining template to use
    template_name = 'core/team_edit.html'

    @method_decorator(login_required)
    def get(self, request):
        """ Handling GET request """
        form = TeamCreateForm()  # Creating ModelForm object

        # Get list of teams, for the sidebar
        side_teams = UserData().get_team_list(request)

        args = {'form': form, 'sidebar_teams': side_teams, 'is_update': False}
        return render(request, self.template_name, args)

    @method_decorator(login_required)
    def post(self, request):
        """ Handling POST request """
        error = ''  # Creating empty variable to handle custom error

        # Creating ModelForm object with POST data
        form = TeamCreateForm(request.POST)

        if not Teams.objects.filter(Q(owner=request.user) | Q(users=request.user)).filter(name=form['name'].value()) \
                .exists():
            # Checking if the user belongs to a Team with the same name
            if form.is_valid():
                # Validating form input
                post = form.save(commit=False)
                post.owner = request.user
                post.save()
                form.save_m2m()
                return redirect('/dashboard/team-' + str(post.id))
        else:
            error = "You belong to a team with the same name"

        # Get list of teams, for the sidebar
        side_teams = UserData().get_team_list(request)

        args = {'form': form, 'sidebar_teams': side_teams, 'error': error, 'is_update': False}
        return render(request, self.template_name, args)


class EditTeam(TemplateView):
    """
    Class to Edit any Team
    """

    # Defining template to use
    template_name = 'core/team_edit.html'

    @method_decorator(login_required)
    def get(self, request, team_id):
        """ Handling GET request """
        user_data = UserData()  # Creating UserData object

        # Checking if the user is the creator of the Team
        # If not authorised then redirect to the team's page
        if not user_data.team_owner_check(request, team_id):
            messages.error(request, 'You are not Authorised to edit this team')
            return redirect(reverse('show_team', args=[team_id]))

        # Get specific team's data
        data = Teams.objects.get(id=team_id)

        # Create ModelForm with the data
        form = TeamCreateForm(instance=data)

        # Get list of teams, for the sidebar
        side_teams = UserData().get_team_list(request)

        args = {'form': form, 'sidebar_teams': side_teams, 'is_update': True}
        return render(request, self.template_name, args)

    @method_decorator(login_required)
    def post(self, request, team_id):
        """ Handling POST request """
        user_data = UserData()  # Creating UserData object

        # Checking if the user is the creator of the Team
        # If not authorised then redirect to the team's page
        if not user_data.team_owner_check(request, team_id):
            messages.error(request, 'You are not Authorised to edit this team')
            return redirect(reverse('show_team', args=[team_id]))

        error = ''  # Creating empty variable to handle custom error

        # Get specific team's data
        data = Teams.objects.get(id=team_id)

        # Create ModelForm with the Existing data and POST data
        form = TeamCreateForm(request.POST, instance=data)

        if not Teams.objects.exclude(id=team_id).filter(Q(owner=request.user) | Q(users=request.user)).filter(
                name=form['name'].value()).exists():
            # Checking if the user belongs to a Team with the same name
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                form.save_m2m()
                return redirect('/dashboard/team-' + str(post.id))
        else:
            error = "You belong to a team with the same name"

        # Get list of teams, for the sidebar
        side_teams = UserData().get_team_list(request)

        args = {'form': form, 'sidebar_teams': side_teams, 'error': error, 'is_update': True}
        return render(request, self.template_name, args)


class CreateTask(TemplateView):
    template_name = 'core/task_edit.html'

    @method_decorator(login_required)
    def get(self, request, team_id='None'):

        user_data = UserData()

        if team_id is not 'None' and not user_data.team_check(request, team_id):
            messages.error(request, 'You are not Authorised to create task in this team')
            return redirect(reverse('dashboard'))

        form = TaskCreateForm()
        side_teams = user_data.get_team_list(request)
        args = {'form': form, 'sidebar_teams': side_teams, 'is_update': False}

        if team_id is 'None':
            args['assignee'] = request.user.get_full_name()
        elif user_data.team_check(request, team_id):
            args['preassigned_team'] = user_data.get_team_details(request, team_id, 'name')[0]['name']

        return render(request, self.template_name, args)

    @method_decorator(login_required)
    def post(self, request, team_id='None'):

        user_data = UserData()

        if team_id is not 'None' and not user_data.team_check(request, team_id):
            messages.error(request, 'You are not Authorised to create task in this team')
            return redirect(reverse('dashboard'))

        post_values = request.POST.copy()
        if team_id is 'None':
            post_values['assignee'] = request.user.id

        form = TaskCreateForm(post_values)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user

            if team_id is not 'None':
                post.team = Teams.objects.get(id=team_id)
                print(post.team)

            post.save()
            form.save_m2m()

            if team_id is 'None':
                return redirect(reverse('dashboard'))
            else:
                return redirect(reverse('show_team', kwargs={'team_id': team_id}))

        side_teams = UserData().get_team_list(request)
        args = {'form': form, 'sidebar_teams': side_teams, 'is_update': False}

        if team_id is 'None':
            args['assignee'] = request.user.get_full_name()
        elif user_data.task_check(request, team_id):
            args['preassigned_team'] = user_data.get_team_details(request, team_id, 'name')

        return render(request, self.template_name, args)


class EditTask(TemplateView):
    template_name = 'core/task_edit.html'

    @method_decorator(login_required)
    def get(self, request, task_id='None'):

        user_data = UserData()

        if task_id is 'None':
            messages.error(request, 'Unknown Error!')
            return redirect(reverse('show_task', args=[task_id]))

        if task_id is not 'None' and not user_data.task_owner_check(request, task_id):
            messages.error(request, 'You are not Authorised to edit this task')
            return redirect(reverse('show_task', args=[task_id]))

        data = Tasks.objects.get(id=task_id)
        form = TaskCreateForm(instance=data)
        side_teams = user_data.get_team_list(request)
        args = {'form': form, 'sidebar_teams': side_teams, 'is_update': True}

        if data.team is None:
            args['assignee'] = request.user.get_full_name()
        else:
            args['preassigned_team'] = data.team

        return render(request, self.template_name, args)

    @method_decorator(login_required)
    def post(self, request, task_id='None'):

        user_data = UserData()

        if task_id is not 'None' and not user_data.task_owner_check(request, task_id):
            messages.error(request, 'You are not Authorised to edit this task')
            return redirect(reverse('show_task', args=[task_id]))

        data = Tasks.objects.get(id=task_id)
        post_values = request.POST.copy()
        if data.team is None:
            post_values['assignee'] = request.user.id

        form = TaskCreateForm(post_values, instance=data)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            form.save_m2m()

            return redirect(reverse('show_task', kwargs={'task_id': task_id}))

        side_teams = UserData().get_team_list(request)
        args = {'form': form, 'sidebar_teams': side_teams, 'is_update': True}

        if data.team is None:
            args['assignee'] = request.user.get_full_name()
        else:
            args['preassigned_team'] = data.team

        return render(request, self.template_name, args)
