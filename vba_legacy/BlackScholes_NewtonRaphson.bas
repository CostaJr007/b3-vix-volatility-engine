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
    Dim epsilon As Double, dVol As Double, vol_1 As Double
    Dim I As Integer, maxIter As Integer, Value_1 As Double, vol_2 As Double
    Dim Value_2 As Double, dx As Double
    
    dVol = 0.00001
    epsilon = 0.00001
    maxIter = 100
    vol_1 = guess
    I = 1
    Do
        Value_1 = EuropeanOption(CallOrPut, S, K, vol_1, r, T, q)
        vol_2 = vol_1 - dVol
        Value_2 = EuropeanOption(CallOrPut, S, K, vol_2, r, T, q)
        dx = (Value_2 - Value_1) / dVol
        If Abs(dx) < epsilon Or I = maxIter Then Exit Do
        vol_1 = vol_1 - (OptionValue - Value_1) / dx
        I = I + 1
    Loop
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
