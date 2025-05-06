import time
import sys
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
SL_PORCENTAJE = 0.001    # Stop Loss: 10% (0.10 = 10%)
TP_PORCENTAJE = 0.002    # Take Profit: 20% (0.20 = 20%)

# --- BLOQUE DE PRUEBA SIMPLE (SIN ESTRATEGIA) ---
# --- FUNCIÓN MEJORADA CON OPCIONES DE DIRECCIÓN Y SL/TP ---
""" def abrir_posicion_manual(direccion="Sell"):
    client = BybitClient()
    precio_actual = float(client.get_price(SYMBOL))
    
    # Calcular cantidad
    qty = round(USD_PARA_OPERAR / precio_actual, 3)
    if qty < 0.001:
        qty = 0.001  # Mínimo permitido en Bybit
    
    # Calcular SL y TP usando las variables globales
    if direccion == "Buy":  # LARGO
        stop_loss = str(round(precio_actual * (1 - SL_PORCENTAJE), 2))  # SL por debajo
        take_profit = str(round(precio_actual * (1 + TP_PORCENTAJE), 2))
        print(f"Abriendo posición de COMPRA (LARGO) en {SYMBOL}")
    else:  # CORTO
        stop_loss = str(round(precio_actual * (1 + SL_PORCENTAJE), 2))  # SL por arriba
        take_profit = str(round(precio_actual * (1 + TP_PORCENTAJE), 2))
        print(f"Abriendo posición de VENTA (CORTO) en {SYMBOL}")
    
    print(f"Precio actual: {precio_actual}")
    print(f"Cantidad: {qty} ({USD_PARA_OPERAR} USD)")
    print(f"Stop Loss: {stop_loss} ({SL_PORCENTAJE*100}%)")
    print(f"Take Profit: {take_profit} (RR: {TP_PORCENTAJE*100}%)")
    
    try:
        respuesta = abrir_posicion(
            SYMBOL, 
            qty, 
            direccion, 
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        print("Respuesta:", respuesta)
        
    except Exception as e:
        print(f"Error al abrir posición: {e}")

if __name__ == "__main__":
    # Ejemplos de uso:
    
    # Para abrir posición según variables globales:
    # - SYMBOL: El símbolo a operar
    # - USD_PARA_OPERAR: Cantidad en USD
    # - SL_PORCENTAJE: Porcentaje de Stop Loss
    # - RR: Ratio riesgo/beneficio para Take Profit
    
    # 1. Abrir posición CORTA con las variables globales
    #abrir_posicion_manual("Sell")
    
    # 2. Abrir posición LARGA con las variables globales
    abrir_posicion_manual("Buy") """
    


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

            # --- Cálculo de SL y TP usando las variables globales ---
            if senal == "long":
                stop_loss = str(round(precio_actual * (1 - SL_PORCENTAJE), 2))  # SL por debajo
                take_profit = str(round(precio_actual * (1 + TP_PORCENTAJE), 2))  # TP por arriba
                print(f"Señal de COMPRA detectada. SL: {stop_loss} ({SL_PORCENTAJE*100}%), TP: {take_profit} ({TP_PORCENTAJE*100}%)")
                respuesta_abrir = abrir_posicion(SYMBOL, qty, "Buy", stop_loss=stop_loss, take_profit=take_profit)
                print("Respuesta abrir posición:", respuesta_abrir)

                # Detener ejecucion despues de abrir posicion
                print("\n¡POSICIÓN ABIERTA! El bot se detendrá para análisis.\n")
                print("Para continuar, ejecute el bot nuevamente.")
                sys.exit(0)  
            elif senal == "short":
                stop_loss = str(round(precio_actual * (1 + SL_PORCENTAJE), 2))  # SL por arriba
                take_profit = str(round(precio_actual * (1 - TP_PORCENTAJE), 2))  # TP por abajo
                print(f"Señal de VENTA detectada. SL: {stop_loss} ({SL_PORCENTAJE*100}%), TP: {take_profit} ({TP_PORCENTAJE*100}%)")
                respuesta_abrir = abrir_posicion(SYMBOL, qty, "Sell", stop_loss=stop_loss, take_profit=take_profit)
                print("Respuesta abrir posición:", respuesta_abrir)

                # Detener ejecucion despues de abrir posicion
                print("\n¡POSICIÓN ABIERTA! El bot se detendrá para análisis.\n")
                print("Para continuar, ejecute el bot nuevamente.")
                sys.exit(0)
            else:
                print("No hay señal clara para operar.")

            

        except Exception as e:
            print(f"Error en la iteración: {e}")

        print(f"Esperando {TIEMPO_ESPERA/60:.0f} minutos para la siguiente iteración...\n")
        time.sleep(TIEMPO_ESPERA)