from django.shortcuts import render
from django.http import Http404, HttpResponse, JsonResponse

from .thesaurus import Thesaurus
from .concept import Concept

thesaurus = Thesaurus()

# TODO clarify meaning of therm_desc
# TODO decople responsabilities (schemes, term_of_the_day, desc)


def home(request):
    schemes = get_scheme_card_data()

    term_of_the_day = thesaurus.get_term_of_the_day()
    term_desc = ""
    if term_of_the_day and 'definition' in term_of_the_day:
        for defn in term_of_the_day['definition']:
            if defn.get('lang') == 'en':
                term_desc = defn['value']
                break
            else:
                term_desc = term_of_the_day['definition'][0]['value']

    return render(request, "keywords/home.html", {
        "schemes": schemes,
        "term_of_the_day": term_of_the_day,
        "term_desc": term_desc
    })


def get_scheme_card_data() -> list[dict]:
    '''
    get and prepare data for every card in the home page. 
    It gets the ConceptSchemes and gets its uri, prefLabel and topConcepts(uri and prefLabel)
    '''
    schemes = []
    # every element will be a card in home
    for conceptSchema in thesaurus.get_ConceptSchemes():
        concept = Concept(thesaurus.g, conceptSchema)

        top_concepts = []
        for top_subject in concept.get_hasTopConcept():
            subject = Concept(thesaurus.g, top_subject)
            top_concepts.append({
                "uri": subject.identifier,
                "prefLabel": subject.get_title()
            })

        schemes.append({
            "uri": concept.identifier,
            "prefLabel": concept.get_title(),
            "top_concepts": top_concepts
        })
    return sorted(schemes, key=lambda x: x['prefLabel'])


def browse(request):
    ConceptScheme_subjects = thesaurus.get_ConceptSchemes()

    keywords = [thesaurus.get_landing_info(
        subject) for subject in ConceptScheme_subjects]

    for keyword in keywords:
        keyword['uri'] = keyword['uri'].split('#')[1]

    return render(request, "keywords/browse.html", {
        "keywords": keywords
    })


def single_keyword(request, keyword: str):
    concept = Concept(thesaurus.g, keyword)

    # check keyword exists
    if not concept.exists():
        raise Http404("Keyword does not exist")

    # return every piece of information associated
    keyword_data = thesaurus.get_keyword_data(keyword)

    relational_predicates = ['broader', 'narrower',
                             'hasTopConcept', 'inScheme', 'related']

    for element_key in relational_predicates:
        if element_key in keyword_data:
            keyword_data[element_key] = split_uris(keyword_data[element_key])

    # Build meta description for SEO from the first available definition
    title = keyword_data.get('title', keyword).replace('_', ' ').title()
    meta_description = f"Archaeological thesaurus entry for {title}."
    if 'definition' in keyword_data:
        for defn in keyword_data['definition']:
            if defn.get('lang') == 'en':
                meta_description = defn['value']
                break
        else:
            meta_description = keyword_data['definition'][0]['value']

    return render(request, 'keywords/single_keyword.html', {
        "keyword_data": keyword_data,
        "meta_description": meta_description,
        "keyword": keyword,
    })


def get_children_of(request, subject_notation: int):
    # get the children of the current element
    concept = Concept(thesaurus.g, subject_notation)
    children_URIs = concept.get_children()

    children = [thesaurus.get_landing_info(child) for child in children_URIs]

    # store if these elements have child to visualize it in frontend
    for child in children:
        child['has_children'] = thesaurus.subject_has_children(child['uri'])
        child['uri'] = child['uri'].split('#')[1]

    # order elements putting first the ones with children
    children = sorted(children, key=lambda x: not x['has_children'])
    response = JsonResponse({'children': children})
    response['X-Robots-Tag'] = 'noindex'
    return response

def getMatchKeywords(request, search: str):
    # get search parameter and search every NamedIndividual that contains that string
    keywords = thesaurus.get_keywords_matching(search)

    keywords = split_uris(keywords)

    response = JsonResponse({'keywords': keywords})
    response['X-Robots-Tag'] = 'noindex'
    return response

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /getMatchKeywords/",
        "Disallow: /get_children_of/",
        "Disallow: /page-404/",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def split_uris(elements: list[dict]) -> list[dict]:
    for element in elements:
        element['uri'] = element['uri'].split('#')[1]
    return elements

def test_404(request):
    return render(request, "404.html", status=404)
