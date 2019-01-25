from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from sparql_queries import mathematical_expression_query, emc_tex, concat



class Sparql:
    """
    https://people.wikimedia.org/~bearloga/notes/wdqs-python.html
    """
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")


    def query(self, query_string):
        self.sparql.setQuery(query_string)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        results_df = pd.io.json.json_normalize(results['results']['bindings'])
        return results_df[['item.value', 'itemLabel.value']]#.head()
        #return results_df[['item.value', 'defining_formula.value']]  # .head()


    def defining_formula_json(self, query_string):
        self.sparql.setQuery(query_string)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        definig_formula = results['results']['bindings'][0]['defining_formula']

        print(type(definig_formula['value']))


    def defining_formula_pd(self, query_string):
        self.sparql.setQuery(query_string)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        results_df = pd.io.json.json_normalize(results['results']['bindings'])
        dfv = results_df[['defining_formula.value']]
        print(dfv)

    def tex_string(self, query_string):
        self.sparql.setQuery(query_string)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        results = results['results']['bindings'][0]
        #link to site
        link = results['item']['value']
        qid = link.split('/')[-1]
        tex_string = results['TeXString']['value']
        item_label = results['itemLabel']['value']
        item_description = results['itemDescription']['value']

        print(qid)
        print(tex_string)
        print(item_label)
        print(item_description)
        print(link)


    def concat(self, query_string):
        self.sparql.setQuery(query_string)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        results = results['results']['bindings'][0]
        for k in results:
            print(k, results[k])


    def formulate_query(self, query, search_string):
        """

        :param query: tuple of query parts
        :param search_item: item that is being searched for, i.e. inserted into query
        :return: entire query
        """
        entire_query = search_string.join(p for p in query)
        return entire_query


    def handle_concat(self, query, search_item):
        entire_query = self.formulate_query(query, search_item)
        self.sparql.setQuery(entire_query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        results = results['results']['bindings'][0]
        print(results)




concat_query = (
"""
SELECT 
?item ?itemLabel ?itemDescription ?searchSpace
WHERE {
     ?item wdt:P1993|wdt:P2534 ?searchSpace;
     FILTER( contains(?searchSpace, """,
""")) 
     #this has to be in the clause, in order to get itemLabel and itemDescription
     SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }     
 }
"""

)


s = Sparql()


_query = concat_query[0] + "'$'" + concat_query[1]

print(_query)
x = '\'$\''

y = '$'

q = concat_query[0] + "\'{}\'".format(y) + concat_query[1]
print(q)
#s.concat(q)

#s.handle_concat(_query, '$')


