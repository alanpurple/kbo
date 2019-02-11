import scrapy
from scrapy.selector import Selector
from mongoengine import connect
import json

from .models import HitLog,KboLog,Schedule

connect('kbostatiz',host='10.102.61.251',port=27017)

class StatizSpider(scrapy.Spider):
    name='statiz'

    def start_requests(self):
        url='http://www.statiz.co.kr/boxscore.php'

        schedules=Schedule.objects()
        for elem in schedules:
            for game in elem.gameList:
                formdata={
                    'opt':'5',
                    'date':game.date,
                    'stadium':game.stadium,
                    'hour':str(game.hour)
                }
                self.gameId=game.date+game.stadium+str(game.hour)
                yield scrapy.FormRequest(url,formdata=formdata,callback=self.parse)

    def parse(self,response):

        with open(self.gameId+'.html','wb') as f:
            f.write(response.body)

        # No need to crawl heads, we already know, it's all same
        # heads= response.css('section.content div')[0].xpath('./div')[1].xpath('./div')[1].xpath('./div/div/div').css('table tr')[0].css('th::text').extract()

        rows=response.css('section.content div')[0].xpath('./div')[1].xpath('./div')[1].xpath('./div/div/div').css('table tr')
        data_len=len(rows)-1

        game_data=[]

        # current_inning='1초'
        inning_data=[]

        # offset=0

        for i in range(data_len):
            row=rows[i+1].css('td')
            # texts=row.css('::text').extract()
            inn_data=row[0].css('::text').extract()
            if len(inn_data)!=0:
                # current_inning=inn_data[0]
                game_data.append(inning_data)
                inning_data=[]
            if len(row[1].css('::text').extract())==0:
                continue
            

            data=HitLog()
            data.thrower=row[1].css('::text').extract()[0]
            batter_data=row[2].css('::text').extract()
            data.batterNum=batter_data[0]
            data.batter=batter_data[1]
            p_data=row[3].css('::text').extract()
            if len(p_data)!=0:
                data.point=p_data[0]
            result_data=row[4].css('::text').extract()
            if len(result_data)==2:
                data.result=result_data[0]+result_data[1]
            else:
                data.result=result_data[0]
            data.status=row[5].css('::text').extract()[0]
            data.lev=float(row[7].css('::text').extract()[0])
            data.res=float(row[8].css('::text').extract()[0])
            data.rea=float(row[9].css('::text').extract()[0])
            data.wpe=float(row[10].css('::text').extract()[0][:-1])
            data.wpa=float(row[11].css('::text').extract()[0])

            inning_data.append(data)

        game = KboLog(id=self.gameId)
        game.innings=game_data

        game.save()

        with open(self.gameId+'.json','wb') as jsonfile:
            json.dump(game_data.__dict__,jsonfile)