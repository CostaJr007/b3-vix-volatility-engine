Attribute VB_Name = "Módulo2"
Public interval     As Double
Public linha_inicial  As Integer
Public iniciador_escala As Integer


Sub macro_timer()
    Set shData = ThisWorkbook.Worksheets("GBM")
    '
    interval = Now + shData.Range("A72").Value
    '
    linha_inicial = 6
    '
    'Tells Excel when to next run the macro.
    Application.OnTime interval, "my_macro"
End Sub

Sub my_macro()
Dim Coluna_1 As Integer
  Set shData = ThisWorkbook.Worksheets("Base de Dados GBM")
    'Mercado aberto.
    If shData.Range("a2").Value > 0 Then
        Application.ScreenUpdating = False
        Application.CalculateFull
        'Call ajusta
        cont_linha = shData.Range("A4").Value
        'If IsError(shData.Range("f2").Value) Then GoTo PulaSeErro
        'End If
        
        shData.Cells(cont_linha + linha_inicial, 1).Value = Now()
        shData.Cells(cont_linha + linha_inicial, 2).Value = shData.Range("b2").Value
        shData.Cells(cont_linha + linha_inicial, 3).Value = shData.Range("c2").Value
        shData.Cells(cont_linha + linha_inicial, 4).Value = shData.Range("d2").Value
        shData.Cells(cont_linha + linha_inicial, 5).Value = shData.Range("e2").Value
        
        'FILTRO VIXBOVA
        If shData.Range("t2").Value <> shData.Cells(cont_linha - 1 + linha_inicial, 20).Value Then
            shData.Cells(cont_linha + linha_inicial, 6).Value = shData.Cells(cont_linha - 1 + linha_inicial, 6).Value
        Else
            shData.Cells(cont_linha + linha_inicial, 6).Value = shData.Range("f2").Value
        End If
        shData.Cells(cont_linha + linha_inicial, 7).Value = shData.Range("g2").Value
        shData.Cells(cont_linha + linha_inicial, 8).Value = shData.Range("h2").Value
        
        'FILTRO VIXBOVA.NEXT
        If shData.Range("AC2").Value <> shData.Cells(cont_linha - 1 + linha_inicial, 29).Value Then
            shData.Cells(cont_linha + linha_inicial, 9).Value = shData.Cells(cont_linha - 1 + linha_inicial, 9).Value
        Else
            shData.Cells(cont_linha + linha_inicial, 9).Value = shData.Range("I2").Value
        End If
        
        shData.Cells(cont_linha + linha_inicial, 11).Value = shData.Range("K2").Value
        shData.Cells(cont_linha + linha_inicial, 12).Value = shData.Range("L2").Value
        shData.Cells(cont_linha + linha_inicial, 13).Value = shData.Range("M2").Value
        shData.Cells(cont_linha + linha_inicial, 14).Value = shData.Range("N2").Value
        shData.Cells(cont_linha + linha_inicial, 16).Value = shData.Range("P2").Value
        shData.Cells(cont_linha + linha_inicial, 17).Value = shData.Range("Q2").Value
        shData.Cells(cont_linha + linha_inicial, 18).Value = shData.Range("R2").Value
        shData.Cells(cont_linha + linha_inicial, 19).Value = shData.Range("S2").Value
        shData.Cells(cont_linha + linha_inicial, 20).Value = shData.Range("t2").Value
        shData.Cells(cont_linha + linha_inicial, 21).Value = shData.Range("u2").Value
        shData.Cells(cont_linha + linha_inicial, 22).Value = shData.Range("V2").Value
        shData.Cells(cont_linha + linha_inicial, 29).Value = shData.Range("AC2").Value
        shData.Cells(cont_linha + linha_inicial, 30).Value = shData.Range("AD2").Value
        shData.Cells(cont_linha + linha_inicial, 31).Value = shData.Range("AE2").Value
        shData.Cells(cont_linha + linha_inicial, 32).Value = shData.Range("AF2").Value
        shData.Cells(cont_linha + linha_inicial, 33).Value = shData.Range("AG2").Value
        
        'PRINTAR OPCOES VALORES
        Coluna_1 = 34
        Do While Coluna_1 < 168
        
            shData.Cells(cont_linha + linha_inicial, Coluna_1).Value = shData.Cells(2, Coluna_1).Value
           Coluna_1 = Coluna_1 + 1
        Loop
            
            
       If iniciador_escala > 0 Then
         Call AtualizarEixo
        End If
        
        'Zera
        'If (cont_linha = 20) Then
            'Call substitui_linhas_anteriores(cont_linha, shData)
        'End If
        '
