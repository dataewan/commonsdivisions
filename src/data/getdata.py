"""Get data from the API."""

import requests
import argparse
import os
import glob
import shutil
import csv
import time
import random

DIVISION_FILE = './data/raw/divisions.csv'

def parsepagerecord(record):
    """Split a division record into interesting parts.

    :record: json object from the API
    :returns: object containing the interestingparts

    """
    parsed = {
        'title': record['title'],
        'date': record['date']['_value'],
        'id': record['_about'].split('/')[-1],
        'uin': record['uin']
    }
    return parsed


def getdivisionpage(pageid):
    """Return a page of divisions

    :pageid: page number to get
    :returns: object containing all the divisions, and a check if there is
        another page to come
    """
    url = 'http://lda.data.parliament.uk/commonsdivisions.json'
    r = requests.get(url, params={'_page': pageid})
    result = r.json()['result']

    # check if there is another page to come
    anotherpage = 'next' in result

    # a list of all the interesting parts of the division
    interestingparts = [parsepagerecord(i) for i in result['items']]

    return {
        'divisions': interestingparts,
        'anotherpage': anotherpage
    }


def deletedivisions():
    """Delete any division files that already exist.
    """
    if os.path.exists(DIVISION_FILE):
        os.remove(DIVISION_FILE)

def getwriter():
    """Get a csv writer to output
    :returns: writer object
    """
    f = open(DIVISION_FILE, 'w')
    writer = csv.DictWriter(f, fieldnames=['title', 'date', 'id', 'uin'])
    writer.writeheader()
    return f, writer



def outputpage(parsedpage, writer):
    """Write out parsed page to file

    :parsedpage: record
    """
    divisions = parsedpage['divisions']
    writer.writerows(divisions)


def getdivisions():
    """Get all the divisions, store them in a text file.
    """
    # delete the existing divisions
    deletedivisions()
    f, writer = getwriter()

    # first record is where we start from
    i = 1
    d = getdivisionpage(i)
    while d['anotherpage']:
        outputpage(d, writer)
        i += 1
        print(i)
        time.sleep(random.random() * 0.2)
        d = getdivisionpage(i)
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--divisions', help='Get all the divisions',
                        action='store_true')
    args = parser.parse_args()
    if args.divisions:
        getdivisions()
