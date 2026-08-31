from pathlib import Path

from scrapy import signals

# Accumulates the per-spider results for every spider that has finished in
# this process, so that a general/aggregated summary can be (re)written
# after each one closes. This covers both a single `scrapy crawl <name>`
# run (aggregate == that one spider) and `scrapy crawlall` (aggregate ==
# every spider run so far), since it lives at module scope and is shared by
# every CrawlSummaryExtension instance within the process.
_SPIDER_RESULTS = []


class CrawlSummaryExtension:
    """Writes a short crawl summary (items saved, pages browsed, elapsed
    time, time per saved item) to a text file and prints it to the
    terminal when a spider finishes, and keeps a general summary file
    aggregating those same statistics across every spider run so far.

    Works the same way for a single `scrapy crawl <name>` run and for
    `scrapy crawlall`, since each spider gets its own `spider_closed`
    signal regardless of how many spiders are running in the process.
    """

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_crawler(cls, crawler):
        output_dir = crawler.settings.get("SUMMARY_DIR", "results_summary")
        ext = cls(output_dir)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        return ext

    @staticmethod
    def _compute_stats(spider, reason):
        stats = spider.crawler.stats.get_stats()

        items_saved = stats.get("item_scraped_count", 0)
        pages_browsed = stats.get("response_received_count", 0)

        start_time = stats.get("start_time")
        finish_time = stats.get("finish_time")
        if start_time and finish_time:
            elapsed_seconds = (finish_time - start_time).total_seconds()
        else:
            elapsed_seconds = 0.0

        return {
            "name": spider.name,
            "reason": reason,
            "items_saved": items_saved,
            "pages_browsed": pages_browsed,
            "elapsed_seconds": elapsed_seconds,
        }

    @staticmethod
    def _format_summary(title, items_saved, pages_browsed, elapsed_seconds,
                         extra_lines=None):
        time_per_item = (
            elapsed_seconds / items_saved if items_saved else None
        )
        lines = [title]
        if extra_lines:
            lines.extend(extra_lines)
        lines.extend([
            f"Items saved: {items_saved}",
            f"Pages browsed: {pages_browsed}",
            f"Total time: {elapsed_seconds:.2f}s",
            "Time per saved item: "
            + (
                f"{time_per_item:.2f}s"
                if time_per_item is not None
                else "N/A"
            ),
        ])
        return "\n".join(lines)

    def spider_closed(self, spider, reason):
        result = self._compute_stats(spider, reason)
        _SPIDER_RESULTS.append(result)

        summary = self._format_summary(
            f"Spider: {result['name']}",
            result["items_saved"],
            result["pages_browsed"],
            result["elapsed_seconds"],
            extra_lines=[f"Finish reason: {result['reason']}"],
        )

        summary_file = self.output_dir / f"{result['name']}_summary.txt"
        summary_file.write_text(summary + "\n", encoding="utf-8")

        print("\n----- Crawl summary -----")
        print(summary)
        print("--------------------------\n")

        self._write_general_summary()

    def _write_general_summary(self):
        total_items = sum(r["items_saved"] for r in _SPIDER_RESULTS)
        total_pages = sum(r["pages_browsed"] for r in _SPIDER_RESULTS)
        total_elapsed = sum(r["elapsed_seconds"] for r in _SPIDER_RESULTS)

        general_summary = self._format_summary(
            "General summary (all spiders)",
            total_items,
            total_pages,
            total_elapsed,
            extra_lines=[f"Spiders run: {len(_SPIDER_RESULTS)}"],
        )

        general_file = self.output_dir / "general_summary.txt"
        general_file.write_text(general_summary + "\n", encoding="utf-8")

        print("\n===== General summary =====")
        print(general_summary)
        print("============================\n")
