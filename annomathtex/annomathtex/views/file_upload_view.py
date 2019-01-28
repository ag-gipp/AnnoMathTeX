from django.shortcuts import render
from django.views.generic import View
from ..forms.uploadfileform import UploadFileForm
from ..forms.save_annotation_form import SaveAnnotationForm
from ..latexprocessing.process_latex_file import get_processed_file
from django.http import HttpResponse
from ..forms.testform import TestForm
from jquery_unparam import jquery_unparam
import json
from django.views.decorators.csrf import csrf_protect




__HIGHLIGHTED__ = {}
__ANNOTATED__ = {}


class FileUploadView(View):
    form_class = UploadFileForm
    initial = {'key': 'value'}
    save_annotation_form = {'form': SaveAnnotationForm()}
    template_name = 'file_upload_template.html'

    def get(self, request, *args, **kwargs):
        form = TestForm()
        return render(request, self.template_name, {'form': form})

    #@csrf_protect
    def post(self, request, *args, **kwargs):

        print('IN POST')

        for k, v in request.POST.items():
            print(k, v)

        if 'file_submit' in request.POST:
            print('in file submit')
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                #TODO add check to see whether file is .tex
                latex_file = get_processed_file(request.FILES['file'])
                return render(request,
                              #'render_file_old.html',
                              'test.html',
                              {'TexFile': latex_file})

            return render(request, "test.html", self.save_annotation_form)

        elif 'highlighted' in request.POST:
            print('in highlighted')
            items = {k:jquery_unparam(v) for (k,v) in request.POST.items()}
            highlighted = items['highlighted']
            annotated = items['annotated']


            #write to database
            __HIGHLIGHTED__.update(highlighted)
            __ANNOTATED__.update(annotated)

            print('__HIGHLIGHTED__: ', __HIGHLIGHTED__)
            print('__ANNOTATED__: ', __ANNOTATED__)




            return HttpResponse(
                json.dumps({'testkey': 'testvalue'}),
                content_type='application/json'
            )


        return render(request, "file_upload_template.html", self.initial)
