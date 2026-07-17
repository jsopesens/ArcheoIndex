from django.test import SimpleTestCase
from django.conf import settings

from rdflib import SKOS, Literal, URIRef

from .thesaurus import Thesaurus
from .concept import Concept, ConceptNotFound, LabelNotFound


class ThesaurusTestCase(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.thesaurus = Thesaurus()
        cls.g = cls.thesaurus.g

    def concept(self, id) -> Concept:
        return Concept(self.g, URIRef(f"{settings.THESAURUS_URI}{id}"))


class ConceptExistsTests(ThesaurusTestCase):
    def test_return_false_for_wrong_format_url(self):
        concept = self.concept('not_valid_value')
        self.assertFalse(concept.exists())

    def test_return_false_for_wrong_concept(self):
        concept = self.concept(0)
        self.assertFalse(concept.exists())

    def test_return_true_for_a_good_concept(self):
        concept = self.concept(1)
        self.assertTrue(concept.exists())


class CheckPredicateTests(ThesaurusTestCase):
    def test_return_false_for_subject_that_does_not_exists(self):
        concept = self.concept(0)
        with self.assertRaises(ConceptNotFound):
            concept.check_predicate(SKOS.narrower)

    def test_return_false_for_wrong_predicate(self):
        concept = self.concept(1)
        self.assertFalse(concept.check_predicate('wrong_predicate'))

    def test_return_true_for_right_predicate(self):
        concept = self.concept(1)
        self.assertTrue(concept.check_predicate(SKOS.hasTopConcept))


class hasNarrowerTests(ThesaurusTestCase):
    def test_return_false_for_wrong_subject(self):
        concept = self.concept(0)
        with self.assertRaises(ConceptNotFound):
            concept.has_narrower()

    def test_return_true_for_right_subject(self):
        concept = self.concept(11)
        self.assertTrue(concept.has_narrower())


class hasTopConceptTests(ThesaurusTestCase):
    def test_return_false_for_wrong_subject(self):
        concept = self.concept(0)
        with self.assertRaises(ConceptNotFound):
            concept.has_hasTopConcept()

    def test_return_true_for_right_subject(self):
        concept = self.concept(1)
        self.assertTrue(concept.has_hasTopConcept())


class getObjectsByPredicateTests(ThesaurusTestCase):
    def test_raise_error_for_concept_that_does_not_exists(self):
        concept = self.concept(0)
        with self.assertRaises(ConceptNotFound):
            concept.get_objects_by_predicate(SKOS.narrower)

    def test_return_empty_for_concept_without_predicate(self):
        concept = self.concept(1)
        self.assertEqual(concept.get_objects_by_predicate(SKOS.narrower), [])

    def test_return_values_for_a_filled_concept(self):
        concept = self.concept(11)
        result = concept.get_objects_by_predicate(SKOS.narrower)
        self.assertGreater(len(result), 0)


class getNarrowerTests(ThesaurusTestCase):
    def test_raises_error_for_wrong_subject(self):
        concept = self.concept(0)
        with self.assertRaises(ConceptNotFound):
            concept.get_narrower()

    def test_return_true_for_right_subject(self):
        concept = self.concept(11)
        self.assertGreater(len(concept.get_narrower()), 0)


class GetHasTopConceptTests(ThesaurusTestCase):
    def test_raises_error_for_wrong_subject(self):
        concept = self.concept(0)
        with self.assertRaises(ConceptNotFound):
            concept.get_hasTopConcept()

    def test_return_true_for_right_subject(self):
        concept = self.concept(1)
        result = concept.get_hasTopConcept()
        self.assertGreater(len(result), 0)


class getChildrenTests(ThesaurusTestCase):
    def test_raises_error_for_wrong_subject(self):
        concept = self.concept(0)
        with self.assertRaises(ConceptNotFound):
            concept.get_children()

    # using concpet 'Africa'
    def test_return_true_for_concepts_with_topConcept(self):
        concept = self.concept(1)
        result = concept.get_children()
        self.assertGreater(len(result), 0)

    def test_return_true_for_concepts_with_narrower(self):
        concept = self.concept(11)
        result = concept.get_children()
        self.assertGreater(len(result), 0)


class getAllDataTests(ThesaurusTestCase):
    def test_raises_error_for_wrong_subject(self):
        concept = self.concept(0)
        with self.assertRaises(ConceptNotFound):
            concept.get_all_data()

    def test_concept_has_three_top_concepts(self):
        concept = self.concept(1)
        triples = list(concept.get_all_data())
        expected_results = {
            "top_concepts": {
                "http://test_thesaurus.org#11",
                "http://test_thesaurus.org#12",
                "http://test_thesaurus.org#13",
            },
            "prefLabels": {
                "lithic",
                "lithique",
                "lítico",
            },
            "notation": {'1'}
        }

        result = {
            "top_concepts": {
                str(obj)
                for _, predicate, obj in triples
                if predicate == SKOS.hasTopConcept
            },
            "prefLabels": {
                str(obj)
                for _, predicate, obj in triples
                if predicate == SKOS.prefLabel
            },
            "notation": {
                str(obj)
                for _, predicate, obj in triples
                if predicate == SKOS.notation
            },
        }

        self.assertSetEqual(result["top_concepts"], expected_results["top_concepts"])
        self.assertSetEqual(result["prefLabels"], expected_results["prefLabels"])
        self.assertSetEqual(result["notation"], expected_results["notation"])


class getTitleTests(ThesaurusTestCase):
    def test_concept_does_not_exists(self):
        concept = self.concept(0)
        with self.assertRaises(ConceptNotFound):
            concept.get_title()

    # concept designed without labels or narrowers
    def test_concept_does_not_have_prefLabel(self):
        concept = self.concept(200)
        with self.assertRaises(LabelNotFound):
            concept.get_title()

    def test_concept_does_not_have_required_language(self):
        concept = self.concept(1)
        with self.assertRaises(LabelNotFound):
            concept.get_title('xxx')
    
    def test_default_language_english(self):
        concept = self.concept(1)
        self.assertEquals(concept.get_title(), 'lithic')
    
    def test_return_diferent_language(self):
        concept = self.concept(1)
        self.assertEquals(concept.get_title('fr'), 'lithique')

