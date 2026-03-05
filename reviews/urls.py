from django.urls import path

from reviews.apps import ReviewsConfig
from reviews.views import ReviewListView, ReviewDeactivatedListView

app_name = ReviewsConfig.name

urlpatterns = [
    path('', ReviewListView.as_view(), name='reviews_list'),
    path('deactivated/', ReviewDeactivatedListView.as_view(), name='reviews_deactivated'),
]