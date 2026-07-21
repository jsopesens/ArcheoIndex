from rdflib import Graph, URIRef, SKOS, Literal

class ConceptNotFound(LookupError):
    pass

class LabelNotFound(LookupError):
    pass

class ConceptDoesNotHaveDefinitions(LookupError):
    pass

class ConceptDoesNotHaveDefinitionInThatLanguage(LookupError):
    pass

RELATIONAL_PREDICATES = {
    SKOS.broader,
    SKOS.narrower,
    SKOS.related,
    SKOS.hasTopConcept,
    SKOS.inScheme,
}

DESCRIPTIVE_PREDICATES = {
    SKOS.prefLabel,
    SKOS.altLabel,
    SKOS.hiddenLabel,
    SKOS.definition,
}

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

    def has_definition(self) -> bool:
        return self.check_predicate(SKOS.definition)
    
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
        return list(self.graph.triples(triple=(self.subject, None, None)))
    
    def get_definitions(self) -> list[Literal]:
        self.require_exists()
        definitions = self.get_objects_by_predicate(SKOS.definition)
        
        if not definitions:
            raise ConceptDoesNotHaveDefinitions
        
        return [
            {
                "value": str(label),
                "lang": label.language
            } for label in definitions]
    
    def get_definition_in(self, language = "en") -> str: 
        definitions = self.get_definitions()
        for definition in definitions:
            if definition["lang"] == language:
                return definition["value"]
        raise ConceptDoesNotHaveDefinitionInThatLanguage(
            f"Concept Does Not Have Definition in {language}"
        )
    
    def serialize(self) -> dict:
        """
        Serialize the concept into a dictionary ready to be consumed by the frontend.
        """
        self.require_exists()

        # get all in data object
        data = {}
        for _, predicate, obj in self.get_all_data():
            predicate_name = predicate.split("#")[-1]
            data.setdefault(predicate_name, []).append(obj)

        for predicate_name, values in data.items():
            predicate_uri = getattr(SKOS, predicate_name, None)
            
            # prepare relational predicates (broader, narrower, related, hasTopConcept, inScheme)
            if predicate_uri in RELATIONAL_PREDICATES:
                data[predicate_name] = [
                    {
                        "uri": value.split("#")[-1],
                        "prefLabel": Concept(self.graph, value).get_title()
                    }
                    for value in values
                ]

            # prepare descriptive predicates (prefLabel, altLabel, hiddenLabel, definition)
            if predicate_uri in DESCRIPTIVE_PREDICATES:
                data[predicate_name] = [
                    {
                        "lang": value.language,
                        "value": str(value)
                    }
                    for value in values
                ]

            # prepare notation
            if predicate_name == "notation":
                data[predicate_name] = str(values[0])

        data["title"] = self.get_title().title()

        return data