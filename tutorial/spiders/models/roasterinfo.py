from mongoengine import EmbeddedDocument,StringField,EmbeddedDocumentField,ListField

class BatterInfo(EmbeddedDocument):
    name=StringField()
    position=StringField()
    toota=StringField()

class RoasterInfo(EmbeddedDocument):
    teamName=StringField()
    thrower=EmbeddedDocumentField(BatterInfo)
    batters=ListField(EmbeddedDocumentField(BatterInfo))