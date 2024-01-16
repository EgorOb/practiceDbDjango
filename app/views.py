from django.shortcuts import render
from django.views.generic import View, TemplateView

class IndexView(View):
    def get(self, request):
        return render(request, 'app/index.html')

class BlogView(TemplateView):
    template_name = 'app/blog.html'

class PostDetailView(TemplateView):
    template_name = 'app/post-details.html'

class AboutView(TemplateView):
    template_name = 'app/about.html'