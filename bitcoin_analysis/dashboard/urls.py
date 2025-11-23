from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('chart/<str:interval>/', views.chart_view, name='chart'),
    path('indicators/', views.indicators_table, name='indicators'),
    path('signals/', views.signals_panel, name='signals'),
    path('backtesting/', views.backtesting, name='backtesting'),
    path('settings/', views.settings_page, name='settings'),
    path('api/chart-data/<str:interval>/', views.chart_data_api, name='chart_data_api'),
]
