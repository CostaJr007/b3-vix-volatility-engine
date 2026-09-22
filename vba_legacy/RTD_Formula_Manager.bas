Attribute VB_Name = "Módulo31"
Const Ser As String = "Forward N&S"

Sub Configurar_Limpar()
    Dim Linha As Integer
    Sheets(Ser).Range("A2").Value = ""
    Sheets(Ser).Range("B3:F" & ULinha(1, Ser)).ClearContents
    Sheets(Ser).Range("A1").Value = "***"
    Sheets("GBM").Range("R1").Value = ""
End Sub

Sub Configurar_RTD_TRYD()
    Dim Linha As Integer
    Dim Ult_Linha As Double
    Dim Percentual As Single
    Dim Contador As Double
    Sheets("GBM").Range("R2").Value = "RTD TRYD SELECIONADO"
    Barra_Progresso.Show vbModeless
    Ult_Linha = ULinha(1, Ser)
    Linha = 3
    Do While Linha <= Ult_Linha
        Sheets(Ser).Range("E" & Linha).Select
        ActiveCell.FormulaR1C1 = "=RTD(""tryd.rtdserver"",,""COT"",RC[-4],""Ult"")/100"
        Sheets(Ser).Range("F" & Linha).Select
        ActiveCell.FormulaR1C1 = "=IF(ISNUMBER(RTD(""tryd.rtdserver"",,""COT"",RC[-5],""Var"")),RTD(""tryd.rtdserver"",,""COT"",RC[-5],""Var"")/100,"""")"
        Sheets(Ser).Range("D" & Linha).Select
        ActiveCell.FormulaR1C1 = "=IF(ISNUMBER(RTD(""tryd.rtdserver"",,""COT"",RC[-3],""FechAj"")),RTD(""tryd.rtdserver"",,""COT"",RC[-3],""FechAj"")/100,0)"
        Sheets(Ser).Range("C" & Linha).Select
        ActiveCell.FormulaR1C1 = "=IF(ISNUMBER(RTD(""tryd.rtdserver"",,""COT"",RC[-2],""FechAjAnt"")),RTD(""tryd.rtdserver"",,""COT"",RC[-2],""FechAjAnt"")/100,0)"
        Sheets(Ser).Range("B" & Linha).Select
        ActiveCell.FormulaR1C1 = "=IF(ISNUMBER(RTD(""tryd.rtdserver"",,""COT"",RC[-1],""Expir"")),RTD(""tryd.rtdserver"",,""COT"",RC[-1],""Expir""),0)"
        Linha = Linha + 1
        Contador = Contador + 1
        Percentual = Contador / Ult_Linha
        AtualizaBarra Percentual
    Loop
    Sheets("GBM").Activate
    Sheets("GBM").Range("R1").Activate
    ActiveCell.FormulaR1C1 = "=RTD(""tryd.rtdserver"",,""COT"",RC[-13],""HORA"")"
    Sheets(Ser).Range("A1").Value = "RTD-TRYD"
    Barra_Progresso.Hide
End Sub



Sub Configurar_RTD_FAST()
     Dim Linha As Integer
    Dim Ult_Linha As Double
    Dim Percentual As Single
    Dim Contador As Double
    Sheets("GBM").Range("R2").Value = "RTD FAST TRADE SELECIONADO"
    Barra_Progresso.Show vbModeless
    Ult_Linha = ULinha(1, Ser)
    Linha = 3
    Do While Linha <= Ult_Linha
        Sheets(Ser).Range("E" & Linha).Select
        ActiveCell.FormulaR1C1 = "=RTD(""srv.rtd"",,""SQT"",RC[-4],""LAST"")/100"
        Sheets(Ser).Range("F" & Linha).Select
        ActiveCell.FormulaR1C1 = "=IF(ISNUMBER(RTD(""srv.rtd"",,""SQT"",RC[-5],""VAR"")/100),RTD(""srv.rtd"",,""SQT"",RC[-5],""VAR"")/100,"""")"
        Sheets(Ser).Range("D" & Linha).Select
        ActiveCell.FormulaR1C1 = "=IF(ISNUMBER(RTD(""srv.rtd"",,""SQT"",RC[-3],""AJU"")/100),RTD(""srv.rtd"",,""SQT"",RC[-3],""AJU"")/100,0)"
        Sheets(Ser).Range("C" & Linha).Select
        ActiveCell.FormulaR1C1 = "=IF(ISNUMBER(RTD(""srv.rtd"",,""SQT"",RC[-2],""AJULAST"")/100),RTD(""srv.rtd"",,""SQT"",RC[-2],""AJULAST"")/100,0)"
        Sheets(Ser).Range("B" & Linha).Select
        ActiveCell.FormulaR1C1 = "=IF(ISNUMBER(RTD(""srv.rtd"",,""SQT"",RC[-1],""DTEX"")),RTD(""srv.rtd"",,""SQT"",RC[-1],""DTEX""),0)"
        Linha = Linha + 1
        Contador = Contador + 1
        Percentual = Contador / Ult_Linha
        AtualizaBarra Percentual
    Loop
    Sheets("GBM").Activate
    Sheets("GBM").Range("R1").Activate
    ActiveCell.FormulaR1C1 = "=RTD(""srv.rtd"",,""SQT"",RC[-13],""TIME"")"
    
    Sheets(Ser).Range("A1").Value = "RTD-FAST"
    Barra_Progresso.Hide
End Sub

Sub Configurar_PROFITCHART()
    Dim Linha As Integer
    Dim Ult_Linha As Double
    Dim Percentual As Single
    Dim Contador As Double
    Sheets("GBM").Range("R2").Value = "RTD PROFITCHART SELECIONADO."
    Barra_Progresso.Show vbModeless
    Ult_Linha = ULinha(1, Ser)
    Linha = 3
    Do While Linha <= Ult_Linha
        Sheets(Ser).Range("E" & Linha).Select
        ActiveCell.FormulaR1C1 = "=RTD(""rtdtrading.rtdserver"",,RC[-4],""ULT"")/100"
        Sheets(Ser).Range("F" & Linha).Select
        ActiveCell.FormulaR1C1 = "=RTD(""rtdtrading.rtdserver"",,RC[-5],""VAR"")/100"
        Sheets(Ser).Range("D" & Linha).Select
        ActiveCell.FormulaR1C1 = "=RTD(""rtdtrading.rtdserver"",,RC[-3],""AJU"")/100"
        Sheets(Ser).Range("C" & Linha).Select
        ActiveCell.FormulaR1C1 = "=RTD(""rtdtrading.rtdserver"",,RC[-2],""AJA"")/100"
        Sheets(Ser).Range("B" & Linha).Select
        ActiveCell.FormulaR1C1 = "=RTD(""rtdtrading.rtdserver"",,RC[-1],""VEN"")"
        Linha = Linha + 1
        Contador = Contador + 1
        Percentual = Contador / Ult_Linha
        AtualizaBarra Percentual
    Loop
    Sheets("GBM").Activate
    Sheets("GBM").Range("R1").Activate
    ActiveCell.FormulaR1C1 = "=RTD(""rtdtrading.rtdserver"",,RC[-13],""HOR"")"
    Sheets(Ser).Range("A1").Value = "LINK DDE-PROFITCHART"
    Barra_Progresso.Hide
End Sub


