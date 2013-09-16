import logging
import json

from mediagoblin.plugins.search import forms
from mediagoblin.plugins.search import registry
from mediagoblin.plugins.search.base import WhooshResultsCursor
from mediagoblin.plugins.search.base import WhooshResultsPagination
from mediagoblin.plugins.search import constants as search_constants

from mediagoblin.tools.response import render_to_response, redirect


_log = logging.getLogger(__name__)


def search_in_index(query, search_criteria={}, request=None):
    indices = registry.IndexRegistry.indices()
    results_found = False
    
    category = search_criteria.get('category', None)
    
    _log.info(category)
    index = registry.IndexRegistry.get(identifier=category)
    _log.info("second")
    _log.info(index) 
    if not index:
        return (results_found, [])
    page = search_criteria.get('page', 1)
    search_results = index.search(query, request, page=page)
    
    _log.info("Results found %s %s"%(category, page))
    _log.info(search_results)
    
    if len(search_results['results']) > 0:
        results_found = True
    
    return (results_found, search_results)

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

    for (tab, category) in enumerate(categories):
        search_criteria.update({
            'category': category
            })

        (curr_results_found, curr_results) = search_in_index(query, search_criteria)
        
        if not curr_results_found:
            continue

        paginator = WhooshResultsPagination(query, search_criteria,
                curr_results, extra_get_params={'tab': tab})
        curr_results['paginator'] = paginator
        results.append(curr_results)
        results_found |= curr_results_found

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
