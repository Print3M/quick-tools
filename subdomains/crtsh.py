#!/usr/bin/python3
#
# Script for scraping subdomains from crt.sh website
# (without API key or any special permission)

import requests
from bs4 import BeautifulSoup
import sys
import time
import random


def get_domains(contents_list):
    """
        Return list of domains without <br/> 
    """
    return [item for item in contents_list if str(item) != '<br/>']


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: crtsh.py <domain>')

    domain = sys.argv[1]

    while True:
        resp = requests.get(f'https://crt.sh/?q={domain}')

        # Catch random 502 error
        if resp.status_code != 502:
            break
        else:
            # If 502 error wait random time (0–1 sec) and try again
            time.sleep(random.random())

    if resp.status_code != 200:
        sys.exit(f'error: response status code {resp.status_code}')

    # Extract from source code
    soup = BeautifulSoup(resp.text, features='html.parser')
    all_trs = soup.find_all('td', {'class': 'outer'})[1].find_all('tr')[1:]

    scraped_domains = []
    for tr in all_trs:
        domains_td = tr.find_all('td')[4]
        scraped_domains += get_domains(domains_td)

    # Create unique list
    scraped_domains = list(set(scraped_domains))
    sys.stdout.write('\n'.join(scraped_domains) + '\n')


if __name__ == '__main__':
    main()
