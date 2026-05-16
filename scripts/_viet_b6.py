import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 4. Bao mat & Quyen rieng tu

### Q51. Dieu gi xay ra khi mot bac si hoi AI ve mot benh nhan cu the?

**A.** Tung buoc bang ngon ngu don gian:

**Thiet lap**: Bac si Linh dang xem xet ho so benh nhan Nguyen Van A trong Epic. Benh nhan bi dau nguc, nghi ngo NMCT.

**Buoc 1: Bac si go cau hoi**
- Bac si Linh click nut "Hoi Nova" trong Epic
- Go: "Benh nhan Nguyen Van A, nam 58 tuoi, dau nguc, ECG cho thay ST elevation. Cac lua chon dieu tri?"
- Nhan Enter

**Buoc 2: Xac thuc & uy quyen**
- Trinh duyet gui cau hoi den cong API voi JWT cua Bac si Linh (duoc phat hanh boi IdP cua Epic qua lien ket Cognito)
- Cong API xac minh: Bac si Linh co duoc uy quyen khong? Co (vai tro bac si)
- Dinh tuyen den trinh xu ly chat Nova

**Buoc 3: Che giau PHI** (trong vong 50ms)
- Trinh xu ly chat Nova nhan: "Benh nhan Nguyen Van A, nam 58 tuoi..."
- Comprehend Medical / DataWorks SDDP quet PHI
- Phat hien: "Nguyen Van A" -> thay the bang <TEN_0>
- Van ban moi: "Benh nhan <TEN_0>, nam 58 tuoi, dau nguc, ECG cho thay ST elevation."

**Buoc 4: Kiem tra cache** (trong vong 50ms)
- Bam cau hoi da che giau
- Kiem tra ElastiCache Redis: co truy van tuong tu truoc do khong?
- Cau hoi pho bien (STEMI la thuong gap): co the co cache hit
- Gia su bo lo: tiep tuc truy xuat

**Buoc 5: Truy xuat** (trong vong 1 giay)
- Tim kiem vector tren OpenSearch: tim cac chunk tuong tu "STEMI ST elevation dau nguc dieu tri"
- Top 3 ket qua: huong dan cap cuu tim mach WHO, giao thuc tim mach noi bo, cap nhat ACC/AHA STEMI 2023
- Tim kiem do thi tren Neptune: tim cac thuc the lien quan (thuoc, chong chi dinh, thu thuat)
- Top 2 ket qua do thi: giao thuc aspirin + heparin, PCI chinh vs tieu huyet khoi

**Buoc 6: Tao LLM** (TTFT trong vong 1 giay, tong 3 giay)
- Soan prompt: system prompt + cac chunk duoc truy xuat + cau hoi da che giau
- Gui den Claude Haiku 4.5 (lane cap cuu) qua API streaming
- Nhan cac token streaming: "Khan cap thoi gian..."
- Tung tu, phan hoi xuat hien trong giao dien nguoi dung cua Bac si Linh

**Buoc 7: Xac thuc** (trong vong 100ms)
- Xac thuc trich dan: moi [1], [2] trich dan cac chunk thuc su? Co
- Diem grounding: duoc tinh la 0,91 (tren nguong 0,7) Co
- Bo loc PHI: co PHI nao trong dau ra khong? Khong (chung toi khong bao gio gui PHI den mo hinh) Co

**Buoc 8: Hien thi cho bac si**
- Bac si Linh thay: "Khan cap thoi gian: Benh nhan STEMI. Khuyen nghi:..."
- Trich dan [1], [2], [3] co the click den cac chunk nguon
- Tong thoi gian da qua: ~3,8 giay

**Buoc 9: Nhat ky kiem toan** (song song, khong dong bo)
- Ghi lai phien: ai hoi, khi nao, cai gi duoc hoi (da che giau), cai gi duoc truy xuat, cai gi duoc tra loi
- Luu tru trong S3 Object Lock / OSS WORM, bat bien trong 6 nam

