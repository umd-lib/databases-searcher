import json
import logging
import furl
import os
import requests

from flask import Flask, request
from dotenv import load_dotenv
from waitress import serve
from paste.translogger import TransLogger
from bs4 import BeautifulSoup

load_dotenv('../.env')

env = {}
for key in ('LIBGUIDES_DB_BASE', 'NO_RESULTS_URL', 'MODULE_URL',
            'SITE_ID', 'SEARCH_ACTION'):
    env[key] = os.environ.get(key)
    if env[key] is None:
        raise RuntimeError(f'Missing environment variable: {key}')

no_results_url = env['NO_RESULTS_URL']
module_url = env['MODULE_URL']
site_id = env['SITE_ID']
search_action = env['SEARCH_ACTION']

debug = os.environ.get('FLASK_DEBUG')

logger = logging.getLogger('databases-searcher')
loggerWaitress = logging.getLogger('waitress')

if debug:
    logger.setLevel(logging.DEBUG)
    loggerWaitress.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    loggerWaitress.setLevel(logging.INFO)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
def root():
    return {'status': 'ok'}


@app.route('/ping')
def ping():
    return {'status': 'ok'}


@app.route('/search')
def search():
    args = request.args

    # Check query param
    if 'q' not in args or args['q'] == '':
        return {
            'error': {
                'msg': 'q parameter is required',
            },
        }, 400

    query = args['q']

    # per_page in this case is just a limit without any real pagination. Using limit as a param would
    # be more accurate, but it is also non-standard.

    limit = 3
    if 'per_page' in args and args['per_page'] != "":
        limit = int(args['per_page'])

    params = {
        'site_id': site_id,
        'search_action': search_action,
        'is_widget': '0',
        'search': query
    }

    full_query_url = env['LIBGUIDES_DB_BASE']

    search_url = furl.furl(full_query_url)

    # Execute Databases search
    try:
        response = requests.get(search_url.url, params=params)
    except Exception as err:
        logger.error(f'Search error at url'
                     '{search_url.url}, params={params}\n{err}')

        return {
            'endpoint': 'databases',
            'error': {
                'msg': f'Search error',
            },
        }, 500

    if response.status_code not in [200, 206]:
        logger.error(f'Received {response.status_code} with q={query}')

        return {
            'endpoint': 'databases',
            'error': {
                'msg': f'Received {response.status_code} for q={query}',
            },
        }, 500

    logger.debug(f'Submitted url={search_url.url}, params={params}')
    logger.debug(f'Received response {response.status_code}')

    json_content = json.loads(response.text)
    rendered_content = None
    if 'data' in json_content:
        rendered_content = parse_results(json_content['data']['html'], limit)

    total_records = 0
    if rendered_content is not None and 'data' in json_content:
        total_records = json_content['data']['count']

    module_link = module_url + query

    api_response = {
        'endpoint': 'databases',
        'query': query,
        'per_page': 3,
        'page': 1,
        'total': total_records,
        'module_link': module_link,
    }

    if total_records > 0:
        api_response['results'] = rendered_content
    else:
        api_response['error'] = build_no_results()

    return api_response


def build_no_results():
    return {
        'msg': 'No Results',
        'no_results_url': no_results_url,
    }


def parse_results(raw_html, limit):
    result = []
    soup = BeautifulSoup(raw_html, 'html.parser')

    i = 0
    for div in soup.find_all("div", {"class": "s-lg-az-result"}):
        rtitle = None
        href = None
        desc = None
        entry = {}
        for title in div.find_all("div", {"class": "s-lg-az-result-title"}):
            rtitle = title.text
        for ahref in div.find_all("a", href=True):
            href = ahref['href']
        for description in div.find_all("div", {"class": "s-lg-az-result-description"}):
            desc = description.text
        if rtitle is not None and href is not None:
            entry['title'] = rtitle
            entry['link'] = href
            entry['description'] = desc
            entry['item_format'] = 'database'
            i = i + 1
            result.append(entry)
        if i >= limit:
            break

    return result


def get_total_records(parsed_content):
    return len(parsed_content)


if __name__ == '__main__':
    # This code is not reached when running "flask run". However the Docker
    # container runs "python app.py" and host='0.0.0.0' is set to ensure
    # that flask listens on port 5000 on all interfaces.

    # Run waitress WSGI server
    serve(TransLogger(app, setup_console_handler=True),
          host='0.0.0.0', port=5000, threads=10)
