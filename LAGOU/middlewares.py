# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import time
import asyncio
import aiohttp
from faker import Faker
from loguru import logger
from scrapy import signals
from time import strftime, localtime
from .settings import DEFAULT_REQUEST_HEADERS


class LagouSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# class LagouDownloaderMiddleware:
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the downloader middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_request(self, request, spider):
#         # Called for each request that goes through the downloader
#         # middleware.
#         # Must either:
#         # - return None: continue processing this request
#         # - or return a Response object
#         # - or return a Request object
#         # - or raise IgnoreRequest: process_exception() methods of
#         #   installed downloader middleware will be called
#         return None
#
#     def process_response(self, request, response, spider):
#         if 'https://sec.lagou.com/verify' in request.url:
#             request.cookies = requests.get(url='https://www.lagou.com/', headers=DEFAULT_REQUEST_HEADERS).cookies
#             return request
#         # Called with the response returned from the downloader.
#
#         # Must either;
#         # - return a Response object
#         # - return a Request object
#         # - or raise IgnoreRequest
#         return response
#
#     def process_exception(self, request, exception, spider):
#         # Called when a download handler or a process_request()
#         # (from other downloader middleware) raises an exception.
#
#         # Must either:
#         # - return None: continue processing this exception
#         # - return a Response object: stops process_exception() chain
#         # - return a Request object: stops process_exception() chain
#         return request
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)


class UserAgentDownloadMiddleware(object):
    def process_request(self, request, spider):
        request.headers['User-Agent'] = Faker().user_agent()


class IPProxyDownloadMiddleware(object):
    async def process_request(self, request, spider):
        async with aiohttp.ClientSession() as client:
            while True:
                responses = await client.get(url='http://127.0.0.1:5555/https')
                proxies = await responses.text()
                if proxies == '43.255.228.150:3128':
                    time.sleep(30)
                    continue
                request.meta['proxy'] = 'https://' + proxies
                logger.debug(f'使用代理{proxies}')
                break


class RequestLOGDownloadMiddleware(object):
    def process_response(self, request, response, spider):
        if response.status == 200:
            logger.debug(f'请求成功{response.url}')
            return response
        else:
            logger.error(f'请求失败{response.url}')
            return request

    def process_exception(self, request, exception, spider):
        logger.debug(f'重试{request.url}')
        return request
