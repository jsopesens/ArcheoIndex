from django.shortcuts import render
from django.http import Http404, HttpResponse, JsonResponse
from rdflib import URIRef
from .thesaurus import Thesaurus
from .concept import Concept

thesaurus = Thesaurus()


def home(request):
    # TODO decople responsabilities (schemes, term_of_the_day, desc)
    schemes = []
    # every element will be a card in home
    for conceptSchema in thesaurus.get_ConceptSchemes():
        result = get_scheme_card_data(conceptSchema)
        schemes.append(result)
    schemes.sort(key=lambda scheme: scheme["prefLabel"])

    return render(request, "keywords/home.html", {
        "schemes": schemes,
        "term_of_the_day": get_term_of_the_day()
    })


def get_scheme_card_data(conceptSchema: URIRef) -> dict:
    '''
    get and prepare data for a card in the home page. 
    It gets the ConceptSchema and gets its uri, prefLabel and topConcepts(uri and prefLabel)
    '''
    concept = Concept(thesaurus.g, conceptSchema)
    top_concepts = []
    for top_subject in concept.get_hasTopConcept():
        subject = Concept(thesaurus.g, top_subject)
        top_concepts.append({
            "uri": subject.identifier,
            "prefLabel": subject.get_title()
        })

    return {
        "uri": concept.identifier,
        "prefLabel": concept.get_title(),
        "top_concepts": top_concepts[:3],
        "has_more_top_concepts": len(top_concepts) > 3
    }


def get_term_of_the_day() -> dict:
    # get all objects with definition (in english)
    terms = thesaurus.get_all_concepts()
    concepts_definitions = []
    for term in terms:
        concept = Concept(thesaurus.g, term)
        if concept.has_definition():
            concepts_definitions.append(
                {"uri": concept.identifier, "definition": concept.get_definition_in("en")}
            )
    
    # randomize object in the list
    import datetime
    import hashlib

    today_str = datetime.date.today().isoformat()
    hash_val = int(hashlib.md5(today_str.encode('utf-8')).hexdigest(), 16)

    random_index = hash_val % len(concepts_definitions)
    selected_concept = concepts_definitions[random_index]    

    return selected_concept


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
