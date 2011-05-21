# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011 Free Software Foundation, Inc
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

from webob import Response, exc
from mediagoblin.db.util import DESCENDING
from mediagoblin.util import Pagination

from mediagoblin.decorators import uses_pagination, get_user_media_entry


@uses_pagination
def user_home(request, page):
    """'Homepage' of a User()"""
    user = request.db.User.find_one({
            'username': request.matchdict['user'],
            'status': 'active'})
    if not user:
        return exc.HTTPNotFound()

    cursor = request.db.MediaEntry.find(
        {'uploader': user,
         'state': 'processed'}).sort('created', DESCENDING)

    pagination = Pagination(page, cursor)
    media_entries = pagination()

    #if no data is available, return NotFound
    if media_entries == None:
        return exc.HTTPNotFound()
    
    template = request.template_env.get_template(
        'mediagoblin/user_pages/user.html')

    return Response(
        template.render(
            {'request': request,
             'user': user,
             'media_entries': media_entries,
             'pagination': pagination}))


@get_user_media_entry
def media_home(request, media):
    """'Homepage' of a MediaEntry()"""
    # Check that media uploader and user correspond.
    if media['uploader'].get('username') != request.matchdict['user']:
        return exc.HTTPNotFound()

    template = request.template_env.get_template(
        'mediagoblin/user_pages/media.html')
    return Response(
        template.render(
            {'request': request,
             'media': media}))
