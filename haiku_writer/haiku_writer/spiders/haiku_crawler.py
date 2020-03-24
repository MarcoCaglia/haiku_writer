# -*- coding: utf-8 -*-
import scrapy
import re
from ..items import HaikuWriterItem

MAX_REC = 200


class HaikuCrawlerSpider(scrapy.Spider):
    name = 'haiku_crawler'
    allowed_domains = []
    start_urls = ['https://old.reddit.com/r/haiku/']

    def parse(self, response):
        items = HaikuWriterItem()
        content = response.xpath('//div[@id="siteTable"]/div')
        for i, post in enumerate(content):
            text = post.xpath('.//div[2]/div/p[1]/a').extract_first()
            timestamp = post.xpath('.//div[2]/div/p[2]/time') \
                .extract_first()
            if isinstance(text, type(None)) or \
               isinstance(timestamp, type(None)):
                continue
            try:
                text = re.findall('tabindex="1">.+</a>', text)[0] \
                    .replace('tabindex="1">', '').replace('</a>', '')
                timestamp = re.findall('datetime="[^"]+"', timestamp)[0] \
                    .replace('datetime=', '').replace('"', '')

                items['timestamp'] = timestamp
                items['text'] = text
            except IndexError:
                pass

            for i in ['2020', '2019', '2018', '2017', '2016', '2015']:
                if i in timestamp:
                    full_page = response.text
                    # print(full_page)
                    next_page = re.findall(
                        'class="next-button"><a href="[^"]+"',
                        full_page
                        )[0].replace('class="next-button"><a href=', '') \
                            .replace('"', '')
                    print(next_page)
                    yield response.follow(
                        next_page,
                        callback=self.parse
                        )

            yield items
