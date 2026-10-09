"""test_rainfall.py - run with:  python -m unittest -v"""
import os
import tempfile
import unittest
from datetime import date

import pandas as pd

import analysis
import storage
import validation


def sample_table():
    df = storage.empty_table()
    rows = [("2026-01-10", "Ahmedabad", 0), ("2026-06-20", "Ahmedabad", 40),
            ("2026-07-05", "Surat", 120), ("2026-07-06", "Ahmedabad", 80),
            ("2026-10-15", "Surat", 10)]
    for d, location, mm in rows:
        df = storage.add_record(df, d, location, mm)
    return df


class TestValidation(unittest.TestCase):
    def test_good_date(self):
        self.assertEqual(validation.check_date("2026-07-15"), date(2026, 7, 15))

    def test_bad_date(self):
        for text in ("15-07-2026", "abc", "2026-13-01", ""):
            with self.assertRaises(ValueError):
                validation.check_date(text)

    def test_future_date(self):
        with self.assertRaises(ValueError):
            validation.check_past_date("2999-01-01")

    def test_rainfall(self):
        self.assertEqual(validation.check_rainfall("12.5"), 12.5)
        for text in ("-1", "abc", "nan", "5000", ""):
            with self.assertRaises(ValueError):
                validation.check_rainfall(text)

    def test_location(self):
        self.assertEqual(validation.check_location("  new delhi "), "New Delhi")
        with self.assertRaises(ValueError):
            validation.check_location("   ")


class TestStorage(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "test.csv")
            storage.save_records(sample_table(), path)
            loaded = storage.load_records(path)
            self.assertEqual(len(loaded), 5)

    def test_missing_file(self):
        self.assertTrue(storage.load_records("no_such_file.csv").empty)

    def test_duplicate(self):
        with self.assertRaises(ValueError):
            storage.add_record(sample_table(), "2026-01-10", "Ahmedabad", 5)

    def test_delete(self):
        self.assertEqual(len(storage.delete_record(sample_table(), 0)), 4)
        with self.assertRaises(ValueError):
            storage.delete_record(sample_table(), 99)


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.df = sample_table()

    def test_total_average(self):
        total, average = analysis.total_and_average(self.df)
        self.assertEqual(total, 250)
        self.assertEqual(average, 50)

    def test_empty(self):
        self.assertEqual(analysis.total_and_average(storage.empty_table()), (0.0, 0.0))

    def test_filter(self):
        self.assertEqual(len(analysis.filter_records(self.df, "surat")), 2)
        july = analysis.filter_records(self.df, "", date(2026, 7, 1), date(2026, 7, 31))
        self.assertEqual(len(july), 2)

    def test_highest_lowest(self):
        high, low = analysis.highest_lowest(self.df)
        self.assertEqual(high["rainfall_mm"], 120)
        self.assertEqual(low["rainfall_mm"], 0)

    def test_compare(self):
        r = analysis.compare_periods(self.df, date(2026, 1, 1), date(2026, 6, 30),
                                     date(2026, 7, 1), date(2026, 12, 31))
        self.assertEqual(r["total1"], 40)
        self.assertEqual(r["total2"], 210)
        self.assertEqual(round(r["percent"]), 425)

    def test_season_and_month(self):
        self.assertEqual(analysis.seasonal_totals(self.df).loc["Monsoon", "total"], 240)
        self.assertEqual(analysis.monthly_totals(self.df)["2026-07"], 200)


if __name__ == "__main__":
    unittest.main()
