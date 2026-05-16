import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 7. Trien khai & Lo trinh

### Q66. Mat bao lau de trien khai tu "quyet dinh duoc dua ra" den "bac si dau tien su dung"?

**A.** Lich trinh thuc te: 6-10 tuan cho tenant benh vien dau tien.

**Phan tich tung tuan**:

**Tuan 1-2: Nen tang**
- Ky hop dong voi Nova
- Cap phep tai khoan AWS/Alibaba
- Thiet lap VPC, IAM, mang
- Ket noi voi IdP benh vien (xac thuc bac si)
- Trien khai OpenSearch va Neptune ban dau

**Tuan 3-4: Nhap du lieu**
- Nhap huong dan WHO
- Tich hop API ICD-11
- Tai len PDF bao cao thu nghiem noi bo (benh vien cung cap)
- Tao nhung vector
- Trich xuat thuc the GraphRAG

**Tuan 5-6: Cau hinh AI**
- Thiet lap cac agent khoa (12 khoa)
- Tuy chinh system prompt
- Cau hinh chinh sach Guardrails
- Khoi tao cache
- Thu thap du lieu fine-tuning (neu ap dung)

**Tuan 7-8: Tich hop & Bao mat**
- Tich hop EHR (FHIR R4)
- Thiet lap webhook SharePoint
- Hoan thien tai lieu tuan thu
- Kiem toan bao mat

**Tuan 9-10: Thi diem & Ra mat**
- Thi diem noi bo (nhan vien Nova): 1 tuan
- Thi diem han che (10-20 bac si): 1 tuan
- Trien khai tung khoa
- Ra mat day du

**Con duong quan trong**:
- Tich hop IdP benh vien: thuong mat 2-3 tuan rieng
- Phe duyet thiet bi y te HSA (neu chua co): 3-6 thang (song song)
- Xem xet an toan lam sang: 2-3 tuan

**Con duong nhanh hon** (neu Nova da lam truoc):
- 4-6 tuan cho cac tenant lap lai
- Cac mau co the tai su dung
- Cac tich hop duoc phe duyet truoc

**Con duong cham hon** (benh vien phuc tap):
- 12-16 tuan neu tich hop EHR la moi
- Nhieu vong tuan thu
- Tuy chinh rong lon yeu cau

---

### Q67. Nhom cua chung toi can lam gi trong qua trinh trien khai?

**A.** Trach nhiem cua benh vien:

**Truoc khi khoi dong** (chuan bi benh vien):
1. Xac dinh nha tai tro du an (CMIO hoac tuong duong)
2. Lap nhom du an benh vien
3. Phe duyet ngan sach ban dau
4. Ky Thoa thuan Dich vu Chu

**Khoi dong den Tuan 2**:

**Trach nhiem nhom benh vien**:
- Chi dinh chuyen gia lam sang (1-2 bac si)
- Thiet lap quyen truy cap cho cac ky su Nova (han che, co pham vi)
- Cung cap chi tiet tich hop IdP
- Xac dinh lien he EHR

**Nova cung cap**:
- Quan ly du an
- Ky su truong
- Can bo tuan thu
- Tu van lam sang

**Tuan 3-4 (nhap du lieu)**:

**Benh vien cung cap**:
- PDF bao cao thu nghiem lam sang noi bo
- Giao thuc cu the cua benh vien
- Tai lieu tham khao theo khoa
- Logo, thuong hieu cho giao dien nguoi dung

**Nova thuc hien**:
- Nhap noi dung
- Cau hinh truy xuat
- Thiet lap cac thuc the GraphRAG

**Tuan 5-6 (cau hinh)**:

**Benh vien cung cap**:
- Tuy chon gion van theo khoa
- Cac chu de bi cam (vi du: cac lieu phap thu nghiem)
- Cac mau tu choi
- Cac mau tin nhan duoc phe duyet

**Nova thuc hien**:
- Cau hinh 12 agent khoa
- Dieu chinh truy xuat theo khoa
- Thiet lap chinh sach Guardrails

**Tuan 7-8 (tich hop)**:

**Benh vien cung cap**:
- Chi tiet diem cuoi FHIR EHR
- Thong tin xac thuc SMART App Launch
- Ngoai le bao mat mang
- Thiet lap duong ham VPN

**Nova thuc hien**:
- Code tich hop FHIR
- Cau hinh SMART
- Thiet lap data plane VPN

**Tuan 9-10 (ra mat)**:

**Benh vien cung cap**:
- Phan hoi bac si
- Lua chon nhom (nhom thi diem)
- Truyen thong den bac si
- Tham du buoi dao tao

