"""
Project Mathematics:
    - https://www.wikidata.org/wiki/Wikidata:WikiProject_Mathematics
    - Contains information about properties that can be used to access mathematical content

Wikidata List of Properties:
    - https://www.wikidata.org/wiki/Wikidata:List_of_properties

Wikidata SPARQL examples
    - https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Finding_John_and_Sarah_Connor


Steps:
    1. Get LaTeX math environment
    2. Split into components
        - Mathematical operators
        - Latex commands
        - identifiers
        - numbers
    3. Define sparql query that looks for the identifier
    4. Return ranking



Important:
    - mass: quantity symbol (P416): m
"""




#Gets all items that have the property P2534 (defining formula)
mathematical_expression_query = """
SELECT 
?item ?itemLabel 
WHERE {
  ?item wdt:P2534 ?mathematical_expression;
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""


# also works
mathematical_expression_query2 = """
SELECT 
?item ?itemLabel 
WHERE {
  ?item wdt:P2534 ?defining_formula;
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""


#get all quanity symbols
quantity_symbols = """
SELECT 
?item ?itemLabel ?quantity_symbol
WHERE {
  ?item wdt:P416 ?quantity_symbol;
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""