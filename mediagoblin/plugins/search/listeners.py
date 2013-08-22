import logging

from sqlalchemy import event

from mediagoblin.plugins.search import registry

_log = logging.getLogger(__name__)


class ORMEventsListener(object):
    def __init__(self, model):
        self.model = model
        self.index_registry = registry.IndexRegistry
        self.listeners = []

    def _after_insert_event_listener(self):
        try:
            event.listen(self.model, 'after_insert',
                self.insert_event_handler)
        except Exception, e:
            _log.debug("Listener activation failed: %s"%(e))
        _log.info("Listening for after_insert event for %s",self.model.__name__)

    def _after_update_event_listener(self):
        try:
            event.listen(self.model, 'after_update',
                self.update_event_handler)
        except Exception as e:
            _log.debug("Listener activation failed: %s"%(e))
        _log.info("Listening for after_update event for %s",self.model.__name__)
    
    def _after_delete_event_listener(self):
        try:
            event.listen(self.model, 'after_delete',
                self.delete_event_handler)
        except Exception as e:
            _log.debug("Listener activation failed: %s"%(e))
        _log.info("Listening for after_delete event for %s",self.model.__name__)

    def insert_event_handler(self, mapper, connection, target):
        index = self.index_registry.get_index_for_object(target)
        try:
            index.add_document_from_model_obj(target)
        except Exception as e:
            _log.debug("Failed to add object to index: %s"%(e))

    def update_event_handler(self, mapper, connection, target):
        index = self.index_registry.get_index_for_object(target)
        index.update_document_from_model_obj(target)

    def delete_event_handler(self, mapper, connection, target):
        index = self.index_registry.get_index_for_object(target)
        index.delete_document_from_model_obj(target)
    
    def activate_listeners(self):
        try:
            self.listeners = [
                self._after_insert_event_listener,
                self._after_update_event_listener,
                self._after_delete_event_listener,
            ]
            for listener in self.listeners:
                listener()
        except Exception as e:
            _log.debug("Activating listeners failed: %s"%(e))
