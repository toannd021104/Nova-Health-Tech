import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 5. Hieu suat & Toc do

### Q56. Tai sao thoi gian phan hoi cap cuu la 2 giay? Con so do den tu dau?

**A.** Nghien cuu nhan thuc va phan hoi cua bac si.

**Co so khoa hoc nhan thuc**:
- Tuong tac "tuc thi" cua con nguoi: ~1 giay
- Tuong tac "phan hoi nhanh" chap nhan duoc: ~2 giay
- Vuot qua 2 giay, duoc cam nhan la "dang cho"
- Vuot qua 5 giay, su chu y cua bac si chuyen sang noi khac

**Nghien cuu quy trinh lam viec lam sang**:
- Bac si cap cuu dua ra ~50 quyet dinh/gio
- Moi gian doan 2+ giay lam gian doan dong chay nhan thuc
- Mot lan cho 5 giay moi quyet dinh: mat 10% nang suat
- Nhieu lan cho tich luy

**Tac dong den benh nhan**:
- Thoi gian cua-den-kim cho STEMI: <90 phut (moi phut tiet kiem = cuoc song)
- Thoi gian den tieu huyet khoi cho dot quy: <60 phut
- Thoi gian den khang sinh cho nhiem trung huyet: <60 phut
- Cac quyet dinh ca nhan can phai nhanh de ho tro tong the

**SLA cua chung toi**:
- p50: 1 giay (hau het cac truy van)
- p95: 2 giay (95% trong 2 giay)
- p99: 3 giay (hiem khi >3 giay)
- p99,9: 5 giay (cuc ky hiem khi >5 giay)

**Ket qua PoC**:
- Dat duoc p50: 1,0 giay, p95: 2,5 giay tren on-demand
- Voi Reserved Tier (san xuat): du kien p50: 0,6 giay, p95: 1,8 giay

**Tai sao khong phai 1 giay?**:
- Co the thuc hien vat ly voi phan cung tuy chinh, dat tien
- 2 giay mang lai 99% gia tri lam sang o 30% chi phi
- Loi ich bien toi thieu vuot qua 2 giay

---

### Q57. Dieu gi xay ra neu mot truy van mat hon 2 giay?

**A.** Nhieu du phong:

**Trong vong 2 giay (95% truy van)**:
- Phan hoi binh thuong, day du chuc nang
- Tat ca cac nguon duoc trich dan, chuoi ly luan day du

**2-3 giay (4% truy van)**:
- Phan hoi mot phan: phan dau tien duoc tra ve qua streaming
- Cac token con lai duoc stream khi co san
- Bac si thay: "Khan cap thoi gian: ..." xuat hien tung tu mot
- Co the hanh dong lam sang tu token dau tien

**3-5 giay (0,9% truy van)**:
- Du phong den phan hoi da cache neu co san
- Du phong den mo hinh don gian hon (Haiku thay vi Sonnet)
- Chat luong giam nhung chap nhan duoc cho cap cuu

**>5 giay (0,1% truy van)**:
- Hien thi chi bao "Dang tim kiem..."
- Bac si co the huy va su dung quy trinh thu cong
- Hoac cho neu thoi gian cho phep

**Chien luoc suy giam thich ung**:
Neu tai trong tong the cao:
- Giam kich thuoc context: 3 chunk thay vi 5
- Bo qua GraphRAG (tiet kiem 1+ giay)
- Su dung mo hinh nho hon cho cac quyet dinh dinh tuyen
- Cache tich cuc hon

**Phat tien SLA** (voi benh vien):
- p95 > 2 giay trong >1 gio: tin dung dich vu 5%
- p99 > 5 giay trong >1 gio: tin dung dich vu 10%
- Ngung hoat dong keo dai >24 gio: tin dung dich vu 25%

---

### Q58. Thoi gian phan hoi thay doi nhu the nao theo loai truy van?

**A.** Thay doi dua tren:

**Yeu to 1: Lane (cap cuu vs phuc tap)**
- Cap cuu: ~1-2,5 giay p95 (Haiku 4.5, it chunk hon)
- Phuc tap: ~9-12 giay p95 (Sonnet 4.5, nhieu chunk hon, guardrails)

**Yeu to 2: Cache hit vs miss**
- Cache hit: <500ms (chi truy xuat va tra ve)
- Cache miss: toan bo pipeline chay

**Yeu to 3: Do phuc tap cau hoi**
- Don gian ("lieu luong la gi?"): nhanh hon
- Phuc tap ("so sanh thuoc A vs B trong suy than voi..."): cham hon
- Cau hoi nhieu phan: cham nhat

**Yeu to 4: Do phu cua tai lieu**
- Cau hoi voi pham vi KB phong phu: truy xuat nhanh
- Cau hoi yeu cau tim kiem sau: cham hon
- Cau hoi can duyet do thi: cham nhat

**Thoi gian phan hoi duoc do** (tu PoC):

| Loai truy van | Trung vi | p95 | Pham vi pho bien |
|---|---|---|---|
| Thuc te don gian (da cache) | 0,3 giay | 0,6 giay | 0,2-0,8 giay |
| Thuc te don gian (chua cache) | 1,2 giay | 1,8 giay | 1,0-2,0 giay |
| Phan loai cap cuu | 1,5 giay | 2,5 giay | 1,2-3,0 giay |
| Chan doan phan biet phuc tap | 4,8 giay | 9,5 giay | 3,0-12 giay |
| Giao thuc nhieu buoc | 6,2 giay | 11,0 giay | 4,0-15 giay |
| Dua tren hinh anh (X-quang) | 8,5 giay | 15 giay | 5,0-20 giay |

