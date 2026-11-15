# rupiah-parse-id

Parser nilai Rupiah kecil untuk aplikasi, ETL, atau pipeline ekstraksi AI yang perlu mengubah format Indonesia menjadi nilai desimal yang konsisten. Menggunakan `Decimal`, bukan `float`, supaya nilai pecahan tidak dibulatkan diam-diam.

## Contoh

```python
from rupiah_parse_id import parse_rupiah, format_rupiah

nilai = parse_rupiah("Rp 1.234.567,89")
print(str(nilai))                 # 1234567.89
print(format_rupiah(nilai))       # Rp 1.234.567,89
```

CLI menerima satu nilai utuh lewat argumen atau stdin:

```sh
rupiah-parse-id --json 'Rp 1.234.567,89'
printf '%s' '-Rp 25.000' | rupiah-parse-id
```

JSON berisi kode mata uang `IDR`, angka kanonis dengan titik desimal untuk mesin, dan format lokal untuk tampilan.

## Format yang didukung

Awalan `Rp` opsional; titik dipakai sebagai pemisah ribuan dan koma sebagai desimal (maksimal dua digit). Contoh: `1.234.567`, `Rp 1234,5`, `-Rp 25.000`, dan `Rp -25.000,50`. Parser memeriksa seluruh masukan—ia tidak mengambil angka dari kalimat dan menolak format yang ambigu seperti `1,234` atau `1,234.56`.

## Batasan dan privasi

Ini hanya parser format, bukan sistem pembukuan atau saran keuangan. Nilai dibaca lokal dan tidak dikirim ke jaringan; input yang gagal tidak dicetak kembali oleh CLI. Tidak ada dependensi runtime.

Python 3.9+. Instalasi: `python -m pip install .`

Tes: `python -m unittest discover -s tests -v`

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
