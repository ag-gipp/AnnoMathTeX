import os
import urllib3
import json
urllib3.disable_warnings()
from github import Github, GithubException



class DataRepoHandler:
    """
    Handles everything that needs to access the data repo ag-gipp/dataAnnoMathTex.
    """

    def __init__(self, token=os.getenv('apikey', False)):
        self.token = token

        #uncomment for local testing
        #if not token:
        #    from .key import local_token
        #    self.token = local_token

        #uncomment for wmflabs
        if not token:
            print('Token not set')
            exit(2)


        self.g = Github(self.token)
        self.repo = self.g.get_repo("ag-gipp/dataAnnoMathTex")
        self.user = self.g.get_user()
        self.evaluation_folder = 'evaluation'

    def commit_file(self, file_name, file_content):
        #return
        try:
            self.repo.create_file(file_name, "commiting file {}".format(file_name), file_content)
        except GithubException as e:
            print(e)
            contents = self.repo.get_contents(file_name)
            self.repo.update_file(file_name, "updating file {}".format(file_name), file_content, contents.sha)
            print("updating file {}".format(file_name))
            print(file_content)
        except AttributeError as e:
            print(e)
        return

    def delete_file(self, file_name):
        contents = self.repo.get_contents(file_name)
        self.repo.delete_file(file_name, "Deleting file {}".format(file_name), contents.sha)
        return

    def commit_formula_concepts(self, annotations):
        f = FormulaConceptHandler(annotations)
        formulae = f.get_formulae()
        encoded_content = self.repo.get_file_contents('sources/formula_concepts.txt')
        decoded_content = encoded_content.decoded_content
        formula_concepts = json.loads(decoded_content)

        for new_formula_name in formulae:
            if new_formula_name in formula_concepts:
                new_formula_tex_string = formulae[new_formula_name]['TeXStrings'][0]
                if new_formula_tex_string not in formula_concepts[new_formula_name]['TeXStrings']:
                    formula_concepts[new_formula_name]['TeXStrings'].append(new_formula_tex_string)

            else:
                formula_concepts[new_formula_name] = formulae[new_formula_name]

        self.commit_file('sources/formula_concepts.txt', json.dumps(formula_concepts))
        return

    def tmp(self):
        encoded_content = self.repo.get_file_contents('sources/formula_concepts.txt')
        decoded_content = encoded_content.decoded_content
        formula_concepts = json.loads(decoded_content)

        del formula_concepts['dummy_formula']

        self.commit_file('sources/formula_concepts.txt', json.dumps(formula_concepts))

        #print(formula_concepts)


    def commit_manual_recommendations(self, cleaned_manual_recommendations):
        #print('in commit_manual_recommendations')
        encoded_content = self.repo.get_file_contents('sources/manual_recommendations.txt')
        #print(encoded_content)
        decoded_content = encoded_content.decoded_content
        #print(decoded_content)
        existing_manual_recommendations = json.loads(decoded_content)

        #print('cleaned_manual_recommendations: {}'.format(cleaned_manual_recommendations))

        for id_or_f, name in cleaned_manual_recommendations:

            if id_or_f in existing_manual_recommendations:
                #print("{} in existing_manual_recommendations".format(id_or_f))
                for item in existing_manual_recommendations[id_or_f]:
                    if name == item['name']:
                        item['count'] += 1
                        break
            else:
                #print(cleaned_manual_recommendations)
                existing_manual_recommendations[id_or_f] = [{'name': name,
                                                             'count': 1}]


        #print('file: {}'.format(existing_manual_recommendations))
        self.commit_file('sources/manual_recommendations.txt', json.dumps(existing_manual_recommendations))
        return

    def get_manual_recommendations(self):
        encoded_content = self.repo.get_file_contents('sources/manual_recommendations.txt')
        decoded_content = encoded_content.decoded_content
        existing_manual_recommendations = json.loads(decoded_content)
        return existing_manual_recommendations

    def get_formula_concepts(self):
        encoded_content = self.repo.get_file_contents('sources/formula_concepts.txt')
        decoded_content = encoded_content.decoded_content
        formula_concepts = json.loads(decoded_content)
        return formula_concepts

    def commit_annotations(self, annotations_file_name, annotations):
        path = 'annotation/{}'.format(annotations_file_name)
        self.commit_file(path, annotations)
        return

    def commit_evaluation(self, evaluation_file_name, evaluation_csv_string):
        path = 'evaluation/{}'.format(evaluation_file_name)
        self.commit_file(path, evaluation_csv_string)


    def commit_to_repo(self, csv_file_name, csv_file_content, annotations):
        self.commit_file(csv_file_name, csv_file_content)
        self.commit_formula_concepts(annotations)
        return




