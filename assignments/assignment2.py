from assignment1 import ElectionResults, TableSerializer
import unittest
import csv
import json
import os

SAMPLE_SRC = "data/U._S._Electoral_College.html"

class ElectionResultsTest(unittest.TestCase):

    def setUp(self):
        self.results = ElectionResults(SAMPLE_SRC)

    def testLoad(self):
        self.results.load()
        assert self.results != None
        assert self.results.soup != None

    def testSetRows(self):
        self.results.set_rows()
        assert len(self.results.rows) == 52 # includes DC and "Totals" lines

    def testGetResults(self):
        results = self.results.get_results()
        assert results[0] == self.results.headers
        assert results[1:] == self.results.rows

    def testGetState(self):
        self.results.set_rows()
        sample_state = "WY"
        state_result = self.results.get_state(sample_state)
        assert state_result['Democratic'] == 69286
        assert state_result['Republican'] == 170962
        assert state_result['Green'] == 0 # tests whether "-" changes to 0

    def testGetTotals(self):
        self.results.set_rows()
        totals = self.results.get_totals()
        assert totals['Democratic'] == 65446032
        assert totals['Total'] == 128556837

class TableSerializerTest(unittest.TestCase):

    def setUp(self):
        self.table = TableSerializer(ElectionResults(SAMPLE_SRC).get_results())

    def testWriteCsv(self):
        outfile_name = 'outfile.csv'
        self.table.write_csv(outfile=outfile_name)
        rows = []
        with open(outfile_name, 'r') as f:
            rows = [row for row in csv.reader(f)]
        assert rows == self.table.rows
        os.remove(outfile_name)

    def testSerializeJson(self):
        serialized_results = self.table.serialize_json()
        headers = ['Republican', 'Democratic', 'Libertarian', 'Green', 'Other', 'Total']
        assert set(serialized_results.keys()) - set([i[0] for i in self.table.rows[1:]]) == set([])
        assert set(serialized_results.values()[0].keys()) - set(headers) == set([])

    def testWriteJson(self):
        outfile_name = 'outfile.json'
        self.table.write_json(outfile=outfile_name)
        with open(outfile_name, 'r') as f:
            results = json.load(f)
        assert results == self.table.serialize_json()
        os.remove(outfile_name)

if __name__ == "__main__":
    unittest.main()
