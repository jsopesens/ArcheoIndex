from rdflib import Graph, URIRef, SKOS
from django.conf import settings

class ConceptNotFound(LookupError):
    pass

class Concept:
    def __init__(self, graph: Graph, identifier:URIRef):
        self.graph = graph
        self.identifier = identifier
        self.subject = URIRef(f"{settings.THESAURUS_URI}{identifier}")
    
    def exists(self) -> bool:
        return (self.subject, None, None) in self.graph

    def require_exists(self) -> None:
        if not self.exists():
            raise ConceptNotFound(f"Concept {self.identifier} does not exists.")

    def check_predicate(self, predicate: URIRef) -> bool:
        self.require_exists()
        return (self.subject, predicate, None) in self.graph 

    def has_narrower(self) -> bool:
        return self.check_predicate(SKOS.narrower)
    
    def has_hasTopConcept(self) -> bool:
        return self.check_predicate(SKOS.hasTopConcept)

    def get_objects_by_predicate(self, predicate: URIRef) -> list[URIRef]:
        self.require_exists()

        return list(
            self.graph.objects(
                subject=self.subject, 
                predicate=predicate
            )
        )

    def get_narrower(self) -> list[URIRef]:
        return self.get_objects_by_predicate(SKOS.narrower)

    def get_hasTopConcept(self) ->list[URIRef]:
        return self.get_objects_by_predicate(SKOS.hasTopConcept)
    
    def get_children(self) -> list[URIRef]:
        return [
            *self.get_narrower(), 
            *self.get_hasTopConcept()
        ]
    
    def get_all_data(self):
        self.require_exists()
        return self.graph.triples(triple=(self.subject, None, None))
    