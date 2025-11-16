from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .algorithm import calculate_node_scores

def catan_board(request):
    """View to render the Catan board interface"""
    return render(request, 'game/board.html')

@csrf_exempt  # Temporary - add CSRF token handling in production
def get_node_scores(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        board_data = data.get('board_data', [])
        
        if not board_data:
            return JsonResponse({'error': 'No board data provided'}, status=400)
        
        scores = calculate_node_scores(board_data)
        
        return JsonResponse({
            'scores': scores,
            'success': True
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'success': False
        }, status=500)