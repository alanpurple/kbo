from mongoengine import Document,StringField,IntField,EmbeddedDocumentField,ListField
from . import HitLog

class KboLog(Document):
    primary=StringField(primary_key=True)
    innings=ListField(ListField(EmbeddedDocumentField(HitLog)))