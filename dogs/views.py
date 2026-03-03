from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

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

class DogCreateView(CreateView):
    model = Dog
    form_class = DogForm
    template_name = 'dogs/create_update.html'
    extra_context = {
        'title': 'Добавить собаку'
    }
    success_url = reverse_lazy('dogs:dogs_list')

class DogDetailView(DetailView):
    model = Dog
    template_name = 'dogs/detail.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        dog_obj = self.get_object()
        context_data['title'] = f'Подробная информация\n{dog_obj}'
        return context_data

@login_required(login_url='users:user_login')
def dog_detail_view(request, pk):
    # dog_object = Dog.objects.get(pk=pk)
    dog_object = get_object_or_404(Dog, pk=pk)
    context = {
        'object': dog_object,
        'title': f'Вы выбрали: {dog_object}'
        # 'title': f'Вы выбрали: {dog_object.name}. Порода: {dog_object.breed_name}',
    }
    return render(request, 'dogs/detail.html', context)

@login_required(login_url='users:user_login')
def dog_update_view(request, pk):
    dog_object = get_object_or_404(Dog, pk=pk)
    if request.method == 'POST':
        form = DogForm(request.POST, request.FILES, instance=dog_object)
        if form.is_valid():
            dog_object = form.save()
            dog_object.save()
            return HttpResponseRedirect(reverse('dogs:dog_detail', args={pk: pk}))
    context = {
        'title': 'Изменить собаку',
        'object': dog_object,
        'form': DogForm(instance=dog_object),
    }
    return render(request, 'dogs/create_update.html', context)

@login_required(login_url='users:user_login')
def dog_delete_view(request, pk):
    dog_object = get_object_or_404(Dog, pk=pk)
    if request.method == 'POST':
        dog_object.delete()
        return HttpResponseRedirect(reverse('dogs:dogs_list'))
    context = {
        'title': 'Удалить собаку',
        'object': dog_object
    }
    return render(request, 'dogs/delete.html', context)