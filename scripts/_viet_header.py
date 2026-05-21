import pathlib

OUT = pathlib.Path("docs/Client_QA_500_Tieng_Viet.md")

HEADER = """# Nova Health Tech - Tro ly AI Lam sang
## 500 Cau hoi & Tra loi - Danh cho Lanh dao Benh vien

**Doi tuong**: CEO, COO, CFO, CMO, Giam doc Y khoa, Truong khoa, Can bo Tuan thu.

**So lieu co so**: 500 bac si, 40 truy van/ngay, 600.000 truy van/thang, chi phi bac si 80 USD/gio.

---

## 1. Loi ich kinh doanh & ROI

"""

OUT.write_text(HEADER, encoding="utf-8")
print("Header written:", OUT.stat().st_size, "bytes")
