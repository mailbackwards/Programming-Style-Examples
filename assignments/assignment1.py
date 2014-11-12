import sys
import csv
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "http://www.archives.gov/federal-register/electoral-college/2012/popular-vote.html"
BASE_FILE = "~/projects/mas500/U._S._Electoral_College.html"

class ElectionResults:
    headers = ['State', 'Democratic', 'Republican', 'Libertarian', 'Green', 'Other', 'Total']

    def __init__(self, src):
        self.src = src
        self.soup = None
        self.rows = None

    def load(self):
        if self.src.startswith('http'):
            r = requests.get(self.src)
            self.html = r.text
        else:
            with open(self.src, 'r') as f:
                self.html = f.read()
        self.soup = BeautifulSoup(self.html)

    def set_rows(self):
        if self.soup is None:
            self.load()
        rows = []
        html_rows = self.soup.find('table').find('table').findAll('tr')
        for html_row in html_rows[1:]:
            row = [html_row.find('th').text] + [td.text for td in html_row.findAll('td')]
            rows.append(row)
        self.rows = rows

    def get_results(self):
        if self.rows is None:
            self.set_rows()
        return [self.headers] + self.rows

    def get_state(self, state):
        states = [i[0] for i in self.rows]
        try:
            row = self.rows[states.index(state)][1:]
        except IndexError:
            return None
        result = {}
        for index, header in enumerate(self.headers[1:]):
            result[header] = 0 if row[index] == "-" else int(row[index].strip("*"))
        return result

    def get_totals(self):
        return self.get_state('Totals')


class TableSerializer:

    def __init__(self, rows):
        self.rows = rows

    def write_csv(self, outfile='outfile.csv'):
        with open(outfile, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(self.rows)

    def serialize_json(self):
        headers = self.rows[0]
        results = {}
        for row in self.rows[1:]:
            key = row[0]
            val = {}
            for index, item in enumerate(row[1:]):
                header = headers[index+1]
                val[header] = item
            results[key] = val
        return results

    def write_json(self, outfile='outfile.json'):
        with open(outfile, 'w') as f:
            json.dump(self.serialize_json(), f)


if __name__ == "__main__":
    args = sys.argv[1:]
    e = ElectionResults(BASE_URL)
    e.set_rows()
    if not args:
        print e.get_results()
    elif args[-1] == "csv":
        TableSerializer(e.get_results()).write_csv()
    elif args[-1] == "json":
        TableSerializer(e.get_results()).write_json()
    else:
        for arg in args:
            print arg.upper() + ": "
            print e.get_state(arg.upper())
            print "---------------"
