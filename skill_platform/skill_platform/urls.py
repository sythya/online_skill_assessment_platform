from django.contrib import admin
from django.urls import path, include
from core import views   # import your custom views
from django.conf import settings
from django.conf.urls.static import static


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
   
# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)