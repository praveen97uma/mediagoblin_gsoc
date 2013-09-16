import logging
import os

from mediagoblin.tools import pluginapi
from mediagoblin.tools.pagination import Pagination
from mediagoblin.plugins.search.exceptions import IndexDoesNotExistsError
from mediagoblin.plugins.search.schemas import MediaEntryIndexSchema

import whoosh

from whoosh.qparser import MultifieldParser

_log = logging.getLogger(__name__)


MAX_RESULTS_PER_PAGE = 15


class SearchIndex(object):
    """
    Represents a search index. 

    This class encapsulates various methods of Whoosh API
    for creating, modifying, updating and searching in a search
    index.
    """
    
    def __init__(self, model, schema, identifier=None, search_index_dir=None, use_multiprocessing=None):
        
        self.config = pluginapi.get_config('mediagoblin.plugins.search')
        self.schema = schema()
        self.field_names = self.schema.names()
        
        self.model = model
        if identifier:
            self.identifier = identifier
        else:
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
        """
        Open the associated index this class is associated with for
        reading/writing.
        """
        self.search_index = whoosh.index.open_dir(self.search_index_dir,
                indexname=self.search_index_name)
        

    def _filter_field_names(self, names):
        """
        Removes field names which end with '_stored'. 
        """
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
        """
        Returns a valid writer object for modiying the index.

        Its necessary to open the index every time a modification has
        to be made to the index.
        """
        self._open_search_index()
        writer = None
        if self.use_multiprocessing:
            writer = self.search_index.writer(procs=4, multisegment=True,
                    limitmb=128)
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
            self.search_index = whoosh.index.open_dir(self.search_index_dir,
                indexname=self.search_index_name)
  
            _log.info("Index %s already exists"%(self.search_index_name))
            return

        self.search_index = whoosh.index.create_in(self.search_index_dir,
                indexname=self.search_index_name, schema=self.schema)
        _log.info("Index created with name " + self.search_index_name) 

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

    def update_document(self, **document):
        """
        Updates an existing document in the index.

        The index must contain a field which is defined as unique and is
        indexed.
        """
        self._check_index_is_valid()
        writer = self._get_writer()
        writer.update_document(**document)
        writer.commit()
    
    def _prepare_document_from_obj(self, obj):
        """
        Creates a dict of field names and corresponding values
        from the object received.

        The values present in the dict prepared is actually stored
        in the index. For the stored fields, the value is taken from
        the corresponding non-stored fields. 
        """
        document = {}
        for name in self.field_names:
            try:
                attr = None
                if name.endswith('_stored'):
                    parent_name = name.replace('_stored', '')
                    attr = getattr(obj, parent_name, None)
                else:
                    attr = getattr(obj, name, None)
                
                if isinstance(attr, int):
                    attr = unicode(attr)

                if attr:
                    document[name] = attr
            except AttributeError:
                _log.info("Attribute %s not found in %s"%(
                    name, obj.__class__.__name__))
        return document


    def add_document_from_obj(self, obj):
        """
        Adds a document to the index created from the given obj.
        """
        document = self._prepare_document_from_obj(obj)
        self.add_document(**document)
        _log.info("Added %s with id %s"%(obj.__class__.__name__, 
                                         str(obj.id)))
    
    def update_document_from_obj(self, obj):
        """
        Updates an existing index entry with the data from the given obj.
        """
        document = self._prepare_document_from_obj(obj)
        self.update_document(**document)
        _log.info("Updated %s with id %s"%(obj.__class__.__name__, 
                                         str(obj.id)))

    def delete_document_from_obj(self, obj):
        """
        Deletes an index entry corresponding to the given object.
        """
        id_stored = unicode(obj.id)
        self._open_search_index()
        self.search_index.delete_by_term('id_stored', id_stored)
        _log.info("Deleted %s with id %s"%(obj.__class__.__name__, 
                                         str(obj.id)))

    def _process_query(self, query):
        """
        Returns a whoosh query object for the given user query string.
        """
        query = unicode(query)
        query = MultifieldParser(self.field_names,
                self.schema).parse(query)
        return query

    def _interpret_results(self, results, request):
        """
        Returns the results in a specific structure.

        This method must be overloaded by the derived classes
        as the way of interpreting the results is different for
        different storage objects.

        `request` is passed from the search view. It is needed
        for generating the data for the search results.
        """
        raise NotImplementedError              

    def search(self, query, request, page=1):
        """
        Performs a search against the index for the given user query.
        """
        self._open_search_index()
        with self.search_index.searcher() as searcher:
            query = self._process_query(query)
            results = searcher.search_page(query, page, pagelen=15)
            all_results = self._interpret_results(results, request)
            return all_results


class WhooshResultsPagination(Pagination):
    """
    Extends pagination.Pagination.
    """
    def __init__(self, query, search_criteria, results, per_page=MAX_RESULTS_PER_PAGE,
                 jump_to_id=False, extra_get_params={}):

        self.query = query
        self.search_criteria = search_criteria
        self.results = results
        page = search_criteria.get('page', 1)
        cursor = WhooshResultsCursor(results)
        super(WhooshResultsPagination, self).__init__(page, cursor, per_page,
            jump_to_id, extra_get_params=extra_get_params)

    def __call__(self):

        #from mediagoblin.plugins.search.views import search_in_indices
        #(results_found, all_results) = search_in_indices(self.query,
        #        self.search_criteria)

        if len(self.results['results'])>0:
            return self.cursor
        return []


class WhooshResultsCursor(object):
    def __init__(self, results):
        self.results = results
        self.cursor_iter = results

    def count(self):
        _log.info("In wrc")
        _log.info(self.results)
        return self.results['total_results_count']

    def __iter__(self):
        for res in self.results['results']:
            yield res
