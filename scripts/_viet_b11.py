import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 10. Trai nghiem nguoi dung

### Q81. Bac si thuc su thay gi tren man hinh khi su dung AI?

**A.** Giao dien sach se, tap trung:

**Cac yeu to giao dien chinh**:
- **Khu vuc nhap chat**: hop van ban cau hoi, tuy chon nhap bang giong noi, nut dinh kem hinh anh (cho X-quang), chuyen doi cap cuu
- **Lich su cuoc tro chuyen**: Q&A truoc do trong phien, click de mo rong bat ky cau tra loi nao, di chuot qua trich dan
- **Hien thi cau tra loi**: phan hoi streaming (tung tu mot), trich dan noi tuyen [1] [2] [3], di chuot de xem truoc nguon, click de mo rong nguon day du
- **Khu vuc hanh dong**: thumbs up/down, tuy chon phan hoi chi tiet, sao chep van ban vao clipboard, chia se voi dong nghiep (trong benh vien)
- **Thanh trang thai**: chi bao lane (Cap cuu/Phuc tap), thoi gian phan hoi, dinh tuyen khoa, so luong trich dan

**Cac nguyen tac UX chinh**:
- **Phan hoi streaming**: tu dau tien xuat hien <2 giay, cac tu xuat hien tu nhien, bat dau doc ngay lap tuc
- **Minh bach nguon**: trich dan luon hien thi, mot click den nguon, ngay nguon noi bat
- **It ma sat**: truy cap mot click tu EHR, context benh nhan duoc dien san, cac truy van pho bien truy cap nhanh

**Trai nghiem di dong**: Thiet ke dap ung, toi uu hoa cam ung, nhap bang giong noi noi bat, giao dien duoc giam luoc.

---

### Q82. Bac si co can dao tao dac biet de su dung he thong nay khong?

**A.** Toi thieu:

**Tong quan onboarding**:
- Huong dan tu phuc vu: 15 phut
- Phien nhom tuy chon: 30 phut
- 1:1 tuy chon: 15-20 phut moi nguoi

**Dinh dang dao tao**:
1. **Huong dan trong ung dung**: 3 trang tuong tac, cac cau hoi va cau tra loi demo, cac mo hinh pho bien
2. **The tham khao nhanh**: 1 trang co the in, cac truy van pho bien, meo de co ket qua tot nhat
3. **Video huong dan** (tuy chon): tong quan 5 phut, demo cac tinh nang pho bien, thuc hanh tot nhat
4. **Phien demo truc tiep** (tuy chon): phien nhom, thuc hanh thuc te, Q&A
5. **Khac phuc su co 1:1** (tuy chon): co san 4 tuan dau, ~10-20% bac si su dung

**Duong cong nang luc du kien**:
- Tuan 1: 80% bac si thoai mai
- Tuan 2: 95% bac si thanh thao
- Tuan 4: 99% bac si thuan thuc

**So sanh voi cac cong cu lam sang khac**:
- Dao tao Epic: 8-40 gio
- Cac cong cu DSS: 2-8 gio
- Tro ly AI cua chung toi: <1 gio
- Ly do: UX tuong tu ChatGPT, quen thuoc

---

### Q83. Bac si co the co cuoc tro chuyen rieng tu hoac chi su dung cho cac truy van chung?

**A.** Cac che do khac nhau:

**Che do 1: Truy van tieu chuan**
- Cau hoi don le
- AI phan hoi
- Khong co bo nho giua cac truy van

**Che do 2: Cuoc tro chuyen nhieu luot**
- Cung phien
- AI nho context
- Bo nho mac dinh 6 luot
- Vuot qua: context duoc tom tat

**Che do 3: Phien cu the cho benh nhan**
- Gan voi lan kham benh nhan
- Tat ca cac truy van ve cung benh nhan
- Lien tuc trong suot lan kham
- Quyen rieng tu duoc duy tri (PHI duoc token hoa)

**Che do 4: Ghi chu ca nhan**
- Su dung ca nhan cua bac si
- "Giup toi suy nghi qua truong hop nay"
- AI nhu doi tac suy nghi
- Kham pha hon

**Quyen rieng tu cuoc tro chuyen**:
- Tat ca cac che do: PHI duoc che giau truoc AI
- Nhat ky kiem toan: duoc ma hoa, an toan
- Cac cuoc tro chuyen khong duoc chia se giua cac bac si
- Tong hop cap khoa chi

