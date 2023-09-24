#!/bin/env python3
#
# Scan provided URLs by different HTTP methods
# URLs can be provided by text file (line by line) or
# directly through command line parameter.
# Custom cookies and headers are supported.
#
import requests
from typing import Dict, List, TextIO, Union
import argparse
import re

USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0; HTC One M9 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'
]

METHODS: List[str] = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
]

EXTRA_METHODS: List[str] = [
    "SETTINGS",
    "HEAD",
    "CONNECT",
    "OPTIONS",
    "TRACE",
]

parser = argparse.ArgumentParser(
    description=f"Scan different HTTP methods for provided URLs. Default methods: {', '.join(METHODS)}.")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-f', metavar='path',
                   type=argparse.FileType('r'), help="file with list of URLs (format: one line = one URL)")
group.add_argument('-u', metavar='url', type=str, help="URL to scan")
parser.add_argument('--headers', metavar='headers', default="", type=str,
                    help="example: 'FIRST=HEADER_VALUE;SECOND=HEADER_VALUE'")
parser.add_argument('--cookies', metavar='cookies', default="", type=str,
                    help="example: 'FIRST=COOKIE_VALUE;SECOND=COOKIE_VALUE'")
parser.add_argument('-e', action='store_true',
                    help=f"use extra methods: {', '.join(EXTRA_METHODS)}")


class Arguments:
    args = parser.parse_args()

    @classmethod
    def get_urls(cls) -> List[str]:
        if cls.args.u:
            return [cls.args.u]

        if cls.args.f:
            file: TextIO = cls.args.f
            lines = [line.strip() for line in file.readlines()]
            file.close()
            return lines

        return []

    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        result = cls._parse_to_dict(cls.args.headers)
        result.update({
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        })
        return result

    @classmethod
    def get_cookies(cls) -> Dict[str, str]:
        return cls._parse_to_dict(cls.args.cookies)

    @classmethod
    def get_methods(cls) -> List[str]:
        return METHODS + (EXTRA_METHODS if cls.args.e else [])

    @staticmethod
    def _parse_to_dict(raw: str) -> Dict[str, str]:
        items = raw.split(';')
        result: Dict[str, str] = dict()

        for item in items:
            if item == '':
                continue

            key, val = item.split("=")
            result.update({key: val})

        return result


class Request:
    error: Union[Exception, None] = None
    resp: Union[requests.Response, None] = None

    def __init__(self,
                 url: str,
                 method: str,
                 headers: Dict[str, str],
                 cookies: Dict[str, str]
                 ) -> None:
        self.method = method

        try:
            self.resp = requests.request(method=method, url=url,
                                         cookies=cookies, headers=headers)
        except Exception as e:
            self.error = e

    def log_resp(self) -> None:
        print(" {:8} ".format(self.method), end="")

        if self.error is None and self.resp is not None:
            print(f"status = {self.resp.status_code}, ", end="")
            print(f"size = {len(self.resp.content)} bytes", end="\n")
        else:
            print(f"error = {self._get_error()}", end="\n")

    def _get_error(self) -> Union[str, None]:
        # Return error string if present, otherwise return full exception
        if self.error is None:
            return None

        err = str(self.error)
        result = re.search(r"Errno.*]\s(.*)'", err)

        return result.group(1) if result else err


def main():
    urls = Arguments.get_urls()
    headers = Arguments.get_headers()
    cookies = Arguments.get_cookies()
    methods = Arguments.get_methods()

    for url in urls:
        print('\n', url, sep="")

        for method in methods:
            req = Request(url, method, headers, cookies)
            req.log_resp()


if __name__ == '__main__':
    main()
