#!/bin/env python

from scrapy.crawler import CrawlerProcess
from scrapy.signals import item_scraped
from gmat_collector.scrapers.veritas import VeritasScraper

process = CrawlerProcess()
process.crawl(VeritasScraper, "mZJVRvqsnV_gmat@gmail.com", "VJQ6I7gMwDL")  # type: Deferred

def _print_result(*args, **kwargs):
    print "Args: %s\nKwargs: %s" % (str(args), str(kwargs))

# attach crawler item processed signal handlers
for crawler in process.crawlers:
    crawler.signals.connect(_print_result, item_scraped)

process.start()
