from django.urls import path
from Online_voting_system import views
from django.contrib import admin
from Online_voting_system.views import (
    register_view,
    login_view,
    logout_view,
    home,
    profile_view,
    create_poll,
    vote_view
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='index'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('create_poll/', create_poll, name='create_poll'),
    path('admin/', admin.site.urls),
    path('vote/<int:poll_id>/', vote_view, name='vote'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


