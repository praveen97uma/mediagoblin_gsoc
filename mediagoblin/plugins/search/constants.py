from mediagoblin.db.models import (MediaEntry, MediaTag, MediaComment,
                                   Collection)

# List of index identifiers
MEDIA_ENTRIES = "media_entries"

MEDIA_TAGS = "media_tags"

MEDIA_COMMENTS = "media_comments"

COLLECTIONS = "collections"


ModelIndexMapping = {
    MediaEntry.__tablename__: MEDIA_ENTRIES,
    MediaTag.__tablename__: MEDIA_TAGS,
    MediaComment.__tablename__: MEDIA_COMMENTS,
    Collection.__tablename__: COLLECTIONS,
}

ENABLED_INDICES = ModelIndexMapping.values()

