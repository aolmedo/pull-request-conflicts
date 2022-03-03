from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from ipe_analysis.models import IPETimeWindow


class HomeView(TemplateView):
    template_name = "index.html"


class IPETimeWindowDetailView(DetailView):
    model = IPETimeWindow
