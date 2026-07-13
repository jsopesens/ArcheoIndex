from rdflib import SKOS, RDF, Graph, URIRef, Literal


class Thesaurus():
    def __init__(self):
        self.g = Graph()
        self.g.parse('ArcheoIndex_thesaurus.ttl')
        self.uri = URIRef('http://archeoindex.org#')

    def get_ConceptSchemes(self) -> list:
        return self.g.subjects(RDF.type, SKOS.ConceptScheme)

    def get_landing_info(self, subject: URIRef) -> dict:
        '''
        convert subject into information needed in landing page (uri, prefLabel)
        '''
        return {
            'uri': subject.toPython(),
            'prefLabel': self.english_preferredLabel(subject=subject)[0][1].toPython()
        }

    def get_children_of(self, subject: URIRef) -> list[URIRef]:
        children = []
        children.extend(self.g.objects(
            subject=subject, predicate=SKOS.hasTopConcept))
        children.extend(self.g.objects(
            subject=subject, predicate=SKOS.narrower))
        return children

    def get_subject_by_notation(self, notation: int) -> URIRef:
        subjects = self.g.subjects(
            predicate=SKOS.notation, object=Literal(notation))
        for subject in subjects:
            return subject

    def subject_has_children(self, subject: str) -> bool:
        return self.has_hasTopConcept(URIRef(subject)) or self.has_narrower(URIRef(subject))

    def has_hasTopConcept(self, subject: URIRef) -> bool:
        return self.check_subject_predicate(subject, SKOS.hasTopConcept)

    def has_narrower(self, subject: URIRef) -> bool:
        return self.check_subject_predicate(subject, SKOS.narrower)

    def check_subject_predicate(self, subject: URIRef, predicate) -> bool:
        return (subject, predicate, None) in self.g

    def keyword_exists(self, subject: str) -> bool:
        return (URIRef(self.uri+subject), None, None) in self.g

    def get_keyword_data(self, subject: str):
        triples = self.g.triples(
            triple=(URIRef(self.uri + subject), None, None))

        data = {}
        for s, predicate, object in triples:
            predicate = predicate.toPython().split('#')[1]
            if predicate not in data:
                data[predicate] = [object]
            else:
                data[predicate].append(object)

        relational_predicates = ['broader', 'narrower', 'hasTopConcept', 
                                 'topConceptOf', 'inScheme', 'related']

        descriptive_predicates = ['definition', 'prefLabel',
                                  'altLabel', 'hiddenLabel']

        for key, values in data.items():
            if key in relational_predicates:
                data[key] = self.convert_uris_into_dict(values)

            if key in descriptive_predicates:
                data[key] = [{'lang': value.language, 'value': value.value}
                             for value in values]

            if key == 'notation':
                data[key] = values[0]

        for label in data.get('prefLabel', []):
            if label.get('lang') == 'en':
                data['title'] = label['value'].title()

        return data

    def convert_uris_into_dict(self, uris: list[URIRef]):
        return [self.get_landing_info(uri) for uri in uris]

    def get_keywords_matching(self, search: str):
        # search into all the prefLabels and hidden labels if they match with search parameter
        prefLabels = self.g.subject_objects(SKOS.prefLabel)
        hiddenLabels = self.g.subject_objects(SKOS.hiddenLabel)
        literal_labels = list(prefLabels) + list(hiddenLabels)
        matching_labels = [{'uri':str(subj),'label': str(obj)} for subj, obj in literal_labels if search.lower() in str(obj).lower()]

        return matching_labels

    def english_preferredLabel(self, subject):
        default = []
        # setup the language filtering
        def langfilter(l_):
            return l_.language == 'en'

        labels = list(filter(langfilter, self.g.objects(subject, SKOS.prefLabel)))
        if len(labels) == 0:
            return default
        else:
            return [(SKOS.prefLabel, l_) for l_ in labels]

    def get_top_concepts(self, scheme_uri: URIRef, limit: int = 5) -> list:
        top_concept_uris = list(self.g.objects(subject=scheme_uri, predicate=SKOS.hasTopConcept))
        top_concepts = []
        for uri in top_concept_uris[:limit]:
            try:
                top_concepts.append(self.get_landing_info(uri))
            except Exception:
                continue
        # Split URIs for templates
        for concept in top_concepts:
            concept['uri'] = concept['uri'].split('#')[1]
        return top_concepts

    def get_all_keyword_ids(self) -> list[str]:
        ids = []
        for concept_type in [SKOS.Concept, SKOS.ConceptScheme]:
            for uri in self.g.subjects(RDF.type, concept_type):
                if uri.toPython().startswith(self.uri.toPython()):
                    ids.append(uri.toPython().split('#')[1])
        return ids

    def get_term_of_the_day(self) -> dict:
        concepts = list(self.g.subjects(RDF.type, SKOS.Concept))
        if not concepts:
            return None
        
        import datetime
        import hashlib
        
        today_str = datetime.date.today().isoformat()
        hash_val = int(hashlib.md5(today_str.encode('utf-8')).hexdigest(), 16)
        
        # Filter to concepts that have a definition to make it interesting
        concepts_with_definition = []
        for concept in concepts:
            if (concept, SKOS.definition, None) in self.g:
                concepts_with_definition.append(concept)
                
        choices = concepts_with_definition if concepts_with_definition else concepts
        random_index = hash_val % len(choices)
        selected_concept = choices[random_index]
        
        keyword_name = selected_concept.toPython().split('#')[1]
        data = self.get_keyword_data(keyword_name)
        data['keyword'] = keyword_name
        return data
        