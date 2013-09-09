import logging

from mediagoblin.plugins.search import forms
from mediagoblin.plugins.search import registry

from mediagoblin.tools.response import render_to_response, redirect


_log = logging.getLogger(__name__)


def search_in_indices(request, query, search_criteria={}):
    indices = registry.IndexRegistry.indices()
    results_found = False
    all_results = []
    
    categories = search_criteria.get('categories', None)
    
    if categories:
        categories = categories.split(',')

    indices = registry.IndexRegistry.indices(categories=categories)
    
    for index in indices:
        search_results = index.search(query, request)
        if len(search_results['results'])>0:
            all_results.append(search_results)
    
    _log.info("Total results found")
    _log.info(all_results)
    
    if all_results:
        results_found = True
    
    return (results_found, all_results)

def search_query(request):
    form = forms.SearchForm(request.form)
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
        'categories': request.GET.get('categories', None),
    }

    (results_found, results) = search_in_indices(request, query, search_criteria)
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
