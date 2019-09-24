import json
import logging


from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from jquery_unparam import jquery_unparam
from ..forms.uploadfileform import UploadFileForm
from ..forms.save_annotation_form import SaveAnnotationForm

from ..views.eval_file_writer import EvalFileWriter
from ..views.data_repo_handler import DataRepoHandler, FormulaConceptHandler, ManualRecommendationsCleaner
from .helper_functions import handle_annotations
from ..config import *

from .helper_classes.token_clicked_handler import TokenClickedHandler
from .helper_classes.file_handler import FileHandler
from .helper_classes.cache_handler import CacheHandler
from .helper_classes.wikipedia_query_handler import WikipediaQueryHandler
from .helper_classes.wikipedia_article_name_handler import WikipediaArticleNameHandler


logging.basicConfig(level=logging.INFO)
__LOGGER__ = logging.getLogger(__name__)


class FileUploadView(View):
    """
    This view is where everything going on in the frontend is handled.
    """
    form_class = UploadFileForm
    initial = {'key': 'value'}
    save_annotation_form = {'form': SaveAnnotationForm()}
    #template_name = 'file_upload_wiki_suggestions_2.html'
    template_name = 'annotation_template_tmp.html'


    def handle_marked(self, request):
        """
        This method receives data from the frontend, when the user mouse clicks the "save" button.

        Annotated items: e.g. the user annotated the identifier "E" with the wikidata item "energy (Q11379)".
        Marked items: A word that wasn't found by the named entity tagger, but the user decided it should have been.
        Unmarked items: A Word that was found by the named entity tagger, but the user decided it shouldn't have been.

        :param request: Request object. Request made by the user through the frontend.
        :return: The rendered response containing the template name and the necessary form.
        """
        print('IN HANDLE MARKED')
        items = {k: jquery_unparam(v) for (k, v) in request.POST.items()}
        annotations = items['annotations']
        file_name = items['fileName']['f']
        manual_recommendations = items['manualRecommendations']

        #print(annotations)


        m = ManualRecommendationsCleaner(manual_recommendations)
        cleaned_manual_recommendations = m.get_recommendations()


        new_annotations = handle_annotations(annotations)

        annotation_file_path = create_annotation_file_path(file_name)
        with open(annotation_file_path, 'w') as f:
            __LOGGER__.debug(' WRITING TO FILE {}'.format(annotation_file_path))
            json.dump(new_annotations, f)


        eval_file_writer = EvalFileWriter(new_annotations, file_name)
        #eval_file_writer.write()
        evaluation_csv_string = eval_file_writer.get_csv_for_repo()
        data_repo_handler = DataRepoHandler()
        #file_name = re.sub(r'\..*', '.csv', file_name)

        annotation_file_name = create_annotation_file_name(file_name)
        evaluation_file_name = create_evaluation_file_name(file_name)
        data_repo_handler.commit_manual_recommendations(cleaned_manual_recommendations)
        data_repo_handler.commit_formula_concepts(annotations)
        data_repo_handler.commit_annotations(annotation_file_name, json.dumps(annotations))
        data_repo_handler.commit_evaluation(evaluation_file_name, evaluation_csv_string)

        return HttpResponse(
            json.dumps({'testkey': 'testvalue'}),
            content_type='application/json'
        )


    def get_repo_content(self):
        """
        Get the repo content for the datarepo/annotation folder, i.e. all files that have been annotated in the past.
        :return:
        """
        file_names = DataRepoHandler().list_directory()
        return HttpResponse(
                            json.dumps({'fileNames': file_names}),
                            content_type='application/json'
        )


    def get(self, request, *args, **kwargs):
        """
        This method handles get request from the frontend.
        :param request: Request object. Request made by the user through the frontend.
        :return: The rendered response containing the template name and the necessary form.
        """
        article_name = CacheHandler().read_file_name_cache()
        processed_file = FileHandler(request).get_processed_wikipedia_article(article_name)
        return render(request, self.template_name, {'File': processed_file, 'test': 3})



    def post(self, request, *args, **kwargs):
        """
        This method handles post request from the frontend. Any data being passed to the backend will be passed through
        a post request, meaning that this method will be called for all tasks that require the frontend in any way to
        access the backend.
        :param request: Request object. Request made by the user through the frontend.
        :return: The rendered response containing the template name, the necessary form and the response data (if
                 applicable).
        """
        #items = {k: jquery_unparam(v) for (k, v) in request.POST.items()}
        #print(items)

        if 'file_submit' in request.POST:
            return FileHandler(request).process_local_file()

        elif 'queryDict' in request.POST:
            print('queryDict')
            return TokenClickedHandler(request).get_recommendations()

        elif 'annotations' in request.POST:
            print('annotations')
            return self.handle_marked(request)

        #todo: remove this method from this view (and others that aren't used)
        #todo: check if not used
        elif 'wikipediaSubmit' in request.POST:
            print("WIKIPEDIA SUBMIT")
            return WikipediaQueryHandler(request).get_suggestions()

        elif 'wikipediaArticleName' in request.POST:
            #todo: put in separate method (consistency)
            print('wikipediaArticleName')
            return WikipediaArticleNameHandler(request).handle_name()

        elif 'getRepoContent' in request.POST:
            print('getRepoContent')
            return self.get_repo_content()



        return render(request, "file_upload_wiki_suggestions_2.html", self.initial)
