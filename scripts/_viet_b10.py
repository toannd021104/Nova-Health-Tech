import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 8. Du lieu & Nguon tri thuc

### Q71. AI lay kien thuc y te tu dau?

**A.** Nhieu nguon duoc giam tuyen:

**Nguon chinh**:
- **Huong dan WHO** (~300 tai lieu): huong dan song, giao thuc benh, cap nhat hang thang
- **API WHO ICD-11** (~120.000 thuc the): phan loai benh quoc te, cap nhat hang ngay
- **Bao cao thu nghiem noi bo** (cu the theo benh vien): du lieu thu nghiem da duoc an danh, giao thuc dieu tri
- **Giao thuc dieu tri** (cu the theo benh vien): SOP, tai lieu lo trinh, cong cu ho tro quyet dinh lam sang
- **PubMed E-utilities** (cong cu thoi gian chay): tim kiem PubMed theo thoi gian thuc, cac bai bao nghien cuu moi nhat

**Nguon tuy chon** (theo benh vien):
- Tich hop giay phep UpToDate (chi phi bo sung)
- Tich hop DynaMed
- Huong dan hoi chuyen khoa (ACC/AHA, ESC, v.v.)
- Tap chi cu the cua benh vien

**Nhung gi chung toi KHONG su dung**:
- Wikipedia (khong dang tin cay)
- Tim kiem internet chung (rui ro ao giac)
- Mang xa hoi benh nhan
- Tai lieu quang cao duoc phe duyet boi cong ty duoc pham (co the co thien vi)

**Kiem soat chat luong nguon**:
- Tat ca cac nguon duoc kiem tra boi hoi dong tu van lam sang
- Co so tham khao khi co the
- Cac to chuc co tham quyen duoc uu tien
- Tan suat cap nhat duoc theo doi

---

### Q72. Du lieu moi nhat la khi nao? Khi nao cap nhat gan nhat?

**A.** Nhip do cap nhat da nguon:

**Cap nhat hang ngay** (02:00 SGT): API WHO ICD-11 - phan anh cac ban phat hanh hang ngay cua WHO, trong vong 24 gio ke tu khi WHO xuat ban.

**Cap nhat hang thang + RSS**: PDF huong dan WHO - Dinh ky: Ngay 1 hang thang 02:30 SGT. Thoi gian thuc: thong bao RSS kich hoat nhap ngay lap tuc.

**Cap nhat hang tuan + webhook**: Bao cao thu nghiem noi bo - Dinh ky: Chu nhat 03:00 SGT. Thoi gian thuc: webhook SharePoint khi co file moi.

**Vo hieu hoa cache**: Khi KB duoc cap nhat, cac cau tra loi da cache lien quan duoc xoa tu dong. Vo hieu hoa dua tren the, chi xoa cac chunk phu hop.

**Hien thi tinh moi trong giao dien nguoi dung**:
- "Cap nhat [ngay]" tren moi trich dan
- Banner tren cac tai lieu cu (>ngay_xem_xet)
- AI co the canh bao: "Luu y: khuyen nghi nay co the loi thoi"

**So sanh voi cac lua chon thay the**:
- UpToDate: ~6 thang tre cho cac bai viet
- Sach giao khoa thu cong: 2-5 nam tre
- Bai bao tap chi truc tiep: thoi gian thuc nhung chua duoc xac minh

**Loi the cua chung toi**: Trong so nhanh nhat trong AI y te. Nguon goc co the xac minh. Vo hieu hoa tu dong.

---

### Q73. Chung toi co the them huong dan lam sang cua rieng minh vao co so kien thuc khong?

**A.** Co, duoc thiet ke cho dieu do.

**Nhung gi benh vien co the them**:
- Giao thuc cu the cua benh vien
- Cac bo lenh chuan
- Chinh sach quan ly khang sinh
- Cac giao thuc cai thien chat luong
- Cac tai lieu giang day
- Cac bien the dia phuong cua huong dan WHO/MOH

