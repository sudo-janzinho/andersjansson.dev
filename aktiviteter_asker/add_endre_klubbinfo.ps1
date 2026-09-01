# Legg til "Endre klubbinfo"-lenke på alle 197 undersider i aktivity_asker
$ErrorActionPreference = "Stop"
$p = "C:\Users\janss\.openclaw\workspace\andersjansson-dev\aktiviteter_asker"
$files = Get-ChildItem $p -Filter "*.html" | Where-Object { $_.Name -notin @("index.html","ny-klubb.html","endre-klubbinfo.html") }

$backPattern = '<a class="back" href="index.html">&larr; Tilbake til alle aktiviteter</a>'
$updated = 0
$skipped = @()

foreach ($f in $files) {
    $c = Get-Content $f.FullName -Raw -Encoding UTF8

    # Hent klubbnavn fra <h2>...</h2>
    $m = [regex]::Match($c, '<h2>(.*?)</h2>')
    if (-not $m.Success) { $skipped += $f.Name; continue }
    $navn = $m.Groups[1].Value.Trim()

    # Sjekk at lenken ikke allerede finnes (idempotent)
    if ($c -match 'endre-klubbinfo.html') { $skipped += $f.Name; continue }

    # Bygg lenken med klubbnavn i query-parameter (URL-encodet)
    $enc = [System.Uri]::EscapeDataString($navn)
    $lenke = '<a class="back" href="endre-klubbinfo.html?klubb=' + $enc + '" style="margin-left:1rem;">Endre klubbinfo &rarr;</a>'

    if (-not $c.Contains($backPattern)) { $skipped += $f.Name; continue }

    $c = $c.Replace($backPattern, $backPattern + "`n  " + $lenke)
    [System.IO.File]::WriteAllText($f.FullName, $c, (New-Object System.Text.UTF8Encoding($false)))
    $updated++
}

Write-Output "Oppdatert: $updated"
Write-Output "Hoppet over (mangler h2 / allerede lagt til / mangler back): $($skipped.Count)"
$skipped | Select-Object -First 20
