$path = "ui/pages/imports/components/base_import_page.py"
$text = Get-Content -Path $path -Raw -Encoding UTF8

$map = @{
    "Ä±" = "ı"
    "Ä°" = "İ"
    "Ã§" = "ç"
    "Ã‡" = "Ç"
    "Ã¶" = "ö"
    "Ã–" = "Ö"
    "Ã¼" = "ü"
    "Ãœ" = "Ü"
    "ÅŸ" = "ş"
    "Åž" = "Ş"
    "ÄŸ" = "ğ"
    "Äž" = "Ğ"
    "â€”" = "—"
    "â†’" = "→"
    "âœ“" = "✓"
    "âš " = "⚠"
}

foreach ($k in $map.Keys) {
    $text = $text.Replace($k, $map[$k])
}

Set-Content -Path $path -Value $text -Encoding UTF8
Write-Output "fixed"
