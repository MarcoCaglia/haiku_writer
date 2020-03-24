# -*- coding: utf-8 -*-
import scrapy
import json
from ..items import HaikuWriterItem
from datetime import datetime as dt


class FailedFetchError(Exception):
    pass


class HaikuRedditsearchSpider(scrapy.Spider):
    name = 'haiku_redditsearch'
    allowed_domains = []
    current_utc = (dt.now() - dt(1970, 1, 1)).total_seconds()
    current_utc = str(current_utc).split('.')[0]
    start_urls = [('https://api.pushshift.io/reddit/search/submission/'
                   '?q=&after=0&before=1583651345&subreddit=haiku&author=&'
                   'aggs=&metadata=true&frequency=hour&advanced=false&sort='
                   'desc&domain=&sort_type=created_utc&size=1000')]

    def parse(self, response):
        item = HaikuWriterItem()
        content = json.loads(response.text)

        content = content['data']

        if not isinstance(content, list):
            raise FailedFetchError('Content object is of type'
                                   f'{type(content)}, instead of list.')
        for i, entry in enumerate(content, start=1):
            item['text'] = entry['title']
            try:
                item['body_text'] = entry['selftext']
            except KeyError:
                item['body_text'] = None
            item['author'] = entry['author']
            current_timestamp = dt.utcfromtimestamp(
                entry['created_utc']
                )
            item['timestamp'] = str(current_timestamp)
            item['url'] = entry['permalink']
            item['subreddit'] = entry['subreddit']

            if i == len(content):
                print(f'Last timestamp is {entry["created_utc"]}')
                next_call = self._generate_next_call(entry["created_utc"])
                yield response.follow(
                    next_call,
                    callback=self.parse
                )

            yield item

    def _generate_next_call(timestamp):
        path = ('https://api.pushshift.io/reddit/search/submission/'
                f'?q=&after=0&before={timestamp}&subreddit=haiku&author=&'
                'aggs=&metadata=true&frequency=hour&advanced=false&sort='
                'desc&domain=&sort_type=num_comments&size=1000')

        yield path

    @staticmethod
    def _get_current_utc():
        timestamp = dt.now()
        epoch = dt(1970, 1, 1)
        utc = (timestamp - epoch).total_seconds()

        yield utc
