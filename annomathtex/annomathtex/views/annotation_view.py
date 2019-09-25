import logging
from jquery_unparam import jquery_unparam
from django.shortcuts import render
from django.views.generic import View

from ..forms.uploadfileform import UploadFileForm
from ..forms.save_annotation_form import SaveAnnotationForm
from .helper_classes.token_clicked_handler import TokenClickedHandler
from .helper_classes.file_handler import FileHandler
from .helper_classes.cache_handler import CacheHandler
from .helper_classes.wikipedia_article_name_handler import WikipediaArticleNameHandler
from .helper_classes.session_saved_handler import SessionSavedHandler


logging.basicConfig(level=logging.INFO)
__LOGGER__ = logging.getLogger(__name__)


class AnnotationView(View):
    """
    This view is where everything going on in the frontend is handled.
    """
    form_class = UploadFileForm
    initial = {'key': 'value'}
    save_annotation_form = {'form': SaveAnnotationForm()}
    template_name = 'annotation_template_tmp.html'


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
        items = {k: jquery_unparam(v) for (k, v) in request.POST.items()}
        action = list(items['action'].keys())[0]
        print('action: {}'.format(action))

        if 'file_submit' in request.POST:
            print('file_submit')
            print('annotate_formula_view')
            return FileHandler(request).process_local_file()

        elif action == 'getRecommendations':
            print('get recommendations')
            print('annotate_formula_view')
            return TokenClickedHandler(request, items).get_recommendations()

        elif action == 'saveSession':
            print('save session')
            print('annotate_formula_view')
            return SessionSavedHandler(request, items).save()

        elif action == 'getRenderedWikipediaArticle':
            print('get rendered wikipedia article')
            print('annotate_formula_view')
            return WikipediaArticleNameHandler(request, items).handle_name()

        return render(request, "file_upload_wiki_suggestions_2.html", self.initial)
