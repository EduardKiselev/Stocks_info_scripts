import os
import pprint

from dotenv import load_dotenv
from tinkoff.invest import Client, InstrumentIdType
from tinkoff.invest.services import InstrumentsService

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.environ['TOKEN']


# Перечень интересующих тикеров
tickers = ["UPRO","ALRS","T"]

# Функция для поиска FIGI по тикеру
def find_figi_by_ticker(ticker):
    result=[]
    with Client(TOKEN) as client:
        instruments = client.instruments.find_instrument(query=ticker)
        for instrument in instruments.instruments:
            if instrument.ticker == ticker:
                result.append(instrument.figi)
    return result

def get_instrument_info_by_figi(figi):
    """Возвращает полную информацию об инструменте по FIGI."""
    with Client(TOKEN) as client:
        instruments: InstrumentsService = client.instruments
        response = instruments.get_instrument_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi)
        return response.instrument

# Создаем список для хранения данных
data = []

# Ищем FIGI для каждого тикера
for ticker in tickers:
    figi = find_figi_by_ticker(ticker)
    if figi:
        data.append({"ticker": ticker, "figi": figi})
        print(f"Найден FIGI для {ticker}: {figi}")
        for f in figi:
            pprint.pp(get_instrument_info_by_figi(f))
    else:
        print(f"FIGI для {ticker} не найден.")