
class IndexRegistry(object):
    _registry = {}

    @staticmethod
    def register(search_index_obj):
        """
        Registers an index object.
        """
        identifier = search_index_obj.identifier
        IndexRegistry._registry[identifier] = search_index_obj
    
    @staticmethod
    def indices():
        """
        Return all the index objects registered.
        """
        return IndexRegistry._registry

    @staticmethod
    def get(identifier, not_found=None):
        """
        Return an index identified bu the `identifier`.

        Returns `not_found` if the index object was not found.
        in the regstered indices.
        """
        index = IndexRegistry._registry.get(identifier, not_found)
        return index

    @staticmethod
    def get_index_for_object(db_object, not_found=None):
        """
        Returns the index object for the given db model object.
        """
        identifier = db_object.__tablename__
        return IndexRegistry.get(identifier, not_found)


class ListenerRegistry(object):
    _registry = {}

    @staticmethod
    def register(listener_obj):
        """
        Registers a search.listeners.ORMEventsListener object.
        """
        identifier = listener_obj.model.__tablename__
        ListenerRegistry._registry[identifier] = listener_obj
    
    @staticmethod
    def indices():
        """
        Return all the listener objects registered.
        """
        return ListenerRegistry._registry

    @staticmethod
    def get(identifier, not_found=None):
        """
        Return an ORMEventsListener object identified by `identifier`.

        Returns `not_found` if the listener object was not found.
        in the regstered list of listeners.
        """
        listener = ListenerRegistry._registry.get(identifier, not_found)
        return listener