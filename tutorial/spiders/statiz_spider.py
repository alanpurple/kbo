import scrapy
from scrapy.selector import Selector
from mongoengine import connect
import json
from bson import json_util

from .models import HitLog,KboLog,Schedule

# connect('kbostatiz',host='10.102.61.251',port=27017)
connect('kbostatiz')

class StatizSpider(scrapy.Spider):
    name='statiz'

    def start_requests(self):
        url='http://www.statiz.co.kr/boxscore.php'

        schedules=Schedule.objects()
        for elem in schedules:
            for game in elem.gameList:

                gameId=game.date+game.stadium+str(game.hour)

                if KboLog.objects(pk=gameId).first()==None:
                    formdata={
                        'opt':'5',
                        'date':game.date,
                        'stadium':game.stadium,
                        'hour':str(game.hour)
                    }
                    yield scrapy.FormRequest(url,formdata=formdata,callback=self.parse,meta={'gameId':gameId})

    def parse(self,response):

        gameId=response.meta['gameId']

        #with open(gameId+'.html','wb') as f:
        #    f.write(response.body)

        # No need to crawl heads, we already know, it's all same
        # heads= response.css('section.content div')[0].xpath('./div')[1].xpath('./div')[1].xpath('./div/div/div').css('table tr')[0].css('th::text').extract()

        rows=response.css('section.content div')[0].xpath('./div')[1].xpath('./div')[1].xpath('./div/div/div').css('table tr')
        data_len=len(rows)-1

        game_data=[]
        json_data=[]

        # current_inning='1초'
        inning_data=[]
        inning_data_json=[]

        # offset=0

        for i in range(data_len):
            row=rows[i+1].css('td')
            # texts=row.css('::text').extract()
            inn_data=row[0].css('::text').extract()
            if len(inn_data)!=0 and len(inning_data)>0:
                game_data.append(inning_data)
                json_data.append(inning_data_json)
                inning_data=[]
                inning_data_json=[]
            if len(row[1].css('::text').extract())==0:
                continue
            

            data=HitLog()
            data_json={}
            data_json['thrower']=row[1].css('::text').extract()[0]
            data.thrower=row[1].css('::text').extract()[0]
            batter_data=row[2].css('::text').extract()
            data_json['batterNum']=batter_data[0]
            data.batterNum=batter_data[0]
            data_json['batter']=batter_data[1]
            data.batter=batter_data[1]
            p_data=row[3].css('::text').extract()
            if len(p_data)!=0:
                data_json['point']=p_data[0]
                data.point=p_data[0]
            result_data=row[4].css('::text').extract()
            if len(result_data)==2:
                data_json['result']=result_data[0]+result_data[1]
                data.result=result_data[0]+result_data[1]
            else:
                data_json['result']=result_data[0]
                data.result=result_data[0]
            data_json['status']=row[5].css('::text').extract()[0]
            data.status=row[5].css('::text').extract()[0]
            data_json['lev']=float(row[7].css('::text').extract()[0])
            data.lev=float(row[7].css('::text').extract()[0])
            data_json['res']=float(row[8].css('::text').extract()[0])
            data.res=float(row[8].css('::text').extract()[0])
            data_json['rea']=float(row[9].css('::text').extract()[0])
            data.rea=float(row[9].css('::text').extract()[0])
            data_json['wpe']=float(row[10].css('::text').extract()[0][:-1])
            data.wpe=float(row[10].css('::text').extract()[0][:-1])
            data_json['wpa']=float(row[11].css('::text').extract()[0])
            data.wpa=float(row[11].css('::text').extract()[0])

            inning_data.append(data)
            inning_data_json.append(data_json)

        game_data.append(inning_data)
        json_data.append(inning_data_json)

        game = KboLog(id=gameId)
        game.innings=game_data

        game.save()

        with open(gameId+'.json','w') as jsonfile:
            json.dump(json_data,jsonfile,ensure_ascii=False)