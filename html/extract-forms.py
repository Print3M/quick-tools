#!/usr/bin/python3
#
# Script for HTML forms extraction.
#
import sys
import requests
from bs4 import BeautifulSoup

def find_all_inputs(elm):
    return elm.find_all('input') + elm.find_all('textarea') + elm.find_all('select')

def without_keys(d, *keys):
    # Exclude :keys from :d
    return dict(filter(lambda key_value: key_value[0] not in keys, d.items()))

def get_html_by_url(url):
    resp = requests.get(url)

    if resp.status_code != 200:
        exit(f'error: response code {resp.status_code}')
    else:
        return resp.text

def main():
    if not sys.stdin.isatty():
        # Get html code from stdin
        html = sys.stdin.read()   
    elif len(sys.argv) == 2:
        # Download html code by passed url
        html = get_html_by_url(sys.argv[1])
    else:
        exit(
            'usage: extract-forms.py <url>\n'
            '       cat code.html | extract-forms.py'
        )

    soup = BeautifulSoup(html, features='html.parser')
    result = '========================= FORMS ======================='

    # Collect all inputs inside of forms
    all_forms = soup.find_all('form')
    for i, form in enumerate(all_forms):
        result += f"""
    {i+1}. form
        action: {form.get('action', '')}
        method: {form.get('method', '')}
        other attrs: {without_keys(form.attrs, 'action', 'method')}
        inputs:"""

        for z, element in enumerate(find_all_inputs(form)):
            result += f"""
            {z+1}. input
                tag: {element.name}
                name: {element.get('name', '')}
                type: {element.get('type', '')}
                other attrs: {without_keys(element.attrs, 'name', 'type')}"""

        # Remove form's inputs (for collecting standalone inputs)
        all_forms[i].clear()

    result += '\n\n=================== STANDALONE INPUTS ====================='
    
    # Collect all inputs without forms
    for i, element in enumerate(find_all_inputs(soup)):
        result += f"""
    {i+1}. input
        tag: {element.name}
        name: {element.get('name', '')}
        type: {element.get('type', '')}
        other attrs: {without_keys(element.attrs, 'name', 'type')}"""

    # Return to stdout
    sys.stdout.write(result + '\n')

if __name__ == '__main__':
    main()