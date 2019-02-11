import scrapy
from scrapy.selector import Selector
from mongoengine import connect
from urllib.parse import unquote

from .models import HitLog,KboLog,Schedule,GameIndex

# connect('kbostatiz',host='10.102.61.251',port=27017)
connect('kbostatiz')

class StatizIndexSpider(scrapy.Spider):
    name='statizindex'

    def start_requests(self):
        url='http://www.statiz.co.kr/schedule.php'
        for year in range(2014,2019):
            for month in range(3,12):
                if (year==2015 or year==2017) and month==11:
                    continue
                formdata={
                    'opt':str(month),
                    'sy':str(year)
                }
                month_str=str(month)
                if month<10:
                    month_str='0'+month_str
                index_date=str(year)+month_str
                if Schedule.objects(pk=index_date).first()==None:
                    # time.sleep(3)
                    yield scrapy.FormRequest(url,formdata=formdata,callback=self.parse)

    def parse(self,response):
        rows=response.css('table')[1].css('td div.hidden-xs')
        if len(rows)==0:
            return
        raw=[]
        for row in rows:
            raw=raw+row.css('a')
        if len(raw)==0:
            return
        for_date=raw[0].attrib['href'].split('?')[1].split('&')[0].split('=')[1].split('-')
        index_date=for_date[0]+for_date[1]

        with open(index_date+'.html','wb') as f:
            f.write(response.body)
        
        gamelistjs=[]
        gamelist=[]

        for a in raw: 
            querydata=a.attrib['href'].split('?')[1]
            detail=querydata.split('&') 
            if len(detail)>1: 
                date=detail[0].split('=')[1]
                stadium=unquote(detail[1].split('=')[1])
                hour=int(detail[2].split('=')[1])
                gamelistjs.append({
                    'date':date,
                    'stadium':stadium,
                    'hour':hour
                    }) 
                gamelist.append(GameIndex(date=date,stadium=stadium,hour=hour))
        
        schedule=Schedule(primary=index_date,gameList=gamelist)
        schedule.save()