**Quy trinh tai len**:
1. Benh vien xuat PDF (da duoc an danh)
2. Gan the voi metadata (khoa, phien ban, ngay)
3. Tai len qua cong thong tin an toan hoac dong bo SharePoint
4. Phe duyet quy trinh lam viec (Giam doc Lam sang phe duyet)
5. Uu tien truy xuat duoc thiet lap
6. Co san trong vong 24 gio

**Cac loai tai lieu duoc ho tro**:
- PDF (pho bien nhat)
- Word/DOCX
- HTML
- Van ban thuan
- Markdown

**Yeu cau chat luong tai lieu**:
- Van ban co the tim kiem (khong phai hinh anh quet)
- Cau truc hop ly (tieu de, doan van)
- Noi dung chat luong (co tham khao khi co the)
- Ngay xuat ban ro rang

**Chi phi**: Tieu chuan: bao gom. Tuy chinh nang cao: 5.000-15.000 USD. Di cu hang loat: 10.000-30.000 USD.

---

### Q74. Dieu gi xay ra khi WHO cap nhat mot khuyen nghi?

**A.** Quy trinh toan dien de dam bao tinh moi:

**Phat hien**: Cac trang huong dan WHO duoc craw hang tuan. So sanh voi phien ban truoc. Canh bao khac biet den nhom tuan thu.

**Quy trinh cap nhat**:
`
1. Phat hien (tu dong): "WHO da cap nhat khuyen nghi corticosteroid COVID-19"
2. Phan loai (trong vong 4 gio): can bo an toan lam sang xem xet
3. Phan loai:
   a. Nho (loi chinh ta, dinh dang): uu tien thap, cap nhat theo lo
   b. Trung binh (thay doi thu tuc): xem xet tieu chuan va nhap
   c. Lon (thay doi khuyen nghi dieu tri): UU TIEN CAO
4. Nhap (trong vong 24 gio doi voi lon):
   a. Phan tich lai PDF WHO
   b. Phan khuc va nhung lai
   c. Cap nhat OpenSearch + Neptune
   d. Vo hieu hoa cache (chi nguon bi anh huong)
5. Giao tiep (trong vong 48 gio doi voi lon):
   a. Thong bao email den tat ca cac tenant benh vien
   b. Banner trong giao dien nguoi dung: "Cap nhat [ngay]: WHO da sua doi khuyen nghi"
   c. Cac cau tra loi truoc day bi anh huong duoc danh dau de danh gia lai
`

**Giai quyet xung dot** (vi du: WHO khong dong y voi MOH):
- AI hien thi ca hai voi ghi nhan
- Banner giai thich su khac biet
- Can bo an toan lam sang xem xet cac truong hop bien

**Chi phi**: Chi phi co so ha tang toi thieu (da duoc xay dung); ~10 gio/thang thoi gian can bo an toan lam sang.

---

### Q75. Dieu gi xay ra khi AI khong co thong tin ve mot truong hop cu the?

**A.** Tu choi trung thuc voi huong dan co ich.

**Cac mau tu choi**:

**Mau 1: KB thieu thong tin**:
> "Toi khong the tra loi dieu nay tu context hien tai. Co so kien thuc hien co khong chua thong tin cu the ve [chu de]. Cac tai nguyen duoc goi y: [danh sach cac lua chon thay the]."

**Mau 2: Cau hoi qua cu the**:
> "Toi khong co thong tin ve truong hop cu the nay. Cach tiep can chung cho cac truong hop tuong tu la [cach tiep can chung]. Doi voi benh nhan cu the: [khuyen nghi tu van chuyen khoa]."

**Mau 3: Chu de gan day khong co nhap**:
> "Day co ve la mot phat trien gan day. Huong dan moi nhat toi co la ngay [ngay]. De cap nhat moi nhat, tham khao [PubMed/UpToDate/hoi chuyen khoa]."

**Nhung gi AI KHONG lam**:
- Khong bịa dat cau tra loi
- Khong ngoai suy tu du lieu han che
- Khong xin loi qua muc
- Khong tuyen bo chuyen mon ma no khong co

