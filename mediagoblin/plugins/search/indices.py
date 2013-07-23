import logging

from mediagoblin.plugins.search.base import SearchIndex

from mediagoblin.db.models import MediaEntry

_log = logging.getLogger(__name__)


class MediaEntrySearchIndex(SearchIndex):
    def __init__(self, model, schema, search_index_dir=None,
        use_multiprocessing=None):
        super(MediaEntrySearchIndex, self).__init__(
            model=model, schema=schema, 
            search_index_dir=search_index_dir,
            use_multiprocessing=use_multiprocessing)

    def _interpret_results(self, results, request_obj=None):
        _log.info(type(results))
        all_results = []
        for result in results:
            _log.info(result)
            obj_id = result['id_stored']
            obj = self.model.query.get(obj_id)
            all_results.append({
                'slug': obj.slug,
                'url': obj.url_for_self(request_obj.urlgen),
            })
        return all_results


class MediaTagSearchIndex(SearchIndex):
    def __init__(self, model, schema, search_index_dir=None,
        use_multiprocessing=None):
        super(MediaTagSearchIndex, self).__init__(
            model=model, schema=schema,
            search_index_dir=search_index_dir,
            use_multiprocessing=use_multiprocessing)

    def _interpret_results(self, results, request_obj):
        _log.info(results)
        all_results = []
        for result in results:
            obj_id = result['id_stored']
            obj = self.model.query.get(obj_id)
            media_entry_obj = MediaEntry.query.get(obj.media_entry)
            all_results.append({
                'slug': media_entry_obj.slug,
                'url': media_entry_obj.url_for_self(request_obj.urlgen)
            })

        return all_results



