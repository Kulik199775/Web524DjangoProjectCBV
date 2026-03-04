from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from dogs.forms import DogForm
from dogs.models import Breed, Dog
from users.services import send_dog_creation

def index(request):
    context = {
        'object_list': Breed.objects.all()[:3],
        'title': 'Питомник - Главная'
    }
    return render(request, 'dogs/index.html', context)

def breeds_list_view(request):
    context = {
        'object_list': Breed.objects.all(),
        'title': 'Питомник - Все наши породы'
    }
    return render(request, 'dogs/breeds.html', context)

def breeds_dogs_list_view(request, pk: int):
    breed_item = Breed.objects.get(pk=pk)
    context = {
        'object_list': Dog.objects.filter(breed_id=pk),
        'title': f'Собаки породы - {breed_item}',
        'breed_pk': breed_item.pk,
    }
    return render(request, 'dogs/dogs.html', context)

class DogsListView(ListView):
    model = Dog
    extra_context = {
        'title': 'Питомник все наши собаки'
    }
    template_name = 'dogs/dogs.html'

class DogCreateView(LoginRequiredMixin, CreateView):
    model = Dog
    form_class = DogForm
    template_name = 'dogs/create_update.html'
    extra_context = {
        'title': 'Добавить собаку'
    }
    success_url = reverse_lazy('dogs:dogs_list')

    def form_valid(self, form):
        self.dog_object = form.save()
        self.dog_object.owner = self.request.user
        self.dog_object.save()
        send_dog_creation(self.request.user.email, self.dog_object)
        return super().form_valid(form)

class DogDetailView(DetailView):
    model = Dog
    template_name = 'dogs/detail.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        dog_obj = self.get_object()
        context_data['title'] = f'Подробная информация\n{dog_obj}'
        return context_data

class DogUpdateView(UpdateView):
    model = Dog
    form_class = DogForm
    template_name = 'dogs/create_update.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        dog_obj = self.get_object()
        context_data['title'] = f'Изменить\n{dog_obj}'
        return context_data

    def get_success_url(self):
        return reverse('dogs:dog_detail', args=[self.kwargs.get('pk')])

class DogDeleteView(DeleteView):
    model = Dog
    template_name = 'dogs/delete.html'
    success_url = reverse_lazy('dogs:dogs_list')

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        dog_obj = self.get_object()
        context_data['title'] = f'Удалить\n{dog_obj}'
        return context_data
