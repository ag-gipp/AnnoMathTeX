"""
Project Mathematics:
    - https://www.wikidata.org/wiki/Wikidata:WikiProject_Mathematics
    - Contains information about properties that can be used to access mathematical content

Wikidata List of Properties:
    - https://www.wikidata.org/wiki/Wikidata:List_of_properties

Wikidata SPARQL examples
    - https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples#Finding_John_and_Sarah_Connor

Good tutorial
    - https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial


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




defining_formula_query = (
"""
SELECT 
?item ?itemLabel ?itemDescription ?definingFormula
WHERE {
  ?item wdt:P2534 ?definingFormula;
  FILTER( contains(?definingFormula, """,
"""))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
"""
)

tex_string_query = (
"""
SELECT 
?item ?itemLabel ?itemDescription ?teXString
WHERE {
     ?item wdt:P1993 ?teXString .
     FILTER( contains(?teXString,""",
""")) 
     #this has to be in the clause, in order to get itemLabel and itemDescription
     SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }     
 }
"""
)



