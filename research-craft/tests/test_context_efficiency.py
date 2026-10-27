"""Scientific information and exact source-recovery contracts, not token estimates."""
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(os.environ.get('RESEARCH_CRAFT_UNDER_TEST',Path(__file__).resolve().parents[1]))
loader=importlib.util.spec_from_file_location('context_research',ROOT/'scripts/research.py')
R=importlib.util.module_from_spec(loader);loader.loader.exec_module(R)

class ContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def run_cli(self,*args):
        out,err=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            try:code=R.main(['--root',str(self.root),*args])
            except SystemExit as ex:code=ex.code
        return code,out.getvalue(),err.getvalue()
    def write(self,name,raw):
        p=self.root/name;p.write_bytes(raw);return p
    def test_protected_content_is_exactly_recoverable(self):
        raw=('Reviewer: Do not omit the failed comparison.\r\n'
             'Advisor (identity unconfirmed): Only if the split is fixed, not otherwise.\r\n'
             'mIoU=70.0500%; Pd decreases by -0.6800 percentage points; Fa=7.7400e-6.\r\n'
             'split=test; seed=17; members=[s001,s007,s019]; LR=1.00e-4.\r\n'
             'Formula: y=x/(n-1), only for n>1; HYPOTHESIS, rival=calibration.\r\n'
             'FAILED: normalization changed; not a verified mechanism.\r\n').encode('utf-8')
        self.write('source.txt',raw)
        code,out,err=self.run_cli('read-slice','source.txt','--range','1:6')
        self.assertEqual(code,0,err);data=json.loads(out)
        self.assertEqual(data['ranges'][0]['text'].encode('utf-8'),raw)
        self.assertEqual(data['sha256'],hashlib.sha256(raw).hexdigest())
        self.assertFalse((self.root/'.research').exists())
    def test_multiple_ranges_keep_boundaries_and_omissions_explicit(self):
        self.write('x.txt',b'A\nB\nC\nD\n')
        code,out,err=self.run_cli('read-slice','x.txt','--range','1:1','--range','3:4')
        self.assertEqual(code,0,err);d=json.loads(out)
        self.assertEqual([r['text'] for r in d['ranges']],['A\n','C\nD\n'])
        self.assertFalse(d['complete_file']);self.assertEqual(d['total_lines'],4)
    def test_stale_source_rejected_even_with_same_size_and_mtime(self):
        p=self.write('x.txt',b'old\n');old=hashlib.sha256(p.read_bytes()).hexdigest();stamp=p.stat()
        p.write_bytes(b'new\n');os.utime(p,ns=(stamp.st_atime_ns,stamp.st_mtime_ns))
        code,out,err=self.run_cli('read-slice','x.txt','--range','1:1','--expect-sha256',old)
        self.assertEqual(code,2);self.assertEqual(out,'');self.assertIn('changed',err.lower())
    def test_invalid_and_out_of_file_ranges_are_not_silently_truncated(self):
        self.write('x.txt',b'one\ntwo\n')
        for span in ['0:1','2:1','1:3','-1:2']:
            code,out,_=self.run_cli('read-slice','x.txt','--range',span)
            self.assertEqual(code,2,span);self.assertEqual(out,'')
    def test_overlapping_ranges_rejected(self):
        self.write('x.txt',b'A\nB\nC\n')
        code,out,_=self.run_cli('read-slice','x.txt','--range','1:2','--range','2:3')
        self.assertEqual(code,2);self.assertEqual(out,'')
    def test_paths_cannot_escape_project(self):
        code,out,_=self.run_cli('read-slice','../outside.txt','--range','1:1')
        self.assertEqual(code,2);self.assertEqual(out,'')
    def test_zero_and_negative_limits_cannot_dump_registry(self):
        self.run_cli('init')
        self.run_cli('issue','add','--title','keep this local')
        for limit in ['0','-1']:
            code,out,_=self.run_cli('list','issues','--limit',limit)
            self.assertEqual(code,2);self.assertEqual(out,'')
    def test_positive_limit_and_id_order_remain_compatible(self):
        self.run_cli('init')
        ids=[]
        for i in range(4):ids.append(self.run_cli('issue','add','--title',str(i))[1].strip())
        code,out,err=self.run_cli('list','issues','--limit','2')
        self.assertEqual(code,0,err);self.assertEqual([r['issue_id'] for r in json.loads(out)],ids[-2:])
        code,out,_=self.run_cli('list','issues','--id',ids[0],'--limit','2')
        self.assertEqual(code,0);self.assertEqual(json.loads(out)[0]['issue_id'],ids[0])
    def test_csv_evidence_keeps_raw_precision_and_multiline_locators(self):
        raw=b'key,note,score\r\na,"two\r\nlines",001.2300\r\nb,ok,-0.006800\r\n'
        self.write('m.csv',raw)
        code,out,err=self.run_cli('summarize-csv','m.csv','--columns','score','--key','key','--evidence')
        self.assertEqual(code,0,err);d=json.loads(out);e=d['evidence']['score']
        self.assertEqual(d['raw_ref']['sha256'],hashlib.sha256(raw).hexdigest())
        self.assertEqual(e['maximum']['raw_value'],'001.2300')
        self.assertEqual(e['maximum']['lines'],[2,3]);self.assertEqual(e['minimum']['raw_value'],'-0.006800')
        self.assertEqual(e['minimum']['lines'],[4,4]);self.assertEqual(e['minimum']['key'],{'key':'b'})
    def test_csv_nonfinite_and_nonnumeric_are_counted_not_silently_proven_absent(self):
        self.write('m.csv',b'score\nNaN\nInfinity\nword\n1.2500\n')
        code,out,err=self.run_cli('summarize-csv','m.csv','--columns','score','--evidence')
        self.assertEqual(code,0,err);e=json.loads(out)['evidence']['score']
        self.assertEqual(e['nonfinite_count'],2);self.assertEqual(e['nonnumeric_count'],1)
        self.assertEqual([r['raw_value'] for r in e['invalid_examples']],['NaN','Infinity','word'])
    def test_csv_default_output_contract_is_unchanged(self):
        self.write('m.csv',b'score\n1\n2\n')
        code,out,err=self.run_cli('summarize-csv','m.csv','--columns','score')
        self.assertEqual(code,0,err);d=json.loads(out)
        self.assertEqual(set(d),{'source','rows','columns'})
        self.assertEqual(d['columns']['score']['mean'],1.5)
    def test_invalid_example_cap_declares_incomplete_coverage(self):
        self.write('m.csv',b'score\nNaN\nbad\nInfinity\nother\n-1.2000\n')
        code,out,err=self.run_cli('summarize-csv','m.csv','--columns','score','--evidence')
        self.assertEqual(code,0,err);e=json.loads(out)['evidence']['score']
        self.assertEqual(len(e['invalid_examples']),3)
        self.assertEqual(e['nonfinite_count']+e['nonnumeric_count'],4)
        self.assertFalse(e['invalid_examples_exhaustive'])
        self.assertEqual(e['minimum']['raw_value'],'-1.2000')
    def test_evidence_mode_refuses_detected_mid_read_mutation(self):
        from unittest.mock import patch
        self.write('m.csv',b'score\n1\n')
        with patch.object(R,'_source_signature',side_effect=[(8,1,7),(8,2,7)]):
            code,out,err=self.run_cli('summarize-csv','m.csv','--columns','score','--evidence')
        self.assertEqual(code,2);self.assertEqual(out,'');self.assertIn('changed',err)
    def test_utf8_bom_is_decoded_while_hash_keeps_original_bytes(self):
        raw=b'\xef\xbb\xbf'+ '不得改写否定。\n'.encode('utf-8');self.write('m.txt',raw)
        code,out,err=self.run_cli('read-slice','m.txt','--range','1:1')
        self.assertEqual(code,0,err);d=json.loads(out)
        self.assertEqual(d['ranges'][0]['text'],'不得改写否定。\n');self.assertEqual(d['sha256'],hashlib.sha256(raw).hexdigest())

if __name__=='__main__':unittest.main()
