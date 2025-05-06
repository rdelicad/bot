''''
Aquí pondrás la lógica de negocio específica para tu bot:

Métodos para obtener balance, precios, colocar órdenes, etc., usando la conexión de bybit_exchange.py.
Así, si cambias de exchange, solo cambias el client y no todo el código.
Ejemplo: métodos como get_balance(), get_price(symbol), place_order(...), etc.
'''
from .bybit_exchange import get_bybit_session

class BybitClient:
    def __init__(self):
        self.session = get_bybit_session()

    def get_saldo(self):
        try:
            saldo = self.session.get_wallet_balance(accountType="UNIFIED")
            coins = saldo['result']['list'][0]['coin']
            for coin in coins:
                print(f"Moneda: {coin['coin']}")
                print(f"  Saldo disponible: {coin['walletBalance']}")
                print(f"  Saldo total (equity): {coin['equity']}")
                print("-" * 30)
        except Exception as e:
            print(f"❌ Error al obtener el saldo: {e}")
            return None
    
    def get_balance(self):
        try:
            balance = self.session.get_wallet_balance(accountType="UNIFIED")
            coins = balance['result']['list'][0]['coin']
            for coin in coins:
                if coin['coin'] == 'USDT':
                    return coin['walletBalance']
            return 0
        except Exception as e:
            print(f"❌ Error al obtener el balance: {e}")
            return None

    def get_price(self, symbol):
        try:
            ticker = self.session.get_tickers(category="linear", symbol=symbol)
            return ticker['result']['list'][0]['lastPrice']
        except Exception as e:
            print(f"❌ Error al obtener el price: {e}")
            return None
    
    def get_candles(self, symbol, interval="1", limit=100, category="linear", return_timestamps=False):
            """"
            Devuelve tres listas: cierres, altos y bajos de las velas.
            """
            try:
                candles = self.session.get_kline(
                    category=category,
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
                #print("Respuesta cruda de velas:", candles)
                # Invierte para que sea de antiguo a reciente
                lista = candles['result']['list'][::-1]
                cierres = [float(c[4]) for c in lista]
                altos = [float(c[2]) for c in lista]
                bajos = [float(c[3]) for c in lista]
                #print(f"mostrar_cierres: {cierres}")
                if return_timestamps:
                    # Si se requiere, devuelve también los timestamps
                    timestamps = [int(c[0]) for c in lista]
                    return cierres, altos, bajos, timestamps
                return cierres, altos, bajos
            except Exception as e:
                print(f"❌ Error al obtener las velas: {e}")
                return [], [], []
    
    def get_volumenes(self, symbol, interval="1", limit=100, category="linear"):
        """
        Devuelve una lista de volúmenes de las velas para el símbolo e intervalo especificados.
        """
        try:
            candles = self.session.get_kline(
                category=category,
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            lista = candles['result']['list'][::-1]
            volumenes = [float(c[5]) for c in lista]
            return volumenes
        except Exception as e:
            print(f"❌ Error al obtener los volúmenes: {e}")
            return []
    
''''
La clave 'list' en la respuesta de Bybit contiene los datos de las velas.
La estructura de cada vela es la siguiente:
['1745743860000', '94307.3', '94307.4', '94265.5', '94281.4', '3.568791', '336487.4957817']
[
    [
        '1745743860000',  # Timestamp
        '94307.3',       # Open
        '94307.4',       # High
        '94265.5',       # Low
        '94281.4',       # Close
        '3.568791',      # Volume
        '336487.4957817' # Quote Volume

    ],
    ...
]
'''