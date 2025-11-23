from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import CurrentPrice


@require_http_methods(["GET"])
def current_price_api(request):
    """
    API endpoint para obter preço atual
    """
    try:
        current_price = CurrentPrice.objects.filter(symbol='BTCUSDT').first()
        if current_price:
            return JsonResponse({
                'symbol': current_price.symbol,
                'price': str(current_price.price),
                'updated_at': current_price.updated_at.isoformat()
            })
        else:
            return JsonResponse({'error': 'Preço não disponível'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
