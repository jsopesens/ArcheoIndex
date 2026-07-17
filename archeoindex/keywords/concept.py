from rdflib import Graph, URIRef, SKOS

class ConceptNotFound(LookupError):
    pass

class LabelNotFound(LookupError):
    pass

class Concept:
    def __init__(self, graph: Graph, subject:URIRef):
        self.graph = graph
        self.subject = subject
        self.identifier = self.subject.split("#")[-1]
    
    def exists(self) -> bool:
        return (self.subject, None, None) in self.graph

    def require_exists(self) -> None:
        if not self.exists():
            raise ConceptNotFound(f"Concept {self.subject} does not exists.")

    def check_predicate(self, predicate: URIRef) -> bool:
        self.require_exists()
        return (self.subject, predicate, None) in self.graph 

    def has_narrower(self) -> bool:
        return self.check_predicate(SKOS.narrower)
    
    def has_hasTopConcept(self) -> bool:
        return self.check_predicate(SKOS.hasTopConcept)

    def has_children(self) -> bool:
        return self.has_narrower() or self.has_hasTopConcept()

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
    
    def get_prefLabels(self) -> list:
        self.require_exists()
        return self.get_objects_by_predicate(SKOS.prefLabel)
    
    def get_title(self, language="en") -> str:
        '''
        gets prefLabel of a conpcet to show in frontend. By default, it returns the text in english.
        '''
        self.require_exists()
        for label in self.get_prefLabels():
            if label.language == language:
                return str(label)
        raise LabelNotFound

    def get_all_data(self):
        self.require_exists()
        return self.graph.triples(triple=(self.subject, None, None))
    