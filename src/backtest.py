from exchange.bybit_client import BybitClient
from stragegies.tradinglatino_strategy import detectar_senal_trading
from indicators.technical_indicators import calcular_ema, calcular_rsi, calcular_macd, calcular_adx, calcular_squeeze_momentum
import pandas as pd
import matplotlib.pyplot as plt
import datetime

def backtest(symbol="BTCUSDT", interval="1", limit=2000):
    client = BybitClient()
    # Obtener también los timestamps
    cierres, _, _, timestamps = client.get_candles(symbol, interval=interval, limit=limit, category="linear", return_timestamps=True)
    df = pd.DataFrame({
        "close": cierres,
        "timestamp": [datetime.datetime.fromtimestamp(ts/1000) for ts in timestamps]
    })

    # Calcular indicadores como listas
    ema10  = calcular_ema(df["close"].tolist(),  10)
    ema55  = calcular_ema(df["close"].tolist(),  55)
    ema200 = calcular_ema(df["close"].tolist(), 200)
    rsi_list = calcular_rsi(df["close"].tolist(), periodo=14)
    macd_line, signal_line, _ = calcular_macd(df["close"].tolist())

    paddings = [len(df) - len(ema10), len(df) - len(ema55), len(df) - len(ema200), len(df) - len(rsi_list), len(df) - len(macd_line), len(df) - len(signal_line)]
    def pad(l):
        return [None] * (len(df) - len(l)) + l

    df["ema10"]   = pad(ema10)
    df["ema55"]   = pad(ema55)
    df["ema200"]  = pad(ema200)
    df["rsi"]     = pad(rsi_list)
    df["macd"]    = pad(macd_line)
    df["signal"]  = pad(signal_line)

    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Simulación de señales
    señales = []
    for i in range(1, len(df)):
        precio = df.at[i, "close"]
        squeeze_mom, squeeze_on = calcular_squeeze_momentum(cierres, altos, bajos)
        adx = calcular_adx(cierres, altos, bajos, periodo=14)
        # ...
        senal = detectar_senal_trading(
            precio_actual, ema_corta, ema_larga, ema_200v, rsi, macd, signal, prev_macd, prev_signal,
            squeeze_mom[-1], squeeze_mom[-2], adx[-1], adx[-2]
        )
        senal = detectar_senal_trading(
            precio,
            df.at[i,   "ema10"],
            df.at[i,   "ema55"],
            df.at[i,   "ema200"],
            df.at[i,   "rsi"],
            df.at[i,   "macd"],
            df.at[i,   "signal"],
            df.at[i-1, "macd"],
            df.at[i-1, "signal"],
            df.at[i-2, "squeeze_mom"], # squeeze_mom anterior
            df.at[i-1, "squeeze_mom"], # squeeze_mom actual
            df.at[i-1, "adx"],         # adx actual
            df.at[i-2, "adx"]          # adx anterior
        )
        if senal:
            señales.append({
                "index": i,
                "timestamp": df.at[i, "timestamp"],
                "close": precio,
                "senal": senal
            })

    # Guardar CSV con timestamp
    pd.DataFrame(señales).to_csv("resultados_backtest.csv", index=False)
    print(f"Total señales generadas: {len(señales)}\n")
    print("Resultados guardados en: resultados_backtest.csv")

    # Visualización automática
    plt.figure(figsize=(15,6))
    plt.plot(df["timestamp"], df["close"], label="Precio")
    for s in señales:
        color = "g" if s["senal"] == "long" else "r"
        plt.scatter(s["timestamp"], s["close"], color=color, marker="^" if s["senal"]=="long" else "v")
    plt.legend()
    plt.title("Señales de la estrategia sobre el precio")
    plt.xlabel("Fecha y hora")
    plt.ylabel("Precio")
    plt.savefig("grafico_backtest.png")  # Guarda el gráfico como imagen
    print("Gráfico guardado en: grafico_backtest.png")
    #plt.show()

if __name__ == "__main__":
    backtest()