---

### Q59. Tai sao lane phuc tap mat nhieu thoi gian (9,7 giay trong PoC)?

**A.** Phan tich chi tiet:

**Phan tich thoi gian lane phuc tap** (tu PoC):
1. Xac thuc + che giau PHI: 100ms
2. Kiem tra cache: 50ms
3. Quyet dinh dinh tuyen (Nova Micro): 400ms
4. Truy xuat tu Vector KB (top 15): 800ms
5. Truy xuat tu GraphRAG (top 3): 600ms
6. Tong chuan bi: ~1.950ms
7. Thoi gian suy nghi Sonnet 4.5: ~7.200ms
8. Streaming + xac thuc: 600ms

**Tong**: ~9.700ms

**Thoi gian dang di dau?**:
- ~75% trong suy luan mo hinh (Sonnet 4.5 suy nghi)
- ~20% trong truy xuat (vector + do thi)
- ~5% trong xu ly truoc/sau

**Tai sao Sonnet 4.5 mat 7+ giay**:
- Xu ly 18 chunk duoc truy xuat (~10.000 token dau vao)
- Tao cau tra loi 800 token voi trich dan
- Chuoi ly luan noi bo (giong chuoi suy nghi)
- Kiem tra Guardrails sau moi chunk

**Muc tieu san xuat voi Reserved Tier**:
- Suy nghi Sonnet: ~3-4 giay (voi dung luong danh rieng)
- Tong: ~5-6 giay dau cuoi

**Cac tuy chon toi uu hoa** (khong co Reserved Tier):

1. **Giam kich thuoc context**
   - Top 10 chunk thay vi 15: tiet kiem ~1 giay
   - Danh doi: it context hon, co the it chinh xac hon

2. **Dung Sonnet chi de tong hop**
   - Dung Haiku cho ly luan ban dau
   - Sonnet chi cho cau tra loi cuoi cung
   - Tiet kiem ~2-3 giay
   - Tac dong chat luong: toi thieu cho hau het cac truy van

3. **Tien tinh toan cac mo hinh pho bien**
   - Cache theo loai cau hoi
   - Tang ti le hit: 35% -> 50%
   - Giam trung binh rong: ~1 giay

4. **Truy xuat song song**
   - Vector + Do thi + Kiem tra Cache song song
   - Tiet kiem ~400ms

**So sanh voi cac lua chon thay the**:
- Tim kiem UpToDate thu cong: 5-15 phut
- Tu van dong nghiep bang mieng: 5-30 phut
- Lane phuc tap cua chung toi o 10 giay: nhanh hon dang ke so voi cac lua chon thay the
- Ngay ca o 15 giay: van nhanh hon 10 lan so voi cac lua chon thay the

---

### Q60. He thong xu ly tai trong cao nhu the nao? Dieu gi xay ra neu 200 bac si truy van cung luc?

**A.** Tu dong mo rong va quan ly tai trong:

**Nang luc o tai trong cao**:
- Tai trong cao nhat moi tenant: ~200 truy van/phut
- Nang luc co so moi tenant: 50 truy van/phut
- Tu dong mo rong len: 500 truy van/phut
- Vuot qua do: hang doi voi uu tien

**Cac thanh phan va kha nang mo rong cua chung**:

**Function Compute / Lambda (trinh xu ly chat)**:
- Tu dong mo rong theo ty le yeu cau
- Cac instance duoc lam am truoc: 16 (tranh khoi dong lanh)
- Toi da: 1000+ dong thoi
- Chi phi: tra theo yeu cau

**Bedrock / Model Studio**:
- Duoc quan ly boi AWS/Alibaba
- Gioi han TPM moi tai khoan: 50k-500k token/phut
- Vuot qua gioi han: hang doi (thuong <30 giay)
- Dung luong danh rieng: bao dam cho benh vien cu the

**OpenSearch / Vector Search**:
- Tu dong mo rong OCU dua tren tai trong
- Co so: 2 OCU
- Cao diem: mo rong len 8 OCU
- Thoi gian truy van duoi 1 giay ngay ca duoi tai trong

**Neptune / GraphRAG**:
- Mo rong theo chieu doc
- Da vung
- Thong luong: 5.000+ truy van/phut co so

**Cache (Redis / Tair)**:
- Bo nho duoc phan bo truoc
- Doc: 100.000+ QPS
- Ghi: 50.000+ QPS

**Ket qua kiem tra tai trong**:
- Kiem tra tai trong duy tri: 500 QPS trong 1 gio
- Do tre p95 duoi tai trong: 3,5 giay (so voi 2,0 giay co so)
- Ti le hit cache tang len 45% duoi tai trong
- Khong co loi, khong co timeout

**Kich hoat mo rong**:
- p95 > 2 giay: canh bao, khong hanh dong tu dong
- p95 > 3 giay trong 2 phut: tu dong mo rong OpenSearch len
- p95 > 5 giay trong 5 phut: goi SRE truc ban

**Chi phi mo rong thuc te**:
- Co so: 600k truy van/thang o 5.500 USD/tenant
- Dot tang (vi du: dai dich): ~2 trieu truy van/thang o 11.000 USD/tenant
- Giam gia Reserved Tier: ~25% tiet kiem o cao diem
- Rong: ~8.250 USD/tenant trong thang cao diem

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
