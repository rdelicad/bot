def detectar_senal_trading(precio, ema_10, ema_55, ema_200, rsi, macd_line, signal_line, prev_macd_line, prev_signal_line):
    # Largo
    if precio > ema_200 and ema_10 > ema_55 and 50 < rsi < 70:
        # Cruce MACD al alza
        if prev_macd_line < prev_signal_line and macd_line > signal_line:
            # Mostrar valores de EMA y RSI
            print(f"EMA 10: {ema_10}, EMA 55: {ema_55}, EMA 200: {ema_200}")
            print(f"RSI: {rsi}, MACD: {macd_line}, Signal: {signal_line}")
            print(f"Prev MACD: {prev_macd_line}, Prev Signal: {prev_signal_line}")
            print(f"Precio: {precio}")
            print(f"Señal de COMPRA detectada. Precio: {precio}")
            return "long"
    # Corto
    if precio < ema_200 and ema_10 < ema_55 and 30 < rsi < 50:
        # Cruce MACD a la baja
        if prev_macd_line > prev_signal_line and macd_line < signal_line:
            # Mostrar valores de EMA y RSI
            print(f"EMA 10: {ema_10}, EMA 55: {ema_55}, EMA 200: {ema_200}")
            print(f"RSI: {rsi}, MACD: {macd_line}, Signal: {signal_line}")
            print(f"Prev MACD: {prev_macd_line}, Prev Signal: {prev_signal_line}")
            print(f"Precio: {precio}")
            print(f"Señal de VENTA detectada. Precio: {precio}")
            return "short"
    return None