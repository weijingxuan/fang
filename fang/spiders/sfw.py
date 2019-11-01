# -*- coding: utf-8 -*-
import scrapy
import re
from fang.items import NewHouseItem,ESFHouseItem
from scrapy_redis.spiders import RedisSpider

class SfwSpider(RedisSpider):
# class SfwSpider(scrapy.Spider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    # start_urls = ['https://www.fang.com/SoufunFamily.htm']
    redis_key = "fang:start_urls"

    def parse(self, response):
        trs=response.xpath("//div[@class='outCont']//tr")
        province=None
        for tr in trs:
            tds=tr.xpath(".//td[not(@class)]")
            province_td=tds[0]
            province_text=province_td.xpath(".//text()").get()
            province_text=re.sub(r"\s","",province_text)#这句话的目的是为了把省份（两行）的空格找到
            if province_text:
                province=province_text#如果有省份，就保存下来，如果没有，就使用之前的
            #不爬取海外的城市的房源
            if province=='其它':
                continue
            city_td=tds[1]
            city_links=city_td.xpath(".//a")
            for city_link in city_links:
                city=city_link.xpath(".//text()").get()
                city_url=city_link.xpath(".//@href").get()
                # 构建新房的url链接
                url_model=city_url.split("//")
                scheme=url_model[0]
                domain=url_model[1]
                # https: // wuhu.newhouse.fang.com / house / s /
                # http: // wuhu.fang.com /
                area=domain.split(".")
                area0=area[0]
                area1=area[1]
                area2=area[2]
                if 'bj.' in domain:
                    newhouse_url='https://newhouse.fang.com/house/s/'
                    esf_url='https://bj.esf.fang.com'
                else:
                    newhouse_url=scheme+"//"+area0+"."+"newhouse."+area1+"."+area2+"house/s/"
                    #构建二手房的url链接
                    # https: // wuhu.esf.fang.com /
                    esf_url=scheme+"//"+area0+"."+"esf."+area1+"."+area2

                    # print("城市,%s%s"%(province,city))
                    # print("新房：%s"%newhouse_url)
                    # print("二手房",esf_url)
                    # 通过meta设置信息,进行返回
                yield scrapy.Request(url=newhouse_url,callback=self.parse_newhouse,meta={"info":(province,city)})
                yield scrapy.Request(url=esf_url,callback=self.parse_esfhoust,meta={"info":(province,city)})



    def parse_newhouse(self,response):
        # 拿到info里面设置的province和city
        province,city=response.meta.get("info")
        lis=response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        for li in lis:
            name=li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            if name is not None:
                name=name.strip()
            houst_type_list=li.xpath(".//div[contains(@class,'house_type')]/a/text()").getall()#这里是getall，所以用lamdba统一去除
            house_type_list=list(map(lambda x:re.sub(r"\s","",x),houst_type_list))
            rooms=list(filter(lambda x:x.endswith("居"),house_type_list))
            area="".join(li.xpath(".//div[contains(@class,'house_type')]/text()").getall())#以列表形式返回，转换成字符串
            area=re.sub(r"\s|－|/","",area)
            address=li.xpath(".//div[@class='address']/a/@title").get()
            district_text="".join(li.xpath(".//div[@class='address']/a//text()").getall())
            district=re.search(r".*\[(.+)\].*",district_text)#对过滤的字符串进行分组
            if district is not None:
                district=district.group(1)
            sale=li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()
            price="".join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
            price=re.sub(r"\s|广告","",price)
            origin_url=li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            origin_url=response.urljoin(origin_url)
            item=NewHouseItem(name=name,rooms=rooms,area=area,address=address,district=district,sale=sale,price=price,
                              origin_url=origin_url,province=province,city=city)
            yield item
        next_url=response.xpath("div[@class='page']//a[@class='next']/@href").get()
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url),callback=self.parse_newhouse,
                                 meta={"info":(province,city)})
    #爬取二手房信息
    def parse_esfhoust(self,response):
        province,city = response.meta.get("info")
        item=ESFHouseItem(province=province,city=city)
        dls=response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for dl in dls:
            item['name']=dl.xpath(".//p[@class='add_shop']/a/@title").get()
            infos=dl.xpath(".//p[@class='tel_shop']/text()").getall()
            infos=list(map(lambda x:re.sub(r"\s","",x),infos))
            for info in infos:
                if "厅" in  info:
                    item['rooms']=info
                elif "层" in info:
                    item["floor"]=info
                elif "向" in info:
                    item['toward']=info
                elif "年" in info:
                    item['year']=re.sub(r"建","",info)
                    # item['year']=info.replace("建","")#这样也可以
                elif "㎡" in info:
                    item['area']=info
            item['address']=dl.xpath(".//p[@class='add_shop']/span/text()").get()
            item['price']="".join(dl.xpath(".//dd[@class='price_right']/span[@class='red']//text()").getall())
            item['unit']="".join(dl.xpath(".//dd[@class='price_right']/span[2]/text()").getall())
            origin_url=dl.xpath(".//h4[@class='clearfix']/a/@href").get()
            item['origin_url']=response.urljoin(origin_url)
            print(item['origin_url'])
            yield item
        next_url=response.xpath("//div[@class='page_al']/p[1]/a/@href").get()
        next_url=response.urljoin(next_url)
        if next_url:
            yield scrapy.Request(url=next_url,callback=self.parse_esfhoust,meta={"info":(province,city)})














