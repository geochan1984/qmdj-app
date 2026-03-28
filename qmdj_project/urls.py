from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cases/', views.case_list_view, name='case_list'),
    path('cases/create/', views.create_case_view, name='create_case'),
    path('cases/<int:case_id>/', views.case_detail_view, name='case_detail'),
    path('cases/import/', views.import_cases_view, name='import_cases'),
    path('cases/<int:case_id>/ai-status/', views.ai_analysis_status_view, name='ai_analysis_status'),
    path('vip/register/', views.vip_register_view, name='vip_register'),
    path('vip/verify/', views.vip_verify_view, name='vip_verify'),
    path('vip/dashboard/', views.vip_dashboard_view, name='vip_dashboard'),
]
