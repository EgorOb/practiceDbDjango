from django.shortcuts import render, get_object_or_404
from django.views.generic import View, TemplateView
from .models import Blog, Entry


class IndexView(View):
    def get(self, request):
        blogs = Blog.objects.all()
        entryes = Entry.objects.all().prefetch_related("authors").select_related("blog").order_by('-pub_date')[:5]  # Получить последние 5 статей по времени поста
        return render(request, 'app/index.html', context={"blogs": blogs, "entryes": entryes})


class BlogView(TemplateView):
    template_name = 'app/blog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Аналог blog = Blog.objects.get(slug_name=kwargs["name"])
        blog = get_object_or_404(Blog, slug_name=kwargs["name"])  # Если в БД не было найдено объекта, то возвращается ошибка 404

        # Добавление данных блога в контекст под ключом 'blog'
        context['blog'] = blog

        return context


class PostDetailView(TemplateView):
    template_name = 'app/post-details.html'


class AboutView(TemplateView):
    template_name = 'app/about.html'


class LoginView(TemplateView):
    template_name = 'app/login.html'
