
class BaseSearchError(Exception):
    """
    Base class for all custom exceptions raised
    by the search plugin.
    """

    def __init__(self, msg=None):
        self.msg = msg

class IndexDoesNotExistsError(BaseSearchError):
    """
    Raised when an index does not exist.
    """

    def __init__(self, msg='', index_dir='', index_name=''):
        super(IndexDoesNotExistsError, self).__init__(msg)
        message = 'Index with name %(name)s does not exists in search index %(dir)s'
        self.msg = message.format({'name': index_name, 'dir': index_dir})
