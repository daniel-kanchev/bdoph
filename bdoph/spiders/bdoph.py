import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bdoph.items import Article


class bdophSpider(scrapy.Spider):
    name = 'bdoph'
    start_urls = ['https://www.bdo.com.ph/news-and-articles']

    def parse(self, response):
        links = response.xpath('//a[text()="Read More"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@title="Go to next page"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//div[@class="pane-content"]//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="field-item even"]//strong/text()').get()
        if date:
            if '20' not in date:
                date = ''
            else:
                if '–' in date or '-' in date:
                    date = " ".join(date.split()[:-1])
                else:
                    date = " ".join(date.split())

        content = response.xpath('//div[@class="field-item even"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