**Luu giu phien**:
- Phien hoat dong: du lieu truc tiep
- Phien gan day: luu tru nong 30 ngay
- Phien cu hon: luu tru 6 nam (kiem toan)
- Tuy chon ca nhan: co the cau hinh

---

### Q84. Bac si co the su dung AI de hoc tap lien tuc khong?

**A.** Duoc ho tro nhu truong hop su dung thu cap:

**Cac truong hop su dung giao duc**:
- **Nghien cuu truong hop**: "Huong dan toi qua chan doan phan biet cho [bieu hien]"
- **Huong dan moi nhat**: "Nhung gi da thay doi trong huong dan ACC/AHA moi?"
- **Ly luan lam sang**: "Tai sao dieu tri nay duoc uu tien hon dieu tri kia?"
- **Kien thuc thuoc**: "Co che tac dung cua [thuoc]"
- **Kham pha chuyen khoa**: "Chuyen gia se suy nghi ve truong hop nay nhu the nao?"

**Tinh nang che do giao duc**:
- Phan hoi chi tiet hon so voi che do lam sang
- Nhieu thong tin nen
- Nhieu trich dan hon
- Thao luan ve cac lua chon thay the

**Chuoi ly luan**:
- Ly luan ro rang duoc hien thi
- "Vi X, do do Y"
- Gia tri giao duc cao

**Cau hoi thuc hanh**:
- "Kiem tra toi ve [chu de]"
- AI tao cac cau hoi thuc hanh
- Hoc tu danh gia

**Phan tich CME**:
- Viec su dung AI co the tinh vao CME (SMC Singapore)
- Benh vien co the cau hinh nhu hoat dong CME
- Tai lieu duoc cung cap

**Chi phi**: Khong co chi phi bo sung (su dung cung co so ha tang). Cung gia. Khong tinh phi cho viec su dung giao duc.

---

### Q85. He thong co ung dung di dong khong?

**A.** Web-first, than thien voi di dong:

**Phuong phap hien tai**:
- Thiet ke web dap ung
- Hoat dong tren trinh duyet di dong
- Giao dien duoc toi uu hoa cam ung

**Su dung di dong**:
- Dien thoai thong minh: day du chuc nang
- May tinh bang: trai nghiem nang cao
- Dua tren trinh duyet: khong can cai dat ung dung

**Tinh nang cu the cho di dong**:
- Nhap bang giong noi noi bat
- Truy cap nhanh cac truy van pho bien
- Giao dien duoc giam luoc
- Cache ngoai tuyen cho cac cau tra loi gan day

**Ung dung ban de** (tuong lai):
- Ung dung iOS: lo trinh
- Ung dung Android: lo trinh
- Tich hop tot hon voi tinh nang dien thoai
- Thong bao day

**Chi phi phat trien ung dung**:
- iOS ban de: 80.000-150.000 USD
- Android ban de: 80.000-150.000 USD
- Bao tri: 30.000-60.000 USD/nam moi nen

**Khuyen nghi**:
- Nam 1: chi web
- Nam 2: Progressive Web App (UX di dong tot hon)
- Nam 3: Ung dung ban de neu nhu cau manh

---

## 11. Nha cung cap & Ho tro

### Q86. Nhom ho tro cua Nova trong nhu the nao?

**A.** Cau truc ho tro nhieu lop:

**Cap 1: Tu phuc vu**
- Cong thong tin tai lieu
- Video huong dan
- Co so du lieu FAQ
- Co so kien thuc
- Co san 24/7

**Cap 2: Ho tro email/chat**
- Gio tieu chuan: 9 SA - 6 CH SGT
- Phan hoi: <4 gio
- Giai quyet: <24 gio dien hinh
- Cac truong hop su dung: cau hoi cach lam, cau hinh

**Cap 3: Ho tro dien thoai**
- Gio lam viec: 8 SA - 8 CH SGT
- Phan hoi: <30 phut
- Cac truong hop su dung: cac van de quan trong, leo thang

**Cap 4: Ho tro khan cap 24/7**
- Co san luc nao cung
- Phan hoi: <15 phut
- Cac truong hop su dung: ngung hoat dong SEV-1, su co bao mat

