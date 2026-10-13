<#
.SYNOPSIS
  extract_financials.ps1 が出力した data.json を assets/dashboard_template.html に流し込み、
  単一HTMLのダッシュボードを生成する（build_dashboard.py の PowerShell 版）。

.DESCRIPTION
  - 外部ライブラリ・CDN不要（フォントのみGoogle Fonts、無ければ標準フォントにフォールバック）。
  - 出力HTMLはダブルクリックで開くだけで動く。BOM無しUTF-8で書き出す。
  - Windows PowerShell 5.1 / PowerShell 7 の両方で動作。

.EXAMPLE
  pwsh scripts/build_dashboard.ps1 data.json -o dashboard.html
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Data,
  [Alias('o')]
  [string]$Out = 'dashboard.html'
)

$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$tpl = [System.IO.Path]::Combine($here, '..', 'assets', 'dashboard_template.html')

$payload = [System.IO.File]::ReadAllText($Data, [System.Text.Encoding]::UTF8)
$dataObj = $payload | ConvertFrom-Json
$template = [System.IO.File]::ReadAllText($tpl, [System.Text.Encoding]::UTF8)

$company = [string]$dataObj.company
$title = $company + ' 財務ダッシュボード'
if ($title.Length -gt 40) { $title = $title.Substring(0, 40) }

$html = $template.Replace('/*__DATA__*/ null', $payload).Replace('__TITLE__', $title)
if ($html.Contains('/*__DATA__*/')) { $html = $html.Replace('/*__DATA__*/', $payload) }

[System.IO.File]::WriteAllText($Out, $html, (New-Object System.Text.UTF8Encoding($false)))

$n = 0
if ($dataObj.metrics) { $n = @($dataObj.metrics.PSObject.Properties).Count }
Write-Host ('OK ダッシュボード生成: {0}' -f $Out)
Write-Host ('   {0} / 指標{1}件 / {2}' -f $dataObj.company, $n, ($dataObj.fiscalYears -join ', '))
