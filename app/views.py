from django.shortcuts import render, get_object_or_404
from django.views.generic import View, TemplateView, DetailView
from .models import Blog, Entry


class IndexView(View):
    def get(self, request):
        blogs = Blog.objects.all()
        all_entryes = Entry.objects.all().prefetch_related("authors").select_related("blog")  # Получить все записи с
        # предварительно загруженными отношениям по авторам и блогу
        most_entryes = all_entryes.order_by('-number_of_comments')[:5]  # Получить последние 5 статей по числу комментариев
        return render(request, 'app/index.html', context={"blogs": blogs, "entryes": most_entryes})


class BlogView(TemplateView):
    template_name = 'app/blog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Аналог blog = Blog.objects.get(slug_name=kwargs["name"])
        blog = get_object_or_404(Blog, slug_name=kwargs["name"])  # Если в БД не было найдено объекта, то возвращается ошибка 404
        blogs = Blog.objects.all()
        resent_posts = blog.entryes.all().order_by("-pub_date")[:3]  # Вывести последние 3 поста
        # Добавление данных блога в контекст под ключом 'blog', 'resent_posts'
        context['blog'] = blog
        context['blogs'] = blogs
        context['resent_posts'] = resent_posts

        return context


class PostDetailView(DetailView):
    model = Entry
    template_name = 'app/post-details.html'


class AboutView(TemplateView):
    template_name = 'app/about.html'


class LoginView(TemplateView):
    template_name = 'app/login.html'