**Nova cung cap**:
- Dao tao onboarding
- Ho tro truc tiep trong thi diem
- Giai quyet van de

**Tong no luc benh vien**:
- Nha tai tro du an: ~5 gio/tuan x 10 tuan = 50 gio
- Chuyen gia lam sang: ~10 gio/tuan x 4 tuan = 40 gio
- CNTT benh vien: ~20 gio/tuan x 4 tuan = 80 gio
- Can bo tuan thu: ~5 gio/tuan x 6 tuan = 30 gio
- Tong: ~200 gio thoi gian benh vien

**Chi phi thoi gian benh vien**:
- ~200 gio x 200 USD/gio ty le pha tron = 40.000 USD
- Day la dau tu cho benh vien
- Duoc hoan von trong 2 tuan dau tien van hanh

---

### Q68. Chung toi co the bat dau voi chuong trinh thi diem nho hon truoc khong?

**A.** Duoc khuyen nghi manh me:

**Cac cau truc thi diem**:

**Phuong an 1: Mot khoa, 30 ngay**
- Chon: Khoa Cap cuu (tac dong cao nhat)
- 20-30 bac si
- Che do chi doc ban dau (goi y, khong co hanh dong lam sang)
- Chi phi: giong nhu trien khai day du co so ha tang
- Gia tri: xac thuc truoc khi trien khai day du

**Phuong an 2: Mot loai chuyen khoa, 60 ngay**
- Chon: Noi khoa tren cac khoa
- 50-100 bac si
- Ket hop che do chi doc va su dung tich cuc
- Nhieu du lieu, nhieu su tu tin

**Phuong an 3: Thi diem toan benh vien 90 ngay**
- Tat ca cac khoa, nhung voi khung "thi diem" ro rang
- De ket thuc neu khong hoat dong
- Dat tien nhung thuc te

**Chi phi trong thi diem**:
- Cung co so ha tang nhu san xuat (2.800-5.500 USD/thang)
- Cong them chi phi trien khai benh vien (40.000 USD)
- Tru cac khoang tiet kiem tiem nang trong thi diem

**Tieu chi thanh cong thi diem**:

**Bat buoc**:
- 70%+ bac si thi diem su dung hang tuan
- 90%+ do chinh xac (duoc xac minh boi can bo an toan lam sang)
- 100% tuan thu luu tru du lieu
- Khong co su co bao mat
- <=5% ti le tu choi (tin hieu-nhieu)

**Mong muon**:
- 80% thoi gian tiet kiem tren cac chu de duoc tu van
- 90%+ thumbs up
- 50%+ ap dung trich dan
- Top 5 truong hop su dung duoc xac dinh

**Cac tuy chon ket thuc thi diem**:

**Thi diem thanh cong**:
- Tiep tuc trien khai day du
- Them cac khoa
- Mo rong quy mo

**Thi diem khong ket luan**:
- Gia han them 60 ngay
- Giai quyet cac van de cu the
- Danh gia lai

**Thi diem that bai**:
- Ngung
- Giai doan giam dan 30 ngay
- Nhat ky kiem toan duoc bao ton (quy dinh)

**Khung thi diem duoc khuyen nghi**:
- Thang 1: trien khai + chuan bi thi diem
- Thang 2: van hanh thi diem (30-60 ngay)
- Thang 3: danh gia + quyet dinh
- Thang 4-6: trien khai day du (neu thanh cong)

---

### Q69. Ai tu phia chung toi can tham gia vao viec trien khai?

**A.** Ban do cac ben lien quan:

**Nha tai tro dieu hanh**:
- CEO/COO: trach nhiem cuoi cung, phe duyet ngan sach
- CFO: giam sat ngan sach, theo doi ROI
- CMO: giam sat an toan lam sang

**Lanh dao du an**:
- Giam doc Thong tin Y te Truong (CMIO): nha tai tro du an chinh
- Quan ly Du an: phoi hop hang ngay
- Giam doc Lam sang: ky duyet lam sang

**Chuyen gia lam sang** (1-2 moi khoa):
- Cac bac si chuyen gia ung ho
- Cung cap dau vao lam sang
- Kiem tra thi diem
- Dao tao dong nghiep

**Nhom CNTT**:
- Giam doc CNTT: lanh dao phia CNTT
- Ky su truong: thuc hien ky thuat
- Ky su Bao mat: xem xet bao mat
- Ky su Mang: VPN, tich hop

**Tuan thu**:
- Can bo Tuan thu: giam sat quy dinh
- DPO: bao ve du lieu
- Co van Phap ly: xem xet hop dong

