import logging
import os

from mediagoblin.tools import pluginapi
from mediagoblin.plugins.search.exceptions import IndexDoesNotExistsError
from mediagoblin.plugins.search.schemas import MediaEntryIndexSchema

import whoosh

from whoosh.filedb.multiproc import MultiSegmentWriter
from whoosh.qparser import MultifieldParser

_log = logging.getLogger(__name__)


class SearchIndex(object):
    """
    Represents a search index. 

    This class encapsulates various methods of Whoosh API
    for creating, modifying, updating and searching in a search
    index.
    """
    
    def __init__(self, model, schema, search_index_dir=None, use_multiprocessing=None):
        
        self.config = pluginapi.get_config('mediagoblin.plugins.search')
        self.schema = schema()
        self.field_names = self.schema.names()
        
        self.model = model
        self.identifier = self.model.__tablename__

        self.search_index = None
        self.search_index_name = ''.join([
            model.__name__,
            self.__class__.__name__.lower()])

        self.search_index_dir = search_index_dir
        if not self.search_index_dir:
            self.search_index_dir = self.config['search_index_dir']
        self.search_index_dir += self.identifier 
        self.use_multiprocessing = use_multiprocessing 
        if not self.use_multiprocessing:
            self.use_multiprocessing = self.config['use_multiprocessing']
    
        self.create_index()

    def _open_search_index(self):
         self.search_index = whoosh.index.open_dir(self.search_index_dir,
                indexname=self.search_index_name)
        

    def _filter_field_names(self, names):
        filtered_names = [name for name in names if not name.endswith('_stored')]
        return filtered_names

    def _index_exists(self):
        """
        Returns whether a valid index exists in self.search_index_dir.
        
        If self.search_index is None, it implies that no index has been
        created yet. In this case, and IndexDoesNotExistsError exception
        is raised.
        """
        if not self.search_index:
            raise IndexDoesNotExistsError(
                self.search_index_dir, self.search_index_name)
        
        if whoosh.index.exists_in(
            self.search_index_dir, indexname=self.search_index_name):
            return True

        return False
    
    def _check_index_is_valid(self):
        self._index_exists()   


    def _get_writer(self):
        self._open_search_index()
        writer = None
        if self.use_multiprocessing:
            writer = MultiSegmentWriter(self.search_index)
        else:
            writer = self.search_index.writer()
        
        return writer


    def create_index(self):
        """
        Creates an index from the supplied `schema`.

        `schema` should be an object of whoosh.fields.Schema.
        """
        if not self.schema:
            return

        if not os.path.exists(self.search_index_dir):
            os.makedirs(self.search_index_dir)
        
        if whoosh.index.exists_in(
            self.search_index_dir, indexname=self.search_index_name):
            _log.info("Index %s already exists"%(self.search_index_name))
            return

        self.search_index = whoosh.index.create_in(self.search_index_dir,
                indexname=self.search_index_name, schema=self.schema)
       

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

    def add_document_from_model_obj(self, model_obj):
        document = {}
        for name in self.field_names:
            try:
                attr = None
                if name.endswith('_stored'):
                    parent_name = name.replace('_stored', '')
                    attr = getattr(model_obj, parent_name)
                else:
                    attr = getattr(model_obj, name)
                
                if isinstance(attr, int):
                    attr = unicode(attr)
                document[name] = attr
            except AttributeError:
                _log.info("Attribute %s not found in %s"%(
                    name, model_obj.__class__.__name__))
        _log.info("Adding document %s"%document['title'])
        
        self.add_document(**document)
    
    def _process_query(self, query):
        query = unicode(query)
        query = MultifieldParser(self.field_names,
                self.schema).parse(query)
        return query

    def _interpret_results(self, results, request):
        _log.info(type(results))
        all_results = []
        for result in results:
            _log.info(result)
            print result.fields()
            obj_id = result['id_stored']
            obj = self.model.query.get(obj_id)
            all_results.append({
                'slug': obj.slug,
                'url': obj.url_for_self(request.urlgen),
            })
        return all_results
                

    def search(self, query, request):
        self._open_search_index()
        with self.search_index.searcher() as searcher:
            query = self._process_query(query)
            results = searcher.search(query)
            all_results = self._interpret_results(results, request)
            return all_results


