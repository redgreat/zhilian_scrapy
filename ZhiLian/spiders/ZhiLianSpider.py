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
    positions = ['人力资源', '人事', '行政', '招聘', '薪酬绩效', 'HRBP', '财务', '会计', '测试', '开发', '前端',
                  '后端',
                  '系统运维', '数据管理', 'UI', '项目管理', '产品', '产品架构师', '市场分析师', '项目经理',
                  '算法架构师',
                  '算法工程师', '方案专家', '硬件工程师', '运营', '运维', '商务', '通路行销', '招投标', '法务',
                  '电催/催收', '外访/催收外访', '设计师', '策划师', '大客户经理', '销售', '供应链', '仓库管理专员',
                  '客服', '车务专员', 'DBA']

    def start_requests(self):
        for position in self.positions:
            url = f"https://www.zhaopin.com/sou/jl=?p=1&kw={position}"
            yield scrapy.Request(url=url, callback=self.parse, meta={'position': position, 'page': 1})

    def parse_detail(self, response):
        # 提取技能要求
        skill = response.xpath('//div[@class="describtion__detail-content"]//text()').getall()
        skill = '\n'.join([s.strip() for s in skill if s.strip()])

        # 获取传递过来的职位信息
        location = response.meta['location']
        company_name = response.meta['company_name']
        company_type = response.meta['company_type']
        education = response.meta['education']
        experience = response.meta['experience']
        salary = response.meta['salary']
        job_name = response.meta['job_name']
        filename = response.meta['filename']

        # 将数据写入 CSV 文件
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                [location, company_name, company_type, education, experience, salary, skill, job_name])

        # 创建Item对象并传递数据
        item = ZhilianItem(
            location=location,
            company_name=company_name,
            company_type=company_type,
            education=education,
            experience=experience,
            salary=salary,
            skill=skill,
            job_name=job_name
        )
        yield item

    def parse(self, response):
        position = response.meta['position']
        current_page = response.meta['page']
        filename = f"../files/ZHILIAN_{position}_全国.csv"

        # 创建文件并写入表头
        if current_page == 1:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['位置', '公司名', '公司行业', '学历要求', '经验要求', '薪资', '技能要求', '职位'])

        div_list = response.xpath('//div[@class="joblist-box__item clearfix joblist-box__item-unlogin"]')
        print(f"Number of items found on page {current_page}: {len(div_list)}")

        if not div_list:
            print(f"No more data found for position '{position}'.")
            return  # 如果没有数据，则停止请求

        for div in div_list:
            job_name = div.xpath(
                './/div[@class="jobinfo__top"]/a[contains(@class, "jobinfo__name")]/text()').extract_first() or ''
            salary = div.xpath('.//p[@class="jobinfo__salary"]/text()').extract_first() or ''
            location = div.xpath('.//div[@class="jobinfo__other-info-item"]/span/text()').extract_first() or ''
            experience = div.xpath('.//div[@class="jobinfo__other-info-item"][2]/text()').extract_first() or ''
            education = div.xpath('.//div[@class="jobinfo__other-info-item"][3]/text()').extract_first() or ''
            company_name = div.xpath('.//a[@class="companyinfo__name companyinfo__name-short"]/text()').extract_first()
            if not company_name:
                company_name = div.xpath('.//a[@class="companyinfo__name"]/text()').extract_first() or ''
            company_type = div.xpath(
                './/div[@class="companyinfo__tag"]/div[@class="joblist-box__item-tag"][3]/text()').extract_first()
            if not company_type:
                company_type = div.xpath(
                    './/div[@class="companyinfo__tag"]/div[@class="joblist-box__item-tag"][2]/text()').extract_first() or ''

            if job_name:
                job_name = job_name.strip()
            if salary:
                salary = salary.strip()
            if location:
                location = location.strip()
            if experience:
                experience = experience.strip()
            if education:
                education = education.strip()
            if company_name:
                company_name = company_name.strip()
            if company_type:
                company_type = company_type.strip()

            detail_url = div.xpath(
                './/div[@class="jobinfo__top"]/a/@href').extract_first() or ''

            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_detail,
                meta={
                    'location': location,
                    'company_name': company_name,
                    'company_type': company_type,
                    'education': education,
                    'experience': experience,
                    'salary': salary,
                    'job_name': job_name,
                    'filename': filename
                }
            )

        if current_page < self.max_pages:  # 检查是否超过最大页码
            next_page = current_page + 1
            next_url = response.urljoin(
                f"https://www.zhaopin.com/sou/jl=?p={next_page}&kw={position}"
            )
            yield scrapy.Request(
                url=next_url, callback=self.parse, meta={'position': position, 'page': next_page}
            )
