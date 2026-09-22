Attribute VB_Name = "Module2"
Option Explicit

Function EuropeanOption(CallOrPut, S, K, v, r, T, q)
Dim d1 As Double, d2 As Double, nd1 As Double, nd2 As Double
Dim nnd1 As Double, nnd2 As Double

d1 = (Log(S / K) + (r - q + 0.5 * v ^ 2) * T) / (v * Sqr(T))
d2 = (Log(S / K) + (r - q - 0.5 * v ^ 2) * T) / (v * Sqr(T))
nd1 = Application.NormSDist(d1)
nd2 = Application.NormSDist(d2)
nnd1 = Application.NormSDist(-d1)
nnd2 = Application.NormSDist(-d2)

If CallOrPut = "Call" Then
  EuropeanOption = S * Exp(-q * T) * nd1 - K * Exp(-r * T) * nd2
Else
  EuropeanOption = -S * Exp(-q * T) * nnd1 + K * Exp(-r * T) * nnd2
End If
End Function

Function ImpliedVolatility(CallOrPut, S, K, r, T, q, OptionValue, guess)

    Dim priceTol As Double, volFloor As Double, volCeil As Double, vol_1 As Double
    Dim I As Integer, maxIter As Integer, Value_1 As Double, vega As Double
    Dim d1 As Double, nd1pdf As Double

    ' FIX (audit 2026-09-22): converge on PRICE error |model - market|,
    ' never on the derivative. Old code exited when Abs(dx) < epsilon
    ' (derivative ~ -Vega near zero), returning silently unconverged.
    ' Uses analytic Vega = S*e^(-qT)*sqrt(T)*phi(d1), vol bracket [1e-4, 5].

    priceTol = 0.0001
    volFloor = 0.0001
    volCeil = 5#
    maxIter = 100

    If guess > volFloor And guess < volCeil Then
        vol_1 = guess
    Else
        vol_1 = 0.25
    End If

    For I = 1 To maxIter

        Value_1 = EuropeanOption(CallOrPut, S, K, vol_1, r, T, q)

        If Abs(Value_1 - OptionValue) < priceTol Then Exit For

        d1 = (Log(S / K) + (r - q + 0.5 * vol_1 ^ 2) * T) / (vol_1 * Sqr(T))
        nd1pdf = Exp(-0.5 * d1 * d1) / Sqr(2 * 3.14159265358979)
        vega = S * Exp(-q * T) * Sqr(T) * nd1pdf

        If Abs(vega) < 0.00000001 Then Exit For

        vol_1 = vol_1 - (Value_1 - OptionValue) / vega
        If vol_1 < volFloor Then vol_1 = volFloor
        If vol_1 > volCeil Then vol_1 = volCeil

    Next I

    ImpliedVolatility = vol_1

End Function

Public Function ULinha(Coluna As Integer, Optional ByVal Plan As String) As Double
    If Plan = "" Then
        Plan = ActiveSheet.Name
    End If
    ULinha = Sheets(Plan).Cells(Sheets(Plan).Rows.Count, Coluna).End(xlUp).Row
End Function

Sub AtualizaBarra(Percentual As Single)
    With Barra_Progresso
        .FrameProcesso.Caption = Format(Percentual, "0%")
        .lblProcesso.Width = Percentual * (.FrameProcesso.Width - 10)
    End With
    DoEvents
End Sub
