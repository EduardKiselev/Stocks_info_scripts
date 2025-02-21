import yfinance as yf

#tickers = yf.Tickers('MSFT AAPL GOOG')
#tickers.tickers['MSFT'].info
data = yf.download(['AAPL',], period='1mo',timeout=10)
print(data)