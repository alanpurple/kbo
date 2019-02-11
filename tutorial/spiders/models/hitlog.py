from mongoengine import EmbeddedDocument,StringField,IntField,FloatField

class HitLog(EmbeddedDocument):
    thrower=StringField()
    batter=StringField()
    batterNum=IntField()
    point=StringField()
    result=StringField()
    status=StringField()
    lev=FloatField()
    res=FloatField()
    rea=FloatField()
    wpe=FloatField()
    wpa=FloatField()