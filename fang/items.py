# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewHouseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    province=scrapy.Field()
    city=scrapy.Field()
    #小区的名字
    name=scrapy.Field()
    price=scrapy.Field()
    #几居,这个是列表
    rooms=scrapy.Field()
    #面积
    area=scrapy.Field()
    address=scrapy.Field()
    #行政区
    district=scrapy.Field()
    #是否在售
    sale=scrapy.Field()
    #详情页面的url
    origin_url=scrapy.Field()

class ESFHouseItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    # 小区的名字
    name=scrapy.Field()
    rooms=scrapy.Field()
    floor=scrapy.Field()
    toward=scrapy.Field()
    year=scrapy.Field()
    address=scrapy.Field()
    area=scrapy.Field()
    #总价
    price=scrapy.Field()
    # 每平方米价格
    unit=scrapy.Field()
    # 详情页面的url
    origin_url = scrapy.Field()