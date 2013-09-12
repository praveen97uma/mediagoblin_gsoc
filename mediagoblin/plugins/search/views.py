import logging
import json

from mediagoblin.plugins.search import forms
from mediagoblin.plugins.search import registry
from mediagoblin.plugins.search.base import WhooshResultsCursor
from mediagoblin.plugins.search.base import WhooshResultsPagination
from mediagoblin.plugins.search import constants as search_constants

from mediagoblin.tools.response import render_to_response, redirect


_log = logging.getLogger(__name__)


def search_in_indices(query, search_criteria={}, request=None):
    indices = registry.IndexRegistry.indices()
    results_found = False
    all_results = []
    
    categories = search_criteria.get('categories', None)
    
    #if categories:
    #    categories = categories.split(',')
    _log.info(categories)
    indices = registry.IndexRegistry.indices(categories=[categories])
    _log.info("second")
    _log.info(indices) 
    
    page = search_criteria.get('page', 1)
    for index in indices:
        _log.info("Page: %s"%(str(page)))
        search_results = index.search(query, request, page=page)
        if len(search_results['results'])>0:
            all_results.append(search_results)
    
    _log.info("Total results found")
    _log.info(all_results)
    
    if all_results:
        results_found = True
    
    return (results_found, all_results)

def search_query(request):
    form = forms.SearchForm(request.form)
    _log.info("Get dict")
    _log.info(request.GET)
    query = request.GET.get('query')
    context = {
        'form': form,
        'results': None,
        'query': query,
        'results_found': False,
    }
    if not query:
        _log.info(query)
        return render_to_response(request, 'mediagoblin/search/search.html',
                context)
    
    search_criteria = {
        'page': int(request.GET.get('page', 1)),
    }

    results_found = False
    results = []
    categories = request.GET.get('categories', None)
    _log.info("prefirst")
    _log.info(categories)
    if not categories:
        categories = search_constants.ENABLED_INDICES
    else:
        _log.info(type(categories))
        categories = categories.split(',')
        
    _log.info("first")
    _log.info(categories)

    for category in categories:
        search_criteria.update({
            'categories': category
            })

        (r_f, r) = search_in_indices(query, search_criteria)
        _log.info(r)
        whoosh_results_cursor = WhooshResultsCursor(r[0])
        paginator = WhooshResultsPagination(search_criteria['page'],
                whoosh_results_cursor, query, search_criteria)
        r[0]['paginator'] = paginator
        results.append(r[0])
        results_found |= r_f

    context.update({
        'results_found': results_found,
        'results': results,
    })
    _log.info("query: %s", query)
    return render_to_response(request, 'mediagoblin/search/search.html',
        context)


def search(request):
    form = forms.SearchForm(request.form)
    query = None
    
    context = {
        'form': form,
        'results': None,
        'query': query,
        'results_found': False,
    }

    if request.method == 'POST' and form.validate():
        query = form.query.data
        result_categories = search_in_indices(request, query)
        context.update({
            'result_categories': result_categories,
            'results_found': True,
            'query': query,
        })

        return render_to_response(request, 'mediagoblin/search/search.html',
                context)

    return render_to_response(request, 'mediagoblin/search/search.html', context)
