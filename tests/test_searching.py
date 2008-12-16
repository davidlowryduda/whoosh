import unittest

from whoosh import fields, index, searching, scoring, store, writing
from whoosh.query import *

class TestReading(unittest.TestCase):
    def setUp(self):
        s = fields.Schema(key = fields.ID(stored = True),
                          name = fields.TEXT,
                          value = fields.TEXT)
        st = store.RamStorage()
        ix = index.Index(st, s, create = True)
        
        w = writing.IndexWriter(ix)
        w.add_document(key = u"A", name = u"Yellow brown", value = u"Blue red green render purple?")
        w.add_document(key = u"B", name = u"Alpha beta", value = u"Gamma delta epsilon omega.")
        w.add_document(key = u"C", name = u"One two", value = u"Three rendered four five.")
        w.add_document(key = u"D", name = u"Quick went", value = u"Every red town.")
        w.add_document(key = u"E", name = u"Yellow uptown", value = u"Interest rendering outer photo!")
        w.close()
        
        self.ix = ix
    
    def _get_keys(self, stored_fields):
        return sorted([d.get("key") for d in stored_fields])
    
    def _docs(self, q, s):
        return self._get_keys([s.stored_fields(docnum) for docnum
                               in q.docs(s)])
    
    def _doc_scores(self, q, s, w):
        return self._get_keys([s.stored_fields(docnum) for docnum, score
                               in q.doc_scores(s, weighting = w)])
    
    def test_docs_method(self):
        s = self.ix.searcher()
        
        self.assertEqual(self._get_keys(s.docs(name = "yellow")), [u"A", u"E"])
        self.assertEqual(self._get_keys(s.docs(value = "red")), [u"A", u"D"])
        
    def test_queries(self):
        s = self.ix.searcher()
        
        tests = [
                 (Term("name", u"yellow"),
                  [u"A", u"E"]),
                 (Term("value", u"red"),
                  [u"A", u"D"]),
                 (Term("value", u"zeta"),
                  []),
                 (Require(Term("value", u"red"), Term("name", u"yellow")),
                  [u"A"]),
                 (And([Term("value", u"red"), Term("name", u"yellow")]),
                  [u"A"]),
                 (Or([Term("value", u"red"), Term("name", u"yellow")]),
                  [u"A", u"D", u"E"]),
                 (Or([Term("value", u"red"), Term("name", u"yellow"), Not(Term("name", u"quick"))]),
                  [u"A", u"E"]),
                 (AndNot(Term("name", u"yellow"), Term("value", u"purple")),
                  [u"E"]),
                 (Variations("value", u"render"), [u"A", u"C", u"E"])
                ]
        
        for query, result in tests:
            self.assertEqual(self._docs(query, s), result)
        
        for wcls in dir(scoring):
            if wcls is scoring.Weighting: continue
            if isinstance(wcls, scoring.Weighting):
                for query, result in tests:
                    self.assertEqual(self._doc_scores(query, s, wcls), result)
        
        for methodname in ("_docs", "_doc_scores"):
            method = getattr(self, methodname)


if __name__ == '__main__':
    unittest.main()
