import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

### Q36. Dieu gi xay ra trong mot cuoc kiem toan quy dinh boi PDPC, MOH hoac HSA?

**A.** Ba loai kiem toan khac nhau, moi loai co the quan ly duoc:

**Kiem toan PDPC (quyen rieng tu)**:
- Duoc kich hoat boi khieu nai, thong bao vi pham, hoac lua chon ngau nhien
- Thong bao: thuong 2-4 tuan truoc
- Thoi gian: 2-5 ngay tai cho, nhieu tuan theo doi
- Tai lieu yeu cau: DPIA, so do luong du lieu, quy trinh quan ly dong y, ke hoach ung pho vi pham, hop dong nha cung cap, nhat ky kiem toan (mau ngau nhien)

**Kiem toan MOH (giay phep HCSA)**:
- Hang nam theo lich hoac duoc kich hoat boi su kien bat loi
- Thong bao: 4-6 tuan truoc
- Thoi gian: 1-3 ngay tai cho
- Tai lieu yeu cau: mo ta dich vu, ke hoach quan tri lam sang, nhat ky su kien bat loi, bao cao dam bao chat luong, trinh do nhan su, du lieu ket qua benh nhan (da duoc an danh)

**Kiem toan HSA (thiet bi y te)**:
- Dinh ky (moi 1-3 nam doi voi Hang B)
- Thong bao: 6-8 tuan truoc
- Thoi gian: 2-4 ngay tai cho
- Tai lieu yeu cau: Ho so Quan ly Rui ro, Bao cao Danh gia Lam sang, bao cao Giam sat Sau thi truong, nhat ky thay doi phan mem, bao cao su kien bat loi, Hoa don Vat lieu An ninh mang

**Su chuan bi cua chung toi**:
- Tat ca tai lieu bat buoc duoc duy tri lien tuc (khong duoc tap hop vao thoi diem kiem toan)
- Xem xet tuan thu noi bo hang quy (phat hien van de truoc co quan quan ly)
- Nguoi lien lac duoc chi dinh cho moi co quan (Can bo Tuan thu, Giam doc Y te, Quan ly Chat luong)

**Ket qua kiem toan thuong**:
- 70%: Dat voi cac khuyen nghi nho
- 25%: Dat voi cac cai tien bat buoc (thoi han ~3 thang)
- 4%: Dat co dieu kien yeu cau kiem toan theo doi
- 1%: Dinh chi giay phep/dang ky (cac van de nghiem trong)

---

### Q37. Chung toi co the tin tuong rang du lieu benh nhan khong roi khoi Singapore khong?

**A.** Co, voi bao dam hop dong va ky thuat:

**Ma trix vi tri du lieu**:

**Du lieu benh nhan (khi duoc xu ly)**:
- **Luu tru**: ap-southeast-1 (Singapore)
- **Trong qua trinh truyen**: TLS 1.3 trong vung Singapore
- **Trong xu ly LLM**: dang token hoa, duoc xu ly tai Singapore
- **Trong nhat ky kiem toan**: dang token hoa, ap-southeast-1, OSS WORM

**Du lieu van hanh**:
- **Chi so he thong**: ap-southeast-1
- **Nhat ky ung dung**: ap-southeast-1
- **Cau hinh**: ap-southeast-1

**Luong du lieu xuyen bien gioi** (han che):

| Dich vu | Vung | Loai du lieu |
|---|---|---|
| Claude API (Bedrock) | ap-southeast-1 (Singapore) | Prompt da token hoa, hoan thanh |
| Qwen API (Model Studio) | Singapore International | Prompt da token hoa, hoan thanh |
| Ghi nhat ky Anthropic | Khong co (voi cau hinh dung) | Khong co |
| Ghi nhat ky Alibaba | Khong co (voi cau hinh dung) | Khong co |
| Thanh toan AWS | us-east-1 (an danh) | Chi chi so su dung |
| Anti-DDoS | Bien toan cau | Chi metadata moi de doa |

**Bao dam luu tru du lieu**:
- AWS Bedrock: cam ket hop dong voi xu ly ap-southeast-1
- Alibaba Model Studio: cam ket hop dong voi Singapore International
- Ca hai deu cung cap chung nhan luu tru du lieu theo yeu cau

