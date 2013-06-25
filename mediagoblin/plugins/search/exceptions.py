
class BaseSearchError(Exception):
    """
    Base class for all custom exceptions raised
    by the search plugin.
    """

    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class IndexDoesNotExistsError(BaseSearchError):
    """
    Raised when an index does not exist.
    """

    def __init__(self, index_dir, index_name):
        self.msg = ('Index with name %s does not exists in search', 
                    'index directory %s'%(index_dir, index_name))

