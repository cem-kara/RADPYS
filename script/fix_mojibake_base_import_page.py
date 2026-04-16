from pathlib import Path

p = Path("ui/pages/imports/components/base_import_page.py")
text = p.read_text(encoding="utf-8")

repl = {
    "ı": "ı",
    "İ": "İ",
    "ç": "ç",
    "Ç": "Ç",
    "ö": "ö",
    "Ö": "Ö",
    "ü": "ü",
    "Ü": "Ü",
    "ÅŸ": "ş",
    "Åž": "Ş",
    "ÄŸ": "ğ",
    "Äž": "Ğ",
    "—": "—",
    "→": "→",
    "✓": "✓",
    "âš ": "⚠",
}

new_text = text
for bad, good in repl.items():
    new_text = new_text.replace(bad, good)

if new_text != text:
    p.write_text(new_text, encoding="utf-8")
    print("fixed")
else:
    print("nochange")