**Xac minh kiem toan**:
- Kiem toan luu tru du lieu hang quy
- Bao cao co san cho cac tenant benh vien
- Nhat ky mang cho thay luong du lieu
- Khoa KMS bi khoa theo vung
- Bucket S3/OSS bi khoa theo vung

**Bang chung thuc te ve luu tru**: Co quan quan ly hoi "Chung minh du lieu benh nhan khong roi Singapore." Chung toi co the cho thay: khoa KMS bi khoa theo vung, bucket S3 bi khoa theo vung, kiem toan egress mang, khong co sao chep xuyen vung duoc kich hoat.

---

### Q38. Dieu gi xay ra neu co vi pham bao mat?

**A.** Lich trinh ung pho vi pham PDPA Singapore duoc xac dinh ro rang:

**Lich trinh (PDPA Muc 26B)**:

| Lich trinh | Hanh dong |
|---|---|
| Gio 1 | Phat hien vi pham, kich hoat nhom ung pho su co |
| Gio 4 | Xac dinh pham vi ban dau (tac dong, ca nhan bi anh huong) |
| Gio 24 | Thong bao noi bo: lanh dao, DPO, cac tenant benh vien |
| Ngay 3 | Phan tich phap y chi tiet dang tien hanh |
| Ngay 3 (72 gio) | **Thong bao PDPC bat buoc** neu vi pham anh huong den 500+ ca nhan hoac gay hai dang ke |
| Ngay 7 | Thong bao cho cac ca nhan bi anh huong |
| Ngay 30 | Bao cao khac phuc chi tiet cho PDPC |
| Ngay 90 | Tuyen bo cong khai (neu ap dung) |

**Phan loai muc do nghiem trong**:

**Cap 1 (Nghiem trong)**: PHI bi lo, >500 ca nhan
- Thong bao PDPC bat buoc trong 72 gio
- Thong bao cho cac ca nhan bi anh huong
- Cong bo cong khai neu truyen thong dua tin
- Phat tien tiem nang: 1 trieu SGD

**Cap 2 (Lon)**: Phoi nhiem PHI han che, <500 ca nhan HOAC khong gay hai ca nhan nhung du lieu bi truy cap
- Thong bao PDPC tuy chon nhung duoc khuyen nghi
- Thong bao cho cac tenant benh vien
- Khac phuc noi bo

**Cap 3 (Nho)**: Khong co PHI bi lo (vi du: chi so he thong bi ro, token da che giau)
- Khac phuc noi bo
- Thong bao PDPC khong bat buoc

**Uoc tinh cap vi pham cua he thong chung toi**:
- Vi pham co kha nang nhat: Cap 3 (he thong chay tren du lieu da token hoa; truy cap PHI thu kho)
- Vi pham nhat ky kiem toan: Cap 3 (nhat ky duoc token hoa)
- Vi pham bucket OSS thu chua PDF goc: Cap 1 (co the gay hai thuc su)

**Chi phi vi pham thuc te** (dien hinh):
- Dieu tra phap y: 50.000-200.000 USD
- Thong bao khach hang: 10.000-50.000 USD
- Phat tien quy dinh: 0-1.000.000 SGD (toi da PDPA)
- Sua chua danh tieng: 50.000-500.000 USD
- Tong: 100.000-2.000.000 USD tuy theo muc do nghiem trong

---

### Q39. Chung toi co can Danh gia Tac dong Quyen rieng tu (DPIA) truoc khi trien khai khong?

**A.** Da duoc tra loi o Q35. Xem chi tiet o do.

---

### Q40. Cac tieu chuan quoc te nao cho AI trong y te chung toi nen tuan theo?

**A.** Mot so tieu chuan lien quan:

**1. ISO 13485 (Quan ly Chat luong Thiet bi Y te)**
- Quan ly chat luong toan dien cho nha san xuat thiet bi y te
- Bat buoc cho thiet bi y te HSA Hang B+
- ~50.000-150.000 USD de chung nhan; ~25.000 USD/nam de duy tri

