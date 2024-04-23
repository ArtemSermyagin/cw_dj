from django.shortcuts import render
# from django.db.models import Сount
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from pytils.translit import slugify

from blog.forms import BlogPostForm
from blog.models import BlogPost
from clients.models import Newsletter, Client


class BlogPostCreateView(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    success_url = reverse_lazy('blog:list')
    extra_context = {
        'title': 'Создание нового блога'
    }

    def form_valid(self, form):
        '''
        при создании динамически формирует slug name для заголовка
        '''
        if form.is_valid():
            new_blog = form.save()
            new_blog.slug = slugify(new_blog.title)
        return super().form_valid(form)


class BlogPostUpdateView(UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    # fields = ('title', 'body', 'preview', 'sign_publication',)
    success_url = reverse_lazy('blog:list')
    extra_context = {
        'title': 'Редактирование блога'
    }

    def form_valid(self, form):
        '''
        при создании динамически формирует slug name для заголовка
        '''
        if form.is_valid():
            new_blog = form.save()
            new_blog.slug = slugify(new_blog.title)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:view', args=[self.kwargs.get('pk')])


class BlogPostDeleteView(DeleteView):
    model = BlogPost
    success_url = reverse_lazy('blog:list')
    extra_context = {
        'title': 'Удаление блога'
    }


class BlogPostDetailView(DetailView):
    model = BlogPost

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        product_item = BlogPost.objects.get(pk=self.kwargs.get('pk'))
        context_data['title'] = f'{product_item.title}'
        return context_data


def num_letter_client(request):
    num_client = Client.objects.count()
    num_letters = Newsletter.objects.count()
    num_letter_create = Newsletter.objects.filter(status='created').count()
    num_letter_started = Newsletter.objects.filter(status='started').count()
    return render(request, 'blog/count_list.html',
                  {'num_client': num_client, 'num_letters': num_letters,
                   'num_letter_create': num_letter_create, 'num_letter_started': num_letter_started})


def get_random_posts(request):
    random_posts = BlogPost.objects.order_by('?')[:3]
    return render(request, 'blog/blogpost_list.html', {'random_posts': random_posts})
