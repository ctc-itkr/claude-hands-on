<#
.SYNOPSIS
  EDINET有価証券報告書の生XBRLから「経営指標等(SummaryOfBusinessResults)」の
  5期分の主要財務指標を抽出し data.json を出力する（extract_financials.py の PowerShell 版）。

.DESCRIPTION
  - .NET 標準機能のみ（System.Xml / System.IO.Compression）。arelle / lxml / pandas 不要。
  - 入力は ZIP でも解凍済みフォルダでも .xbrl 直接でも可。
  - IFRS / 日本基準(JGAAP) を要素名の候補で自動判定。
  - Windows PowerShell 5.1 / PowerShell 7 の両方で動作。出力は BOM 無し UTF-8。

.EXAMPLE
  pwsh scripts/extract_financials.ps1 <有報ZIP or フォルダ or .xbrl> -o data.json
  （Windowsで pwsh が無い場合）powershell -File scripts\extract_financials.ps1 <入力> -o data.json
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$InputPath,
  [Alias('o')]
  [string]$Out = 'data.json'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null

# 相対年度（コンテキストID接頭辞）: 古い -> 新しい
$PERIODS = @('Prior4Year', 'Prior3Year', 'Prior2Year', 'Prior1Year', 'CurrentYear')

# 抽出する指標。tags は候補ローカル名を優先順で並べ、最初に見つかったものを採用
# （IFRS要素と日本基準要素を混在させ会計基準を自動吸収）。scale は表示単位への変換係数。
$METRICS = @(
  [ordered]@{ key = 'revenue'; li = '売上収益'; lj = '売上高'; unit = '億円'; kind = 'bar'; scale = 1e8;
    tags = @('RevenueIFRSSummaryOfBusinessResults', 'NetSalesSummaryOfBusinessResults',
      'OperatingRevenue1SummaryOfBusinessResults', 'GrossOperatingRevenueSummaryOfBusinessResults',
      'OrdinaryIncomeRevenueSummaryOfBusinessResults', 'TotalOperatingRevenueSummaryOfBusinessResults') }
  [ordered]@{ key = 'income2'; li = '税引前利益'; lj = '経常利益'; unit = '億円'; kind = 'line'; scale = 1e8;
    tags = @('ProfitLossBeforeTaxIFRSSummaryOfBusinessResults', 'OrdinaryIncomeLossSummaryOfBusinessResults') }
  [ordered]@{ key = 'profit'; li = '当期利益（親会社帰属）'; lj = '当期純利益'; unit = '億円'; kind = 'bar'; scale = 1e8;
    tags = @('ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults',
      'ProfitLossAttributableToOwnersOfParentSummaryOfBusinessResults',
      'NetIncomeLossSummaryOfBusinessResults') }
  [ordered]@{ key = 'totalassets'; li = '総資産'; lj = '総資産'; unit = '億円'; kind = 'bar'; scale = 1e8;
    tags = @('TotalAssetsIFRSSummaryOfBusinessResults', 'TotalAssetsSummaryOfBusinessResults') }
  [ordered]@{ key = 'equity'; li = '親会社所有者持分'; lj = '純資産'; unit = '億円'; kind = 'bar'; scale = 1e8;
    tags = @('EquityAttributableToOwnersOfParentIFRSSummaryOfBusinessResults',
      'NetAssetsSummaryOfBusinessResults') }
  [ordered]@{ key = 'cfo'; li = '営業キャッシュ・フロー'; lj = '営業キャッシュ・フロー'; unit = '億円'; kind = 'bar'; scale = 1e8;
    tags = @('CashFlowsFromUsedInOperatingActivitiesIFRSSummaryOfBusinessResults',
      'NetCashProvidedByUsedInOperatingActivitiesSummaryOfBusinessResults',
      'CashFlowsFromUsedInOperatingActivitiesSummaryOfBusinessResults') }
  [ordered]@{ key = 'roe'; li = 'ROE（持分利益率）'; lj = '自己資本利益率'; unit = '%'; kind = 'line'; scale = 0.01;
    tags = @('RateOfReturnOnEquityIFRSSummaryOfBusinessResults',
      'RateOfReturnOnEquitySummaryOfBusinessResults') }
  [ordered]@{ key = 'equityratio'; li = '自己資本比率'; lj = '自己資本比率'; unit = '%'; kind = 'line'; scale = 0.01;
    tags = @('RatioOfOwnersEquityToGrossAssetsIFRSSummaryOfBusinessResults',
      'EquityToAssetRatioIFRSSummaryOfBusinessResults',
      'EquityToAssetRatioSummaryOfBusinessResults') }
  [ordered]@{ key = 'eps'; li = '基本的EPS'; lj = '1株当たり当期純利益'; unit = '円'; kind = 'line'; scale = 1;
    tags = @('BasicEarningsLossPerShareIFRSSummaryOfBusinessResults',
      'BasicEarningsLossPerShareSummaryOfBusinessResults') }
  [ordered]@{ key = 'dividend'; li = '1株当たり配当'; lj = '1株当たり配当'; unit = '円'; kind = 'bar'; scale = 1;
    tags = @('DividendPaidPerShareSummaryOfBusinessResults') }
  [ordered]@{ key = 'employees'; li = '従業員数'; lj = '従業員数'; unit = '人'; kind = 'line'; scale = 1;
    tags = @('NumberOfEmployees') }
)

