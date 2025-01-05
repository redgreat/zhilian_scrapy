# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# 写csv文件
import csv
from datetime import datetime


class ZhilianPipeline(object):
    def open_spider(self, spider):
        # 打开文件，并创建一个 CSV 写入器
        filename = '../files/ZHILIAN' + datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
        self.fp = open(filename, 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.fp)

        # 写入表头
        self.writer.writerow(
            ['职位名称', '公司名称', '工作城市', '薪资范围', '学历要求', '公司类型', '公司规模', '工作经验', '福利待遇']
        )

    def process_item(self, item, spider):
        # 将item的值按照顺序写入 CSV
        row = [
            item.get('poname', ''),
            item.get('coname', ''),
            item.get('city', ''),
            item.get('providesalary', ''),
            item.get('degree', ''),
            item.get('coattr', ''),
            item.get('cosize', ''),
            item.get('worktime', ''),
            item.get('welfare', '')
        ]
        self.writer.writerow(row)
        return item

    def close_spider(self, spider):
        self.fp.close()
