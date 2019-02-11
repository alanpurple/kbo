from mongoengine import Document,StringField,IntField,EmbeddedDocumentField,ListField
from . import GameIndex

class Schedule(Document):
    primary=StringField(primary_key=True)
    gameList=ListField(EmbeddedDocumentField(GameIndex))