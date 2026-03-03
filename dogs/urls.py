from django.urls import path
from dogs.views import (index, breeds_list_view, breeds_dogs_list_view, DogsListView, DogCreateView, DogDetailView,
DogUpdateView, DogDeleteView)

from dogs.apps import DogsConfig

app_name = DogsConfig.name

urlpatterns = [
    path('', index, name='index'),
    #breeds
    path('breeds/', breeds_list_view, name='breeds'),
    path('breeds/<int:pk>/dogs/', breeds_dogs_list_view, name='breeds_dogs'),

    #dogs
    path('dogs/', DogsListView.as_view(), name='dogs_list'),
    path('dogs/create/', DogCreateView.as_view(), name='dog_create'),
    path('dogs/detail/<int:pk>/', DogDetailView.as_view(), name='dog_detail'),
    path('dogs/update/<int:pk>/', DogUpdateView.as_view(), name='dog_update'),
    path('dogs/delete/<int:pk>/', DogDeleteView.as_view(), name='dog_delete'),
]