# DEI（会社情報）ローカル名 -> 出力キー
$DEI = [ordered]@{
  edinetCode = 'EDINETCodeDEI'; secCode = 'SecurityCodeDEI';
  company    = 'FilerNameInJapaneseDEI'; accounting = 'AccountingStandardsDEI';
  fyEnd      = 'CurrentFiscalYearEndDateDEI'; fyStart = 'CurrentFiscalYearStartDateDEI';
}
# 逆引き（DEIローカル名 -> キー）
$DEI_REV = @{}
foreach ($k in $DEI.Keys) { $DEI_REV[$DEI[$k]] = $k }
$SPEC_IFRS_KEYS = @('totalassets', 'equityratio', 'dividend', 'employees')

function Find-Xbrl {
  param([string]$Path)
  if ($Path.ToLower().EndsWith('.xbrl')) { return $Path }
  $root = $Path
  if (Test-Path -LiteralPath $Path -PathType Leaf) {
    # ZIP とみなして展開を試みる
    try {
      $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('edinet_' + [guid]::NewGuid().ToString('N'))
      [System.IO.Compression.ZipFile]::ExtractToDirectory($Path, $tmp)
      $root = $tmp
    }
    catch { $root = $Path }
  }
  $cands = Get-ChildItem -LiteralPath $root -Recurse -Filter '*.xbrl' -File |
    Where-Object { ($_.FullName -notmatch 'AuditDoc') -and $_.Name.StartsWith('jp') }
  $pub = @($cands | Where-Object { $_.FullName -match 'PublicDoc' })
  if ($pub.Count -eq 0) { $pub = @($cands) }
  if ($pub.Count -eq 0) { throw "XBRLインスタンス(.xbrl)が見つかりません: $Path" }
  # asr(有報)本体を最優先、次にパス長の短い順
  $pub = $pub | Sort-Object `
    @{ Expression = { if ($_.Name -match 'asr') { 0 } else { 1 } } }, `
    @{ Expression = { $_.FullName.Length } }
  return $pub[0].FullName
}

function Get-CtxClass {
  # コンテキストIDを (相対年度, 優先度) に分類。0=連結, 1=個別。対象外は $null。
  param([string]$Ctxid)
  foreach ($p in $PERIODS) {
    foreach ($suf in @('Duration', 'Instant')) {
      if ($Ctxid -ceq ($p + $suf)) { return @($p, 0) }
      if ($Ctxid -ceq ($p + $suf + '_NonConsolidatedMember')) { return @($p, 1) }
    }
  }
  return @($null, $null)
}

# --- XBRL 読み込み ---
$xbrlPath = Find-Xbrl -Path $InputPath
$doc = New-Object System.Xml.XmlDocument
$doc.Load($xbrlPath)
$nodes = $doc.SelectNodes('//*')

