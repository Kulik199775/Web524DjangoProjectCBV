from django.http import HttpResponseForbidden
from django.shortcuts import reverse, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from redis.commands.search.querystring import querystring

from reviews.models import Review
from reviews.forms import ReviewForm
from reviews.utils import generate_slug
from users.models import UserRoles


class ReviewListView(ListView):
    model = Review
    extra_context = {
        'title': 'Наши отзывы',
    }
    template_name = 'reviews/reviews.html'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(sign_of_review=True)
        return queryset


class ReviewDeactivatedListView(ListView):
    model = Review
    extra_context = {
        'title': 'Неактивные отзывы',
    }
    template_name = 'reviews/reviews.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(sign_of_review=False)
        return queryset


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/create_update.html'
    extra_context = {
        'title': 'Добавить отзыв'
    }

    def form_valid(self, form):
        if self.request.user.role not in (UserRoles.USER, UserRoles.ADMIN):
            return HttpResponseForbidden
        self.object = form.save()
        if self.object.slug == 'temp_slug':
            self.object.slug = generate_slug()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class ReviewDetailView(DetailView):
    model = Review
    template_name = 'reviews/detail.html'
    extra_context = {
        'title': 'Просмотр отзыва'
    }


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/create_update.html'

    def get_success_url(self):
        return reverse('reviews:review_detail', kwargs={'slug': self.object.slug})

    def get_object(self, queryset=None):
        review_object = super().get_object(queryset)
        if review_object.author != self.request.user and self.request.user not in [UserRoles.ADMIN,
                                                                                   UserRoles.MODERATOR]:
            raise PermissionDenied
        return review_object

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        review_object = self.get_object()
        context_data['review'] = f'Изменить отзыв\n{review_object.dog}'
        return context_data


class ReviewDeleteView(PermissionRequiredMixin, DeleteView):
    model = Review
    template_name = 'reviews/delete.html'
    permission_required = 'reviews.delete_review'
    extra_context = {
        'title': 'Удалить отзыв'
    }

    def get_object(self, queryset=None):
        review_object = super().get_object(queryset)
        return review_object

    def has_permission(self):
        has_perm = super().has_permission()
        if has_perm:
            return True
        review = self.get_object()
        return review.author == self.request.user

    def get_success_url(self):
        return reverse('reviews:reviews_list')


def review_toggle_activity(request, slug):
    review_object = get_object_or_404(Review, slug=slug)
    if review_object.sign_of_review:
        review_object.sign_of_review = False
        review_object.save()
        return redirect(reverse('reviews:reviews_deactivated'))
    else:
        review_object.sign_of_review = True
        review_object.save()
        return redirect(reverse('reviews:reviews_list'))