**Cac vai tro**:
- **Quan ly Thanh cong Khach hang (CSM)**: quan he moi tenant, xem xet hang quy, huong dan chien luoc, toi uu hoa chi phi
- **Quan ly Tai khoan Ky thuat (TAM)**: lien lac ky thuat, xem xet kien truc, huong dan thuc hanh tot nhat, leo thang van de
- **Ky su Ho tro**: ho tro hang ngay, khac phuc su co ky thuat, tro giup cau hinh, bao cao loi
- **SRE Truc ban**: do tin cay 24/7, ung pho su co, suc khoe he thong, cac van de hieu suat
- **Tu van Lam sang**: cac cau hoi lam sang, huong dan tuan thu, phat trien chuyen mon

**Chi phi**:
- Ho tro tieu chuan: bao gom
- Ho tro cao cap: 20.000-40.000 USD/nam
- Ho tro doanh nghiep: 50.000-100.000 USD/nam

---

### Q87. Chung toi co the nhan duoc lien he ky thuat chuyen dung khong?

**A.** Co, nhieu tuy chon:

**Dich vu tieu chuan**:
- Nhom ho tro dung chung
- Phan cong theo vong
- Du cho hau het nhu cau

**Dich vu cao cap** (chi phi bo sung):
- TAM chuyen dung (Quan ly Tai khoan Ky thuat)
- CSM chuyen dung (Quan ly Thanh cong Khach hang)
- Duong day truc tiep
- Xem xet hang quy

**Dich vu doanh nghiep**:
- Nhom chuyen dung
- Bao phu 24/7 chuyen dung
- Ho tro nhung
- Tham gia chien luoc

**So sanh cap dich vu**:

| Tinh nang | Tieu chuan | Cao cap | Doanh nghiep |
|---|---|---|---|
| TAM | Dung chung | Chuyen dung | Chuyen dung |
| CSM | Dung chung | Chuyen dung | Chuyen dung |
| Thoi gian phan hoi | Tieu chuan | Nhanh hon | Nhanh nhat |
| Lien he truc tiep | Khong | TAM + CSM | Nhom day du |
| Xem xet | Hang nam | Hang quy | Hang thang |
| Chi phi | Bao gom | 20-40k/nam | 50-100k/nam |

**Khuyen nghi**:
- Benh vien nho: ho tro tieu chuan
- Benh vien vua: dang xem xet cao cap
- Benh vien lon/he thong: doanh nghiep

---

### Q88. Nova cung cap loai dao tao va onboarding nao?

**A.** Chuong trinh toan dien:

**Dao tao truoc khi trien khai**:
1. **Hoi thao khoi dong trien khai** (1 ngay): tong quan du an, phu hop cac ben lien quan, tieu chi thanh cong, xac dinh rui ro. Chi phi: bao gom.
2. **Nghien cuu sau ve kien truc** (1 ngay): nhom CNTT benh vien, hieu biet ky thuat, lap ke hoach tich hop. Chi phi: bao gom.
3. **Briefing bao mat & tuan thu** (nua ngay): nhom tuan thu benh vien, huong dan chi tiet, xem xet tai lieu. Chi phi: bao gom.
4. **Hoi thao cau hinh lam sang** (1 ngay): truong khoa, cac quyet dinh tuy chinh, tuy chon chuyen khoa. Chi phi: bao gom.

**Dao tao trien khai**:
5. **Dao tao bac si chuyen gia** (4 gio trong 2 tuan): cac bac si duoc chon (chuyen gia lam sang), dao tao thuc hanh, thuc hanh tot nhat. Chi phi: bao gom.
6. **Dao tao nguoi dung cuoi** (1-2 gio moi bac si): huong dan tu phuc vu, cac phien nhom tuy chon, 1:1 tuy chon. Chi phi: bao gom.
7. **Dinh huong truong khoa** (2 gio): dao tao cu the theo khoa, tong quan cau hinh, giam sat chat luong. Chi phi: bao gom.

**Dao tao lien tuc**:
8. **Ban tin hang thang** (doc 15 phut): tinh nang moi, thuc hanh tot nhat, meo va thu thuat. Chi phi: bao gom.
9. **Hoi thao web hang quy** (1 gio): nghien cuu sau ve cac chu de, thong bao tinh nang moi, Q&A voi nhom san pham. Chi phi: bao gom.
10. **Hoi nghi nguoi dung hang nam** (2 ngay): cung cap cao cap, ket noi voi dong nghiep, hoi thao thuc hanh, noi dung chien luoc. Chi phi: 1.500-3.000 USD moi nguoi tham du.
11. **Cac phien dao tao tuy chinh** (theo yeu cau): cu the theo khoa, cu the theo sang kien moi, tap trung vao chuyen khoa. Chi phi: 5.000-15.000 USD moi phien.

