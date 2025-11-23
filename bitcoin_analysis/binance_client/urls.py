from django.urls import path
from . import views

app_name = 'binance_client'

urlpatterns = [
    path('current-price/', views.current_price_api, name='current_price'),
]