**Tuong duong phia Nova**:
- Giam doc Tai khoan: lanh dao quan he
- Quan ly Du an: phoi hop
- Ky su truong: lanh dao ky thuat
- Tu van Lam sang: lien lac lam sang
- Can bo Tuan thu: ho tro quy dinh

**Nhip do giao tiep**:

**Hang tuan trong trien khai**:
- Quan ly du an (benh vien) <-> Quan ly du an (Nova)
- Cuoc hop trang thai 30 phut
- Cac hang muc hanh dong, cac van de can giai quyet

**Hai tuan mot lan trong trien khai**:
- CMIO <-> Giam doc Tai khoan
- Xem xet 60 phut
- Thao luan chien luoc

**Hang thang sau trien khai**:
- Xem xet nhom day du
- Chi so hieu suat
- Cai tien lien tuc

**Hang quy sau trien khai**:
- Xem xet dieu hanh
- Phan tich ROI
- Lap ke hoach lo trinh

**Cam ket thoi gian uoc tinh**:

| Vai tro | Gio/tuan trong trien khai | Sau trien khai |
|---|---|---|
| Nha tai tro dieu hanh | 1 | <1 |
| CMIO | 5 | 2 |
| Chuyen gia lam sang | 5-10 | 2-3 |
| Truong CNTT | 10-15 | 2-5 |
| Tuan thu | 5 | 1-2 |
| Bac si nguoi dung cuoi | 0 (trong phat trien) | 0,5 (su dung he thong) |

---

### Q70. Chung toi co the tuy chinh he thong theo nhu cau cu the cua benh vien khong?

**A.** Co, nhieu cap do tuy chinh:

**Cap 1: Cau hinh** (khong co code)
- Cai dat theo khoa
- Tuy chon gion van (trang trong hon, tro chuyen hon)
- Muc do chi tiet (ngan gon vs toan dien)
- Dinh dang (dau dong vs van xuoi)
- Phong cach trich dan (noi tuyen vs cuoi)
- Ngon ngu (tieng Anh, tieng Trung, v.v.)
- Thuong hieu benh vien

**Chi phi**: Bao gom trong thiet lap tieu chuan
**Lich trinh**: 1-2 tuan

**Cap 2: Prompt tuy chinh** (it code)
- System prompt theo khoa
- Huong dan cu the cua benh vien
- Cac tinh chinh chuyen khoa

**Chi phi**: 5.000-10.000 USD thiet lap
**Lich trinh**: 2-3 tuan

**Cap 3: Quy trinh lam viec tuy chinh** (it code)
- Cac luong phe duyet cu the cua benh vien
- Cac quy tac dinh tuyen tuy chinh
- Xu ly dac biet cho cac dieu kien nhat dinh

**Chi phi**: 15.000-30.000 USD
**Lich trinh**: 4-6 tuan

**Cap 4: Tich hop tuy chinh** (code)
- Tich hop cac he thong cu the cua benh vien
- Nguon du lieu tuy chinh
- API benh vien

**Chi phi**: 40.000-100.000 USD
**Lich trinh**: 8-12 tuan

**Cap 5: Tinh nang tuy chinh** (code dang ke)
- Giao dien nguoi dung cu the cua benh vien
- Tinh nang chi danh cho benh vien
- Tuy chinh nang cao

**Chi phi**: 100.000-300.000 USD
**Lich trinh**: 6-9 thang

**Cac tuy chinh pho bien**:

**Cau hinh chuyen khoa**:
- Lieu luong dua tren can nang nhi khoa
- Cac can nhac lao khoa
- Cac quy tac an toan thai ky/cho con bu

**Boi canh dia phuong**:
- Danh muc thuoc cua benh vien
- Nhan thuoc Singapore
- Cac lua chon thuoc generic dia phuong

**Tich hop quy trinh lam viec**:
- SSO cu the cua benh vien
- Cac lo trinh phan loai tuy chinh
- Cac luong ban giao noi bo

**Bao cao tuy chinh**:
- Chi so cu the cua benh vien
- Bang dieu khien theo khoa
- Dinh dang bao cao tuan thu

**Danh doi**:

**Nhieu tuy chinh hon**:
- Phu hop hon voi benh vien
- Chi phi cao hon
- Trien khai lau hon
- Ganh nang bao tri nhieu hon

**It tuy chinh hon**:
- Nhanh hon, re hon
- Chat luong tieu chuan
- De nang cap hon
- Co the khong phu hop hoan hao

**Khuyen nghi**:
- Nam 1: tuy chinh toi thieu (Cap 1-2)
- Nam 2: xac dinh khoang trong, tuy chinh Cap 3
- Nam 3+: dua tren nhu cau duoc chung minh

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
