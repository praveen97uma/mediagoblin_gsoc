import logging

from mediagoblin.db.models import MediaEntry

from mediagoblin.plugins.search import schemas
from mediagoblin.plugins.search.base import SearchIndex
from mediagoblin.plugins.search import registry

_log = logging.getLogger(__name__)

media_entry_search_index = SearchIndex(
    model = MediaEntry,
    schema = schemas.MediaEntryIndexSchema,
)


def register_indices():
    registry.IndexRegistry.register(media_entry_search_index)
    _log.info("Registered %(index_name)s index for %(model_name)s"%({
        'index_name': media_entry_search_index.__class__.__name__,
        'model_name': MediaEntry.__class__.__name__}))


