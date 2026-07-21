from rdflib import SKOS, RDF, Graph, URIRef, Literal
from django.conf import settings
from itertools import chain


class Thesaurus():
    def __init__(self):
        self.g = Graph()
        self.g.parse(settings.THESAURUS_PATH)
        self.uri = URIRef(settings.THESAURUS_URI)


    def get_all_concepts(self) -> list[URIRef]:
        return list(chain(
            self.g.subjects(RDF.type, SKOS.Concept),
            self.g.subjects(RDF.type, SKOS.ConceptScheme)
        ))


    def get_ConceptSchemes(self) -> list:
        return self.g.subjects(RDF.type, SKOS.ConceptScheme)


    def get_keywords_matching(self, search: str):
        '''
        search into all the prefLabels and hidden labels if they match with search parameter
        '''
        labels = (
            list(self.g.subject_objects(SKOS.prefLabel))
            + list(self.g.subject_objects(SKOS.hiddenLabel))
        )

        return [
            (subject, label)
            for subject, label in labels
            if search.lower() in str(label).lower()
        ]


    def get_all_keyword_ids(self) -> list[str]:
        ids = []
        for concept_type in [SKOS.Concept, SKOS.ConceptScheme]:
            for uri in self.g.subjects(RDF.type, concept_type):
                if uri.toPython().startswith(self.uri.toPython()):
                    ids.append(uri.toPython().split('#')[1])
        return ids

