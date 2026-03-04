from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import Http404
from django.forms import inlineformset_factory
from django.core.exceptions import PermissionDenied

from dogs.forms import DogForm, DogParentForm, DogCreateForm
from dogs.services import send_views_mail
from dogs.models import Breed, Dog, DogParent
from users.services import send_dog_creation
from users.models import UserRoles


def index(request):
    context = {
        'object_list': Breed.objects.all()[:3],
        'title': 'Питомник - Главная'
    }
    return render(request, 'dogs/index.html', context)


class BreedListView(ListView):
    model = Breed
    extra_context = {
        'title': 'Все наши породы'
    }
    template_name = 'dogs/breeds.html'


class DogBreedsListView(ListView):
    model = Dog
    template_name = 'dogs/dogs.html'
    extra_context = {
        'title': 'Собаки выбранной породы'
    }

    def get_queryset(self):
        queryset = super().get_queryset().filter(breed_id=self.kwargs.get('pk'))
        queryset = queryset.filter(is_active=True)
        return queryset


class DogsListView(ListView):
    model = Dog
    extra_context = {
        'title': 'Питомник все наши собаки'
    }
    template_name = 'dogs/dogs.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_active=True)
        return queryset


class DogsDeactivatedListView(LoginRequiredMixin, ListView):
    model = Dog
    extra_context = {
        'title': 'Питомник - неактивные собаки'
    }
    template_name = 'dogs/dogs.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role in [UserRoles.MODERATOR, UserRoles.ADMIN]:
            queryset = queryset.filter(is_active=False)
        if self.request.user.role == UserRoles.USER:
            queryset = queryset.filter(is_active=False, owner=self.request.user)
        return queryset


class DogCreateView(LoginRequiredMixin, CreateView):
    model = Dog
    form_class = DogCreateForm
    template_name = 'dogs/create_update.html'
    extra_context = {
        'title': 'Добавить собаку'
    }
    success_url = reverse_lazy('dogs:dogs_list')

    def form_valid(self, form):
        if self.request.user.role != UserRoles.USER:
            raise PermissionDenied
        dog_object = form.save()
        dog_object.owner = self.request.user
        dog_object.save()
        send_dog_creation(self.request.user.email, dog_object)
        return super().form_valid(form)


class DogDetailView(DetailView):
    model = Dog
    template_name = 'dogs/detail.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        dog_object = self.get_object()
        context_data['title'] = f'Подробная информация\n{dog_object}'
        dog_object_increase = get_object_or_404(Dog, pk=dog_object.pk)
        if dog_object.owner != self.request.user and not self.request.user.is_staff:
            # if not self.request.user.is_staff:
            dog_object_increase.views_count()
        if dog_object.owner:
            object_owner_email = dog_object.owner.email
            if dog_object_increase.views % 100 == 0 and dog_object_increase.views != 0:
                send_views_mail(dog_object, object_owner_email, dog_object_increase.views)
        return context_data


class DogUpdateView(LoginRequiredMixin, UpdateView):
    model = Dog
    form_class = DogForm
    template_name = 'dogs/create_update.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        DogParentFormset = inlineformset_factory(Dog, DogParent, form=DogParentForm, extra=1)
        if self.request.method == 'POST':
            formset = DogParentFormset(self.request.POST, instance=self.object)
        else:
            formset = DogParentFormset(instance=self.object)
        dog_object = self.get_object()
        context_data['formset'] = formset
        context_data['title'] = f'Изменить\n{dog_object}'
        return context_data

    def form_valid(self, form):
        context_data = self.get_context_data()
        formset = context_data['formset']
        dog_object = form.save()
        if formset.is_valid():
            formset.instance = dog_object
            formset.save()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        dog_object = super().get_object(queryset)
        # Может редактировать как владелец, так и администрация сайта
        # if self.object.owner != self.request.user and not self.request.user.is_staff:

        # Может редактировать только владелец
        if dog_object.owner != self.request.user:
            raise PermissionDenied()
        return dog_object

    def get_success_url(self):
        return reverse('dogs:dog_detail', args=[self.kwargs.get('pk')])


class DogDeleteView(PermissionRequiredMixin, DeleteView):
    model = Dog
    template_name = 'dogs/delete.html'
    success_url = reverse_lazy('dogs:dogs_list')
    permission_required = 'dogs.delete_dog'
    permission_denied_message = 'У вас нет необходимых прав для этого действия'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        dog_object = self.get_object()
        context_data['title'] = f'Удалить\n{dog_object}'
        return context_data


def dog_toggle_activity(request, pk):
    dog_object = get_object_or_404(Dog, pk=pk)
    if dog_object.is_active:
        dog_object.is_active = False
    else:
        dog_object.is_active = True
    dog_object.save()
    return redirect(reverse('dogs:dogs_list'))
