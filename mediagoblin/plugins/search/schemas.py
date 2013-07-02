from whoosh.fields import Schema
from whoosh.fields import ID
from whoosh.fields import TEXT
from whoosh.fields import DATETIME


class MediaEntrySearchSchema(Schema):
    """
    Represents the schema of the search index corresponding 
    to db.models.MediaEntry objects.
    """
    # id of the media entry object. this field is indexed
    # and is set to be unique so as to facilitate updating
    # of existing documents in the index
    id = ID(unique=True)

    # stores same value as that of id but is stored with the index
    # we need this value if we want to retrieve objects from db
    id_stored = ID(stored=True)

    uploader = TEXT
    title = TEXT
    slug = TEXT
    created = DATETIME
    description = TEXT
    media_type = TEXT
    license = TEXT