class FormulaConceptHandler:
    """
    Prepares the formulae for adding to the formula concepts file.
    """

    def __init__(self, annotations):
        self.annotations = annotations

    def extract_formulae(self):
        formulae = {}


        print('FORMULA CONCEPT HANDLER:\n')
        print(self.annotations)

        if 'global' in self.annotations:
            g = self.annotations['global']
            for key in g:
                instance = g[key]
                if instance['type'] == 'Formula':
                    #print(instance)
                    formulae[key.replace('__EQUALS__', '=')] = {
                        'name': instance['name'].replace('__EQUALS__', '=')
                        #'sourcesWithNums': instance['sourcesWithNums']
                    }

        if 'local' in self.annotations:
            l = self.annotations['local']
            for key in l:
                for unique_id in l[key]:
                    instance = l[key][unique_id]
                    if instance['type'] == 'Formula':
                        formulae[key.replace('__EQUALS__', '=')] = {
                            'name': instance['name'].replace('__EQUALS__', '=')
                            #'sourcesWithNums': instance['sourcesWithNums']
                        }

        return formulae


    def add_identifiers(self):
        formulae = self.extract_formulae()
        if 'global' in self.annotations:
            g = self.annotations['global']
            for key in g:
                instance = g[key]
                m = instance['mathEnv']
                is_identifier = True if instance['type'] == 'Identifier' else False
                if m in formulae and is_identifier:
                    if 'identifiers' in formulae[m]:
                        formulae[m]['identifiers'][key] = instance['name']
                    else:
                        formulae[m]['identifiers'] = {key: instance['name']}

        if 'local' in self.annotations:
            l = self.annotations['local']
            for key in l:
                for unique_id in l[key]:
                    instance = l[key][unique_id]
                    m = instance['mathEnv']
                    is_identifier = True if instance['type'] == 'Identifier' else False
                    if m in formulae and is_identifier:
                        if 'identifiers' in formulae[m]:
                            formulae[m]['identifiers'][key] = instance['name']
                        else:
                            formulae[m]['identifiers'] = {key: instance['name']}
        return formulae


    def get_formulae(self):
        formulae = self.add_identifiers()
        reversed_formulae = {}

        for formula_string in formulae:
            name = formulae[formula_string]['name']
            identifiers = formulae[formula_string]['identifiers']
            reversed_formulae[name] = {'TeXStrings': [formula_string],
                                       'Identifiers': identifiers}

        return reversed_formulae



class ManualRecommendationsCleaner:
    """
    Prepares the manual recommendations for adding them to the manual recommendations file.
    """

    def __init__(self, manual_recommendations):
        self.manual_recommendations = manual_recommendations

    def get_recommendations(self):
        cleaned_manual_recommendations = []

        for id_or_f in self.manual_recommendations:
                for num in self.manual_recommendations[id_or_f]:
                    name = self.manual_recommendations[id_or_f][num]['name']
                    id_or_f = id_or_f.replace('__EQUALS__', '=')
                    cleaned_manual_recommendations.append((id_or_f, name))

        return cleaned_manual_recommendations



if __name__ == '__main__':
    #For testing purposes
    from key import local_token
    d = DataRepoHandler(local_token)

    d.tmp()

    #l = ['Angular_velocity.csv', 'Harmonic_oscillator.csv', 'Mass-energy_equivalence.csv', 'Quantum_harmonic_oscillator.csv', 'Velocity.csv', 'sun.csv']
    #for i in l:
    #d.delete_file('evaluation/mass-energy-equivalence.csv')
    #initial_formulae_file = json.dumps({'dummy_formula': {'TeXStrings': ['empty'], 'Identifiers': 'empty'}})
    #initial_formulae_file = json.dumps({})

    #initial_manual_recommendations_file = json.dumps({})
    #initial_manual_recommendations_file = json.dumps({" \\foo{2} E ": [{"name": "fooform", "count": 1}]})
    #d.commit_file('sources/manual_recommendations.txt', initial_manual_recommendations_file)
    #d.commit_file('sources/formula_concepts.txt', initial_formulae_file)
