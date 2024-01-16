from django.shortcuts import render
from django.views import View
from django.http import HttpRequest


class IndexView(View):
    def get(self, request):
        return render(request, 'app/index.html')

