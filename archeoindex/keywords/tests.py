from django.test import SimpleTestCase

from rdflib import SKOS, Literal

from .thesaurus import Thesaurus
from .concept import Concept, ConceptNotFound

class ConceptExistsTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g

    def test_return_false_for_wrong_format_url(self):
        identifier = 'not_valid_value'
        concept = Concept(self.g, identifier)
        self.assertFalse(concept.exists())

    def test_return_false_for_wrong_concept(self):
        identifier = '0'
        concept = Concept(self.g, identifier)
        self.assertFalse(concept.exists())

    def test_return_true_for_a_good_concept(self):
        identifier = '1'
        concept = Concept(self.g, identifier)
        self.assertTrue(concept.exists())

class CheckPredicateTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g

    def test_return_false_for_subject_that_does_not_exists(self):
        concept = Concept(self.g, '0')

        with self.assertRaises(ConceptNotFound): 
            concept.check_predicate(SKOS.narrower)
    
    def test_return_false_for_wrong_predicate(self):
        concept = Concept(self.g, '1')
        self.assertFalse(concept.check_predicate('wrong_predicate'))

    def test_return_true_for_right_predicate(self):
        concept = Concept(self.g, '1')
        self.assertTrue(concept.check_predicate(SKOS.hasTopConcept))

class hasNarrowerTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g

    def test_return_false_for_wrong_subject(self):
        concept = Concept(self.g, '0')
        with self.assertRaises(ConceptNotFound):
            concept.has_narrower()

    # using concept 'Africa'
    def test_return_true_for_right_subject(self):
        concept = Concept(self.g, '11')
        self.assertTrue(concept.has_narrower())

class hasTopConceptTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g

    def test_return_false_for_wrong_subject(self):
        concept = Concept(self.g, '0')
        with self.assertRaises(ConceptNotFound):
            concept.has_hasTopConcept()

    # using concpet 'Place'
    def test_return_true_for_right_subject(self):
        concept = Concept(self.g, '1')
        self.assertTrue(concept.has_hasTopConcept())

class getObjectsByPredicateTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g

    def test_raise_error_for_concept_that_does_not_exists(self):
        concept = Concept(self.g, '0')
        with self.assertRaises(ConceptNotFound):
            concept.get_objects_by_predicate(SKOS.narrower)
    
    def test_return_empty_for_concept_without_predicate(self):
        concept = Concept(self.g, '1')
        self.assertEqual(concept.get_objects_by_predicate(SKOS.narrower), [])
    
    
    def test_return_values_for_a_filled_concept(self):
        concept = Concept(self.g, '11')
        result = concept.get_objects_by_predicate(SKOS.narrower)
        self.assertGreater(len(result), 0)

class getNarrowerTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g

    def test_raises_error_for_wrong_subject(self):
        concept = Concept(self.g, '0')
        with self.assertRaises(ConceptNotFound):
            concept.get_narrower()

    # using concpet 'Africa'
    def test_return_true_for_right_subject(self):
        concept = Concept(self.g, '11')
        self.assertGreater(len(concept.get_narrower()), 0)
        
class GetHasTopConceptTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g


    def test_raises_error_for_wrong_subject(self):
        concept = Concept(self.g, '0')
        with self.assertRaises(ConceptNotFound):
            concept.get_hasTopConcept()

    # using concpet 'Africa'
    def test_return_true_for_right_subject(self):
        concept = Concept(self.g, '1')
        result = concept.get_hasTopConcept()
        self.assertGreater(len(result), 0)
        
class getChildrenTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g

    def test_raises_error_for_wrong_subject(self):
        concept = Concept(self.g, '0')
        with self.assertRaises(ConceptNotFound):
            concept.get_children()

    # using concpet 'Africa'
    def test_return_true_for_concepts_with_topConcept(self):
        concept = Concept(self.g, '1')
        result = concept.get_children()
        self.assertGreater(len(result), 0)

    def test_return_true_for_concepts_with_narrower(self):
        concept = Concept(self.g, '11')
        result = concept.get_children()
        self.assertGreater(len(result), 0)

class getAllDataTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g

    def test_raises_error_for_wrong_subject(self):
        concept = Concept(self.g, '0')
        with self.assertRaises(ConceptNotFound):
            concept.get_all_data()

    def test_concept_has_three_top_concepts(self):
        concept = Concept(self.g, '1')
        triples = list(concept.get_all_data())
        
        expected_top_concepts = {
            "http://test_thesaurus.org#11",
            "http://test_thesaurus.org#12",
            "http://test_thesaurus.org#13",
        }
        expected_prefLabels = {
            ("lithic"),
            ("lithique"),
            ("lítico"),
        }
        expected_notation = {'1'}

        top_concepts = {
            str(obj)
            for _, predicate, obj in triples
            if predicate == SKOS.hasTopConcept
        }
        notation = {
            str(obj)
            for _, predicate, obj in triples
            if predicate == SKOS.notation
        }
        prefLabels = {
            str(obj)
            for _, predicate, obj in triples
            if predicate == SKOS.prefLabel
        }

        self.assertSetEqual(top_concepts, expected_top_concepts)
        self.assertSetEqual(notation, expected_notation)
        self.assertSetEqual(prefLabels, expected_prefLabels)
