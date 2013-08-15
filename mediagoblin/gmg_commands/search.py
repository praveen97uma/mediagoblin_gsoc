import logging

from mediagoblin.plugins.search import utils

_log = logging.getLogger(__name__)


def search_parser_setup(subparser):
    pass

def delete_all_indices(args):
    _log.info("Deleting indices...")
    utils.delete_all_indices()
