import copy
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools/research"))
import paper_rebaseline as p


class PaperRebaselineTests(unittest.TestCase):
    def test_66_cells(self):
        rows = p.run_order()
        self.assertEqual(len(rows), 66)
        self.assertEqual([sum(r["stage"] == s for r in rows) for s in ("primary", "recall", "width")], [36,24,6])

    def test_primary_position_balance(self):
        rows = p.run_order()[:36]
        for position in range(6):
            self.assertEqual({rows[6*b+position]["cell"] for b in range(6)}, set(p.CELLS))

    def test_sweep_repetitions(self):
        rows = p.run_order()[36:60]
        for v in ("PAPER", "MODERN"):
            for l in (50,75,125,150):
                self.assertEqual(sum(r["version"]==v and r["l_search"]==l for r in rows),3)

    def test_paper_cli(self):
        c=p.run_order()[2]
        self.assertEqual(p.search_argv("b","i","q","g",c),["b","uint8","i","8","32","q","g","10","l2","2","0","100"])

    def test_modern_cli(self):
        c=p.run_order()[4]
        self.assertEqual(p.search_argv("b","i","q","g",c),["b","uint8","i","8","32","q","g","10","l2","pq","2","0","100"])

    def test_percentile_identity(self):
        text="L I/O Width QPS AvgLat(us) P99 Lat Mean Hops Mean IOs Recall@10\n100 32 3000 2600 8000 0 123 99.14"
        a=p.parse_output(text,"PAPER",100,32);b=p.parse_output(text,"MODERN",100,32)
        self.assertEqual(a["p999_latency_us"],8000);self.assertIsNone(a["p99_latency_us"])
        self.assertEqual(b["p99_latency_us"],8000);self.assertIsNone(b["p999_latency_us"])
        self.assertIsNone(a["p95_latency_us"])

    def test_exit_zero_diagnostics_rejected(self):
        for text in ("[ERROR] Failed Bad file descriptor", "mem_L = 0, please use larger value."):
            with self.assertRaises(ValueError):p.parse_output(text,"PAPER",100,32)

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):p.parse_output("100 32 nan 2600 8000 0 123 99.14","PAPER",100,32)

    def test_duplicate_rows_rejected(self):
        row="100 32 3000 2600 8000 0 123 99.14\n"
        with self.assertRaises(ValueError):p.parse_output(row*2,"PAPER",100,32)

    def test_missing_row_rejected(self):
        with self.assertRaises(ValueError):p.parse_output("75 32 3000 2600 8000 0 123 99.14","PAPER",100,32)

    def test_deterministic_block_bootstrap(self):
        a=p.paired([90,80,95,91,85,89],[100]*6)
        self.assertEqual(a,p.paired([90,80,95,91,85,89],[100]*6))
        self.assertEqual(a["n"],6);self.assertEqual(a["statistical_unit"],"block")

    def test_quantile_convention(self):
        self.assertEqual(p.quantile([0,10],.95),9.5)

    def test_empty_metrics_not_zero(self):
        with self.assertRaises(ValueError):p.descriptive([])

    def test_incomplete_pairs(self):
        with self.assertRaises(ValueError):p.paired([1],[1,2])

    def fixture(self):
        plan=dict(execution_ready=True,order=p.run_order(),binaries=dict(PAPER="a",MODERN="b"),
                  indexes=dict(PAPER="paper",MODERN=p.INDEX))
        records=[dict(**r,run_id=str(i),subject_commit=p.PAPER if r["version"]=="PAPER" else p.MODERN,
                      binary_sha256=plan["binaries"][r["version"]],input_package_sha256=p.INPUT,
                      index_package_sha256=plan["indexes"][r["version"]],checksums_valid=True,
                      environment_valid=True,telemetry_valid=True,quality_valid=True,exit_code=0,status="accepted")
                 for i,r in enumerate(plan["order"])]
        return plan,records,dict(pre_audits_pass=True,post_audits_pass=True)

    def test_complete_synthetic_ledger(self):
        plan,records,audits=self.fixture();self.assertTrue(p.validate_records(plan,records,audits))

    def test_blocked_plan_never_accepts(self):
        plan,records,audits=self.fixture();plan["execution_ready"]=False
        with self.assertRaises(ValueError):p.validate_records(plan,records,audits)

    def test_fail_closed_evidence(self):
        for key,value in [("sequence",99),("subject_commit","wrong"),("binary_sha256","wrong"),
                          ("index_package_sha256","wrong"),("input_package_sha256","wrong"),
                          ("checksums_valid",False),("environment_valid",False),("telemetry_valid",None),
                          ("quality_valid",None),("exit_code",1)]:
            with self.subTest(key=key):
                plan,records,audits=self.fixture();records[0][key]=value
                with self.assertRaises(ValueError):p.validate_records(plan,records,audits)

    def test_missing_run(self):
        plan,records,audits=self.fixture()
        with self.assertRaises(ValueError):p.validate_records(plan,records[:-1],audits)

    def test_reused_run(self):
        plan,records,audits=self.fixture();records[1]["run_id"]=records[0]["run_id"]
        with self.assertRaises(ValueError):p.validate_records(plan,records,audits)

    def test_missing_post_audit(self):
        plan,records,audits=self.fixture();audits["post_audits_pass"]=False
        with self.assertRaises(ValueError):p.validate_records(plan,records,audits)

    def test_validation_does_not_mutate(self):
        plan,records,audits=self.fixture();before=copy.deepcopy((plan,records));p.validate_records(plan,records,audits)
        self.assertEqual((plan,records),before)


if __name__ == "__main__":unittest.main()
