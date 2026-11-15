"""Parse strict Indonesian Rupiah number strings without floating-point loss."""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from typing import Iterable


_AMOUNT_PATTERN = re.compile(
    r"^(?P<before>-)?\s*(?:Rp\s*)?(?P<after>-)?\s*"
    r"(?P<number>(?:[0-9]{1,3}(?:\.[0-9]{3})+|[0-9]+)(?:,[0-9]{1,2})?)$",
    re.IGNORECASE,
)


def parse_rupiah(text: str) -> Decimal:
    """Parse a whole Rupiah amount string using Indonesian separators.

    Accepted examples: ``Rp 1.234.567,89``, ``-Rp 25.000``, ``Rp -25.000``,
    ``1234,5``. This parses the complete amount only; it does not extract values
    from sentences or guess US-style separators.
    """
    if not isinstance(text, str):
        raise TypeError("nilai Rupiah harus berupa string")
    match = _AMOUNT_PATTERN.fullmatch(text.strip())
    if match is None or (match.group("before") and match.group("after")):
        raise ValueError("format Rupiah tidak valid; gunakan titik ribuan dan koma desimal (maksimal 2 digit)")

    number = match.group("number").replace(".", "").replace(",", ".")
    try:
        amount = Decimal(number)
    except InvalidOperation as error:
        raise ValueError("format Rupiah tidak valid") from error
    if match.group("before") or match.group("after"):
        amount = -amount
    return amount


def canonical_amount(amount: Decimal) -> str:
    """Return a stable machine-readable decimal string without trailing zeros."""
    if not isinstance(amount, Decimal):
        raise TypeError("amount harus berupa Decimal")
    if not amount.is_finite():
        raise ValueError("amount harus berupa angka desimal finite")
    if amount.is_zero():
        return "0"
    text = format(amount, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def format_rupiah(amount: Decimal) -> str:
    """Format a Decimal as a human-readable Rupiah amount."""
    canonical = canonical_amount(amount)
    negative = canonical.startswith("-")
    if negative:
        canonical = canonical[1:]
    integer, separator, fraction = canonical.partition(".")
    groups: list[str] = []
    while integer:
        groups.append(integer[-3:])
        integer = integer[:-3]
    grouped = ".".join(reversed(groups)) or "0"
    decimal_part = f",{fraction}" if separator else ""
    return f"{'-' if negative else ''}Rp {grouped}{decimal_part}"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rupiah-parse-id",
        description="Parse satu nilai Rupiah dengan format angka Indonesia secara presisi.",
    )
    parser.add_argument("amount", nargs="?", help="nilai utuh, mis. 'Rp 1.234,50'; default membaca stdin")
    parser.add_argument("--json", action="store_true", help="keluarkan hasil sebagai JSON")
    args = parser.parse_args(argv)
    raw = args.amount if args.amount is not None else sys.stdin.read()

    try:
        amount = parse_rupiah(raw)
        canonical = canonical_amount(amount)
        formatted = format_rupiah(amount)
    except (TypeError, ValueError) as error:
        print(f"rupiah-parse-id: {error}.", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({"currency": "IDR", "amount": canonical, "formatted": formatted}, ensure_ascii=False))
    else:
        print(formatted)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
