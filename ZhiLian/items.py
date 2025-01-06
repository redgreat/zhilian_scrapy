# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item
from scrapy import Field


# 继承父类scrapy.Item的属性和方法，该类用于定义需要爬取数据的子段
class ZhilianItem(scrapy.Item):
    # define the fields for your item here like:
    # 职位
    job_name = scrapy.Field()
    # 公司名
    company_name = scrapy.Field()
    # 公司行业
    company_type = scrapy.Field()
    # 位置
    location = scrapy.Field()
    # 薪资
    salary = scrapy.Field()
    # 学历要求
    education = scrapy.Field()
    # 经验要求
    experience = scrapy.Field()
    # 技能要求
    skill = scrapy.Field()