**2. ISO 14971 (Quan ly Rui ro Thiet bi Y te)**
- Khung quan ly rui ro cu the
- Thanh phan bat buoc cua ho so nop HSA
- Danh gia rui ro lien tuc duoc yeu cau

**3. IEC 62304 (Vong doi Phan mem Thiet bi Y te)**
- Quy trinh vong doi cu the cho phan mem
- Yeu cau tai lieu: thiet ke, kiem tra, quan ly thay doi
- Hau het nha phat trien SaMD My/EU tuan theo dieu nay

**4. ISO 27001 (Bao mat Thong tin)**
- Da yeu cau doi voi AWS/Alibaba (chung toi ke thua)
- Cac benh vien thuong yeu cau Nova duy tri

**5. SOC 2 Type II (Bao mat/Tinh san sang)**
- Nguon goc My, nhung ngay cang duoc yeu cau
- AWS/Alibaba duoc chung nhan o lop dam may

**Duoc khuyen nghi cho Nova**:
- ISO 13485 + IEC 62304: bat buoc cho HSA Hang B
- ISO 27001 + 27018: ke thua tu nha cung cap dam may (khong can chung nhan Nova rieng biet)
- HITRUST CSF: chi neu theo duoi thi truong My

**Tong chi phi chung nhan**: ~200.000-400.000 USD nam dau. Xung dang cho viec ban hang benh vien cao cap.

---

### Q41. Bao mat du lieu benh nhan duoc xu ly nhu the nao?

**A.** Hai lop bao ve:

**Lop 1: Che giau PHI tai thoi diem nhap**
- DataWorks SDDP / Comprehend Medical quet voi cac goi quy tac PHI y te
- Phat hien: ten, MRN, NRIC/FIN, ngay sinh, so dien thoai, email
- Hanh dong: cach ly den /raw/_quarantine/, thong bao quan tri vien, tai lieu bi loai tru khoi chi muc

**Lop 2: Token hoa tai thoi diem chay**
- FC /chat preflight chay SDDP tren tin nhan den va bat ky phan du lieu benh nhan nao tu EHR
- PHI duoc phat hien tro thanh cac token KMS co the dao nguoc: <TEN_0>, <MRN_0>, <NGAY_SINH_0>, <DIEN_THOAI_0>, <EMAIL_0>, <NRIC_0>
- LLM chi thay cac token. Cau tra loi duoc de-token hoa trong giao dien nguoi dung chi.
- Nhat ky kiem toan luu giu dang da token hoa.

**Tai sao token hoa tot hon chi ma hoa**:
- Ma hoa: du lieu bi khoa toan hoc voi mot khoa. Voi khoa, ban co the phuc hoi ban goc.
- Token hoa: du lieu duoc thay the bang mot token ngau nhien. Khong co bang anh xa rieng biet, ban khong the dao nguoc.
- Ngay ca khi AI bi xam pham: no se noi "<TEN_0>", khong phai ten that
- Ngay ca khi nhat ky kiem toan bi xam pham: chi co token, khong co PHI

**Noi bang anh xa song**:
- Kho an toan co han che cao, tach biet khoi he thong chinh
- Yeu cau phe duyet hai nguoi cho bat ky truy cap nao
- Khong the truy cap tu cac he thong san xuat bi xam pham
- Ngay ca khi tin tac co du lieu san xuat + nhat ky kiem toan, ho khong the lay ten benh nhan cho den khi pha vo kho rieng biet

---

### Q42. Bac si co the xem lich su cuoc tro chuyen AI cua ho khong?

**A.** Co, nhieu cap do truy cap:

**Truy cap ca nhan** (moi bac si):
- Lich su cua rieng ho
- Quyen rieng tu: chi du lieu cua rieng ho
- Xu huong va thong tin chi tiet

**Truy cap khoa** (truong khoa):
- Du lieu khoa tong hop
- So sanh voi dong nghiep (an danh)
- Hieu suat khoa

**Truy cap benh vien** (Giam doc Y te):
- Tat ca chi so
- Xem xuyen khoa
- Goc do chien luoc

**Truy cap kiem toan** (Can bo Tuan thu):
- Phat lai phien day du
- Tim kiem theo ngay, bac si, benh nhan, chu de
- Ho tro kiem toan quy dinh

