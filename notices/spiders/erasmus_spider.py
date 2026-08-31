import scrapy
import json
from notices.items import EacItem
from scrapy.http import Response
from typing import Any, Iterable


class EramusSpider(scrapy.Spider):
    name = "erasmus"
    custom_settings = {
        'ITEM_PIPELINES': {
            'notices.pipelines.EacPipeline': 100
        },
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 7,
        'CONCURRENT_REQUESTS': 7,
        'RETRY_TIMES': 35,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 403, 404, 408],
    }
    allowed_domains = ["erasmus-plus.ec.europa.eu"]

    api_url = (
        "https://erasmus-plus.ec.europa.eu/eac-api/content"
        "?language=en&page%5Boffset%5D={offset}&page%5Blimit%5D=10"
        "&sortonly=false&type=calls"
        "&filters%5Bcomputed_call_status%5D%5B0%5D=open"
    )

    async def start(self) -> Iterable[scrapy.Request]:
        # Start from first page (offset 0). The computed_call_status=open
        # filter is applied server-side so we never fetch already-closed
        # calls.
        yield scrapy.Request(
            url=self.api_url.format(offset=0),
            callback=self.parse_api,
            meta={'offset': 0}
        )

    def parse_api(self, response: Response) -> Iterable[Any]:
        data = json.loads(response.text)
        fundings = data.get('data', [])

        for funding in fundings:
            closing_date = funding.get('deadlineDate', 'No deadline day')

            item = EacItem()
            item['closing_date'] = closing_date
            item['title'] = funding.get('title', 'No title')
            item['closing_time'] = funding.get(
                'deadlineTime', 'No deadline time'
            )
            item['link'] = response.urljoin(funding.get('url', 'No link'))
            item['country'] = 'União Europeia'
            yield item

        # Pagination handling
        if len(fundings) > 0:
            current_offset = response.meta['offset']
            next_offset = current_offset + 1
            next_page_url = self.api_url.format(offset=next_offset)
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_api,
                meta={'offset': next_offset}
            )
