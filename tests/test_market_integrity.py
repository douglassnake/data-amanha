"""Testes isolados da camada de cotações, sem contato com provedores."""
import ast
import unittest
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote as url_quote
import numpy as np
import pandas as pd

module = ast.parse(Path("app.py").read_text(encoding="utf-8"))
allowed = {
    "valid_market_price", "market_timestamp", "age_description",
    "parse_coinbase_trade", "parse_yahoo_bar",
}
functions = [
    node for node in module.body
    if isinstance(node, ast.FunctionDef) and node.name in allowed
]
env = {
    "np": np, "pd": pd, "datetime": datetime, "timezone": timezone,
    "url_quote": url_quote,
    "COINBASE_ALLOWED": {"BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD"},
}
exec(compile(ast.Module(body=functions, type_ignores=[]), "app.py", "exec"), env)


class TestMarketIntegrity(unittest.TestCase):
    def test_required_functions_present(self):
        self.assertEqual(len(functions), len(allowed))

    def test_invalid_prices_never_become_zero(self):
        for value in ("0", "-1", "NaN", "Infinity", None, "erro"):
            self.assertIsNone(env["valid_market_price"](value))
        self.assertEqual(env["valid_market_price"]("42000.5"), 42000.5)

    def test_coinbase_requires_authentic_timestamp(self):
        self.assertIsNone(env["parse_coinbase_trade"]("BTC-USD", {"price": "73000"}))
        self.assertIsNone(env["parse_coinbase_trade"]("BTC-USD", {"price": "0", "time": "2026-11-11T15:00:00Z"}))
        self.assertIsNone(env["parse_coinbase_trade"]("NOT-A-MARKET", {"price": "73000", "time": "2026-11-11T15:00:00Z"}))
        result = env["parse_coinbase_trade"]("BTC-USD", {
            "price": "73000", "time": "2026-11-11T15:00:00Z", "bid": "72999"
        })
        self.assertEqual(result["Preço"], 73000)
        self.assertIn("+00:00", result["Última observação (UTC)"])
        self.assertEqual(result["Fonte"], "Coinbase Exchange")

    def test_yahoo_bar_timestamp_and_price(self):
        stamps = pd.date_range("2026-11-11 14:00:00", periods=3, freq="5min", tz="UTC")
        series = pd.Series([95.0, 100.0, 101.5], index=stamps)
        result = env["parse_yahoo_bar"]("AAPL", series)
        self.assertEqual(result["Preço"], 101.5)
        self.assertIn("2026-11-11T14:10:00+00:00", result["Última observação (UTC)"])
        self.assertIn("atraso", result["Modalidade"])

    def test_no_timestamp_claim_if_timezone_missing(self):
        stamps = pd.date_range("2026-11-11", periods=2, freq="5min")
        result = env["parse_yahoo_bar"]("MSFT", pd.Series([100, 105], index=stamps))
        self.assertEqual(result["Última observação (UTC)"], "Fuso não informado")


if __name__ == "__main__":
    unittest.main()
