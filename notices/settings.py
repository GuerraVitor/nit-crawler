# Scrapy settings for notices project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
from pathlib import Path
from shutil import which

BOT_NAME = "notices"

SPIDER_MODULES = ["notices.spiders"]
NEWSPIDER_MODULE = "notices.spiders"
COMMANDS_MODULE = "notices.commands"
LOG_LEVEL = 'INFO'



# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "notices (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

custom_settings = {
    'FEED_EXPORT_BATCH_ITEM_COUNT': 0,  # Disable batching
}

ITEM_PIPELINES = {
}

EXTENSIONS = {
    "notices.extensions.CrawlSummaryExtension": 500,
}

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# The root directory of your Scrapy project (nit-crawler/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Define the output directory
OUTPUT_DIR = BASE_DIR / "results_spiders"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Directory where per-spider crawl summaries (items saved, pages browsed,
# elapsed time, time per saved item) are written
SUMMARY_DIR = BASE_DIR / "results_summary"
os.makedirs(SUMMARY_DIR, exist_ok=True)

FEEDS = {
    f'{OUTPUT_DIR}/%(name)s.json': {
        'format': 'json', 'encoding': 'utf8', 'indent': 4, 'overwrite': True,
    }
}
