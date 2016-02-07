#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, asyncio
from collections import deque

import feedparser

class FeedBloom(object):
    line_len = 0
    entries = deque()
    _config_dir = os.path.join(os.path.join(os.environ.get('HOME'), '.config',), 'feedbloom/')
    feeds_file = os.path.join(_config_dir, 'feeds.txt')
    event_loop = asyncio.get_event_loop()

    def _get_urls(self):
        with open(self.feeds_file, 'r') as fd:
            return [f.strip() for f in  fd.readlines()]

    def get_entries(self):
        _entries = []
        for url in self._get_urls():
            content = feedparser.parse(url)
            _entries += content.entries
        entries = self.sort_entries(_entries)
        self.limit_entries(entries)

        self.event_loop.call_later(40, self.get_entries)

    def sort_entries(self, entries):
        return sorted(entries, key=lambda e: e.updated_parsed, reverse=True)

    def limit_entries(self, entries):
        if entries[:10] != self.entries:
            self.entries = deque(entries[:10])

    def get_entry(self):
        if self.entries:
            return self.entries[0]

    def format_time(self, time):
        return '{time.tm_mday:0>2}/{time.tm_mon:0>2}/{time.tm_year:0>2} {time.tm_hour:0>2}:{time.tm_min:0>2}'.format(time=time)


    def format_entry(self, entry):
        return '{} - {} - {}'.format(self.format_time(entry.updated_parsed), entry.title, entry.link)

    def print_entry(self):
        print(' ' * self.line_len, end='\r', flush=True)
        entry = self.get_entry()
        formatted = self.format_entry(entry)
        self.line_len = len(formatted)
        print(formatted, end='\r', flush=True)
        self.entries.rotate()
        self.event_loop.call_later(5, self.print_entry)

    def run(self):
        self.get_entries()
        self.print_entry()
        self.event_loop.run_forever()


def main():
    feedbloom = FeedBloom()
    feedbloom.run()
