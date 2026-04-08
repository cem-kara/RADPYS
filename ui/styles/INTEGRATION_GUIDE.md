# ui/styles/INTEGRATION_GUIDE.md

# RADPYS v2 · Tema Sistemi — Entegrasyon Kılavuzu
════════════════════════════════════════════════════════════════

## 🎯 Sistem Mimarı

**Koyu Tema** (colors.DARK)  
↓  
colors.py (renk token'ları)  
↓  
ThemeManager (QApplication'a uygula)  
↓  
UI güncelle (signal)

Aynısı **Açık Tema** (LIGHT) için.

---

## 📦 Struktur

```
ui/styles/
├── colors.py           (DARK/LIGHT token sözlükleri)
├── themes.py           (get_tokens() helper)
├── theme_manager.py    (ThemeManager singleton)
├── icons.py            (50+ SVG icon)
└── __init__.py         (tüm export'lar)
```

---

## 🚀 Hızlı Başlama

### main.py'da

```python
from ui.styles import ThemeManager
from PySide6.QtWidgets import QApplication

app = QApplication([])
ThemeManager.apply_dark(app)  # Başlangıçta koyu tema
```

### Tema Değişimi

```python
from ui.styles import ThemeManager

# Açık temaya geç
ThemeManager.apply_light(app)

# Tema değişim sinyalini dinle
ThemeManager.instance().theme_changed.connect(on_theme_changed)
```

### Renkler Kodda

```python
from ui.styles import DARK, LIGHT, get_tokens

# Token sözlüğü al
tokens = get_tokens("dark")
color = tokens["TEXT_PRIMARY"]  # "#d6e4f0"

# QSS'de
qss = f"color: {color};"
widget.setStyleSheet(qss)
```

---

## 🎨 Renk Token'ları (Tam Liste)

### Zemin
```
BG_DARK, BG_PRIMARY, BG_SECONDARY, BG_TERTIARY, BG_ELEVATED
BG_HOVER, BG_SELECTED
```

### Kenarlıklar
```
BORDER_PRIMARY, BORDER_SECONDARY, BORDER_STRONG, BORDER_FOCUS
```

### Metin
```
TEXT_PRIMARY        (ana metin)
TEXT_SECONDARY      (etiketler)
TEXT_MUTED          (placeholder)
TEXT_DISABLED       (devre dışı)
TEXT_TABLE_HEADER   (tablo başlığı)
```

### Form Alanları
```
INPUT_BG, INPUT_BORDER, INPUT_BORDER_FOCUS
```

### Vurgu
```
ACCENT, ACCENT2, ACCENT_BG
ACCENT_10, ACCENT_20, ACCENT_35  (opaklık varyasyonları)
```

### Butonlar
```
BTN_PRIMARY_*       (mavi butonlar)
BTN_SECONDARY_*     (transparan butonlar)
BTN_DANGER_*        (kırmızı butonlar)
BTN_SUCCESS_*       (yeşil butonlar)
BTN_WARNING_TEXT
```

### Durum Renkleri
```
STATUS_SUCCESS, STATUS_SUCCESS_BG, STATUS_SUCCESS_BORDER
STATUS_WARNING, STATUS_WARNING_BG, STATUS_WARNING_BORDER
STATUS_ERROR, STATUS_ERROR_BG, STATUS_ERROR_BORDER
STATUS_INFO
```

### Diğer
```
OVERLAY_LOW, OVERLAY_MID, OVERLAY_HIGH
MONOSPACE, PLACEHOLDER
```

---

## 📱 Icon Sistemi

### Kullanım

```python
from ui.styles import Icons, ic

# QIcon al (QPushButton, QAction için)
icon = Icons.get("users", size=20, color="accent")
button.setIcon(icon)

# Kısayol
button.setIcon(ic("users", size=20, color="accent"))

# Renk rolleri
ic("bell", color="primary")       # ana rengi
ic("check", color="success")      # başarı rengi
ic("alert", color="error")        # hata rengi
```

### Mevcut İkonlar

```
Personel:      users, user_add, user_check, user_minus
Bildirim:      bell, bell_dot
Arama/Menü:    search, menu, settings
Sağlama:       check, x, circle_check, circle_x
Navigasyon:    chevron_up, chevron_down, chevron_left, chevron_right
               arrow_up, arrow_down
Tarih/Zaman:   calendar, clock
Güvenlik:      lock, unlock, eye, eye_off
İletişim:      mail, phone, world_wide_web
Düzenleme:     trash2, edit, edit2, copy
Dosya:         download, upload
Medya:         play, pause, stop
Diğer:         alert, info
```

---

## ✅ Entegrasyon Adımları

1. **main.py'a ekle:**
   ```python
   from ui.styles import ThemeManager
   ThemeManager.apply_dark(app)
   ```

2. **Kodda renk kullan:**
   ```python
   from ui.styles import DARK
   color = DARK["TEXT_PRIMARY"]
   ```

3. **Icon'ları ekle:**
   ```python
   from ui.styles import ic
   button.setIcon(ic("users"))
   ```

4. **QSS'de template oluştur** (isteğe bağlı):
   ```qss
   QLineEdit {
       background-color: {INPUT_BG};
       color: {TEXT_PRIMARY};
   }
   ```
   Token'ları derleme işlemi ayrı olacak.

---

## 🔄 QSS Şablonları

Eğer QSS template sistemi istiyorsanız, theme_template.qss oluşturun ve dosyanın içinde placeholder'lar kullanın:

```qss
QLineEdit {
    background-color: {INPUT_BG};
    border: 1px solid {BORDER_PRIMARY};
    color: {TEXT_PRIMARY};
}
```

Sonra Python'da derle:

```python
from ui.styles import get_tokens

tokens = get_tokens("dark")
template = Path("ui/theme_template.qss").read_text()

qss = template
for key, val in tokens.items():
    qss = qss.replace(f"{{{key}}}", val)

app.setStyleSheet(qss)
```

---

## 💡 İpuçları

- **Tema değişim:** `ThemeManager.switch_theme(app, "light")`
- **Dinamik renkler:** Token'ları her yerde erişebilir hale getir
- **Icon'ları genişlet:** `icons.py`'de `SVG_PATHS` dict'e SVG ekle
- **Özel renkler:** DARK/LIGHT dict'lerine yeni token'lar ekle

---

## 📚 API Özeti

| Fonksiyon | Açıklama |
|-----------|----------|
| `ThemeManager.apply_dark(app)` | Koyu tema uygula |
| `ThemeManager.apply_light(app)` | Açık tema uygula |
| `ThemeManager.switch_theme(app, "light")` | Tema değiştir |
| `ThemeManager.current_theme()` | Aktif tema adını döner |
| `get_tokens("dark")` | Token sözlüğü al |
| `Icons.get("users", size=20)` | QIcon oluştur |
| `ic("users")` | Kısayol |

Hazır! Tema sisteminiz modern ve temiz.
