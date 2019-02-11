import scrapy
from scrapy.selector import Selector
from mongoengine import connect

from .models import HitLog,KboLog,Schedule,GameIndex

connect('kbostatiz',host='10.102.61.251',port=27017)

class StatizIndexSpider(scrapy.Spider):
    name='statizindex'

    def start_requests(self):
        url='http://www.statiz.co.kr/schedule.php'
        for year in range(2014,2019):
            for month in range(3,12):
                formdata={
                    'opt':str(month),
                    'sy':str(year)
                }
                self.index_date=str(year)+str(month)
                yield scrapy.FormRequest(url,formdata=formdata,callback=self.parse)

    def parse(self,response):
        with open(self.index_date+'.html','wb') as f:
            f.write(response.body)

        raw=response.css('table')[1].css('a')
        
        gamelistjs=[]
        gamelist=[]

        for a in raw: 
            querydata=a.attrib['href'].split('?')[1]
            detail=querydata.split('&') 
            if len(detail)>1: 
                date=detail[0].split('=')[1]
                stadium=detail[1].split('=')[1]
                hour=int(detail[2].split('=')[1])
                gamelistjs.append({
                    'date':date,
                    'stadium':stadium,
                    'hour':hour
                    }) 
                gamelist.append(GameIndex(date=date,stadium=stadium,hour=hour))
        
        schedule=Schedule(primary=self.index_date,gameList=gamelist)
        schedule.save()