import logging

from mediagoblin.plugins.search import forms
from mediagoblin.plugins.search import registry

from mediagoblin.tools.response import render_to_response, redirect


_log = logging.getLogger(__name__)


def search_in_indices(request, query):
    indices = registry.IndexRegistry.indices()
    all_results = []
    for index in indices.itervalues():
        results = index.search(query)
        if len(results)>0:
            for result in results:
                obj_id = result['id']
                obj = index.model.query.get(obj_id)
                all_results.append({
                    'slug': obj.slug,
                    'url': obj.url_for_self(request.urlgen),
                })
    return all_results

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
        all_results = search_in_indices(request, query)
        context.update({
            'results': all_results,
            'results_found': True,
            'query': query,
        })

        return render_to_response(request, 'mediagoblin/search/search.html',
                context)

    return render_to_response(request, 'mediagoblin/search/search.html', context)
