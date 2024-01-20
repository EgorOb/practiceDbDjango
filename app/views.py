from django.shortcuts import render, get_object_or_404
from django.views.generic import View, TemplateView, DetailView
from .models import Blog, Entry, Tag, Comment


class IndexView(View):
    def get(self, request):
        blogs = Blog.objects.all()
        all_entryes = Entry.objects.all().prefetch_related("authors").select_related("blog")  # Получить все записи с
        # предварительно загруженными отношениям по авторам и блогу
        most_entryes = all_entryes.order_by('-number_of_comments')[:5]  # Получить последние 5 статей по числу комментариев
        fresh_entryes = all_entryes[:5]  # Получить последние 5 статей по дате
        tags = Tag.objects.all()[:10]  # Получить 10 тегов

        return render(request, 'app/index.html', context={"blogs": blogs,
                                                          "most_entryes": most_entryes,
                                                          "entryes": all_entryes[:3],
                                                          "fresh_entryes": fresh_entryes,
                                                          "tags": tags,
                                                          })


class BlogView(TemplateView):
    template_name = 'app/blog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Аналог blog = Blog.objects.get(slug_name=kwargs["name"])
        blog = get_object_or_404(Blog, slug_name=kwargs["name"])  # Если в БД не было найдено объекта, то возвращается ошибка 404
        blogs = Blog.objects.exclude(id=blog.id)
        resent_posts = blog.entryes.all()[:3]  # Вывести последние 3 поста
        # Добавление данных блога в контекст под ключом 'blog', 'resent_posts'
        context['blog'] = blog
        context['blogs'] = blogs
        context['resent_posts'] = resent_posts

        return context


class PostDetailView(DetailView):
    model = Entry  # модель, которая будет браться за основу. В шаблоне можно получить данные из названия модели
    # с маленькой буквы (entry)
    slug_field = "slug_headline"  # Для идентификации объекта по полю slug передаём название поля slug из БД

    # Если хотим обрабатывать slug параметр (оставить комментарием)
    # slug_url_kwarg = "slug" - по умолчанию (этот параметр берется из адресной строки)
    # Если хотим обрабатывать по int параметру (оставить комментарием)
    # pk_url_kwarg = "pk" - по умолчанию (этот параметр берется из адресной строки)

    template_name = 'app/post_detail.html'  # можно не указывать, но тогда по умолчанию файл должен
    # называться и лежать здесь `<app_label>/<model_name><template_name_suffix>.html`, (template_name_suffix
    # это суффикс у шаблона с префиксом по умолчанию '_detail') в нашем случае это будет
    # `app/entry_detail.html`, тогда template_name можно не прописывать, он сам возьмёт его

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["blog_entryes"] = self.get_queryset().filter(blog=context['entry'].blog).exclude(id=context['entry'].id)
        context["blogs"] = Blog.objects.values('name', 'slug_name')
        context["blog_tags"] = Tag.objects.filter(entry__blog=context['entry'].blog).distinct()

        return context


class AboutView(TemplateView):
    template_name = 'app/about.html'


class AboutServiceView(TemplateView):
    template_name = 'app/about_service.html'

class LoginView(TemplateView):
    template_name = 'app/login.html'
