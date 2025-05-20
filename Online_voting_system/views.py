from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST

from polls.models import Poll, Vote, Rating, Announcement, Choice, Profile
from polls.forms import RegisterForm, PollCreateForm, ChoiceFormSet, AvatarUploadForm

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'Online_voting_system/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Неверные данные для входа.")
    return render(request, 'Online_voting_system/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect('login')

@login_required
def home(request):
    if request.method == 'POST' and 'rate_submit' in request.POST:
        poll_id = request.POST.get('poll_id')
        rating_value = int(request.POST.get('rating_value', 0))
        if poll_id and 1 <= rating_value <= 5:
            try:
                poll = Poll.objects.get(id=poll_id)
            except Poll.DoesNotExist:
                messages.error(request, "Опрос не найден.")
                return redirect('index')

            if Rating.objects.filter(poll=poll, user_name=request.user.username).exists():
                messages.warning(request, "Вы уже оценили этот опрос.")
            else:
                Rating.objects.create(
                    poll=poll,
                    rating_value=rating_value,
                    user_name=request.user.username
                )
                messages.success(request, f"Вы оценили опрос на {rating_value} ⭐")
            return redirect('index')

    query = request.GET.get('q', '')
    poll_status = request.GET.get('status', '')
    sort = request.GET.get('sort')

    polls = Poll.objects.all()

    if query:
        polls = polls.filter(question__icontains=query)
    if poll_status == 'active':
        polls = polls.filter(end_date__gte=timezone.now())
    elif poll_status == 'ended':
        polls = polls.filter(end_date__lt=timezone.now())

    if sort == 'new':
        polls = polls.order_by('-pub_date')
    elif sort == 'old':
        polls = polls.order_by('pub_date')
    elif sort == 'rating':
        polls = sorted(polls, key=lambda p: p.average_rating() or 0, reverse=True)

    voted_poll_ids = Vote.objects.filter(user_name=request.user.username).values_list('poll_id', flat=True)
    rated_poll_ids = Rating.objects.filter(user_name=request.user.username).values_list('poll_id', flat=True)

    poll_results = {}
    for poll in polls:
        votes = poll.votes.all()
        total_votes = votes.count()
        results = []
        for choice in poll.choices.all():
            count = votes.filter(vote_choice=choice).count()
            percent = round((count / total_votes) * 100, 1) if total_votes > 0 else 0
            results.append({
                'text': choice.choice_text,
                'count': count,
                'percent': percent,
            })
        results.sort(key=lambda x: x['count'], reverse=True)
        poll_results[poll.id] = results

    context = {
        'polls': polls,
        'query': query,
        'poll_status': poll_status,
        'sort': sort,
        'voted_poll_ids': list(voted_poll_ids),
        'rated_poll_ids': list(rated_poll_ids),
        'poll_results': poll_results,
    }
    return render(request, 'Online_voting_system/index.html', context)

@login_required
def profile_view(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    votes = Vote.objects.filter(user_name=user.username)
    ratings = Rating.objects.filter(user_name=user.username)
    announcements = Announcement.objects.filter(author=user)

    if request.method == 'POST' and request.FILES.get('avatar'):
        avatar_form = AvatarUploadForm(request.POST, request.FILES, instance=profile)
        if avatar_form.is_valid():
            avatar_form.save()
            messages.success(request, "Аватар успешно обновлён!")
            return redirect('profile')
    else:
        avatar_form = AvatarUploadForm(instance=profile)

    context = {
        'user': user,
        'profile': profile,
        'votes': votes,
        'ratings': ratings,
        'announcements': announcements,
        'avatar_form': avatar_form,
    }
    return render(request, 'Online_voting_system/profile.html', context)

@login_required
def create_poll(request):
    if request.method == 'POST':
        form = PollCreateForm(request.POST, request.FILES)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            poll = form.save(commit=False)
            poll.pub_date = timezone.now()
            poll.author = request.user
            poll.save()
            for choice_form in formset:
                if choice_form.cleaned_data:
                    choice_text = choice_form.cleaned_data.get('choice_text')
                    if choice_text and choice_text.strip():
                        Choice.objects.create(poll=poll, choice_text=choice_text)
            messages.success(request, "Опрос успешно создан!")
            return redirect('index')
        else:
            if not form.is_valid():
                messages.error(request, "Проверьте правильность заполнения полей опроса.")
            if not formset.is_valid():
                messages.error(request, "Укажите минимум два варианта ответа.")
    else:
        form = PollCreateForm()
        formset = ChoiceFormSet()
    return render(request, 'Online_voting_system/create_poll.html', {
        'form': form,
        'formset': formset,
    })

@require_POST
@login_required
def vote_view(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if not poll.is_active():
        messages.error(request, "Голосование по этому опросу уже завершено.")
        return redirect('index')

    if Vote.objects.filter(poll=poll, user_name=request.user.username).exists():
        messages.warning(request, "Вы уже голосовали в этом опросе.")
        return redirect('index')

    if poll.allow_multiple_choices:
        selected_choices = request.POST.getlist('choices')
    else:
        selected_choice = request.POST.get('choice')
        selected_choices = [selected_choice] if selected_choice else []

    if not selected_choices or not all(selected_choices):
        messages.error(request, "Выберите хотя бы один корректный вариант.")
        return redirect('index')

    for choice_id in selected_choices:
        try:
            choice = poll.choices.get(id=choice_id)
            Vote.objects.create(
                poll=poll,
                user_name=request.user.username,
                vote_choice=choice,
            )
        except Choice.DoesNotExist:
            messages.error(request, "Ошибка выбора варианта.")
            return redirect('index')

    messages.success(request, "Спасибо за голос!")
    return redirect('index')
