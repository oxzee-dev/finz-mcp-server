"""
finz MCP Server
Financial data tools for Claude Desktop via FastMCP + yfinance.

Install:  pip install fastmcp yfinance pandas
Dev:      fastmcp dev server.py
Run:      python server.py
"""

import json
import yfinance as yf
from fastmcp import FastMCP

# ─────────────────────────────────────────────────────────────
# Server
# ─────────────────────────────────────────────────────────────
mcp = FastMCP(
    name="finz",
    instructions=(
        "Financial data tools powered by Yahoo Finance. "
        "Use these to get stock prices, news, earnings, "
        "financial statements, insider transactions, and SEC filings."
    ),
)

yf.set_tz_cache_location("/tmp")


# ─────────────────────────────────────────────────────────────
# Serialization — handles DataFrames, numpy types, Timestamps
# ─────────────────────────────────────────────────────────────
def serialize(obj) -> dict | list:
    import pandas as pd
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return json.loads(obj.to_json(date_format="iso", default_handler=str))
    return json.loads(json.dumps(obj, default=str))


# ─────────────────────────────────────────────────────────────
# Formatting helpers
# ─────────────────────────────────────────────────────────────
def fmt(v, d=2):
    if v is None: return None
    try: return round(float(v), d)
    except: return None

def fmt_B(v):
    if v is None: return None
    try: return f"{round(float(v)/1_000_000_000, 2)} B$"
    except: return None

def fmt_M(v):
    if v is None: return None
    try: return f"{round(float(v)/1_000_000, 2)} M$"
    except: return None

def fmt_pct(v):
    if v is None: return None
    try: return f"{round(float(v)*100, 2)} %"
    except: return None

def chg(cur, prev):
    if cur is None or prev is None: return None
    try:
        c, p = float(cur), float(prev)
        return round(((c-p)/p)*100, 2) if p != 0 else None
    except: return None


# ─────────────────────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────────────────────

@mcp.tool
def get_ticker(symbol: str) -> dict:
    """
    Full market snapshot for a stock: price, valuation, ratios,
    margins, risk, debt, dividends, and price targets.
    Example: get_ticker("AAPL")
    """
    ticker = yf.Ticker(symbol.upper())
    info = ticker.info
    cur  = info.get("currentPrice") or info.get("regularMarketPrice")
    prev = info.get("previousClose") or info.get("regularMarketPreviousClose")
    one_day = chg(cur, prev)
    wk52    = fmt_pct(info.get("52WeekChange"))

    return {
        "ticker": symbol.upper(),
        "shortName": info.get("shortName"),
        "main_info": {
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "currency": info.get("currency"),
            "currentPrice": fmt(cur),
            "oneDayChange": f"{one_day} %" if one_day is not None else None,
            "fiftyTwoWeekChange": wk52,
            "marketCap": fmt_B(info.get("marketCap")),
            "PE": fmt(info.get("trailingPE")),
            "forwardPE": fmt(info.get("forwardPE")),
            "PS": fmt(info.get("priceToSalesTrailing12Months")),
            "recommendation": info.get("recommendationKey"),
            "PT_Low": fmt(info.get("targetLowPrice")),
            "PT_High": fmt(info.get("targetHighPrice")),
        },
        "valuation": {
            "marketCap": fmt_B(info.get("marketCap")),
            "enterpriseValue": fmt_B(info.get("enterpriseValue")),
            "priceToBook": fmt(info.get("priceToBook")),
            "enterpriseToRevenue": fmt(info.get("enterpriseToRevenue")),
            "enterpriseToEbitda": fmt(info.get("enterpriseToEbitda")),
            "sharesOutstanding": fmt_M(info.get("sharesOutstanding")),
        },
        "ratios": {
            "trailingPE": fmt(info.get("trailingPE")),
            "forwardPE": fmt(info.get("forwardPE")),
            "pegRatio": fmt(info.get("pegRatio")),
            "priceToBook": fmt(info.get("priceToBook")),
            "profitMargins": fmt_pct(info.get("profitMargins")),
            "operatingMargins": fmt_pct(info.get("operatingMargins")),
            "returnOnEquity": fmt_pct(info.get("returnOnEquity")),
            "returnOnAssets": fmt_pct(info.get("returnOnAssets")),
            "debtToEquity": fmt(info.get("debtToEquity")),
        },
        "price_performance": {
            "currentPrice": fmt(cur),
            "previousClose": fmt(prev),
            "dayLow": fmt(info.get("dayLow")),
            "dayHigh": fmt(info.get("dayHigh")),
            "fiftyTwoWeekLow": fmt(info.get("fiftyTwoWeekLow")),
            "fiftyTwoWeekHigh": fmt(info.get("fiftyTwoWeekHigh")),
            "fiftyDayAverage": fmt(info.get("fiftyDayAverage")),
            "twoHundredDayAverage": fmt(info.get("twoHundredDayAverage")),
        },
        "debt": {
            "totalDebt": fmt_B(info.get("totalDebt")),
            "totalCash": fmt_B(info.get("totalCash")),
            "freeCashflow": fmt_B(info.get("freeCashflow")),
            "operatingCashflow": fmt_B(info.get("operatingCashflow")),
            "currentRatio": fmt(info.get("currentRatio")),
            "quickRatio": fmt(info.get("quickRatio")),
        },
        "dividends": {
            "dividendYield": fmt_pct(info.get("dividendYield")),
            "dividendRate": fmt(info.get("dividendRate")),
            "payoutRatio": fmt_pct(info.get("payoutRatio")),
            "exDividendDate": info.get("exDividendDate"),
        },
        "risk": {
            "beta": fmt(info.get("beta")),
            "overallRisk": info.get("overallRisk"),
            "auditRisk": info.get("auditRisk"),
            "boardRisk": info.get("boardRisk"),
        },
        "price_targets": {
            "targetLowPrice": fmt(info.get("targetLowPrice")),
            "targetHighPrice": fmt(info.get("targetHighPrice")),
            "targetMeanPrice": fmt(info.get("targetMeanPrice")),
            "recommendationKey": info.get("recommendationKey"),
            "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
        },
    }


