from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard",),
    path('profile/', views.profile_view, name='profile'),
    path("delete-file/<int:file_id>/", views.delete_file,
         name="delete_file"),
    path("previous-reviews/", views.previous_reviews, name="previous_reviews"),
    path("reanalyze/<int:file_id>/", views.reanalyze_file, name="reanalyze_file"),
    path('all-database/', views.show_all_models, name='all_models'),


]
