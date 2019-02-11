from mongoengine import EmbeddedDocument,StringField,IntField

class GameIndex(EmbeddedDocument):
    date=StringField()
    stadium=StringField()
    hour=IntField()