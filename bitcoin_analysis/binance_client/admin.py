from django.contrib import admin
from .models import Candle, CurrentPrice


@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'interval', 'open_time', 'close_price', 'volume']
    list_filter = ['symbol', 'interval', 'open_time']
    search_fields = ['symbol']
    readonly_fields = ['created_at']
    date_hierarchy = 'open_time'


@admin.register(CurrentPrice)
class CurrentPriceAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'price', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
