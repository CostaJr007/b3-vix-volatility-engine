Attribute VB_Name = "exportargrafico"
Sub ExportarRR()
    
    Dim abaTemporaria As Worksheet
    Dim graficoTemporario As Chart
    Application.ScreenUpdating = False
    
    ActiveSheet.ChartObjects("RRVOL").Activate
    ActiveChart.PlotArea.Select
    ActiveChart.ChartArea.Select
    ActiveChart.ChartArea.Copy
    
    Set abaTemporaria = Worksheets.Add
    Charts.Add
    ActiveChart.Location where:=xlLocationAsObject, Name:=abaTemporaria.Name
    
    Set graficoTemporario = ActiveChart
    
    graficoTemporario.Paste
    
    With Selection
        .Height = 1080
        .Width = 1080
    End With
    
    abaTemporaria.ChartObjects(1).Select
    With Selection
        .Height = 720
        .Width = 1920
    End With
    
    
    caminhoDoArquivo = ActiveWorkbook.Path
    nomeDaImagem = "\" & Worksheets("GBM").Range("A53") & Worksheets("GBM").Range("B53") & ".jpg"

    graficoTemporario.Export caminhoDoArquivo & nomeDaImagem
    
    Application.DisplayAlerts = False
    abaTemporaria.Delete
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
End Sub

Sub ExportarMove()
    
    Dim abaTemporaria As Worksheet
    Dim graficoTemporario As Chart
    Application.ScreenUpdating = False
    
    ActiveSheet.ChartObjects("MOVE").Activate
    ActiveChart.PlotArea.Select
    ActiveChart.ChartArea.Select
    ActiveChart.ChartArea.Copy
    
    Set abaTemporaria = Worksheets.Add
    Charts.Add
    ActiveChart.Location where:=xlLocationAsObject, Name:=abaTemporaria.Name
    
    Set graficoTemporario = ActiveChart
    
    graficoTemporario.Paste
    
    With Selection
        .Height = 1080
        .Width = 1080
    End With
    
    abaTemporaria.ChartObjects(1).Select
    With Selection
        .Height = 720
        .Width = 1920
    End With
    
    
    caminhoDoArquivo = ActiveWorkbook.Path
    nomeDaImagem = "\" & Worksheets("GBM").Range("A54") & Worksheets("GBM").Range("B53") & ".jpg"

    graficoTemporario.Export caminhoDoArquivo & nomeDaImagem
    
    Application.DisplayAlerts = False
    abaTemporaria.Delete
    Application.DisplayAlerts = True
    Application.ScreenUpdating = True
End Sub


Sub Printar_Tela()
Dim Area As Range
Dim Grafico As ChartObject
Dim oImg As Picture
Dim sPath As String, rRange As String
Dim Planilha As Worksheet

Set Planilha = Sheets("Forward N&S")
With Planilha
Set Area = .Range("a50:v198")
Area.CopyPicture
Set Grafico = .ChartObjects.Add(0, 0, Area.Width, Area.Height)
End With

With Grafico
.Paste

End With




End Sub