'PulaSeErro:
        Application.ScreenUpdating = True
        Application.CalculateFull
    End If
    'Calls the timer macro so it can be run again at the next interval.
    Call macro_timer
End Sub

Sub stop_macro()
    Application.OnTime earliesttime:=interval, procedure:="my_macro", schedule:=False
    iniciador_escala = 0
    
End Sub

Sub substitui_linhas_anteriores(linha_atual, shData)
    For I = 0 To linha_atual - 10
        shData.Cells(linha_inicial + I, 1).Value = shData.Cells(linha_inicial + linha_atual, 1)
        shData.Cells(linha_inicial + I, 2).Value = shData.Cells(linha_inicial + linha_atual, 2)
        shData.Cells(linha_inicial + I, 3).Value = shData.Cells(linha_inicial + linha_atual, 3)
        shData.Cells(linha_inicial + I, 4).Value = shData.Cells(linha_inicial + linha_atual, 4)
        shData.Cells(linha_inicial + I, 5).Value = shData.Cells(linha_inicial + linha_atual, 5)
        shData.Cells(linha_inicial + I, 6).Value = shData.Cells(linha_inicial + linha_atual, 6)
        shData.Cells(linha_inicial + I, 7).Value = shData.Cells(linha_inicial + linha_atual, 7)
        shData.Cells(linha_inicial + I, 14).Value = shData.Cells(linha_inicial + linha_atual, 14)
        shData.Cells(linha_inicial + I, 15).Value = shData.Cells(linha_inicial + linha_atual, 15)
        shData.Cells(linha_inicial + I, 16).Value = shData.Cells(linha_inicial + linha_atual, 16)
        shData.Cells(linha_inicial + I, 17).Value = shData.Cells(linha_inicial + linha_atual, 17)
        shData.Cells(linha_inicial + I, 18).Value = shData.Cells(linha_inicial + linha_atual, 18)
        shData.Cells(linha_inicial + I, 19).Value = shData.Cells(linha_inicial + linha_atual, 19)
    Next I
End Sub

