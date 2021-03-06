"""
Scrapes all resource types from AWS documentation.

How to run::

    pip install scrapy
    scrapy runspider scraper.py -o resource_types.json

Output will be a JSON file::

    [
    {"service": "Amazon AppFlow", "resource_type": "flow", "arn_format": "arn:${Partition}:appflow::${Account}:flow/${flowName}"},
    {"service": "Amazon AppFlow", "resource_type": "connectorprofile", "arn_format": "arn:${Partition}:appflow::${Account}:connectorprofile/${profileName}"},
    ...
    ]
"""

import json
import scrapy


class ResourceTypeSpider(scrapy.Spider):
    name = 'tocspider'
    start_urls = ['https://docs.aws.amazon.com/service-authorization/latest/reference/toc-contents.json']
    download_delay = 0.250
    final_list = []

    def parse(self, response):
        j = json.loads(response.text)
        j = j['contents']

        def select_title(xs, title):
            return [x for x in xs if x['title'] == title][0]

        j = select_title(j, 'Reference')['contents']
        j = select_title(j, 'Actions, resources, and condition keys')['contents']

        for page in j:
            title = page['title']
            href = page['href']
            yield response.follow(href, self.parse_ref)


    def parse_ref(self, response):
        res_service = response.xpath('//h2[starts-with(text(),"Resource types defined by")]/text()').get()
        service = str(res_service).replace("Resource types defined by", "").strip()
        trs = response.xpath("//th[text()='Resource types']/../../..//tr")[1:]

        for tr in trs:
            tds = tr.xpath('td')
            row = []
            for td in tds:
                text = "".join([x.get().strip() for x in td.xpath(".//text()")])
                row.append(text)

            yield {'service': service, 'resource_type': row[0], 'arn_format': row[1]}
