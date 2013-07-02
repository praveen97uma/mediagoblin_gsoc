import os

from mediagoblin.tools import pluginapi
from mediagoblin.plugins.search.exceptions import IndexDoesNotExistsError

from whoosh import index

config = pluginapi.get_config('mediagoblin.plugins.search')

SEARCH_INDEX_DIR = config['search_index_dir']
USE_MULTIPROCESSING = config['use_multiprocessing']


class SearchIndex(object):
    """
    Represents a search index. 

    This class encapsulates various methods of Whoosh API
    for creating, modifying, updating and searching in a search
    index.
    """
    
    def __init__(self, search_index_dir=SEARCH_INDEX_DIR,
            use_multiprocessing=USE_MULTIPROCESSING):
        self.schema = None
        self.search_index = None
        self.search_index_name = self.__class__.__name__.lower()
        self.search_index_dir = search_index_dir
        self.use_multiprocessing = use_multiprocessing

    def _index_exists(self):
        if not self.search_index:
            raise IndexDoesNotExistsError(
                self.search_index_dir, self.search_index_name)
        
        if self.index.exists_in(
            self.search_index_dir, indexname=self.search_index_name):
            return True

        return False
    
    def _check_index_is_valid(self):
        self._index_exists()   


    def _get_writer(self):
        writer = None
        if self.use_multiprocessing:
            writer = MultiSegmentWriter(self.search_index)
        else:
            writer = self.search_index.writer()
        
        return writer


    def create_index(self, schema):
        """
        Creates an index from the supplied `schema`.

        `schema` should be an object of whoosh.fields.Schema.
        """
        if not os.path.exists(self.search_index_dir):
            os.mkdir(self.search_index_dir)

        self.search_index = index.create_in(self.search_index_dir,
                indexname=self.search_index_name)
         
    def add_document(self, **document):
        """
        Adds a document to the index represented by this class.
        """
        self._check_index_is_valid()
        writer = self._get_writer()
        writer.add_document(**document)
        writer.commit()

    def add_documents(self, documents):
        """
        Adds multiple documents to the index.

        documents should be an iterable object composed of dicts.
        """
        self._check_index_is_valid()
        writer = self._get_writer()
        for document in documents:
            writer.add_document(**document)

        writer.commit()

    def update_document(self, document={}):
        """
        Updates an existing document in the index.

        The index must contain a field which is defined as unique and is
        indexed.
        """
        self._check_index_is_valid()
        writer = self._get_writer()
        writer.update_document(**document)
        writer.commit()