**Ti le tu choi**: Muc tieu 5-10% (mot so tu choi la hanh vi chinh xac)
- <5%: AI co the qua tu tin
- >15%: Khoang trong KB dang ke

**Theo doi mo hinh**:
- Theo doi cac tu choi thuong xuyen
- Xac dinh khoang trong KB
- Them noi dung con thieu
- Cai tien lien tuc

---

## 9. Tich hop & Quy trinh lam viec

### Q76. AI tich hop voi EHR hien co cua chung toi nhu the nao?

**A.** Tich hop dua tren tieu chuan:

**Tich hop qua SMART on FHIR**:
- HL7 FHIR R4 (tieu chuan nganh)
- SMART App Launch v2 (xac thuc)
- OAuth 2.0 + OpenID Connect

**Ho tro EHR hien dai**:
- Epic: ho tro SMART day du tu 2018
- Cerner Millennium: ho tro SMART day du
- Allscripts: ho tro SMART tu 2020
- Oracle Health: ho tro SMART

**Luong ra mat**:
1. Bac si mo ho so benh nhan trong EHR
2. Click nut "Hoi Nova" (duoc nhung trong thanh ben hoac thanh nut EHR)
3. EHR khoi dong iframe voi context benh nhan
4. Tro ly AI tai trong iframe
5. Context benh nhan duoc chuyen an toan
6. Bac si dat cau hoi

**Pham vi du lieu**:
- Nhan khau hoc benh nhan (tuoi, gioi tinh)
- Chan doan hien tai
- Thuoc hien tai
- Sinh hieu/xet nghiem gan day
- Loai gap

**Bi loai tru theo mac dinh**:
- Lich su ho so day du
- Tien su gia dinh (tru khi duoc yeu cau)
- Ghi chu tu cac nha cung cap khac
- Du lieu thanh toan

**Chi phi tich hop**: EHR hien dai: 15.000-30.000 USD. EHR cu hon: 30.000-80.000 USD. EHR tuy chinh: 50.000-150.000 USD.

---

### Q77. Dieu gi xay ra neu EHR cua chung toi khong ho tro SMART on FHIR?

**A.** Cac con duong tich hop thay the:

**Con duong 1: Nhan tin HL7 v2**
- Tieu chuan cu hon, hau het EHR cu ho tro
- Tich hop dua tren tin nhan theo thoi gian thuc
- Trien khai phuc tap hon
- Chi phi: 30.000-80.000 USD

**Con duong 2: Tich hop co so du lieu**
- Doc truc tiep co so du lieu EHR
- Cu the theo nha cung cap (Epic CCDR, v.v.)
- Yeu cau thoa thuan nha cung cap
- Chi phi: 50.000-150.000 USD

**Con duong 3: API tuy chinh**
- Xay dung bo chuyen doi cho API doc quyen cua EHR
- Yeu cau tai lieu nha cung cap
- Cong viec tuy chinh moi EHR
- Chi phi: 80.000-200.000 USD

**Con duong 4: Su dung doc lap**
- Bac si nhap context thu cong
- AI duoc su dung khong co tich hop EHR
- It tien loi hon nhung co chuc nang
- Khong co chi phi bo sung

**Con duong 5: HL7 FHIR + Mirth Connect**
- Cau noi nguon mo
- Chuyen doi HL7 v2 -> FHIR
- Middleware tu luu tru
- Chi phi: 20.000-50.000 USD

**Khuyen nghi theo EHR**:
- EHR hien dai: Dung SMART on FHIR (tieu chuan)
- EHR cu hon: HL7 v2 + cau noi Mirth Connect
- EHR tuy chinh: Su dung doc lap ban dau, lap ke hoach di cu sang EHR dua tren tieu chuan theo thoi gian

---

### Q78. AI co truy cap vao tat ca du lieu benh nhan cua chung toi khong?

**A.** Han che va co kiem soat:

**Truy cap mac dinh**:
- Chi du lieu bac si chia se trong truy van
- Qua context ra mat EHR
- Cu the cho lan kham hien tai

