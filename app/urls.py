from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/codeboard/admin', admin.site.urls),
    path('api/admin/', include('admin_dash.urls')),
    path('api/leaderboard/', include('leaderboard.urls')),
    path('api/auth/', include('ccs_auth.urls')),
]