**Luu giu du lieu**:
- Phien hoat dong: du lieu truc tiep
- Phien gan day: luu tru nong 30 ngay
- Phien cu hon: luu tru 6 nam (yeu cau HCSA)
- Xoa tu dong sau 6 nam

---

### Q43. Dieu gi xay ra neu mot bac si roi benh vien?

**A.** Quy trinh offboarding ro rang:

**Ngay 1 (ngay roi)**:
- Thu hoi quyen truy cap ngay lap tuc
- Vo hieu hoa tai khoan IDaaS
- Xoa phien hoat dong
- Xac nhan thu hoi phan cung (neu co)

**Ngay 1-7**:
- Xac minh tat ca quyen truy cap da bi thu hoi
- Kiem tra nhat ky kiem toan cho bat ky hoat dong bat thuong nao truoc khi roi
- Luu giu nhat ky kiem toan (6 nam theo HCSA)

**Dai han**:
- Nhat ky kiem toan cua bac si duoc luu giu theo yeu cau quy dinh
- Khong co truy cap sau khi roi
- Bao mat du lieu benh nhan duoc duy tri

**Lich su cuoc tro chuyen**:
- Cac cuoc tro chuyen cua bac si duoc luu giu trong nhat ky kiem toan
- Khong the truy cap boi bac si sau khi roi
- Co the truy cap boi quan tri vien benh vien cho muc dich kiem toan
- Bao ve quyen rieng tu duoc duy tri

**Tiep nhan bac si moi**:
- Onboarding tu phuc vu: 15 phut
- Phien demo tuy chon: 30 phut
- Khong can dao tao ky thuat
- Truy cap ngay lap tuc sau khi IDaaS duoc cau hinh

---

### Q44. Lam the nao de biet he thong AI dang hoat dong tot hay dang suy giam?

**A.** Giam sat theo thoi gian thuc va xu huong:

**Chi so hieu suat duoc theo doi**:

**1. Toc do**:
- Do tre (p50, p95, p99)
- Thoi gian den token dau tien
- Tong thoi gian phan hoi

**2. Chat luong**:
- Do chinh xac (so voi tieu chuan vang)
- Ti le trich dan
- Ti le tu choi
- Phat hien ao giac

**3. Do tin cay**:
- Thoi gian hoat dong
- Ti le loi
- Thanh cong chuyen doi du phong
- Thoi gian phuc hoi

**4. Su hai long nguoi dung**:
- Thumbs up/down
- Chat luong phan hoi
- Chi so ap dung

**5. Chi so kinh doanh**:
- Chi phi moi truy van
- Su dung tai nguyen
- Lap ke hoach nang luc

**Phat hien suy giam**:

**Canh bao theo thoi gian thuc**:
- Do tre p95 > 2s trong 5 phut
- Ti le loi > 1% trong 10 phut
- Diem chat luong giam > 5% trong tuan

**Phan tich xu huong**:
- So sanh tuan-qua-tuan
- Thang-qua-thang
- Quy-qua-quy

**Phat hien bat thuong**:
- Ngoai le thong ke
- Nhan dang mo hinh
- Phat hien bat thuong dua tren ML

**Kich hoat hanh dong**:

**Ngay lap tuc**:
- Goi bac si truc ban SRE
- Canh bao nhom ky thuat
- Leo thang len chi huy su co

**Ngan han**:
- Dieu tra nguyen nhan goc
- Thuc hien sua chua
- Ngan chan tai phat

**Dai han**:
- Cai tien kien truc
- Thay doi quy trinh
- Cap nhat dao tao

---

### Q45. Chung toi co the kiem tra cac tuyen bo nay mot cach doc lap khong?

**A.** Co, nhieu tuy chon xac minh:

**1. Bao cao Trung tam Tin tuong AWS/Alibaba**
- AWS Artifact: tai xuong SOC 2, ISO 27001, bao cao PCI-DSS
- Trung tam Tin tuong Alibaba: goi tuong tu
- Tat ca chung nhan co the xac minh cong khai

**2. Kiem toan code doc lap**
- Benh vien co the thue cong ty bao mat ben thu ba
- Nova cung cap quyen truy cap code (theo NDA)
- Chi phi dien hinh: 30.000-80.000 USD
- Cac benh vien hop ly da lam dieu nay

