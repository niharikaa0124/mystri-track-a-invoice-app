"""Starter checks exercise basic setup. They are not complete acceptance coverage."""
import tempfile
import unittest
from pathlib import Path
from ledger import storage, reporting, importing


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = storage.connect(Path(self.tmp.name) / 'demo.sqlite3')
        storage.seed(self.db)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_seed_is_repeatable(self):
        storage.seed(self.db)
        self.assertEqual(len(reporting.invoices(self.db)), 6)

    def test_seed_summary(self):
        summary = reporting.overview(self.db)['summary']
        self.assertEqual(summary['invoice_count'], 6)
        self.assertEqual(summary['outstanding'], 3209.99)

    def test_one_valid_invoice(self):
        result = importing.import_csv(self.db, 'customer_id,invoice_number,amount,due_date\nHARBOR,SMOKE-1,25.00,2026-09-09\n', 'invoices')
        self.assertEqual(result['imported'], 1)

    def test_payment_reference_when_amount_is_unique(self):
        result = importing.import_csv(self.db, 'payment_id,customer_id,invoice_number,amount\nSMOKE-P1,HARBOR,INV-100,20.00\n', 'payments')
        self.assertEqual(result['imported'], 1)
        invoice = next(r for r in reporting.invoices(self.db) if r['invoice_number'] == 'INV-100')
        self.assertEqual(invoice['paid'], 20.00)

    def test_duplicate_invoice_is_skipped(self):
        row = {
            "customer_id": "HARBOR",
            "invoice_number": "DUP-001",
            "amount": 100.00,
            "due_date": "2026-09-21",
        }

        first = storage.insert_invoice(self.db, row)
        second = storage.insert_invoice(self.db, row)

        self.assertEqual(first, "imported")
        self.assertEqual(second, "skipped")

        count = self.db.execute(
            """
            SELECT COUNT(*)
            FROM invoices
            WHERE customer_id = ? AND invoice_number = ?
            """,
            (row["customer_id"], row["invoice_number"]),
        ).fetchone()[0]

        self.assertEqual(count, 1)

    from ledger import storage, reporting, importing

    def test_conflicting_duplicate_invoice_is_rejected(self):
        row = {
            "customer_id": "HARBOR",
            "invoice_number": "CONFLICT-001",
            "amount": 100.00,
            "due_date": "2026-09-21",
        }

        storage.insert_invoice(self.db, row)

        conflicting_row = {
            "customer_id": "HARBOR",
            "invoice_number": "CONFLICT-001",
            "amount": 999.00,
            "due_date": "2026-09-21",
        }

        with self.assertRaises(ValueError):
            storage.insert_invoice(self.db, conflicting_row)

        count = self.db.execute(
            """
            SELECT COUNT(*)
            FROM invoices
            WHERE customer_id = ? AND invoice_number = ?
            """,
            (row["customer_id"], row["invoice_number"]),
        ).fetchone()[0]

        self.assertEqual(count, 1)

    def test_open_filter_returns_only_open_invoices(self):
        rows = reporting.invoices(self.db, 'open')

        self.assertTrue(rows)
        self.assertTrue(all(row['status'] == 'open' for row in rows))


    def test_paid_filter_returns_only_paid_invoices(self):
        rows = reporting.invoices(self.db, 'paid')

        self.assertTrue(rows)
        self.assertTrue(all(row['status'] == 'paid' for row in rows))
    def test_invalid_data_row_does_not_block_valid_rows(self):
        csv_text = (
            'customer_id,invoice_number,amount,due_date\n'
            'HARBOR,MIXED-001,50.00,2026-09-21\n'
            'UNKNOWN,MIXED-002,75.00,2026-09-21\n'
            'MAPLE,MIXED-003,25.00,2026-09-21\n'
        )

        result = importing.import_csv(
            self.db,
            csv_text,
            'invoices'
        )

        self.assertEqual(result['imported'], 2)
        self.assertEqual(result['skipped'], 0)
        self.assertEqual(result['rejected'], 1)
        self.assertEqual(result['errors'][0]['line'], 3)

        rows = reporting.invoices(self.db)

        invoice_numbers = {
            row['invoice_number']
            for row in rows
        }

        self.assertIn('MIXED-001', invoice_numbers)
        self.assertNotIn('MIXED-002', invoice_numbers)
        self.assertIn('MIXED-003', invoice_numbers)

    def test_export_has_header(self):
        self.assertTrue(reporting.export_csv(self.db).startswith('customer_id,invoice_number,amount,paid,balance,status'))

    

if __name__ == '__main__':
    unittest.main()