---

### Q89. Chung toi co the anh huong den lo trinh san pham khong?

**A.** Nhieu kenh dau vao:

**Hoi dong tu van khach hang**:
- Cac cuoc hop hang quy
- Cac benh vien hang dau duoc dai dien
- Dau vao chien luoc
- Xem truoc lo trinh
- Bieu quyet ve uu tien

**He thong yeu cau tinh nang**:
- Nop qua cong thong tin
- Bieu quyet cho cac yeu cau cua nguoi khac
- Lo trinh cong khai (cap cao)
- Cap nhat trang thai

**Hoi dong tu van lam sang**:
- Cac lanh dao lam sang tu khach hang
- Uu tien lam sang
- Nhu cau chuyen khoa
- Co hoi nghien cuu

**Chuong trinh beta**:
- Truy cap som vao cac tinh nang
- Cung cap phan hoi truoc GA
- Hinh thanh thiet ke cuoi cung
- Duoc cong nhan trong san pham

**Tham gia truc tiep**:
- TAM/CSM chuyen tiep dau vao
- Uu tien quan ly tai khoan
- Cac cuoc thao luan chien luoc
- Cac tinh nang tuy chinh cho khach hang quan trong

**Muc do anh huong**:
- **Rat co anh huong** (top 10 khach hang): duong day truc tiep den nhom san pham, cac tinh nang tuy chinh duoc tai tro, trong luong bieu quyet lo trinh, bao tro dieu hanh
- **Co anh huong vua** (30 khach hang tiep theo): kiem tra hang quy, dau vao lo trinh, truy cap beta, ho tro tieu chuan
- **Khach hang tieu chuan**: dau vao ban tin, tham gia khao sat, phan hoi cong khai, bieu quyet

---

### Q90. Lich su theo doi cua Nova la gi? Day co phai la cong ty on dinh khong?

**A.** Cau hoi tham dinh quan trong.

**Nen tang cong ty**:
- Co tru so tai Singapore
- Tap trung vao cong nghe cham soc suc khoe
- Duoc thanh lap boi cac lanh dao lam sang va ky thuat
- Duoc ho tro boi cac nha dau tu co uy tin

**Chi so on dinh**:
- Tai chinh: duoc tai tro cho 24+ thang runway
- Mo hinh doanh thu dinh ky
- Nhieu vong tai tro Series
- Phuong phap tang truong bao thu

**Co so khach hang**:
- 5+ tenant benh vien tai Singapore
- 50+ benh vien quoc te (duoc lap ke hoach/hoat dong)
- Ti le giu chan 95%+
- Khach hang tham khao co san

**Doi ngu**:
- 50+ nhan vien
- Lanh dao cap cao: 10+ nam kinh nghiem nganh
- Tu van lam sang: cac bac si dang hanh nghe
- Ky thuat: nhan tai hang dau

**Xac nhan nganh**:
- Thanh vien Hoi dong AI Verify
- Doi tac IMDA
- Da dang ky HSA
- Thanh vien lien minh cham soc suc khoe

**Kich ban that bai va bien phap bao ve**:
- **Neu Nova gap van de tai chinh**: AWS/Alibaba tiep tuc chay co so ha tang; benh vien co the tu chay (voi ky quy code); thong bao 90 ngay.
- **Neu Nova bi mua lai**: tiep tuc duoc bao dam boi ben mua lai; cac dieu khoan hop dong tieu chuan ap dung; benh vien giu quyen.
- **Neu Nova ngung hoat dong**: thoa thuan ky quy code (duoc khuyen nghi); cac thanh phan nguon mo; AWS/Alibaba se duy tri; di cu sang nha cung cap thay the.

**Tham dinh duoc khuyen nghi**:
1. Xem xet tai chinh Nova (duoc bao ve boi NDA)
2. Kiem tra tham khao voi cac khach hang hien tai
3. Xem xet kien truc ky thuat
4. Xem xet tai lieu tuan thu
5. Thao luan lo trinh

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
