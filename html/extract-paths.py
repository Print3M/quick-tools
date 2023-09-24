#!/usr/bin/python3
#
# Script for scraping paths from URL recursively.
#
import requests
import re
import argparse
from typing import List, Set, Dict, Union
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(
    description=f"Extract all paths from provided URL")
parser.add_argument('-u', metavar='url', type=str, help="URL to scrap", required=True)
parser.add_argument('--headers', metavar='headers', default="", type=str,
                    help="example: 'FIRST=HEADER_VALUE;SECOND=HEADER_VALUE'")
parser.add_argument('--cookies', metavar='cookies', default="", type=str,
                    help="example: 'FIRST=COOKIE_VALUE;SECOND=COOKIE_VALUE'")

class Arguments:
    args = parser.parse_args()

    @classmethod
    def get_url(cls) -> str:
        return cls.args.u

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

class Site:
    def __init__(self, html: str) -> None:
        self.soup = BeautifulSoup(html, features='html.parser')

    def extract_media_urls(self) -> Set[str]:
        result: List[str] = []
        result += self._get_attr_from_tags('img', 'src')
        result += self._get_attr_from_tags('video', 'src') 
        result += self._get_attr_from_tags('link', 'href') 

        return set(result)

    def extract_script_urls(self) -> Set[str]:
        result: List[str] = []
        result += self._get_attr_from_tags('script', 'src') 

        return set(result)

    def extract_link_urls(self) -> Set[str]:
        result: List[str] = []
        result += self._get_attr_from_tags('a', 'href')
        result += self._get_attr_from_tags('form', 'action') 

        return set(result)

    def _get_attr_from_tags(self, tag_name: str, attr_name: str) -> List[str]:
        tags = self.soup.find_all(tag_name)
        result: List[str] = []

        for tag in tags:
            value = tag.get(attr_name)

            if value:
                result.append(value)

        return result

PATHS = set()

if __name__ == "__main__":
    args = {
        "url": Arguments.get_url(),
        "cookies": Arguments.get_cookies(),
        "headers": Arguments.get_headers() 
    }
    print(f"[*] Scraping: {args['url']} ")
    req = requests.get(**args)

    print("[*] Extracting urls")
    site = Site(req.text)

    print("\n[+] Media urls:")
    print(*site.extract_media_urls(), sep="\n")

    print("\n[+] Script urls:")
    print(*site.extract_script_urls(), sep="\n")    

    print("\n[+] Link urls:")
    print(*site.extract_link_urls(), sep="\n")    
