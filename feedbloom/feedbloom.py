#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio, os, argparse
from collections import deque

import feedparser

_config_dir = os.path.join(os.path.join(os.environ.get('HOME'), '.config',), 'feedbloom/')

class FeedBloom(object):
    line_len = 0
    entries = deque()
    event_loop = asyncio.get_event_loop()

    def __init__(self, **kwargs):
        self.output_format = kwargs['output_format']
        self.flush = kwargs['flush']
        self.limit = kwargs['limit']
        self.feedfile = kwargs['feedfile']
        self.refreshtime = kwargs['refreshtime']
        self.printtime = kwargs['printtime']

    def _get_urls(self):
        with open(self.feedfile, 'r') as fd:
            return [f.strip() for f in  fd.readlines()]

    def get_entries(self):
        _entries = []
        for url in self._get_urls():
            content = feedparser.parse(url)
            _entries += content.entries
        entries = self.sort_entries(_entries)
        self.limit_entries(entries)

        self.event_loop.call_later(self.refreshtime, self.get_entries)

    def sort_entries(self, entries):
        return sorted(entries, key=lambda e: e.updated_parsed, reverse=True)

    def limit_entries(self, entries):
        if entries[:self.limit] != self.entries:
            self.entries = deque(entries[:self.limit])

    def get_entry(self):
        if self.entries:
            return self.entries[0]

    def format_entry(self, entry):
        return self.output_format.format(entry=entry)

    def flush_line(self):
        if self.flush:
            print(' ' * self.line_len, end='\r', flush=True)
            self.end = '\r'
        else:
            self.end = '\n'

    def print_entry(self):
        self.flush_line()

        entry = self.get_entry()
        formatted = self.format_entry(entry)
        self.line_len = len(formatted)
        print(formatted, end=self.end, flush=self.flush)

        self.entries.rotate()
        self.event_loop.call_later(self.printtime, self.print_entry)

    def run(self):
        self.get_entries()
        self.print_entry()
        self.event_loop.run_forever()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Feed Reader inspired by news channels bottom stripes.',
        prog='feedbloom',
        epilog='Enjoy!')

    parser.add_argument(
        '--format',
        help='''Output format of Feedbloom using python `str.format`
        with feed entry as kwarg''',
        default='{entry.updated} - {entry.title} - {entry.link}')

    parser.add_argument(
        '--limit',
        help="Set limit of shown entries",
        default=10,
        type=int)

    parser.add_argument(
        '--flush',
        help="Flush lines to print entries. This is set to default.",
        dest='flush',
        default=True,
        action='store_true')

    parser.add_argument(
        '--no-flush',
        help=" Don't flush lines to print entries",
        dest='flush',
        action='store_false')

    parser.add_argument(
        '--feedfile',
        help="Path of file with feed urls.",
        default=os.path.join(_config_dir, 'feeds.txt'),
    )

    parser.add_argument(
        '--refreshtime',
        help="Time to refresh feeds (in seconds).",
        type=int,
        default=300,
    )

    parser.add_argument(
        '--printtime',
        help="Time between feed prints",
        type=int,
        default=5,
    )

    return parser.parse_args()

def main():
    args = parse_args()
    feedbloom = FeedBloom(
        output_format=args.format,
        flush=args.flush,
        limit=args.limit,
        feedfile=args.feedfile,
        refreshtime=args.refreshtime,
        printtime=args.printtime)
    feedbloom.run()
