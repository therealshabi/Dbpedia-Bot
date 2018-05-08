from SPARQLWrapper import SPARQLWrapper, JSON
import json
from vocabulary.vocabulary import Vocabulary as vb
from nlp import find_entities
from flask import Flask, request
from flask_restful import Resource, Api
from flask import jsonify


def obtain_result(named_entity, query_properties):
    property_code = []
    properties = open('property.json', 'r')
    properties = json.load(properties)
    print(type(properties))

    noun = query_properties[0]
    noun_synonyms = vb.synonym(noun, format="dict")

    for p, prop in properties.items():
        if prop == noun:
            property_code.append(p)
            break

    if len(property_code)==0:
        for p, prop in properties.items():
            if type(noun_synonyms) != bool:
                for synonym in noun_synonyms.itervalues():
                    if prop == synonym:
                        property_code.append(p)
                        break

    print(property_code)

    if (len(named_entity) != 0):
        if (len(property_code) != 0):
            sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
            query = """SELECT ?label ?property WHERE
                        { 
                        ?entity rdfs:label ?label .
                        ?entity wdt:""" + property_code[0] + """ ?property_id .
                        ?property_id rdfs:label ?property .
                        FILTER (STR(?label) = '""" + named_entity[0] + """') .
                        FILTER (LANG(?property) = "en")
                        }"""
            print query
        else:
            sparql = SPARQLWrapper("https://dbpedia.org/sparql")
            query = """SELECT ?label ?description WHERE
                        { 
                        ?entity rdfs:label ?label .
                        ?entity dbo:abstract ?description .
                        FILTER (STR(?label) = '""" + named_entity[0] + """') .
                        }"""
            print query

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        result = []
        try:
            results = sparql.query().convert()
            print(results)
            for data in results["results"]["bindings"]:
                result.append(data["property"]["value"])

            result = list(set(result))
            response = []
            for i in result:
                print(i)
                response.append(str(i))
            print(response)
            data = {"status": "200", "data": response}
            result = json.dumps(data)
        except:
            response = ["Unable to retrieve data"]
            data = {"status": "500", "data": response}
            result = json.dumps(data)
    else:
        response = ["Unable to retrieve data"]
        data = {"status": "500", "data": response}
        result = json.dumps(data)

    print(result)
    return result


app = Flask(__name__)
api = Api(app)


class Departments_Meta(Resource):
    def get(self):
        return jsonify(departments="Shahbaz")


class Query(Resource):
    def get(self, query):
        print query
        named_entity, query_properties = find_entities(query)
        result = obtain_result(named_entity, query_properties)
        return result
        # We can have PUT,DELETE,POST here. But in our API GET implementation is sufficient


api.add_resource(Query, '/wiki/<string:query>')
api.add_resource(Departments_Meta, '/')

if __name__ == '__main__':
    app.run()
