import logging
import shutil

from subprocess import call

from mediagoblin.plugins import search


_log = logging.getLogger(__name__)


def delete_all_indices():
    all_indices = search.registry.IndexRegistry.indices()

    for index in all_indices.itervalues():
        index_dir = index.search_index_dir
        call(['rm -r %s'%(index_dir)], shell=True)
        _log.info("Deleting index for %s stored in %s"%(
            index.model.__class__.__name__, index_dir)) 


def create_all_indices():
    search.register_indices()

