from mongoengine import Document,StringField,IntField,EmbeddedDocumentField,ListField
from . import HitLog
from . import RoasterInfo

class KboLog(Document):
    primary=StringField(primary_key=True)
    awayTeam=EmbeddedDocumentField(RoasterInfo)
    homeTeam=EmbeddedDocumentField(RoasterInfo)
    innings=ListField(ListField(EmbeddedDocumentField(HitLog)))