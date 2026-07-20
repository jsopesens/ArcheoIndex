from rdflib import SKOS, RDF, Graph, URIRef, Literal
from django.conf import settings
from itertools import chain

class Thesaurus():
    def __init__(self):
        self.g = Graph()
        self.g.parse(settings.THESAURUS_PATH)
        self.uri = URIRef(settings.THESAURUS_URI)

    def get_all_concepts(self) ->list[URIRef]:
        return list(chain(
            self.g.subjects(RDF.type, SKOS.Concept),
            self.g.subjects(RDF.type, SKOS.ConceptScheme)
        ))

    def get_ConceptSchemes(self) -> list:
        return self.g.subjects(RDF.type, SKOS.ConceptScheme)

    def get_keywords_matching(self, search: str):
        # search into all the prefLabels and hidden labels if they match with search parameter
        prefLabels = self.g.subject_objects(SKOS.prefLabel)
        hiddenLabels = self.g.subject_objects(SKOS.hiddenLabel)
        literal_labels = list(prefLabels) + list(hiddenLabels)
        matching_labels = [{'uri': str(subj), 'label': str(
            obj)} for subj, obj in literal_labels if search.lower() in str(obj).lower()]

        return matching_labels

    def get_all_keyword_ids(self) -> list[str]:
        ids = []
        for concept_type in [SKOS.Concept, SKOS.ConceptScheme]:
            for uri in self.g.subjects(RDF.type, concept_type):
                if uri.toPython().startswith(self.uri.toPython()):
                    ids.append(uri.toPython().split('#')[1])
        return ids
