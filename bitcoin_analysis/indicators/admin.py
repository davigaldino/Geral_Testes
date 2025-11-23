from django.contrib import admin
from .models import IndicatorValue, SupportResistanceLevel, FibonacciLevel


@admin.register(IndicatorValue)
class IndicatorValueAdmin(admin.ModelAdmin):
    list_display = ['indicator_name', 'candle', 'value', 'created_at']
    list_filter = ['indicator_name', 'created_at']
    search_fields = ['indicator_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'candle__open_time'


@admin.register(SupportResistanceLevel)
class SupportResistanceLevelAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'interval', 'level_type', 'price', 'strength', 'detected_at']
    list_filter = ['symbol', 'interval', 'level_type', 'detected_at']
    search_fields = ['symbol']
    readonly_fields = ['created_at']


@admin.register(FibonacciLevel)
class FibonacciLevelAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'interval', 'level_percentage', 'price', 'detected_at']
    list_filter = ['symbol', 'interval', 'detected_at']
    search_fields = ['symbol']
    readonly_fields = ['created_at']
