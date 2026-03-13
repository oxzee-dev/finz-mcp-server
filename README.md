# finz-mcp `MCP SERVER`

Financial data MCP server for Claude Desktop, built with **FastMCP** + **yfinance**.

## Tools

| Tool | Description |
|---|---|
| `get_ticker` | Price, valuation, ratios, risk, dividends, price targets |
| `get_news` | Latest news articles (title, summary, date, URL) |
| `get_earnings` | Earnings dates & EPS estimates |
| `get_growth_estimate` | Analyst revenue & earnings growth estimates |
| `get_income_stmt` | Annual income statement |
| `get_balance_sheet` | Annual balance sheet |
| `get_insider_transactions` | Insider buy/sell transactions |
| `get_sec_filings` | SEC filings (type, date, URL) |

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
# Interactive inspector (browser UI to test each tool)
fastmcp dev server.py

# Stdio mode (what Claude Desktop uses)
python server.py
```

## Connect to Claude Desktop

Edit your config file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "finz": {
      "command": "python",
      "args": ["/absolute/path/to/finz-mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop — a 🔨 hammer icon confirms the tools are loaded.

## Usage examples

```
What's the latest news on PLTR?
Get the balance sheet for AAPL
Show insider transactions for TSLA
Compare earnings estimates for NVDA and AMD
```
