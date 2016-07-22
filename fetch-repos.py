#!/usr/bin/env python

import json
import httplib
import os
import re
import sys
import time
import urlparse


def fetch_repo(url):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    repos = []
    http = httplib.HTTPSConnection(netloc)
    http.request('GET',
            '%s?%s' % (path, query),
            None,
            {
                'User-Agent' : 'Jenkins Infra Repo Merger',
                'Authorization' : 'token %s' % auth_token(),
            })
    res  = http.getresponse()
    print res.status, res.reason

    if res.status != 200:
        print 'Something failed!'
        print res.read()
        exit(1)

    data = res.read()
    headers = res.getheaders()

    data = json.loads(data)
    for repo in data:
        repos.append(repo['name'])

    links = parse_link_header(res.getheader('link'))
    http.close()

    if links.has_key('next'):
        repos.extend(fetch_repo(links['next']))

    return repos


"""
Return the auth token located in ~/.github
"""
def auth_token():
    token = os.path.expanduser('~/.github-access-token')
    print "Reading %s" % token

    if os.path.exists(token):
        with file(token, 'r') as f:
            return f.read().strip()
    return None

"""
Parse the Link header into a dict of something useful
"""
def parse_link_header(header):
    links = {}

    for part in header.split(','):
        pieces = part.split(';')
        url = re.findall('<(.*)>', pieces[0])[0]
        name = re.findall('rel="(.*)"', pieces[1])[0]
        links[name] = url

    return links

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Need to pass a GitHub org name as the first argument'
        exit(1)

    print 'Fetching repos for %s', sys.argv[1]
    repos = fetch_repo('https://api.github.com/orgs/%s/repos?type=public' % sys.argv[1])
    with file('repos', 'w+') as f:
        for r in repos:
            f.write('%s\n' % r)
    exit(0)
