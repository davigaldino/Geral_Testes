from django.contrib import admin
from .models import TradingSignal


@admin.register(TradingSignal)
class TradingSignalAdmin(admin.ModelAdmin):
    list_display = ['candle', 'signal_type', 'confidence_score', 'created_at']
    list_filter = ['signal_type', 'created_at', 'confidence_score']
    search_fields = ['candle__symbol']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('candle')