**3. Xem xet kien truc**
- Nhom CISO/bao mat cua benh vien xem xet tai lieu kien truc
- Phien hoi dap voi ky thuat cua Nova
- Bao cao kiem tra xam nhap duoc chia se

**4. Demo truc tiep**
- Cho thay luong du lieu thuc te: dat cau hoi -> xem che giau -> xem truy xuat -> xem cau tra loi
- Cho thay muc nhat ky kiem toan duoc tao ra
- Cho thay du lieu KHONG roi khoi vung Singapore

**5. Tai lieu tuan thu**
- DPIA (Q35): tai lieu day du co san
- Bao cao kiem tra xam nhap: duoc chia se theo yeu cau
- Chung chi ISO 27001 (ke thua tu dam may)
- Bao cao SOC 2 Type II

**6. Giam sat cua rieng benh vien**
- SIEM cua benh vien co the nhap nhat ky kiem toan cua chung toi
- Benh vien thay cung du lieu chung toi thay
- Khong can "tin tuong chung toi"

**7. Quyen kiem toan**
- Dieu khoan hop dong tieu chuan: benh vien co the kiem toan Nova mot lan moi nam
- Thong bao 30 ngay
- Pham vi hop ly

---

### Q46. Dieu gi xay ra khi chung toi ket thuc hop dong?

**A.** Quy trinh ket thuc ro rang:

**Ngay 1-30 sau khi ket thuc**:
- Dich vu tiep tuc (giai doan giam dan)
- Benh vien xuat du lieu
- Nha cung cap moi tich hop (neu ap dung)

**Ngay 30**:
- Dich vu bi vo hieu hoa
- Du lieu bi xoa khoi cac he thong hoat dong
- Nhat ky kiem toan duoc luu giu theo quy dinh (6 nam HCSA)

**Ngay 30-90**:
- Hoa don cuoi cung duoc thanh toan
- Bao mat tiep tuc (5 nam sau khi ket thuc)

**Nghia vu dai han**:
- Nhat ky kiem toan: 6 nam (yeu cau HCSA)
- Bao mat: 5 nam sau khi ket thuc
- Cac yeu cau boi thuong: 1 nam sau su co

**Xuat du lieu**:
- Dinh dang tieu chuan (JSON, CSV)
- Nhat ky kiem toan trong dinh dang co the doc duoc
- Tai lieu kien truc
- Cau hinh (khong co bi mat)

**Ho tro di cu**:
- Tai lieu xuat
- Phien hoi dap ky thuat
- Thoi gian an toan 30 ngay cho cac van de

**Khoa nha cung cap**:
- Thap. IP quan trong (corpus, prompt, khai thac) la trong code Nova so huu.
- Cac bit cu the cho dam may (Bedrock, Model Studio) co cac tuong duong hang hoa.
- Chi phi di cu: ~50-100k USD ky thuat, 2-4 tuan.

---

### Q47. Chung toi co the su dung he thong nay cho y te tu xa khong?

**A.** Co, voi dieu chinh. Y te tu xa co cac quy tac cu the:

**Huong dan Y te Tu xa MOH Singapore (2015, cap nhat 2022)**:
- Tu van y te tu xa phai bao gom bac si truc tiep theo thoi gian thuc
- Khong dong bo (luu tru va chuyen tiep) yeu cau phe duyet MOH cu the
- AI co the ho tro ca hai che do

**Doi voi he thong cua chung toi trong y te tu xa**:

**Dong bo (tu van video truc tiep)**:
- Tro ly AI duoc truy cap boi bac si trong khi tu van
- Benh nhan chi thay bac si
- Goi y AI duoc bac si xem xet truoc khi thao luan
- Giong nhu quy trinh lam viec tai cho

**Khong dong bo (vi du: xem xet hinh anh da khoa)**:
- Benh nhan gui hinh anh
- AI pre-screen de phan loai
- Bac si xem xet (voi goi y AI la mot dau vao)
- Quyet dinh duoc ghi lai

