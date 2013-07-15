# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging

from mediagoblin.tools import pluginapi

from mediagoblin.plugins.search import indices

from sqlalchemy import event
from mediagoblin.db.models import MediaEntry

_log = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(__file__)


def mediaentry_add_listener(mapper, connection, target):
    _log.info("Received request for addding mediaentry")
    _log.info(type(connection))
    _log.info(target.title)

def setup_plugin():
    _log.info('Setting up Search...')

    config = pluginapi.get_config(__name__)

    _log.debug('Search config: {0}'.format(config))

    routes = [
        ('mediagoblin.plugins.search.search',
            '/search',
            'mediagoblin.plugins.search.views:search'),
    ]

    pluginapi.register_routes(routes)
    indices.register_indices()
    #event.listen(MediaEntry, 'after_insert', mediaentry_add_listener)
    #event.listen(MediaEntry, 'before_insert', mediaentry_before_add_listener)
    #_log.info("Registered listening event") 


hooks = {
    'setup': setup_plugin}
