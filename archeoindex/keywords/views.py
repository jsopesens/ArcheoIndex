from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse

from .thesaurus import Thesaurus

thesaurus = Thesaurus()

def index(request):
    ConceptScheme_subjects = thesaurus.get_ConceptSchemes()
    
    keywords = [thesaurus.get_landing_info(subject) for subject in ConceptScheme_subjects]
    
    for keyword in keywords:
        keyword['uri'] = keyword['uri'].split('#')[1]

    return render(request, "keywords/index.html", {
        "keywords": keywords
    })

def single_keyword(request, keyword: str):
    # check keyword exists
    if not thesaurus.keyword_exists(keyword):
        return HttpResponseNotFound("keyword doesn't exist")

    # return every piece of information associated
    keyword_data = thesaurus.get_keyword_data(keyword)

    relational_predicates = ['broader', 'narrower', 'broaderTransitive',
                            'hasTopConcept', 'topConceptOf','inScheme', 
                            'related', 'semanticRelation']    
    
    for element_key in relational_predicates:
        if element_key in keyword_data:
            keyword_data[element_key] = split_uris(keyword_data[element_key])
    
    return render(request, 'keywords/single_keyword.html', {
        "keyword_data": keyword_data,
    })

def get_children_of(request, subject_notation: int):
    # get the children of the current element
    subject = thesaurus.get_subject_by_notation(notation=subject_notation)
    children_subjects = thesaurus.get_children_of(subject=subject)
    children = [thesaurus.get_landing_info(child) for child in children_subjects]

    # store if these elements have child to visualize it in frontend
    for child in children:
        child['has_children'] = thesaurus.subject_has_children(child['uri'])
        child['uri'] = child['uri'].split('#')[1]

    # order elements putting first the ones with children
    children = sorted(children, key=lambda x: not x['has_children'])
    return JsonResponse({'children': children})

def getMatchKeywords(request, search: str):
    # get search parameter and search every NamedIndividual that contains that string
    keywords = thesaurus.get_keywords_matching(search)

    keywords = split_uris(keywords)

    return JsonResponse({'keywords': keywords})

def split_uris(elements: list[dict]) -> list[dict]:
    for element in elements:
        element['uri'] = element['uri'].split('#')[1]
    return elements
