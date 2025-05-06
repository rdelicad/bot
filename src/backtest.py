from exchange.bybit_client import BybitClient
from stragegies.tradinglatino_strategy import detectar_senal_trading
from indicators.technical_indicators import calcular_ema, calcular_rsi, calcular_macd, calcular_adx, calcular_squeeze_momentum
import pandas as pd
import matplotlib.pyplot as plt
import datetime

def backtest(symbol="BTCUSDT", interval="240", limit=1000):
    client = BybitClient()
    # Obtener también los timestamps
    cierres, altos, bajos, timestamps = client.get_candles(symbol, interval=interval, limit=limit, category="linear", return_timestamps=True)
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

    # Calcular squeeze_mom y adx para todo el dataset
    # La función no acepta argumentos extra, solo cierres, altos, bajos
    squeeze_mom, _ = calcular_squeeze_momentum(cierres, altos, bajos)
    squeeze_mom = [s * 75 if s is not None else None for s in squeeze_mom]  # escala 75

    adx = calcular_adx(cierres, altos, bajos, periodo=14)  # suavizado 14, longitud di 14
    adx = [a * 2 if a is not None else None for a in adx]  # escala 2

    def pad(l):
        return [None] * (len(df) - len(l)) + l

    df["ema10"] = pad(ema10)
    df["ema55"] = pad(ema55)
    df["ema200"] = pad(ema200)
    df["rsi"] = pad(rsi_list)
    df["macd"] = pad(macd_line)
    df["signal"] = pad(signal_line)
    df["squeeze_mom"] = pad(squeeze_mom)
    df["adx"] = pad(adx)

    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Simulación de señales
    señales = []
    last_signal = None
    for i in range(2, len(df)):
        precio = df.at[i, "close"]
        senal = detectar_senal_trading(
            precio,
            df.at[i,   "ema10"],   # no se usan, pero se pasan por compatibilidad
            df.at[i,   "ema55"],
            df.at[i,   "ema200"],
            df.at[i,   "rsi"],
            df.at[i,   "macd"],
            df.at[i,   "signal"],
            df.at[i-1, "macd"],
            df.at[i-1, "signal"],
            df.at[i-2, "squeeze_mom"], # squeeze anterior
            df.at[i-1, "squeeze_mom"], # squeeze actual
            df.at[i-1, "adx"],         # adx actual
            df.at[i-2, "adx"],         # adx anterior
            last_signal                # NUEVO: para evitar señales repetidas
        )
        if senal:
            señales.append({
                "index": i,
                "timestamp": df.at[i, "timestamp"],
                "close": precio,
                "senal": senal
            })
            last_signal = senal
        # Solo resetea last_signal cuando el adx gira en sentido contrario
        elif last_signal == "long" and df.at[i-1, "adx"] > df.at[i-2, "adx"]:
            last_signal = None
        elif last_signal == "short" and df.at[i-1, "adx"] < df.at[i-2, "adx"]:
            last_signal = None

    # Guardar CSV con timestamp
    pd.DataFrame(señales).to_csv("resultados_backtest.csv", index=False)
    print(f"Total señales generadas: {len(señales)}\n")
    print("Resultados guardados en: resultados_backtest.csv")

    # Visualización automática
    """ plt.figure(figsize=(15,6))
    plt.plot(df["timestamp"], df["close"], label="Precio")
    for s in señales:
        color = "g" if s["senal"] == "long" else "r"
        plt.scatter(s["timestamp"], s["close"], color=color, marker="^" if s["senal"]=="long" else "v")
    plt.legend()
    plt.title("Señales de la estrategia sobre el precio")
    plt.xlabel("Fecha y hora")
    plt.ylabel("Precio")
    plt.savefig("grafico_backtest.png")  # Guarda el gráfico como imagen
    print("Gráfico guardado en: grafico_backtest.png") """
    #plt.show()

    # Gráfico de ADX y Squeeze Momentum con valles y tres subplots separados
    fig, axs = plt.subplots(3, 1, figsize=(15, 10), sharex=True)

    # Precio arriba
    axs[0].plot(df["timestamp"], df["close"], label="Precio")
    axs[0].set_ylabel("Precio")
    axs[0].legend()

    # ADX en el medio
    axs[1].plot(df["timestamp"], df["adx"], color="orange", label="ADX (x2)")
    axs[1].axhline(23, color="red", linestyle="--", linewidth=1, label="Key level 23")
    axs[1].set_ylabel("ADX")
    axs[1].legend()

    # Squeeze Momentum como valles abajo
    x = df["timestamp"]
    y = df["squeeze_mom"]
    axs[2].axhline(0, color="gray", linestyle="--", linewidth=1)
    axs[2].fill_between(x, 0, y, where=[v > 0 for v in y], color="green", alpha=0.5)
    axs[2].fill_between(x, 0, y, where=[v < 0 for v in y], color="red", alpha=0.5)
    axs[2].plot(x, y, color="purple", label="Squeeze Momentum", linewidth=1)
    axs[2].set_ylabel("Squeeze")
    axs[2].legend()
    axs[2].set_xlabel("Fecha y hora")

    plt.tight_layout()
    plt.savefig("grafico_indicadores.png")
    print("Gráfico de ADX y Squeeze guardado en: grafico_indicadores.png")

if __name__ == "__main__":
    backtest()