import logging

from mediagoblin.plugins.search.base import SearchIndex
from mediagoblin.plugins.search import constants as search_constants

from mediagoblin.db.models import MediaEntry

_log = logging.getLogger(__name__)


class MediaEntrySearchIndex(SearchIndex):
    def __init__(self, model, schema, search_index_dir=None,
        use_multiprocessing=None):
        super(MediaEntrySearchIndex, self).__init__(
            model=model, schema=schema,
            identifier=search_constants.MEDIA_ENTRIES,
            search_index_dir=search_index_dir,
            use_multiprocessing=use_multiprocessing)
        self.verbose_name = "Media Entries"
        self.css_id = "media_entries"

    def _interpret_results(self, results, request_obj=None):
        _log.info("Searched in Media Entries")
        all_results = {
            'verbose_name': self.verbose_name,
            'css_id': self.css_id,
            'results': [],
            'total_results_count': len(results),
        }

        obj_ids = set([result['id_stored'] for result in results])
    
        search_results = []
        for obj_id in obj_ids:
            obj = self.model.query.get(obj_id)
            search_results.append(obj)
            #search_results.append({
            #    'slug': obj.slug,
            #    'url': obj.url_for_self(request_obj.urlgen),
            #})
        
        all_results['results'] = search_results

        _log.info("Found results ")
        _log.info(all_results)
        
        return all_results


class MediaTagSearchIndex(SearchIndex):
    def __init__(self, model, schema, search_index_dir=None,
        use_multiprocessing=None):
        super(MediaTagSearchIndex, self).__init__(
            model=model, schema=schema,
            identifier=search_constants.MEDIA_TAGS,
            search_index_dir=search_index_dir,
            use_multiprocessing=use_multiprocessing)
        
        self.verbose_name = "Media Tags"
        self.css_id = "media_tags"

    def _interpret_results(self, results, request_obj):
        _log.info("Searched in Media Tags")
        _log.info(results)
        all_results = {
            'verbose_name': self.verbose_name,
            'css_id': self.css_id,
            'results': [],
            'total_results_count': len(results),
        }
        obj_ids = set([result['id_stored'] for result in results])
        search_results = []
        for obj_id in obj_ids:
            obj = self.model.query.get(obj_id)
            media_entry_obj = MediaEntry.query.get(obj.media_entry)
            search_results.append(media_entry_obj)
            #search_results.append({
            #    'slug': media_entry_obj.slug,
            #    'url': media_entry_obj.url_for_self(request_obj.urlgen)
            #})
        all_results['results'] = search_results
        _log.info("Found results")
        _log.info(all_results)
        return all_results


class MediaCommentSearchIndex(SearchIndex):
    def __init__(self, model, schema, search_index_dir=None,
        use_multiprocessing=None):
        super(MediaCommentSearchIndex, self).__init__(
            model=model, schema=schema,
            identifier=search_constants.MEDIA_COMMENTS,
            search_index_dir=search_index_dir,
            use_multiprocessing=use_multiprocessing)
        
        self.verbose_name = "Media Comments"
        self.css_id = "media_comments"

    def _interpret_results(self, results, request_obj):
        _log.info("Searched in Media Comments")
        _log.info(results)
        all_results = {
            'verbose_name': self.verbose_name,
            'css_id': self.css_id,
            'results': [],
            'total_results_count': len(results),
        }
        obj_ids = set([result['id_stored'] for result in results])
        search_results = []
        for obj_id in obj_ids:
            obj = self.model.query.get(obj_id)
            media_entry_obj = MediaEntry.query.get(obj.media_entry)
            search_results.append(media_entry_obj)
            #search_results.append({
            #    'slug': media_entry_obj.slug,
            #    'url': media_entry_obj.url_for_self(request_obj.urlgen)
            #})
        all_results['results'] = search_results
        _log.info("Found results for Media Comments")
        _log.info(all_results)
        return all_results

