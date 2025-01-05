# -*- coding: utf-8 -*-
import json
import scrapy
from scrapy.spiders import CrawlSpider
from ZhiLian.items import ZhilianItem
import csv


class ZhilianspiderSpider(scrapy.Spider):
    name = 'ZhiLianSpider'
    allowed_domains = ['zhaopin.com']
    max_pages = 10
    positions = ['人力资源', '人事', '行政', '招聘', '薪酬绩效', 'HRBP', '财务', '会计', '测试', '开发', '前端', '后端',
                 '系统运维', '数据管理', 'UI', '项目管理', '产品', '产品架构师', '市场分析师', '项目经理', '算法架构师',
                 '算法工程师', '方案专家', '硬件工程师', '运营', '运维', '商务', '通路行销', '招投标', '法务',
                 '电催/催收', '外访/催收外访', '设计师', '策划师', '大客户经理', '销售', '供应链', '仓库管理专员',
                 '客服', '车务专员', 'DBA']
    citys = [538,  # 上海
             530,  # 北京
             763,  # 广州
             765,  # 深圳
             531,  # 天津
             736,  # 武汉
             854,  # 西安
             801,  # 成都
             635,  # 南京
             653,  # 杭州
             551,  # 重庆
             682,  # 厦门
             600,  # 大连
             631,  # 长春
             599,  # 沈阳
             702,  # 济南
             703,  # 青岛
             639,  # 苏州
             636,  # 无锡
             654,  # 宁波
             719,  # 郑州
             749,  # 长沙
             681,  # 福州
             664,  # 合肥
             622,  # 哈尔滨
             ]

    # 拼接初始化Url
    start_urls = ["https://www.zhaopin.com/"]

    # start_urls = ["https://www.zhaopin.com/sou/jl={citycode}/kw={position}/p=1"]

    def start_requests(self):
        for position in self.positions:
            for city in self.citys:
                url = f"https://www.zhaopin.com/sou/jl={city}/kw={position}/p=1"
                yield scrapy.Request(url=url, callback=self.parse, meta={'position': position, 'city': city, 'page': 1})

    def parse(self, response):
        position = response.meta['position']
        city = response.meta['city']
        current_page = response.meta['page']
        filename = f"./files/ZHILIAN_{position}_全国.csv"

        # 创建文件并写入表头
        if current_page == 1:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['位置', '公司名', '公司行业', '学历要求', '经验要求', '薪资', '技能要求', '职位'])

        li_list = response.xpath('//li[@class="job-card-wrapper"]')
        print(f"Number of items found on page {current_page}: {len(li_list)}")

        if not li_list:
            print(f"No more data found for position '{position}' in city '{city}'.")
            return  # 如果没有数据，则停止请求

        for li in li_list:
            poname = li.xpath('//div[@class="joblist-box__item clearfix"]'
                              '//div[@class="jobinfo__top"]/p/text()').extract_first() or ''
            providesalary = li.xpath('//div[@class="jobinfo"]'
                                     '//div[@class="jobinfo__top"]/p/text()').extract_first() or ''
            city = li.xpath('//div[@class="jobinfo__other-info"]/div[1]/text()').extract_first() or ''
            worktime = li.xpath('//div[@class="jobinfo__other-info"]/div[2]/text()').extract_first() or ''
            coattr = li.xpath('//div[@class="jobinfo__other-info"]/div[3]/text()').extract_first() or ''
            cosize = li.xpath('//div[@class="jobinfo__other-info"]/div[4]/text()').extract_first() or ''
            title = li.xpath(".//span[@class='job-name']/text()").extract_first() or ''
            salary = li.xpath(".//span[@class='salary']/text()").extract_first() or ''
            area = li.xpath(".//span[@class='job-area']/text()").extract_first() or ''

            # 确保提取job_lable_list的正确性
            job_lable_list = li.xpath(".//ul[@class='tag-list']//text()").extract()
            if len(job_lable_list) >= 2:
                experience = job_lable_list[0] or ''
                education = job_lable_list[1] or ''
            else:
                experience = ''
                education = ''

            company = li.xpath(".//h3[@class='company-name']/a/text()").extract_first() or ''

            # 确保提取company_message的正确性
            company_message = li.xpath(".//ul[@class='company-tag-list']//text()").extract()
            company_type = company_message[0] if company_message else ''

            # 提取boon字段
            boon = li.xpath('.//div[@class="job_card_footer"]//div[@class="info-desc"]/text()').extract()
            boon = boon[0] if boon else None
            # 技能
            skill_list = li.xpath(
                ".//div[@class='job-card-footer clearfix']//ul[@class='tag-list']/li/text()"
            ).extract() or []
            skill = "|".join(skill_list)

            # 将数据写入 CSV 文件
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([title, area, salary, experience, education, company, company_type, skill])

            # 创建BossItem对象并传递数据
            book = ZhilianItem(
                poname=poname,
                coname=area,
                city=salary,
                providesalary=experience,
                degree=education,
                coattr=company,
                cosize=company_type,
                worktime=skill,
                welfare=skill
            )
            yield book

        # 处理下一页
        if current_page < self.max_pages:  # 检查是否超过最大页码
            next_page = current_page + 1
            next_url = response.urljoin(
                f"https://www.zhaopin.com/sou/jl={city}/kw={position}/p={next_page}"
            )
            yield scrapy.Request(
                url=next_url, callback=self.parse, meta={'position': position, 'city': city, 'page': next_page}
            )
