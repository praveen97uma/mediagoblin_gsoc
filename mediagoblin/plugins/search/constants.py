from mediagoblin.db.models import (MediaEntry, MediaTag)
# List of index identifiers
MEDIA_ENTRIES = "media_entries"

MEDIA_TAGS = "media_tags"


ModelIndexMapping = {
    MediaEntry.__tablename__: MEDIA_ENTRIES,
    MediaTag.__tablename__: MEDIA_TAGS,
}

ENABLED_INDICES = ModelIndexMapping.values()

