from django.shortcuts import render, get_object_or_404, resolve_url, redirect
from django.views.generic import View, TemplateView, DetailView, CreateView, FormView
from .models import Blog, Entry, Tag, Comment, AuthorProfile
from .forms import CommentForm, CustomUserCreationForm, EntryForm
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied


class IndexView(View):
    def get(self, request):
        blogs = Blog.objects.all()
        all_entryes = Entry.objects.all().prefetch_related("authors").select_related("blog")  # Получить все записи с
        # предварительно загруженными отношениям по авторам и блогу
        most_entryes = all_entryes.order_by('-number_of_comments')[:5]  # Получить последние 5 статей по числу комментариев
        fresh_entryes = all_entryes[:5]  # Получить последние 5 статей по дате
        tags = Tag.objects.all()[:10]  # Получить 10 тегов

        # Применение пагинации, для реализации постраничного вывода

        paginator = Paginator(all_entryes, 3)  # Показывать по 3 статей на странице. Можно передать параметр пользователь сам решит сколько ему покажется
        page = request.GET.get('page')  # по умолчанию передаётся page в параметрах запроса, чтобы понять на какой мы сейчас странице
        try:
            entryes = paginator.page(page)
        except PageNotAnInteger:
            # Если страница не является целым числом, показать первую страницу.
            entryes = paginator.page(1)
        except EmptyPage:
            # Если страница выходит за пределы допустимого диапазона (например, 9999), показать последнюю страницу результатов.
            entryes = paginator.page(paginator.num_pages)

        return render(request, 'app/index.html', context={"blogs": blogs,
                                                          "most_entryes": most_entryes,
                                                          "entryes": entryes,
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
        context["blog_tags"] = Tag.objects.filter(entry__blog=blog).distinct()
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

    def post(self, request, *args, **kwargs):
        form = CommentForm(data=request.POST)
        if form.is_valid():
            user = request.user
            entry = self.get_object()
            text = form.cleaned_data.get('text')
            parent = form.cleaned_data.get('parent')
            Comment.objects.create(user=user, entry=entry, text=text, parent=parent)

        return redirect('app:post-detail', slug=kwargs["slug"])


class PersonalAccountView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'app/personal_account.html'
    login_url = '/login/signin/'
    permission_denied_message = "Доступ разрешен только со статусом автора"
    permission_required = 'app.can_add_entry'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ## Можно явно проверить разрешение
        # if not self.request.user.has_perm('app.can_add_entry'):
        #     raise PermissionDenied(self.permission_denied_message)
        profile_author = get_object_or_404(AuthorProfile, user=self.request.user)  # Проверяем что есть профиль автора
        entries = profile_author.entrys.all()
        comments = Comment.objects.filter(entry__in=entries).filter(parent__isnull=True).order_by('-created_at')[:5]
        context["profile_author"] = profile_author
        context["entries"] = entries
        context["comments"] = comments
        context['entry_form'] = EntryForm()  # Добавляем форму в контекст
        return context

    def post(self, request, **kwargs):
        form = EntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = Entry(blog=form.cleaned_data.get("blog"),
                  headline=form.cleaned_data.get("headline"),
                  slug_headline=form.cleaned_data.get("slug_headline"),
                  summary=form.cleaned_data.get("summary"),
                  body_text=form.cleaned_data.get("body_text"),
                  image=form.cleaned_data.get("image"),
                  pub_date=form.cleaned_data.get("pub_date"))
            profile_author = get_object_or_404(AuthorProfile,
                                               user=self.request.user)
            entry.save()
            entry.authors.add(profile_author)
            entry.tags.add(*form.cleaned_data.get("tags"))

        return redirect('app:personal-account')






class AboutView(TemplateView):
    template_name = 'app/about.html'


class AboutServiceView(TemplateView):
    template_name = 'app/about_service.html'


class LoginView(TemplateView):
    template_name = 'app/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if next_ := self.request.GET.get('next'):
            context["next"] = next_
        return context

    def post(self, request, *args, **kwargs):
        if kwargs["param"] == "signin":
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)  # Авторизируем пользователя в системе
                next_ = request.GET.get("next", "/")  # Реализуем перенаправление,
                # если есть next, то перенаправляем на адрес, иначе на главную страницу
                return redirect(next_)
            else:
                # Обработка ошибок валидации формы
                return render(request, self.template_name, {"form_signin": form})
        elif kwargs["param"] == "signup":
            form = CustomUserCreationForm(data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                email = form.cleaned_data.get('email')
                password = form.cleaned_data.get('password1')
                user = User.objects.create_user(username=username, email=email,
                                                password=password)
                user.save()
                if form.data.get('become-author') == 'on':  # Получили данные о нажатом переключателе
                    AuthorProfile.objects.create(user=user)  # Создали профиль автора для пользователя
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Авторизируем пользователя в системе

                next_ = request.GET.get("next", "/")  # Реализуем перенаправление,
                # если есть next, то перенаправляем на адрес, иначе на главную страницу
                return redirect(next_)
            return render(request, self.template_name, {"form_signup": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("/")
