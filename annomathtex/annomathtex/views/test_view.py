from django.shortcuts import render
from django.views.generic import TemplateView
from ..latexprocessing.process_latex_file import get_processed_file




class TestView(TemplateView):
    #template_name = "render_file_template.html"
    template_name = "test2.html"


