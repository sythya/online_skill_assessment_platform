from django.contrib import admin
from django.urls import path, include
from core import views   # import your custom views

urlpatterns = [

    # Admin panel
    path('admin/', admin.site.urls),

    # Custom login
    path('login/', views.login_view, name='login'),

    # Logout (keep Django logout)
    path('logout/', views.logout_view, name='logout'),

    # Core app
    path('', include('core.urls')),
]