@mcp.tool
def get_news(symbol: str) -> dict:
    """
    Latest news articles for a stock: title, summary, date, provider, URL.
    Example: get_news("NVDA")
    """
    ticker = yf.Ticker(symbol.upper())
    news = []
    for item in (ticker.news or [])[:11]:
        content   = item.get("content", {})
        click_url = content.get("clickThroughUrl") or {}
        news.append({
            "title":      content.get("title"),
            "summary":    content.get("summary") or content.get("description") or "",
            "pubDate":    content.get("pubDate"),
            "provider":   content.get("provider", {}).get("displayName"),
            "source_url": click_url.get("url"),
        })
    return {"ticker": symbol.upper(), "news": news}


@mcp.tool
def get_earnings(symbol: str) -> dict:
    """
    Earnings dates and EPS estimates for a ticker.
    Example: get_earnings("AAPL")
    """
    stock = yf.Ticker(symbol.upper())
    return {
        "ticker": symbol.upper(),
        "earnings_dates":    serialize(stock.earnings_dates),
        "earnings_estimate": serialize(stock.earnings_estimate),
    }


@mcp.tool
def get_growth_estimate(symbol: str) -> dict:
    """
    Analyst revenue and earnings growth estimates for a ticker.
    Example: get_growth_estimate("MSFT")
    """
    stock = yf.Ticker(symbol.upper())
    return {
        "ticker": symbol.upper(),
        "revenue_estimates": serialize(stock.revenue_estimate),
        "earnings_estimate": serialize(stock.earnings_estimate),
    }


@mcp.tool
def get_income_stmt(symbol: str) -> dict:
    """
    Annual income statement for a ticker.
    Example: get_income_stmt("AAPL")
    """
    stock = yf.Ticker(symbol.upper())
    return {
        "ticker": symbol.upper(),
        "income_stmt": serialize(stock.get_income_stmt()),
    }


@mcp.tool
def get_balance_sheet(symbol: str) -> dict:
    """
    Annual balance sheet for a ticker.
    Example: get_balance_sheet("AAPL")
    """
    stock = yf.Ticker(symbol.upper())
    return {
        "ticker": symbol.upper(),
        "balance_sheet": serialize(stock.get_balance_sheet()),
    }


@mcp.tool
def get_insider_transactions(symbol: str) -> dict:
    """
    Recent insider buy/sell transactions for a ticker.
    Example: get_insider_transactions("PLTR")
    """
    stock = yf.Ticker(symbol.upper())
    return {
        "ticker": symbol.upper(),
        "insider_transactions": serialize(stock.get_insider_transactions()),
    }


@mcp.tool
def get_sec_filings(symbol: str) -> dict:
    """
    SEC filings list (type, date, URL) for a ticker.
    Example: get_sec_filings("TSLA")
    """
    stock = yf.Ticker(symbol.upper())
    return {
        "ticker": symbol.upper(),
        "sec_filings": serialize(stock.sec_filings or []),
    }


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # mcp.run() # For Local run
    mcp.run(transport="sse", host="0.0.0.0", port=8000, path="/mcp") # for HTTP SSE MCP

