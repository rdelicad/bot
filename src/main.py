import time
from exchange.bybit_client import BybitClient
from exchange.trading import abrir_posicion, cerrar_posicion
from stragegies.tradinglatino_strategy import detectar_senal_trading
from indicators.technical_indicators import (
    calcular_ema,
    calcular_adx,
    calcular_rsi,
    calcular_macd,
    calcular_estocastico,
    calcular_squeeze_momentum,
    calcular_volume_profile
)

INTERVALO = "1"         # Temporalidad (ej: "1", "5", "15", "60", "240")
USD_PARA_OPERAR = 100   # Capital a invertir en USD
SYMBOL = "BTCUSDT"      # Símbolo
TIEMPO_ESPERA = 60      # Tiempo de espera entre iteraciones (segundos)
RIESGO_SL = 0.01        # Stop Loss: 1% (0.01 = 1%)
RR = 1.5                # Ratio riesgo/beneficio para Take Profit (ej: 1.5)

if __name__ == "__main__":
    client = BybitClient()
    while True:
        try:
            print("\n--- Nueva iteración ---")
            cierres, altos, bajos = client.get_candles(SYMBOL, interval=INTERVALO, limit=1000, category="linear")
            ema_10 = calcular_ema(cierres, 10)
            ema_55 = calcular_ema(cierres, 55)
            ema_200 = calcular_ema(cierres, 200)
            rsi_14 = calcular_rsi(cierres, periodo=14)
            macd_line, signal_line, _ = calcular_macd(cierres)

            precio_actual = cierres[-1]
            ema_corta = ema_10[-1]
            ema_larga = ema_55[-1]
            ema_200v = ema_200[-1]
            rsi = rsi_14[-1]
            macd = macd_line[-1]
            signal = signal_line[-1]
            prev_macd = macd_line[-2]
            prev_signal = signal_line[-2]

            senal = detectar_senal_trading(
                precio_actual, ema_corta, ema_larga, ema_200v, rsi, macd, signal, prev_macd, prev_signal
            )

            qty = round(USD_PARA_OPERAR / precio_actual, 3)
            if qty < 0.001:
                qty = 0.001

            # --- Cálculo de SL y TP ---
            if senal == "long":
                stop_loss = round(precio_actual * (1 - RIESGO_SL), 2)
                take_profit = round(precio_actual * (1 + RIESGO_SL * RR), 2)
            elif senal == "short":
                stop_loss = round(precio_actual * (1 + RIESGO_SL), 2)
                take_profit = round(precio_actual * (1 - RIESGO_SL * RR), 2)

            # --- Abrir posición ---
            if senal == "long":
                print(f"Señal de COMPRA detectada. SL: {stop_loss}, TP: {take_profit}")
                respuesta_abrir = abrir_posicion(SYMBOL, qty, "Buy", stop_loss=stop_loss, take_profit=take_profit)
                print("Respuesta abrir posición:", respuesta_abrir)
            elif senal == "short":
                print(f"Señal de VENTA detectada. SL: {stop_loss}, TP: {take_profit}")
                respuesta_abrir = abrir_posicion(SYMBOL, qty, "Sell", stop_loss=stop_loss, take_profit=take_profit)
                print("Respuesta abrir posición:", respuesta_abrir)
            else:
                print("No hay señal clara para operar.")

        except Exception as e:
            print(f"Error en la iteración: {e}")

        print(f"Esperando {TIEMPO_ESPERA/60:.0f} minutos para la siguiente iteración...\n")
        time.sleep(TIEMPO_ESPERA)