**Tom tat quyen rieng tu**:
- Ten benh nhan "Nguyen Van A" da duoc che giau truoc bat ky xu ly mo hinh nao
- Dich vu LLM Anthropic / Alibaba KHONG BAO GIO thay "Nguyen Van A"
- Nhat ky kiem toan hien thi <TEN_0> khong phai ten that
- Neu kiem toan duoc xem xet, ten that chi duoc tiet lo qua quy trinh tai nhan dang rieng biet, co han che cao

---

### Q52. Neu mot hacker xam nhap vao tai khoan dam may cua chung toi va co gang tai xuong tat ca du lieu thi sao?

**A.** Nhieu lop phong thu:

**Lop 1: Kiem soat truy cap tai khoan**
- Tai khoan root AWS/Alibaba: MFA phan cung, khong bao gio duoc su dung truc tiep
- Nguoi dung IAM voi truy cap dua tren vai tro
- Lien ket voi Entra ID cua Nova (xac thuc tap trung)
- Khong co khoa API ton tai lau; chi co token STS ngan han

**Lop 2: Kiem soat mang**
- Cach ly VPC: cac dich vu du lieu khong the truy cap internet
- Nhom bao mat: mac dinh tu choi, danh sach cho phep ro rang
- Diem cuoi VPC: cac dich vu duoc truy cap qua PrivateLink, khong phai internet cong cong
- Egress cong NAT: chi den cac IP cu the

**Lop 3: Ma hoa**
- Du lieu luu tru: KMS BYOK (benh vien co the thu hoi khoa)
- Du lieu trong qua trinh truyen: TLS 1.3
- Sao luu duoc ma hoa voi khoa rieng biet
- Xoay vong khoa: 90 ngay

**Lop 4: Kiem toan & Phat hien**
- CloudTrail: moi cuoc goi API duoc ghi lai
- GuardDuty: phat hien bat thuong (cac mo hinh API bat thuong)
- Macie: phat hien PHI trong S3 (canh bao neu PHI di chuyen den bucket cong cong)
- ARMS LLM Trace Explorer: cac mo hinh cuoc goi AI

**Lop 5: Sao luu / Bat bien**
- S3 Object Lock: nhat ky kiem toan bat bien trong 6 nam
- Khong the xoa ngay ca boi quan tri vien Nova
- Sao chep xuyen vung

**Lop 6: Bao ve moi de doa noi bo**
- Khong co quan tri vien Nova don le nao co quyen truy cap day du (phan cong trach nhiem)
- Quy tac hai nguoi cho truy cap du lieu san xuat
- Cong cu Quan ly Truy cap Dac quyen (PAM)
- Xem xet truy cap hang quy

**Kich ban xau nhat**:
- Tin tac xam pham tai khoan AWS san xuat cua Nova
- Tai xuong tat ca bucket S3 va chi muc OpenSearch
- Ket qua: IP Nova bi lo (kien truc he thong, prompt), nhung **KHONG CO PHI BENH NHAN BI LO**
- Nova doi mat voi thiet hai danh tieng kinh doanh va co the thong bao khach hang
- Benh nhan KHONG the duoc nhan dang tu du lieu vi pham

**Tai sao kien truc cua chung toi chong vi pham tot hon**:
- Token hoa tai thoi diem nhap (PHI khong bao gio duoc luu tru vinh vien)
- Tach biet kho anh xa
- Phong thu theo chieu sau
- Mac dinh tu choi mang

---

### Q53. Kich ban vi pham xau nhat la gi? Co ai co the danh cap du lieu benh nhan khong?

**A.** Phan tich theo danh muc du lieu:

**Du lieu chung toi luu giu**:
1. **Nhat ky kiem toan** (da token hoa, khong co PHI)
2. **Nhung** (bieu dien toan hoc, khong phai van ban)
3. **Cac chunk cua WHO/ICD-11** (du lieu cong cong du sao)
4. **Bao cao thu nghiem noi bo** (nhay cam, nhung da duoc an danh)
5. **Du lieu cau hinh** (cai dat he thong)

**Du lieu chung toi KHONG luu giu** (sau khi che giau PHI):
- Ten benh nhan
- MRN
- So NRIC/FIN
- Ngay sinh
- So dien thoai
- Dia chi email

