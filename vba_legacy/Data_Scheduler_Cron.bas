Attribute VB_Name = "Módulo11"

Sub Start()

Call Cron

Application.OnTime Now + TimeValue("00:00:01"), "Dados"
Application.OnTime Now + TimeValue("00:00:01"), "status"


End Sub
Sub Cron()

Application.OnTime Now + TimeValue("00:00:03"), "Cron"
Application.ScreenUpdating = False
Application.CalculateFull


If Workbooks(ThisWorkbook.Name).Worksheets("DEFINIÇÕES").Range("a7").Value = 1 Then
    Dim shtact As Worksheet, wkbact As Workbook
    Set wkbact = ActiveWorkbook
    Set shtact = ActiveSheet
    ThisWorkbook.Activate
    Dim sht As Worksheet
    Dim shtname As String
    For Each sht In Worksheets
        'sht.Activate
        shtname = sht.Name
           If ActiveWorkbook.Name = ThisWorkbook.Name And shtname <> "GBM" And shtname <> "DEFINIÇÕES" And shtname <> "Forward N&S" And shtname <> "RRVOL" And shtname <> "historico" And shtname <> "tstat2" And shtname <> "VXOWZ" And shtname <> "Curva" And shtname <> "Feriados" And shtname <> "GARCH" Then
            If sht.Range("M5").Value = "Neg." Then
                With Sheets(shtname)
                    .Range("H5").Value = Now
                End With
            End If
        End If
    Next
    wkbact.Activate
    shtact.Activate
End If
Application.ScreenUpdating = True




End Sub
Sub Dados()

Dim interv As String
interv = Workbooks(ThisWorkbook.Name).Worksheets("DEFINIÇÕES").Range("b1").Value
Application.OnTime Now + TimeValue(interv), "Dados"
Application.OnTime Now + TimeValue(interv), "status"
Application.ScreenUpdating = False
Application.CalculateFull


If Workbooks(ThisWorkbook.Name).Worksheets("DEFINIÇÕES").Range("a7").Value = 1 Then
    Dim shtact As Worksheet, wkbact As Workbook
    Set wkbact = ActiveWorkbook
    Set shtact = ActiveSheet
    ThisWorkbook.Activate
    Dim sht As Worksheet
    Dim shtname As String
    For Each sht In Worksheets
        sht.Activate
        shtname = sht.Name
         If ActiveWorkbook.Name = ThisWorkbook.Name And shtname <> "GBM" And shtname <> "DEFINIÇÕES" And shtname <> "Forward N&S" And shtname <> "RRVOL" And shtname <> "historico" And shtname <> "tstat2" And shtname <> "VXOWZ" And shtname <> "Curva" And shtname <> "Feriados" And shtname <> "GARCH" Then
            If sht.Range("H5").Value <> sht.Range("H6").Value Then
                Range("H6:M500").Value = Range("H5:M499").Value
                Range("I5:K5").Value = Range("L6").Value
            End If
        End If
    Next
    wkbact.Activate
    shtact.Activate
End If
Application.ScreenUpdating = True



End Sub

Private Sub status()

Application.ScreenUpdating = False
        Application.CalculateFull

If Workbooks(ThisWorkbook.Name).Worksheets("GBM").Range("F3").Value = 1 Then
   Dim shtact As Worksheet, wkbact As Workbook
    Set wkbact = ActiveWorkbook
    Set shtact = ActiveSheet
    ThisWorkbook.Activate
    Dim sht As Worksheet
    Dim shtname As String
    For Each sht In Worksheets
        sht.Activate
        shtname = sht.Name
         If ActiveWorkbook.Name = ThisWorkbook.Name And shtname <> "GBM" And shtname <> "DEFINIÇÕES" And shtname <> "Forward N&S" And shtname <> "JUSTO" And shtname <> "historico" And shtname <> "tstat2" And shtname <> "Base de Dados GBM" And shtname <> "Curva" And shtname <> "Feriados" And shtname <> "GARCH" Then
            If sht.Range("G9").Value <> 7 Then
            Call ajusta
                
        
            End If
        End If
    Next
    wkbact.Activate
    shtact.Activate


End If
Application.ScreenUpdating = True
        Application.CalculateFull

End Sub

