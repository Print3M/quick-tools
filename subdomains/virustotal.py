#!/usr/bin/python3
#
# Script for scraping subdomains from virustotal.com
# by its API (without API key or any special permission)

import sys
import json
import requests
import random

USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 8.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 6P Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.83 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0; HTC One M9 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.3',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'
]

def get_api_data(domain):
    """
        This function is based on simple fact about virustotal API. Pagination is based on 'cursor' URL param.
        All pages of API are based on the same 'cursor' parameter with one diffrent char (id_char).
        This char is every fourth character of upper case alphabet, then (if needed) lower case alphabet.
        For example: first page – A, second page – E, third page – I ...
        So we can enumerate all pages of requested domain.
    """
    i = 0
    domains = []
    while True:
        id_char = 'AEIMQUYcgkosw'[i]
        resp = requests.get(
            f'https://www.virustotal.com/ui/domains/{domain}/subdomains?relationships=resolutions&cursor=ST{id_char}wCi4%3D&limit=40',
            headers={
                'User-Agent': random.choice(USER_AGENTS)
            }
        )
        data = resp.json()

        if resp.status_code > 400 or len(data['data']) == 0:
            if resp.status_code == 429:
                sys.exit(
                    'error: API throttling mechanism requires reCaptcha.'
                    'Wait a few minutes and try again.'
                )
            break
        else:
            scraped = [item['id'] for item in data['data']]

            # Because of 'limit=40' final four pages don't provide any unique domains.
            # We have to detect last page with unique domains and break the loop.
            if set(scraped).issubset(domains):
                # All domains are redundant, so that was the last url (page)
                break
            else:
                domains += scraped
                i += 1

    return domains


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: virustotal.py <domain>')

    domain = sys.argv[1]
    domains = list(set(get_api_data(domain)))
    sys.stdout.write('\n'.join(domains) + '\n')


if __name__ == '__main__':
    main()
