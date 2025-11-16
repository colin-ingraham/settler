

from django.urls import path
from . import views

urlpatterns = [
    path('', views.catan_board, name='catan_board'),
    path('api/calculate-scores/', views.get_node_scores, name='get_node_scores'),
]