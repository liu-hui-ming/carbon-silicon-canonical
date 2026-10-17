# P0 media evidence batch — DT5322 (headed Chrome, resume-safe)
$ErrorActionPreference = "Stop"
$repo = "e:\carbon-silicon-canonical"
$entries = "e:\hundred-crayfish-legion\_tmp_dt5322_report_entries.json"
$catalog = "e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json"
$state = "$repo\_tmp_media_evidence_state_dt5322.json"
$log = "$repo\_tmp_dt5322_batch.log"

Set-Location $repo
attrib -R media_archive /S /D 2>$null

$args = @(
  "-X", "utf8",
  "scripts\media_evidence_archive_batch.py",
  $entries,
  "0", "0",
  "--state", $state,
  "--catalog", $catalog,
  "--source-workbook", "2碳硅道体明细表-更新至20261012.xlsx（私有，不含价格）"
)
Write-Host "Logging to $log"
& python @args 2>&1 | Tee-Object -FilePath $log
