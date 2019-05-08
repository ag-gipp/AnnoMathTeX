import json
import logging
import pickle

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from ..forms.testform import TestForm
from jquery_unparam import jquery_unparam
from itertools import zip_longest
from time import time

from ..parsing.txt_parser import TXTParser
from ..parsing.tex_parser import TEXParser
from ..recommendation.arxiv_evaluation_handler import ArXivEvaluationListHandler
from ..recommendation.wikipedia_evaluation_handler import WikipediaEvaluationListHandler
from ..recommendation.static_wikidata_handler import StaticWikidataHandler
from ..forms.uploadfileform import UploadFileForm
from ..forms.save_annotation_form import SaveAnnotationForm
from ..recommendation.math_sparql import MathSparql
from ..recommendation.ne_sparql import NESparql

from ..views.eval_file_writer import EvalFileWriter
from ..config import *


logging.basicConfig(level=logging.INFO)
__LOGGER__ = logging.getLogger(__name__)

__MARKED__ = {}
__UNMARKED__ = {}
__ANNOTATED__ = {}

__LINE_DICTS__ = {}


class FileUploadView(View):
    """
    This view is where everything going on in the frontend is handled.
    """
    form_class = UploadFileForm
    initial = {'key': 'value'}
    save_annotation_form = {'form': SaveAnnotationForm()}
    template_name = 'file_upload_template.html'

    def get_concatenated_recommendations(self, type, wikidata_results, arXiv_evaluation_items,
                                         wikipedia_evaluation_items, word_window):
        """
        Concatenate the recommendations from the various sources and show them in the first column.
        :param wikidata_results: The results that were obtained from querying the wikidata query service API.
        :param arXiv_evaluation_items: The results that were obtained from checking string matches of the character
                                       in the evaluation list from ArXiv. Only for identifiers.
        :param wikipedia_evaluation_items: The results that were obtained from checking string matches of the character
                                           in the evaluation list from Wikipedia. Only for identifiers.
        :param word_window: The named entities (as found by the tagger) that surround the identifier/formula within
                            the text.
        :return: A list of unique results where as long as the source contains more results the order goes Wikidata,
                 ArXiv, Wikipedia, Word Window.
        """



        all_recommendations = zip_longest(
                                              wikidata_results,
                                              arXiv_evaluation_items,
                                              wikipedia_evaluation_items,
                                              word_window,
                                              fillvalue={'name':'__FILLVALUE__'}
                                          )
        count = 0
        seen = ['__FILLVALUE__']
        concatenated_recommendations = []
        for zip_r in all_recommendations:
            #print(zip_r)
            for r in zip_r:
                if count == recommendations_limit: break
                if r['name'] not in seen:
                    if 'qid' not in r:
                        results = NESparql().concatenated_column_search(r['name'])
                        r = results[0] if results else r
                    concatenated_recommendations.append(r)
                    seen.append(r['name'])
                    count += 1


        return concatenated_recommendations

    def get_word_window(self, unique_id):
        """
        This method produces the word window for a selected (by the user) formula or identifier. It iteratively takes
        named entities from the lines before and after the selected token(s) to fill the number of named entities as
        specified by the recommendation limit.
        :param unique_id: The unique id if the token (identifier or formula).
        :return: a list of named entities that appear around the selected token.
        """

        word_window = []
        limit = int(recommendations_limit / 2)

        dicts = self.cache_to_dicts()
        #print(self.cache_to_dicts())
        #__LOGGER__.debug(' Line Dicts: ', dicts)

        identifier_line_dict = dicts['identifiers']
        line_dict = dicts['lines']

        #print(identifier_line_dict)
        #print(line_dict)

        print(unique_id)

        if unique_id in identifier_line_dict:
            line_num = identifier_line_dict[unique_id]

        else:
            return []

        print('AFTER IF ELSE')

        i = 0
        #todo: fix
        while i < limit:
            # lines before
            b = line_num - i
            # lines after
            a = line_num + i

            if b in line_dict:
                for word in reversed(line_dict[b]):
                    # value not yet in word window
                    if not list(filter(lambda d: d['name'] == word.content, word_window)):
                        word_window.append({
                            'name': word.content,
                            #'unique_id': word.unique_id
                        })
                        i += 1
            if a in line_dict:
                for word in reversed(line_dict[a]):
                    # value not yet in word window
                    if not list(filter(lambda d: d['name'] in word.content, word_window)):
                        word_window.append({
                            'name': word.content,
                            #'unique_id': word.unique_id
                        })
            i += 1

        if not word_window:
            word_window = [{}]

        return word_window[:recommendations_limit]

    def dicts_to_cache(self, dicts):
        """

        :param dicts:
        :return:
        """
        path = view_cache_path + 'dicts'

        #print(dicts)

        with open(path, 'wb') as outfile:
            pickle.dump(dicts, outfile)

        __LOGGER__.debug(' Wrote file to {}'.format(path))


    def cache_to_dicts(self):
        """

        :return:
        """
        path = view_cache_path + 'dicts'
        with open(path, 'rb') as infile:
            dicts = pickle.load(infile)
        #delete cached file
        #os.unlink(path)

        #__LOGGER__.debug(' IN CACHE TO DICTS, DICTS: {}'.format(dicts))

        return dicts


    def write_to_eval_file(self, annotations):
        """
        wirte the evaluations to the evaluations file
        :param annotations:
        :return:
        """

        loc = annotations['local']
        glob = annotations['global']

        with open(evaluations_path, 'w') as f:
            for token_content in loc:
                for id in loc[token_content]:
                    row = None


        """"#path defined in config
        with open(evaluations_path, 'r') as f:
            __LOGGER__.debug(' WRITING TO FILE {}'.format(evaluations_path))
            eval_dict = json.load(f)
            for source in evaluation:
                eval_dict[source] += evaluation[source]

        __LOGGER__.debug(eval_dict)
        with open(evaluations_path, 'w') as f:
            __LOGGER__.debug(' WRITING TO FILE {}'.format(evaluations_path))
            json.dump(eval_dict, f)"""






    def handle_file_submit(self, request):
        """
        In this method the user selected file is checked for the type of the file (txt, tex, html,...) and the
        appropriate parser for the file type is selected. After the file is processed by the parser it is returned to
        the frontend for rendering.

        The dictionaries __LINE__DICT__ and __IDENTIFIER_LINE_DICT__ are needed for the creation of the word window
        surrounding a token (it is constructed when the user mouse clicks a token (identifier or formula).

        __LINE__DICT__ is a dictionary of line numbers as keys and a list of the named entities that appear on the

        __IDENTIFIER_LINE_DICT__ is a dictionary of the unique ids of identifiers as keys and the line number they
        appear on as values.

        :param request: Request object. Request made by the user through the frontend.
        :return:
        """
        __LOGGER__.debug('file submit')
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            request_file = request.FILES['file']
            file_name = str(request_file)
            if file_name.endswith('.tex'):
                __LOGGER__.info(' tex file ')
                line_dict, identifier_line_dict, processed_file = TEXParser(request_file, file_name).process()
            elif file_name.endswith('.txt'):
                __LOGGER__.info(' text file ')
                line_dict, identifier_line_dict, processed_file = TXTParser(request_file, file_name).process()
                #__LOGGER__.debug(' identifier_line_dict: {}'.format(identifier_line_dict))
            else:
                line_dict, identifier_line_dict, processed_file = None, None, None

            #__LINE__DICT__, __IDENTIFIER_LINE_DICT__ = line_dict, identifier_line_dict

            #__LINE_DICTS__['identifiers'] = identifier_line_dict
            #__LINE_DICTS__['lines'] = line_dict
            #__LOGGER__.debug(' line dicts after creating: {}'.format(__LINE_DICTS__))

            dicts = {'identifiers': identifier_line_dict, 'lines': line_dict}

            self.dicts_to_cache(dicts)



            return render(request,
                          'annotation_template.html',
                          {'File': processed_file})


        return render(request, "render_file_template.html", self.save_annotation_form)

    def handle_marked(self, request):
        """
        This method receives data from the frontend, when the user mouse clicks the "save" button.

        Annotated items: e.g. the user annotated the identifier "E" with the wikidata item "energy (Q11379)".
        Marked items: A word that wasn't found by the named entity tagger, but the user decided it should have been.
        Unmarked items: A Word that was found by the named entity tagger, but the user decided it shouldn't have been.

        :param request: Request object. Request made by the user through the frontend.
        :return: The rendered response containing the template name and the necessary form.
        """
        items = {k: jquery_unparam(v) for (k, v) in request.POST.items()}
        marked = items['marked']
        unmarked = items['unmarked']
        annotated = items['annotated']
        file_name = items['fileName']['f']

        __LOGGER__.debug(' ITEMS : {}'.format(items))


        __MARKED__.update(marked)
        __UNMARKED__.update(unmarked)
        __ANNOTATED__.update(annotated)
        __LOGGER__.debug(' ANNOTATED: {}'.format(annotated))


        annotation_file_path = create_annotation_file_path(file_name)
        with open(annotation_file_path, 'w') as f:
            __LOGGER__.debug(' WRITING TO FILE {}'.format(annotation_file_path))
            json.dump(__ANNOTATED__, f)

        """"#path defined in config
        with open(evaluations_path, 'r') as f:
            __LOGGER__.debug(' WRITING TO FILE {}'.format(evaluations_path))
            eval_dict = json.load(f)
            for source in evaluation:
                eval_dict[source] += evaluation[source]

        __LOGGER__.debug(eval_dict)
        with open(evaluations_path, 'w') as f:
            __LOGGER__.debug(' WRITING TO FILE {}'.format(evaluations_path))
            json.dump(eval_dict, f)"""

        eval_file_writer = EvalFileWriter(annotated)
        eval_file_writer.write()

        return HttpResponse(
            json.dumps({'testkey': 'testvalue'}),
            content_type='application/json'
        )

    def handle_query_dict(self, request):
        """
        This method handles the use case, when the user selects a token (word, identifier or formula) to annotate.
        Depending on the type of the token, different types of data are sent back to the frontend.

        Identifier:
            - Wikidata query is made
            - ArXiv evaluation list is checked for matches8
            - Wikipedia evaluation list is checked for matches
            - Word window is computed

        Formula:
            - Wikidata query is made
            - Word window is computed

        Word (must not necessarily be named entity, as found by tagger):
            - Wikidata query is made


        For identifier and formulae, additionaly the concatenated results are computed, taking results from each of the
        sources and combining them in one column.

        :param request: Request object. Request made by the user through the frontend.
        :return: The rendered response containing the template name, the necessary form and the response data.
        """
        start = time()
        items = {k: jquery_unparam(v) for (k, v) in request.POST.items()}
        search_string = [k for k in items['queryDict']][0]
        token_type_dict = items['tokenType']
        token_type = [k for k in token_type_dict][0]
        unique_id = [k for k in items['uniqueId']][0]

        __LOGGER__.debug('making wikidata query for search string: {}'.format(search_string))

        concatenated_results, wikidata_results, word_window, \
        arXiv_evaluation_items, wikipedia_evaluation_items = None, None, None, None, None

        if token_type == 'Identifier':
            #wikidata_results = MathSparql().identifier_search(search_string)
            wikidata_results = StaticWikidataHandler().check_identifiers(search_string)
            #arXiv_evaluation_list_handler = ArXivEvaluationListHandler()
            #wikipedia_evaluation_list_handler = WikipediaEvaluationListHandler()
            arXiv_evaluation_items = ArXivEvaluationListHandler().check_identifiers(search_string)
            wikipedia_evaluation_items = WikipediaEvaluationListHandler().check_identifiers(search_string)
            word_window = self.get_word_window(unique_id)
            """concatenated_results = self.get_concatenated_recommendations(
                'identifier',
                wikidata_results,
                arXiv_evaluation_items,
                wikipedia_evaluation_items,
                word_window
            )"""
            concatenated_results = None
        elif token_type == 'Word':
            wikidata_results = NESparql().named_entity_search(search_string)
        elif token_type == 'Formula':
            m = items['mathEnv']
            k = list(m.keys())[0]
            if m[k]:
                math_env = k + '=' + m[k]
            else:
                math_env = k
            __LOGGER__.debug('math_env: {}'.format(math_env))
            wikidata_results = MathSparql().aliases_search(math_env)

        __LOGGER__.debug(' wikidata query made in {}'.format(time()-start))

        __LOGGER__.debug(' word window: {}'.format(word_window))
        __LOGGER__.debug(' wikipedia: {}'.format(wikipedia_evaluation_items))
        __LOGGER__.debug(' arxiv: {}'.format(arXiv_evaluation_items))
        __LOGGER__.debug(' wikidata: {}'.format(wikidata_results))

        def fill_to_limit(dict_list):
            dict_list += [{'name': ''} for _ in range(recommendations_limit-len(dict_list))]
            return dict_list


        return HttpResponse(
            json.dumps({'wikidataResults': fill_to_limit(wikidata_results),
                        'arXivEvaluationItems': fill_to_limit(arXiv_evaluation_items),
                        'wikipediaEvaluationItems': fill_to_limit(wikipedia_evaluation_items),
                        'wordWindow': fill_to_limit(word_window)}),
            content_type='application/json'
        )

    def get(self, request, *args, **kwargs):
        """
        This method handles get request from the frontend.
        :param request: Request object. Request made by the user through the frontend.
        :return: The rendered response containing the template name and the necessary form.
        """
        form = TestForm()
        return render(request, self.template_name, {'form': form})



    def post(self, request, *args, **kwargs):
        """
        This method handles post request from the frontend. Any data being passed to the backend will be passed through
        a post request, meaning that this method will be called for all tasks that require the frontend in any way to
        access the backend.
        :param request: Request object. Request made by the user through the frontend.
        :return: The rendered response containing the template name, the necessary form and the response data (if
                 applicable).
        """
        __LOGGER__.debug('in post {}'.format(os.getcwd()))
        if 'file_submit' in request.POST:
            return self.handle_file_submit(request)

        elif 'marked' in request.POST:
            return self.handle_marked(request)


        elif 'queryDict' in request.POST:
            return self.handle_query_dict(request)

        return render(request, "file_upload_template.html", self.initial)
