from mediagoblin.plugins.search.indices import MediaEntrySearchIndex
from mediagoblin.plugins.search import schemas


class IndexerAndSearcher(object):
    """
    Encapsulates methods that runs the indexing and searching
    tasks.
    """

    def __init__(self, search_index=None, searcher=None):
        self.search_index = search_index

    def search(self, query):
        pass

    def add_document(self, document):
        pass

    def add_documents(self, documents):
        pass



media_entry_indexer = IndexerAndSearcher(MediaEntrySearchIndex)