Sub AtualizarEixo()
    On Error Resume Next

    Application.ScreenUpdating = False
    
    Worksheets("TELA").ChartObjects("VIXBOVA").Activate
    ActiveChart.Axes(xlValue, xlPrimary).MinimumScale = Worksheets("Base de Dados GBM").Range("F3").Value - Worksheets("Base de Dados GBM").Range("Y9").Value
    ActiveChart.Axes(xlValue, xlPrimary).MaximumScale = Worksheets("Base de Dados GBM").Range("F4").Value + Worksheets("Base de Dados GBM").Range("Y9").Value
    ActiveChart.Axes(xlValue, xlSecondary).MinimumScale = Worksheets("Base de Dados GBM").Range("M3").Value - Worksheets("Base de Dados GBM").Range("Y11").Value
    ActiveChart.Axes(xlValue, xlSecondary).MaximumScale = Worksheets("Base de Dados GBM").Range("M4").Value + Worksheets("Base de Dados GBM").Range("Y11").Value
    
    Worksheets("TELA").ChartObjects("GFMOVE").Activate
    ActiveChart.Axes(xlValue, xlPrimary).MinimumScale = Worksheets("Base de Dados GBM").Range("C3").Value - Worksheets("Base de Dados GBM").Range("Y7").Value
    ActiveChart.Axes(xlValue, xlPrimary).MaximumScale = Worksheets("Base de Dados GBM").Range("C4").Value + Worksheets("Base de Dados GBM").Range("Y7").Value
    ActiveChart.Axes(xlValue, xlSecondary).MinimumScale = Worksheets("Base de Dados GBM").Range("E3").Value - Worksheets("Base de Dados GBM").Range("Y8").Value
    ActiveChart.Axes(xlValue, xlSecondary).MaximumScale = Worksheets("Base de Dados GBM").Range("E4").Value + Worksheets("Base de Dados GBM").Range("Y8").Value
    
    Worksheets("TELA").ChartObjects("CORINGA").Activate
    'ActiveChart.Axes(xlValue, xlPrimary).MinimumScale = Worksheets("Base de Dados GBM").Range("C3").Value - Worksheets("Base de Dados GBM").Range("Y9").Value
    'ActiveChart.Axes(xlValue, xlPrimary).MaximumScale = Worksheets("Base de Dados GBM").Range("C4").Value + Worksheets("Base de Dados GBM").Range("Y9").Value
    ActiveChart.Axes(xlValue, xlPrimary).MinimumScale = Worksheets("Base de Dados GBM").Range("G3").Value - Worksheets("Base de Dados GBM").Range("Y10").Value
    ActiveChart.Axes(xlValue, xlPrimary).MaximumScale = Worksheets("Base de Dados GBM").Range("G4").Value + Worksheets("Base de Dados GBM").Range("Y10").Value
    ActiveChart.Axes(xlValue, xlSecondary).MinimumScale = Worksheets("Base de Dados GBM").Range("F3").Value - Worksheets("Base de Dados GBM").Range("Y9").Value
    ActiveChart.Axes(xlValue, xlSecondary).MaximumScale = Worksheets("Base de Dados GBM").Range("F4").Value + Worksheets("Base de Dados GBM").Range("Y9").Value
    
    Worksheets("TELA").ChartObjects("VIXBOVAFUT").Activate
    ActiveChart.Axes(xlValue, xlPrimary).MinimumScale = Worksheets("Base de Dados GBM").Range("I3").Value - Worksheets("Base de Dados GBM").Range("Y12").Value
    ActiveChart.Axes(xlValue, xlPrimary).MaximumScale = Worksheets("Base de Dados GBM").Range("I4").Value + Worksheets("Base de Dados GBM").Range("Y12").Value
    ActiveChart.Axes(xlValue, xlSecondary).MinimumScale = Worksheets("Base de Dados GBM").Range("M3").Value - Worksheets("Base de Dados GBM").Range("Y11").Value
    ActiveChart.Axes(xlValue, xlSecondary).MaximumScale = Worksheets("Base de Dados GBM").Range("M4").Value + Worksheets("Base de Dados GBM").Range("Y11").Value
    
    Application.ScreenUpdating = True
    
    'Range("C7").Select
     'ActiveChart.Axes(xlValue, xlPrimary)
     'MinimumScaleIsAuto = True
     
     End Sub

Sub EixoAutomático()
    On Error Resume Next
    Worksheets("TELA").ChartObjects("VIXBOVA").Activate
    ActiveChart.Axes(xlValue, xlPrimary).MinimumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlPrimary).MaximumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlSecondary).MinimumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlSecondary).MaximumScaleIsAuto = True
    
    Worksheets("TELA").ChartObjects("GFMOVE").Activate
    ActiveChart.Axes(xlValue, xlPrimary).MinimumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlPrimary).MaximumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlSecondary).MinimumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlSecondary).MaximumScaleIsAuto = True
    
    Worksheets("TELA").ChartObjects("CORINGA").Activate
    ActiveChart.Axes(xlValue, xlPrimary).MinimumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlPrimary).MaximumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlSecondary).MinimumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlSecondary).MaximumScaleIsAuto = True
    
    Worksheets("TELA").ChartObjects("VIXBOVAFUT").Activate
    ActiveChart.Axes(xlValue, xlPrimary).MinimumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlPrimary).MaximumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlSecondary).MinimumScaleIsAuto = True
    ActiveChart.Axes(xlValue, xlSecondary).MaximumScaleIsAuto = True

End Sub
Sub IniciarEixo()
iniciador_escala = 1
End Sub
Sub PararEixo()
iniciador_escala = 0

End Sub