**Muc do nghiem trong vi pham theo loai du lieu**:

| Du lieu | Muc do nghiem trong vi pham | Tin tac co the lam gi |
|---|---|---|
| Nhat ky kiem toan (da token hoa) | Thap | Cac mo hinh thong ke, khong co PHI |
| Nhung | Rat thap | Cac vector toan hoc, khong the dao nguoc thanh van ban |
| Cac chunk tri thuc | Khong co | Du lieu cong cong |
| Bao cao thu nghiem (da an danh) | Trung binh | Chi tiet thu nghiem, khong nhan dang benh nhan |
| Cau hinh | Thap | Kien thuc kien truc he thong |
| Khoa KMS | Nghiem trong (nhung can xam pham rieng biet) | Co the giai ma neu cac lop khac cung bi xam pham |

**Dao nguoc token hoa**:
- Bang anh xa tu token tro lai PHI nam trong kho rieng biet, co han che cao
- Truy cap kho yeu cau phe duyet hai nguoi dac biet
- Kho KHONG the truy cap tu cac he thong san xuat bi xam pham
- Ngay ca khi tin tac co du lieu san xuat + nhat ky kiem toan, ho khong the lay ten benh nhan cho den khi pha vo kho rieng biet

**Kich ban xau nhat thuc te**:
- Tin tac xam pham tai khoan san xuat AWS cua Nova
- Tai xuong tat ca bucket S3 va chi muc OpenSearch
- Ket qua: IP Nova bi lo (kien truc he thong, prompt), nhung **KHONG CO PHI BENH NHAN BI LO**
- Nova doi mat voi thiet hai danh tieng kinh doanh va co the thong bao khach hang
- Benh nhan KHONG the duoc nhan dang tu du lieu vi pham

**So sanh voi vi pham dien hinh**:
- SingHealth 2018: ~1,5 trieu ho so benh nhan, PHI day du bi lo (vi pham cap may chu)
- Singtel 2022: Du lieu khach hang bao gom thong tin nhan dang
- Kien truc nay: ngay ca khi toan bo he thong bi xam pham, khong co PHI bi lo

**Rui ro dinh luong**:
- Xac suat xam pham tai khoan day du: <0,1% moi nam (co so nganh cho dam may duoc bao mat tot)
- Thiet hai trong truong hop xau nhat: han che (khong co PHI bi lo)
- Bao hiem bao gom: 5-10 trieu USD (du cho cac kich ban co the xay ra)

---

### Q54. Giai thich cac thuc hanh ma hoa cua chung toi bang ngon ngu don gian.

**A.** Ba loai ma hoa:

**1. Ma hoa luu tru (khi du lieu duoc luu tru)**
- Giong nhu ket an tai ngan hang: du lieu bi khoa trong cac tep duoc ma hoa tren dia
- Ngay ca khi ai do danh cap o cung, ho khong the doc du lieu ma khong co khoa
- Duoc thuc hien boi: AWS KMS / Alibaba KMS

**2. Ma hoa trong qua trinh truyen (khi du lieu di chuyen)**
- Giong nhu phong bi kin: du lieu duoc ma hoa trong khi di chuyen giua cac he thong
- Ngay ca khi ai do nghe trom cap mang, ho chi thay ky tu vo nghia
- Duoc thuc hien boi: TLS 1.3 (HTTPS hien dai)

**3. Ma hoa trong khi su dung (trong khi xu ly)**
- Kho nhat trong ba loai: du lieu can duoc giai ma de xu ly
- Duoc giam thieu boi: thoi gian giai ma toi thieu, bo nho quy trinh co lap, mo-dun bao mat phan cung

**Quan ly khoa**:

**Khoa la gi?** Mot chuoi ngau nhien dai khoa/mo khoa du lieu duoc ma hoa.

