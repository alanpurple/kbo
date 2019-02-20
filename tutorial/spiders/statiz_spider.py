import scrapy
from scrapy.selector import Selector
from mongoengine import connect
import json
from bson import json_util
from os.path import exists

from .models import HitLog,KboLog,Schedule,BatterInfo,RoasterInfo

# connect('kbostatiz',host='10.102.61.251',port=27017)
connect('kbostatiz')

class StatizSpider(scrapy.Spider):
    name='statiz'

    def start_requests(self):
        url='http://www.statiz.co.kr/boxscore.php'

        schedules=Schedule.objects()
        for elem in schedules.first:
            for game in elem.gameList:

                gameId=game.date+game.stadium+str(game.hour)

                # if KboLog.objects(pk=gameId).first()==None:
                if not exists('./rawdata/'+gameId+'.html'):
                    formdata={
                        'opt':'5',
                        'date':game.date,
                        'stadium':game.stadium,
                        'hour':str(game.hour)
                    }
                    yield scrapy.FormRequest(url,formdata=formdata,callback=self.parse,meta={'gameId':gameId})

    def parse(self,response):

        gameId=response.meta['gameId']

        game = KboLog(id=gameId)
        game_json={}

        # No need to crawl heads, we already know, it's all same
        # heads= response.css('section.content div')[0].xpath('./div')[1].xpath('./div')[1].xpath('./div/div/div').css('table tr')[0].css('th::text').extract()
        content_divs=response.css('section.content div')[0].xpath('./div')[1].xpath('./div')
        bat_seq_divs=content_divs[0].xpath('./div')
        away_team_name=bat_seq_divs[0].xpath('./div/div')[0].css('h3 b::text')[0].extract().split(',')[0]
        away_team_rows=bat_seq_divs[0].xpath('./div/div')[1].css('table tr')
        away_thrower_raw=away_team_rows[-1].css('::text').extract()
        away_thrower_json={'name':away_thrower_raw[0],'position':away_thrower_raw[1],'toota':away_thrower_raw[2]}
        away_thrower=BatterInfo(name=away_thrower_raw[0],position=away_thrower_raw[1],toota=away_thrower_raw[2])
        away_batters_raw=[elem.css('::text').extract() for elem in away_team_rows[1:-1]]
        away_batters_json=[{'name':elem[1],'position':elem[2],'toota':elem[3]} for elem in away_batters_raw]
        away_batters=[BatterInfo(name=elem[1],position=elem[2],toota=elem[3]) for elem in away_batters_raw]

        game.awayTeam=RoasterInfo(teamName=away_team_name,thrower=away_thrower,batters=away_batters)
        game_json['awayTeam']={'teamName':away_team_name,'thrower':away_thrower_json,'batters':away_batters_json}

        home_team_name=bat_seq_divs[1].xpath('./div/div')[0].css('h3 b::text')[0].extract().split(',')[0]
        home_team_rows=bat_seq_divs[1].xpath('./div/div')[1].css('table tr')
        home_thrower_raw=home_team_rows[-1].css('::text').extract()
        home_thrower_json={'name':home_thrower_raw[0],'position':home_thrower_raw[1],'toota':home_thrower_raw[2]}
        home_thrower=BatterInfo(name=home_thrower_raw[0],position=home_thrower_raw[1],toota=home_thrower_raw[2])
        home_batters_raw=[elem.css('::text').extract() for elem in home_team_rows[1:-1]]
        home_batters_json=[{'name':elem[1],'position':elem[2],'toota':elem[3]} for elem in home_batters_raw]
        home_batters=[BatterInfo(name=elem[1],position=elem[2],toota=elem[3]) for elem in home_batters_raw]

        game.homeTeam=RoasterInfo(teamName=home_team_name,thrower=home_thrower,batters=home_batters)
        game_json['homeTeam']={'teamName':home_team_name,'thrower':home_thrower_json,'batters':home_batters_json}


        rows=content_divs[1].xpath('./div/div/div').css('table tr')
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

        
        game.innings=game_data
        game_json['innings']=json_data

        game.save()

        with open('./jsondata/'+gameId+'.json','w') as jsonfile:
            json.dump(game_json,jsonfile,ensure_ascii=False)

        with open('./rawdata/'+gameId+'.html','wb') as f:
            f.write(response.body)