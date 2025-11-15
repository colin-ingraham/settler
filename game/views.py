from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def catan_board(request):
    """
    View to render the Catan board interface
    """
    return render(request, 'game/board.html')