**BYOK (Mang Khoa Cua Rieng Ban)**:
- Benh vien tao khoa ma hoa trong tai khoan AWS/Alibaba cua rieng ho
- Chia se voi dich vu ma hoa cua Nova
- Benh vien co the thu hoi bat ky luc nao -> ngay lap tuc ngan Nova truy cap du lieu
- Cung cap cho benh vien quyen kiem soat toi thuong

**Xoay vong khoa**:
- Khoa moi duoc tao moi 90 ngay
- Du lieu cu duoc ma hoa lai voi khoa moi
- Cac khoa cu duoc giu lai de giai ma sao luu (cung duoc xoay vong)

**Nhat ky truy cap khoa**:
- Moi lan su dung khoa duoc ghi lai
- "Ai giai ma cai gi, khi nao"
- Duong dan ho tro kiem toan tuan thu

**Vi du thuc te**:
Tuong tuong ket an ngan hang:
- Ma hoa = cac buc tuong thep va cua
- Khoa = ma so ket hop
- Nhat ky kiem toan = camera ghi lai moi lan vao

Trong he thong cua chung toi:
- AWS KMS / Alibaba KMS = nha cung cap ket an
- BYOK = benh vien so huu ma so ket hop
- CloudTrail / ActionTrail = camera

Neu ke cuop danh cap ket an: van bi khoa.
Neu ke cuop lay duoc ma so: camera cho thay chung vao.
Neu benh vien thay doi ma so: Nova khong the vao cho den khi duoc dat lai.

---

### Q55. Token hoa PHI la gi va tai sao no tot hon chi ma hoa?

**A.** Su khac biet quan trong:

**Ma hoa**: Du lieu bi xao tron toan hoc voi mot khoa. Voi khoa, ban co the phuc hoi ban goc.

**Token hoa**: Du lieu duoc thay the bang mot token ngau nhien. Khong co bang anh xa rieng biet, ban khong the phuc hoi ban goc.

**Vi du voi ten benh nhan**:

**Phuong phap ma hoa**:
`
Goc: "Nguyen Van A"
Da ma hoa: "x7K9pQ2..." (phu thuoc vao khoa)
Voi khoa: co the phuc hoi thanh "Nguyen Van A"
`

**Phuong phap token hoa**:
`
Goc: "Nguyen Van A"
Token: "<TEN_BENH_NHAN_001>"
Bang anh xa (he thong rieng biet): {001: "Nguyen Van A"}
Khong co bang anh xa: token khong the dao nguoc
`

**Tai sao token hoa tot hon cho AI**:
1. **AI khong bao gio thay PHI that**: mo hinh chi thay <TEN_BENH_NHAN_001>, khong phai "Nguyen Van A"
2. **Ngay ca khi dau ra AI bi ro**: no se noi <TEN_BENH_NHAN_001>, khong phai ten that
3. **Token khong can duoc ma hoa**: no da ngau nhien; ma hoa danh cho bang anh xa

**Noi bang anh xa song**:
- Kho co han che cao, tach biet khoi he thong chinh
- Yeu cau phe duyet hai nguoi cho bat ky truy cap nao
- Duoc ma hoa KMS voi khoa rieng biet
- Duoc ghi nhat ky kiem toan

**Cac truong hop loi**:
- Dau ra AI vo tinh bi ro: "<TEN_BENH_NHAN_001>" - KHONG the nhan dang, muc do nghiem trong thap
- Nhat ky kiem toan bi xam pham: cac token, khong phai PHI - KHONG the nhan dang, muc do nghiem trong thap
- CA HAI bi xam pham + kho bi xam pham: yeu cau xam pham nhieu lop - cuc ky kho xay ra

**So sanh voi chi ma hoa**:
- Chi ma hoa: "giai ma voi khoa, thay tat ca PHI"
- Token hoa + ma hoa: ngay ca voi tat ca cac khoa, chi thay cac token

**Vi du thuc te**:
- Ma hoa: khoa nha cua ban voi khoa. Mat khoa, mat quyen truy cap.
- Token hoa: giu so dia chi trong ket an rieng biet. Ngay ca khi ai do vao nha ban, ho khong biet ai song o do cho den khi pha vo ket an so dia chi rieng biet.

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
