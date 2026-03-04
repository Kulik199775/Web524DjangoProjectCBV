from django.urls import path
from dogs.views import (index, breeds_list_view, breeds_dogs_list_view, DogsListView, DogCreateView, DogDetailView,
DogUpdateView, DogDeleteView)

from dogs.apps import DogsConfig
from django.views.decorators.cache import cache_page, never_cache

app_name = DogsConfig.name

urlpatterns = [
    path('', cache_page(60)(index), name='index'),
    #breeds
    path('breeds/', cache_page(60)(breeds_list_view), name='breeds'),
    path('breeds/<int:pk>/dogs/', breeds_dogs_list_view, name='breeds_dogs'),

    #dogs
    path('dogs/', DogsListView.as_view(), name='dogs_list'),
    path('dogs/create/', never_cache(DogCreateView.as_view()), name='dog_create'),
    path('dogs/detail/<int:pk>/', DogDetailView.as_view(), name='dog_detail'),
    path('dogs/update/<int:pk>/', never_cache(DogUpdateView.as_view()), name='dog_update'),
    path('dogs/delete/<int:pk>/', DogDeleteView.as_view(), name='dog_delete'),
]