# --- DEI 収集 & 全ファクト収集 ---
$dei = @{}
$facts = @{}   # "localName|period" -> @(prio, value)
foreach ($el in $nodes) {
  $ln = $el.LocalName
  if ($DEI_REV.ContainsKey($ln)) {
    $t = $el.InnerText
    if ($t) { $dei[$DEI_REV[$ln]] = $t.Trim() }
  }
  $cref = $el.GetAttribute('contextRef')
  if ([string]::IsNullOrEmpty($cref)) { continue }
  $cls = Get-CtxClass -Ctxid $cref
  $period = $cls[0]
  if ($null -eq $period) { continue }
  $prio = [int]$cls[1]
  $txt = $el.InnerText
  if ($null -eq $txt) { continue }
  $txt = $txt.Trim()
  if ($txt -eq '' -or $txt -eq '-' -or $txt -eq '－') { continue }
  $mapkey = "$ln|$period"
  $cur = $facts[$mapkey]
  if (($null -eq $cur) -or ($prio -lt [int]$cur[0])) { $facts[$mapkey] = @($prio, $txt) }
}

function Get-Val {
  param($Facts, [string]$Tag, [string]$Period)
  $v = $Facts["$Tag|$Period"]
  if ($v) { return $v[1] } else { return $null }
}

$acc = ''
if ($dei.ContainsKey('accounting')) { $acc = [string]$dei['accounting'] }
$isIfrs = $acc.ToUpper().StartsWith('IFRS')

# --- 指標ごとに5期分を組み立て ---
# 注意: PowerShell の変数名は大文字小文字を区別しないため、出力用は $METRICS と衝突しない名前($metricsOut)にする
$metricsOut = [ordered]@{}
foreach ($m in $METRICS) {
  $matched = $null
  $series = @($null, $null, $null, $null, $null)
  foreach ($tag in $m.tags) {
    $vals = @()
    foreach ($p in $PERIODS) { $vals += (Get-Val -Facts $facts -Tag $tag -Period $p) }
    if (@($vals | Where-Object { $null -ne $_ }).Count -gt 0) { $matched = $tag; $series = $vals; break }
  }
  if ($null -eq $matched) { continue }
  $outArr = @()
  foreach ($v in $series) {
    if ($null -eq $v) { $outArr += , $null; continue }
    try {
      $num = [double]::Parse($v, [System.Globalization.CultureInfo]::InvariantCulture)
      $outArr += [math]::Round($num / [double]$m.scale, 4)
    }
    catch { $outArr += , $null }
  }
  if ($matched.Contains('IFRS') -or ($isIfrs -and ($SPEC_IFRS_KEYS -contains $m.key))) { $label = $m.li } else { $label = $m.lj }
  if ($matched.Contains('IFRS')) { $label = $label + '（IFRS）' }
  $metricsOut[$m.key] = [ordered]@{ label = $label; unit = $m.unit; kind = $m.kind; data = $outArr }
}

# --- 会計年度ラベル（決算期末から5期分を生成）---
$fyEnd = ''
if ($dei.ContainsKey('fyEnd')) { $fyEnd = [string]$dei['fyEnd'] }
$fys = @()
$mo = [regex]::Match($fyEnd, '^(\d{4})-(\d{2})')
if ($mo.Success) {
  $y = [int]$mo.Groups[1].Value
  $mth = [int]$mo.Groups[2].Value
  for ($i = 0; $i -lt 5; $i++) { $fys += ('{0}/{1}' -f ($y - 4 + $i), $mth) }
}
else {
  for ($i = 1; $i -le 5; $i++) { $fys += ('第{0}期' -f $i) }
}

$company = if ($dei.ContainsKey('company')) { [string]$dei['company'] } else { '（会社名不明）' }
$result = [ordered]@{
  company     = $company
  edinetCode  = $(if ($dei.ContainsKey('edinetCode')) { [string]$dei['edinetCode'] } else { '' })
  secCode     = $(if ($dei.ContainsKey('secCode')) { [string]$dei['secCode'] } else { '' })
  accounting  = $acc
  fyEnd       = $fyEnd
  fiscalYears = $fys
  source      = 'EDINET XBRL: ' + [System.IO.Path]::GetFileName($xbrlPath)
  metrics     = $metricsOut
}

$json = $result | ConvertTo-Json -Depth 8
[System.IO.File]::WriteAllText($Out, $json, (New-Object System.Text.UTF8Encoding($false)))

$labels = @($metricsOut.Values | ForEach-Object { $_.label }) -join '、'
Write-Host ('OK 抽出完了: {0} ({1}) -> {2}' -f $result.company, $result.accounting, $Out)
Write-Host ('   決算期末 {0} / 会計年度 {1}' -f $fyEnd, ($fys -join ', '))
Write-Host ('   取得指標 {0}件: {1}' -f $metricsOut.Count, $labels)