**Truy cap theo yeu cau** (voi su dong y):
- Ghi chu gap gan day
- Gia tri xet nghiem cu the
- Thuoc hien tai
- Di ung va chong chi dinh

**Yeu cau su dong y**:
- Moi truy van cho du lieu cu the
- Hoac: su dong y toan cau moi phien
- Duoc ghi lai trong nhat ky kiem toan

**Nguyen tac giam thieu du lieu**:
- Chi su dung nhung gi can thiet
- Loai bo sau khi su dung
- Xem xet luu giu dinh ky

**Phan quyen theo bac si**:
- Giong nhu quyen truy cap EHR cua ho
- AI khong the vuot qua quyen cua bac si
- Ke thua tu EHR

**Cach ly moi tenant**:
- Du lieu Benh vien A: chi co the truy cap tai Benh vien A
- Chia se xuyen benh vien: yeu cau su dong y + NEHR-Pro

---

### Q79. Bac si dieu duong hoac cac vai tro lam sang khac co the su dung he thong nay khong?

**A.** Truy cap va tuy chinh dua tren vai tro:

**Vai tro bac si tieu chuan**:
- Ho tro quyet dinh lam sang day du
- Goi y chan doan
- Khuyen nghi dieu tri
- Lieu luong thuoc
- Hau het cac truong hop su dung

**Vai tro dieu duong** (co the cau hinh):
- Cac truy van cham soc tai giuong
- Cac cau hoi quan ly thuoc
- Giao thuc cham soc vet thuong
- Tai lieu giao duc benh nhan

**Vai tro duoc si**:
- Tuong tac thuoc
- Xac minh lieu luong
- Cac lua chon thay the trong danh muc thuoc
- Cac quyet dinh duoc ly lam sang

**Cac vai tro y te lien minh** (co the cau hinh):
- Vat ly tri lieu: giao thuc phuc hoi
- Dinh duong: huong dan dinh duong
- Cong tac xa hoi: tai nguyen xuat vien

**Cau hinh theo vai tro**:
- System prompt theo vai tro
- Quyen truy cap du lieu theo vai tro
- Guardrails theo vai tro
- Dinh dang dau ra theo vai tro

**Chi phi moi vai tro bo sung**: Cau hinh: 5.000-15.000 USD. Dao tao tuy chinh: 5.000-10.000 USD. Tuy chinh giao dien nguoi dung: 10.000-30.000 USD.

---

### Q80. Bac si co the su dung nhap bang giong noi khong?

**A.** Co, nhap bang giong noi duoc ho tro:

**Cong nghe nhap bang giong noi**:
- AWS Transcribe / Alibaba Speech
- Phien am theo thoi gian thuc
- Duoc dao tao voi thuat ngu y te
- Da ngon ngu

**Hieu suat theo ngon ngu**:
- Tieng Anh: tot nhat (nhieu du lieu dao tao nhat)
- Tieng Trung: rat tot
- Tieng Malay: tot
- Tieng Tamil: han che nhung co chuc nang
- ASEAN khac: thay doi

**Cac truong hop su dung thich hop voi giong noi**:
- Trong khi kham benh nhan (ranh tay)
- Cac cau hoi nhanh
- Theo doi trong khi di chuyen
- Di chuyen giua cac phong

**Cac truong hop su dung thich hop voi go phim**:
- Cac kich ban lam sang chi tiet
- Nhieu tham so
- Chan doan phan biet phuc tap
- Khi co lo ngai ve quyen rieng tu (nguoi khac o gan)

**Quyen rieng tu voi giong noi**:
- Am thanh khong duoc luu tru theo mac dinh
- Chi van ban duoc phien am
- Cung bao ve PHI nhu nhap van ban
- Nhat ky kiem toan o dang van ban

**Chi phi**: Phien am giong noi: ~0,006 USD/phut. Cho truy van dien hinh (30 giay): ~0,003 USD. Chi phi khong dang ke.

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
