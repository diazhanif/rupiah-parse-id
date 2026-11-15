import json
import subprocess
import sys
import unittest
from decimal import Decimal

from rupiah_parse_id import canonical_amount, format_rupiah, parse_rupiah


class RupiahParsingTests(unittest.TestCase):
    def test_parses_indonesian_grouping_and_decimal_exactly(self):
        amount = parse_rupiah("Rp 1.234.567,89")
        self.assertEqual(amount, Decimal("1234567.89"))
        self.assertEqual(canonical_amount(amount), "1234567.89")
        self.assertEqual(format_rupiah(amount), "Rp 1.234.567,89")

    def test_accepts_unprefixed_and_plain_integer_values(self):
        self.assertEqual(parse_rupiah("1234567"), Decimal("1234567"))
        self.assertEqual(parse_rupiah("12.345"), Decimal("12345"))
        self.assertEqual(parse_rupiah("0,5"), Decimal("0.5"))

    def test_accepts_negative_sign_before_or_after_currency_prefix(self):
        self.assertEqual(parse_rupiah("-Rp 25.000"), Decimal("-25000"))
        self.assertEqual(parse_rupiah("Rp -25.000,50"), Decimal("-25000.50"))
        self.assertEqual(format_rupiah(parse_rupiah("-Rp 25.000")), "-Rp 25.000")

    def test_rejects_ambiguous_or_malformed_amounts(self):
        invalid = (
            "Rp 1.23",
            "Rp 12.34.567",
            "1,234",
            "1,234.56",
            "Rp 1.000,123",
            "-Rp -1.000",
            "Rp 1.000 rupiah",
            "invoicenya Rp 10.000",
            "Rp 1..000",
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_rupiah(value)

    def test_zero_and_trailing_zeros_have_canonical_output(self):
        self.assertEqual(canonical_amount(parse_rupiah("-Rp 0,00")), "0")
        self.assertEqual(format_rupiah(parse_rupiah("Rp 1.000,50")), "Rp 1.000,5")

    def test_cli_json_returns_exact_machine_value(self):
        process = subprocess.run(
            [sys.executable, "-m", "rupiah_parse_id", "--json"],
            input="Rp 1.234.567,89",
            text=True,
            capture_output=True,
            check=True,
        )
        payload = json.loads(process.stdout)
        self.assertEqual(payload, {
            "currency": "IDR",
            "amount": "1234567.89",
            "formatted": "Rp 1.234.567,89",
        })

    def test_cli_rejects_invalid_text_without_echoing_it(self):
        private_like = "memo-rahasia-913 Rp 12.34"
        process = subprocess.run(
            [sys.executable, "-m", "rupiah_parse_id"],
            input=private_like,
            text=True,
            capture_output=True,
        )
        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertNotIn("memo-rahasia-913", process.stderr)


if __name__ == "__main__":
    unittest.main()
