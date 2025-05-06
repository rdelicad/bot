def detectar_senal_trading(
    precio, ema_10, ema_55, ema_200, rsi, macd_line, signal_line,
    prev_macd_line, prev_signal_line, squeeze_anterior, squeeze_actual, adx_actual, adx_anterior,
    last_signal
):
    # LONG: ADX gira a la baja y Squeeze se gira al alza (solo una vez hasta el siguiente giro)
    if (
        adx_actual < adx_anterior and squeeze_anterior < 0 and squeeze_actual > squeeze_anterior
        and abs(squeeze_actual) > 0.1 and last_signal != "long"
    ):
        return "long"
    # SHORT: ADX gira al alza y Squeeze se gira a la baja (solo una vez hasta el siguiente giro)
    if (
        adx_actual > adx_anterior and squeeze_anterior > 0 and squeeze_actual < squeeze_anterior
        and abs(squeeze_actual) > 0.1 and last_signal != "short"
    ):
        return "short"
    return None