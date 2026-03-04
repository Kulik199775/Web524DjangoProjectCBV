from django.urls import path
from dogs.views import (index, BreedListView, DogBreedsListView, DogsListView, DogCreateView, DogDetailView,
DogUpdateView, DogDeleteView, dog_toggle_activity, DogsDeactivatedListView)

from dogs.apps import DogsConfig
from django.views.decorators.cache import cache_page, never_cache

app_name = DogsConfig.name

urlpatterns = [
    path('', cache_page(60)(index), name='index'),
    #breeds
    path('breeds/', cache_page(60)(BreedListView.as_view()), name='breeds'),
    path('breeds/<int:pk>/dogs/', cache_page(60)(DogBreedsListView.as_view()), name='breeds_dogs'),

    #dogs
    path('dogs/', DogsListView.as_view(), name='dogs_list'),
    path('dogs/deactivate/', DogsDeactivatedListView.as_view(), name='dogs_list_deactivated'),
    path('dogs/create/', never_cache(DogCreateView.as_view()), name='dog_create'),
    path('dogs/detail/<int:pk>/', DogDetailView.as_view(), name='dog_detail'),
    path('dogs/update/<int:pk>/', never_cache(DogUpdateView.as_view()), name='dog_update'),
    path('dogs/toggle/<int:pk>/', dog_toggle_activity, name='dog_toggle_activity'),
    path('dogs/delete/<int:pk>/', DogDeleteView.as_view(), name='dog_delete'),
]
