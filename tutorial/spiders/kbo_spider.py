import scrapy
from scrapy.selector import Selector

class KboSpider(scrapy.Spider):
    name='kbo'

    def start_requests(self):
        urls=['https://www.koreabaseball.com/Game/LiveTextView2.aspx']
        formdata={
            'leagueId':'1',
            'seriesId':'0',
            'gameId':'20180920SSWO0',
            'gyear':'2018'
        }
        for url in urls:
            yield scrapy.FormRequest(url,formdata=formdata,callback=self.parse)

    def parse(self,response):
        broadcast=response.xpath('//div[@id="numCont1"]/span/text()')

        print(broadcast[0].extract())

        # with open('kbo-sample.html','wb') as f:
        #     f.write(response.body)