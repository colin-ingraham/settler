from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.catan_board, name='catan_board'),
]