**Cau hinh duoc khuyen nghi cho trien khai y te tu xa**:
- Nguong grounding: 0,85 (so voi 0,7 tai cho)
- Mac dinh tu choi: tich cuc hon
- Trich dan bat buoc trong moi cau tra loi (khong co phan hoi chi co tu su)

---

### Q48. Dieu gi xay ra neu co thay doi lon trong quy dinh?

**A.** Quy trinh thich ung quy dinh:

**Cap 1: Chi cap nhat tai lieu**
- Vi du: thong tu MOH moi nhan manh cac quy tac hien co
- Quy trinh: Cap nhat tai lieu noi bo, dao tao nhan vien, khong thay doi he thong
- Lich trinh: 1-2 tuan
- Chi phi: ~2.000 USD thoi gian noi bo

**Cap 2: Thay doi cau hinh**
- Vi du: chu de bi cam moi trong Guardrails (vi du: "khong thao luan ve tinh trang thieu thuoc cu the")
- Quy trinh: Cap nhat chinh sach Guardrails, trien khai qua CI/CD, giam sat
- Lich trinh: 1 tuan
- Chi phi: ~5.000 USD ky thuat + kiem toan

**Cap 3: Thay doi kien truc**
- Vi du: yeu cau luu tru du lieu moi (vi du: "ten benh nhan phai duoc ma hoa voi khoa do benh vien kiem soat")
- Quy trinh: Xem xet thiet ke, thay doi ky thuat, xem xet quy dinh, trien khai, kiem toan
- Lich trinh: 4-12 tuan
- Chi phi: 25.000-100.000 USD tuy theo pham vi

**Theo doi thay doi tuan thu**:
- Can bo tuan thu dang ky: thong tu MOH, ban tin PDPC, cap nhat IMDA, thong bao HSA
- Xem xet tuan thu hang quy
- Kiem toan ben ngoai hang nam bao gom tat ca cac thay doi

**Giao tiep**:
- Thay doi lon: email tat ca cac tenant benh vien 30 ngay truoc
- Thay doi nho: ban tin hang thang
- Thay doi quan trong theo thoi gian thuc: chuoi dien thoai cho cac can bo an toan lam sang

---

### Q49. Chung toi co can bao hiem dac biet cho viec trien khai AI nay khong?

**A.** Co, mot so loai bao hiem:

**1. Bao hiem Trach nhiem Mang (Cyber Liability)**
- Bao gom: dieu tra phap y, thong bao khach hang, phat tien quy dinh
- Pham vi khuyen nghi: 5-10 trieu USD
- Phi bao hiem: 20.000-80.000 USD/nam
- Khau tru: 1-2% chi phi su co

**2. Bao hiem Loi va Thieu sot (E&O)**
- Bao gom: loi phan mem, dich vu khong dap ung mong doi
- Pham vi khuyen nghi: 5-10 trieu USD
- Phi bao hiem: 15.000-40.000 USD/nam

**3. Bao hiem Trach nhiem Nghe nghiep (Benh vien)**
- Cap nhat cho "ho tro quyet dinh tang cuong AI"
- Chi phi: thuong tang phi bao hiem 5-12%
- Mot so cong ty bao hiem giam gia cho nhat ky kiem toan AI co the xac minh

**4. Bao hiem Gian doan Kinh doanh**
- Bao gom: mat doanh thu trong thoi gian ngung hoat dong
- Pham vi: 500k-2 trieu USD
- Phi bao hiem: 10.000-20.000 USD/nam

**Tong phi bao hiem khuyen nghi cho Nova**: ~80.000-150.000 USD/nam

**Thi truong bao hiem tai Singapore**:
- Cac nha cung cap chinh: AIG, Chubb, Howden, Zurich
- Thi truong y te cu the: dang noi len
- Moi gioi chuyen biet: AON Healthcare, Marsh Healthcare

**Meo dam phan**:
- Tong hop chung nhan tuan thu
- Chuan bi ke hoach ung pho su co
- Ket qua kiem tra xam nhap
- So do kien truc (voi trong tam bao mat)
- Tai chinh 3 nam

---

### Q50. Lam the nao de chung toi biet he thong AI dang hoat dong tot hay dang suy giam?

**A.** Da duoc tra loi o Q44. Xem chi tiet o do.

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
