import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 3. Tuan thu & Quy dinh Singapore

### Q26. PDPA la gi va tai sao chung toi phai quan tam?

**A.** PDPA = Personal Data Protection Act (Luat Bao ve Du lieu Ca nhan Singapore, 2012, sua doi 2020).

**Nhung gi no yeu cau**:
1. **Lay su dong y** truoc khi thu thap du lieu ca nhan, hoac co co so phap ly ro rang
2. **Thong bao cho moi nguoi** ve du lieu ban thu thap va ly do ("Nghia vu Thong bao")
3. **Chi su dung du lieu cho muc dich da neu**
4. **Giu du lieu chinh xac**
5. **Bao ve du lieu** voi bao mat hop ly
6. **Cho phep moi nguoi truy cap va chinh sua** du lieu cua ho
7. **Thong bao cho co quan quan ly (PDPC) trong vong 72 gio** ve vi pham du lieu anh huong den 500+ ca nhan hoac gay hai dang ke
8. **Bo nhiem Can bo Bao ve Du lieu (DPO)** cho to chuc cua ban

**Doi voi he thong cua chung toi**:
- Du lieu benh nhan la "Du lieu Ca nhan" theo PDPA. Cac quy tac bao ve nghiem ngat ap dung.
- Comprehend Medical / DataWorks SDDP che giau PHI truoc khi no den AI. AI khong bao gio thay ten that, MRN, NRIC.
- Nhat ky kiem toan luu giu dang token da che giau, khong bao gio PHI thu.
- Vi pham (vi du: ai do danh cap co so du lieu) cua cac token da che giau it nghiem trong hon nhieu so voi PHI thu.

**Phat tien vi pham**:
- Len den 1.000.000 SGD HOAC 10% doanh thu hang nam (tuy theo so nao cao hon)
- Cac truong hop thuc te: Singtel bi phat 1 trieu SGD+ vao nam 2020; Marina Bay Sands bi phat 74.000 SGD

**Doi voi Nova**:
- Bo nhiem DPO (trach nhiem 1 FTE, khong nhat thiet phai toan thoi gian)
- Duy tri quy trinh thong bao vi pham
- Dao tao tuan thu PDPA hang nam cho tat ca nhan vien
- Danh gia Tac dong Quyen rieng tu cho viec trien khai AI

**Ket luan**: PDPA la lanh tho quen thuoc. Viec trien khai AI phu hop voi PDPA **vi** no giam thieu phoi nhiem PHI, khong phai bat chap no.

---

### Q27. HCSA la gi va no ap dung cho chung toi nhu the nao?

**A.** HCSA = Healthcare Services Act 2020 (Luat Dich vu Cham soc Suc khoe Singapore).

**Nhung gi thay doi vao nam 2020**:
- HCSA thay the Luat Benh vien Tu nhan va Phong kham Y te (PHMC) cu nam 1980
- Cap nhat cho viec cung cap dich vu cham soc suc khoe hien dai: y te tu xa, suc khoe di dong, **ho tro quyet dinh lam sang dua tren AI**

**Danh muc dich vu theo HCSA**:
- Dich vu benh vien
- Dich vu chuyen khoa
- Dich vu y te lien minh
- **Dich vu Ho tro Quyet dinh Lam sang (CDS)**: lien quan den tro ly AI cua chung toi
- Dich vu y te tu xa

**Doi voi ho tro quyet dinh lam sang cu the**:
- Yeu cau giay phep tu MOH (Bo Y te)
- Dich vu phai dua tren bang chung (yeu cau trich dan phu hop voi HCSA)
- Cac su kien bat loi phai bao cao cho MOH
- Phai hoat dong duoi su giam sat cua bac si co phep hanh nghe duoc neu ten
- Giay phep gia han hang nam voi kiem tra cua MOH

**Tac dong thuc te doi voi Nova**:
- Neu Nova phuc vu benh vien CII: phai chiu danh gia an ninh mang nha cung cap
- Nova nen co chung nhan Cybersecurity Code of Practice (CCoP)
- Kiem tra xam nhap hang nam (~30.000-50.000 USD)
- Giam sat SOC 24/7 (da la phan cua SRE tieu chuan)

**Kien truc cua chung toi vs yeu cau CSA**:
- Anti-DDoS: Co (AWS Shield Advanced / Alibaba Anti-DDoS)
- WAF: Co (AWS WAF / Alibaba WAF)
- Nhat ky kiem toan bat bien: Co (S3 Object Lock / OSS WORM)
- Ma hoa: Co (KMS BYOK)
- Nhat ky truy cap: Co (CloudTrail / ActionTrail)
- Ung pho su co: Co (runbooks + truc ban)

---

### Q28. PDPA, HIPAA va GDPR khac nhau nhu the nao?

**A.** Tat ca deu la luat quyen rieng tu, voi pham vi dia ly va noi dung khac nhau:

**PDPA (Singapore, 2012/2020)**:
- Pham vi: du lieu ca nhan cua ca nhan tai Singapore
- Linh vuc: lien nganh (khong cu the cho y te)
- Phat tien: len den 1 trieu SGD hoac 10% doanh thu
- Chuyen du lieu xuyen bien gioi: yeu cau bao ve tuong duong
- Thong bao vi pham: 72 gio den PDPC

**HIPAA (Hoa Ky, 1996)**:
- Pham vi: Thong tin Suc khoe Duoc Bao ve (PHI) cua benh nhan My
- Linh vuc: cu the cho y te
- Phat tien: len den 1,5 trieu USD moi cap vi pham
- Chuyen du lieu xuyen bien gioi: yeu cau BAA voi tat ca cac nha xu ly phu
- Thong bao vi pham: 60 ngay

**GDPR (Lien minh Chau Au, 2018)**:
- Pham vi: du lieu ca nhan cua cu dan EU
- Linh vuc: lien nganh voi cac quy tac bo sung cho du lieu "danh muc dac biet" (suc khoe)
- Phat tien: len den 20 trieu EUR hoac 4% doanh thu toan cau
- Chuyen du lieu xuyen bien gioi: yeu cau quyet dinh tuong duong hoac SCC
- Thong bao vi pham: 72 gio

**Doi voi Nova**:
- **Luon ap dung PDPA** (trien khai Singapore)
- **Ap dung HIPAA** khi xu ly du lieu benh nhan My (vi du: neu mot cong ty bao hiem My hop tac)
- **Ap dung GDPR** khi xu ly du lieu cu dan EU (vi du: benh nhan la nguoi nuoc ngoai EU tai Singapore)
- **Quy tac nghiem ngat nhat thang**: khi cac quy tac mau thuan, tuan theo quy tac nghiem ngat nhat ap dung

**He thong cua chung toi dap ung ca ba** vi no duoc thiet ke cho tap hop sieu nghiem ngat nhat.

---

### Q29. Chung toi co can phe duyet tu MOH (Bo Y te) truoc khi trien khai khong?

**A.** Co dieu kien. Hai con duong:

**Con duong 1: Giay phep HCSA cho ho tro quyet dinh lam sang**
- Bat buoc neu AI duoc su dung cho cac quyet dinh chan doan hoac dieu tri
- Benh vien nop don; Nova cung cap tai lieu ho tro
- Quy trinh 3-4 thang, bat buoc truoc khi ra mat

**Con duong 2: Phan loai thiet bi y te HSA**
- Co quan Khoa hoc Suc khoe quan ly cac thiet bi y te bao gom phan mem
- Phan loai phu thuoc vao muc do rui ro:
  - **Hang A** (rui ro thap): chi thong bao, khong can phe duyet chinh thuc
  - **Hang B**: phe duyet tieu chuan, ~3 thang
  - **Hang C**: phe duyet nang cao, ~6 thang
  - **Hang D** (rui ro cao nhat, vi du: chan doan tu dong): phe duyet truoc khi ra thi truong, ~12 thang

**Phan loai du kien cua he thong chung toi**: Hang B.

**Ly do Hang B**:
- Day la ho tro quyet dinh lam sang thong bao cho bac si
- Quyet dinh lam sang cuoi cung duoc dua ra boi bac si
- Dau ra la thong tin, khong phai chi thi
- Cau tra loi "sai" gay bat tien nhung yeu cau loi bac si de gay hai cho benh nhan

**Lich trinh phe duyet**: 3-6 thang
**Chi phi nop don**: ~5.000-15.000 SGD cho HSA + 25.000-75.000 USD tu van quy dinh

**Ghi chu thoi gian**: Dieu nay chong lap voi viec xay dung ky thuat, khong mo rong no theo thu tu.

---

### Q30. Khung AI Verify cua IMDA la gi? Chung toi co phai su dung no khong?

**A.** AI Verify la khung kiem tra AI Co trach nhiem cua Singapore duoc IMDA ra mat nam 2023.

**No la gi**:
- Bo cong cu + khung quan tri
- 11 nguyen tac dao duc AI duoc danh gia:
  1. Minh bach
  2. Giai thich duoc
  3. Lap lai duoc/Tai tao duoc
  4. An toan
  5. Bao mat
  6. Manh me
  7. Cong bang
  8. Quan tri Du lieu
  9. Trach nhiem giai trinh
  10. Quyen tu chu & Giam sat cua Con nguoi
  11. Tang truong Bao trum, Xa hoi & Moi truong

**Co bat buoc khong?**:
- **Tu nguyen** doi voi AI chung
- **Duoc khuyen nghi manh me** cho AI y te
- **Bat buoc tren thuc te** doi voi cac hop dong cham soc suc khoe cua chinh phu

**Tai sao chung toi su dung no du sao**:
- Kiem toan AI cua ban theo AI Verify la yeu to phan biet tin cay voi cac benh vien
- Quan he doi tac IMDA cho phep ban tiep thi "Duoc chung nhan AI Verify"
- Bo cong cu mien phi, ~10.000-30.000 USD tu van de chay kiem toan day du

**Anh xa AI Verify cho he thong cua chung toi**:

| Nguyen tac | Trien khai cua chung toi |
|---|---|
| Minh bach | Trich dan tren moi cau tra loi, phien ban mo hinh hien thi |
| Giai thich duoc | Cac chunk duoc truy xuat hien thi trong phan mo rong "Tai sao cau tra loi nay?" |
| Lap lai duoc | Nhat ky kiem toan cho phep tai tao chinh xac |
| An toan | Bedrock Guardrails + diem grounding |
| Bao mat | Ma hoa, IDaaS, nhat ky kiem toan |
| Manh me | Red team 200+ prompt doi nghich truoc khi ra mat |
| Cong bang | Nhat quan gion van giua cac khoa, khong co thien vi nhan khau hoc trong dinh tuyen |
| Quan tri Du lieu | Tuan thu PDPA + theo doi nguon goc |
| Trach nhiem giai trinh | Can bo an toan lam sang + chat_trace |
| Quyen tu chu | Bac si dua ra quyet dinh cuoi cung, AI tu van |
| Tang truong Bao trum | Ho tro da ngon ngu (tieng Anh + tieng Trung qua Cohere v3) |

**Khuyen nghi**: Hoan thanh danh gia ban than AI Verify vao thang 5 cua viec trien khai. Xuat ban bao cao tom tat cho cac benh vien doi tac. Su dung nhu yeu to phan biet thi truong.

---

### Q31. Luat An ninh mang 2018 la gi?

**A.** Luat An ninh mang Singapore thiet lap bao ve Co so Ha tang Thong tin Quan trong (CII).

**Ai la CII**:
- Cac nha khai thac dich vu thiet yeu trong 11 linh vuc:
  1. Ngan hang/tai chinh
  2. **Y te** (lien quan den chung toi)
  3. Nang luong
  4. Nuoc
  5. Vien thong
  6. Giao thong duong bo
  7. Hang khong
  8. Hang hai
  9. Dich vu Chinh phu
  10. Truyen thong
  11. Thong tin-truyen thong

**Chi dinh CII y te**:
- Cac benh vien lon (vi du: SGH, NUH, NTFH) la CII
- **He thong ho tro quyet dinh lam sang** cua ho co the duoc chi dinh la cac thanh phan CII
- Dieu nay them ganh nang tuan thu nhung cung them ho tro an ninh mang cua chinh phu

**Yeu cau doi voi CII (va nha cung cap CII nhu Nova)**:
- Kiem toan an ninh mang hang nam (kiem toan vien duoc CSA phe duyet)
- Bao cao su co trong vong 2 gio ke tu khi phat hien
- Cac bai tap an ninh mang bat buoc
- Cac kiem soat ky thuat cu the: ma hoa, nhat ky truy cap, du phong

**Tac dong thuc te doi voi Nova**:
- Neu Nova phuc vu benh vien CII: phai chiu danh gia an ninh mang nha cung cap
- Nova nen co chung nhan Cybersecurity Code of Practice (CCoP)
- Kiem tra xam nhap hang nam (~30.000-50.000 USD)
- Giam sat SOC 24/7 (da la phan cua SRE tieu chuan)

**Kien truc cua chung toi vs yeu cau CSA**:
- Anti-DDoS: Co (AWS Shield Advanced / Alibaba Anti-DDoS)
- WAF: Co (AWS WAF / Alibaba WAF)
- Nhat ky kiem toan bat bien: Co (S3 Object Lock / OSS WORM)
- Ma hoa: Co (KMS BYOK)
- Nhat ky truy cap: Co (CloudTrail / ActionTrail)
- Ung pho su co: Co (runbooks + truc ban)

---

### Q32. Chung toi co can phe duyet tu MOH truoc khi trien khai khong?

**A.** Da duoc tra loi o Q29. Xem them chi tiet o do.

---

### Q33. Benh nhan co quyen yeu cau du lieu cua ho KHONG duoc AI xu ly khong?

**A.** Theo PDPA, co. Ba co che tu choi:

**1. Rut lai su dong y (quyen PDPA)**
- Benh nhan co the rut lai su dong y cho viec su dung du lieu cu the
- Benh vien phai tuan thu trong thoi gian hop ly
- Doi voi AI: dung xu ly du lieu cua benh nhan nay qua tro ly AI

**2. Tu choi theo tung lan kham**
- Benh nhan co the tu choi su tham gia cua AI cho mot lan tu van cu the
- Bac si ghi chu "benh nhan tu choi tu van AI"
- Tro ly AI bi bo qua cho lan kham do
- Quyen tieu chuan theo dao duc y te

**3. Co hieu vinh vien trong EHR**
- Benh nhan danh dau "khong xu ly AI" trong ho so benh nhan cua ho
- EHR gui co hieu voi moi cuoc goi API
- Tro ly AI tra ve: "Benh nhan da tu choi; tu van AI khong co san cho truong hop nay"

**Tac dong van hanh**:
- Ti le tu choi du kien: <5% dua tren cac trien khai tuong tu
- Thiet ke quy trinh lam viec: tu choi la "click de bo qua" khong phai su gian doan van hanh lon
- Chi phi ho tro tu choi: toi thieu (~5.000 USD ky thuat mot lan cho tich hop co hieu EHR)

**Nhat ky kiem toan**: Moi truy van AI ghi lai trang thai dong y. Neu benh nhan sau do phan doi, kiem toan cho thay lieu viec su dung AI co duoc uy quyen vao thoi diem do hay khong.

---

### Q34. Chung toi co nghia vu cong khai bao cao cac su kien bat loi do AI gay ra khong?

**A.** Nhieu nghia vu bao cao:

**1. Bao cao Su kien Bat loi Bat buoc cua HSA**
- Thiet bi y te Hang B (he thong cua chung toi): cac su kien nghiem trong trong vong 7 ngay
- "Nghiem trong" = tu vong, benh de doa tinh mang, nhap vien, ton thuong vinh vien
- Nop qua he thong MEDDR truc tuyen cua HSA

**2. Bao cao Su co Nghiem trong cua MOH**
- Bao cao cap benh vien cho cac su co lam sang
- Cac su kien co the quy cho AI di qua bao cao su co benh vien tieu chuan
- Du lieu tong hop hang nam duoc bao cao cho MOH

**3. Bao cao Ky luat SMC**
- Neu mot bac si bi cao buoc da phu thuoc qua muc vao AI gay hai
- Benh vien bao cao cho Uy ban Ky luat SMC
- Doc lap voi bao cao he thong

**4. Cong bo cong khai**
- Khong co bao cao cong khai bat buoc o Singapore (khac voi mot so nuoc EU)
- Thuc hanh tot nhat duoc khuyen nghi: bao cao tong hop hang nam cho cong dong benh vien
- Cac an pham thuong mai thuong yeu cau cong bo tu nguyen

**Lich bao cao thuc te**:

| Tan suat | Bao cao |
|---|---|
| Trong vong 2 gio | Kich hoat ung pho su co noi bo |
| Trong vong 24 gio | Uy ban an toan benh vien duoc thong bao |
| Trong vong 7 ngay | Bao cao su kien nghiem trong HSA (neu ap dung) |
| Trong vong 30 ngay | Bao cao phan tich nguyen nhan goc |
| Hang quy | Xu huong tong hop cho lanh dao dieu hanh |
| Hang nam | Bao cao tom tat cong khai (duoc khuyen nghi) |

---

### Q35. Chung toi co can Danh gia Tac dong Quyen rieng tu (DPIA) truoc khi trien khai khong?

**A.** Co, duoc khuyen nghi manh me.

**Khi nao DPIA duoc yeu cau (PDPA Muc 16)**:
- Xu ly du lieu ca nhan nhay cam (suc khoe la nhay cam)
- Xu ly quy mo lon
- Cong nghe moi voi cac tac dong quyen rieng tu

**Ca ba dieu kien ap dung** cho viec trien khai cua chung toi.

**Cac thanh phan DPIA**:

1. **Mo ta xu ly**
   - Du lieu nao duoc thu thap
   - Cach xu ly (che giau PHI, suy luan AI, kiem toan)
   - Ai co quyen truy cap

2. **Su can thiet va tinh tuong xung**
   - Tai sao can ho tro AI
   - Lieu cac lua chon thay the it xam pham hon co the dat duoc cung muc tieu
   - Cac buoc giam thieu du lieu

3. **Danh gia rui ro**
   - Rui ro doi voi chu the du lieu (quyen rieng tu, do chinh xac du lieu, quyen tu chu)
   - Diem xac suat va muc do nghiem trong

4. **Bien phap giam thieu**
   - Ky thuat: che giau PHI, ma hoa, kiem toan
   - To chuc: dao tao, quan tri, hop dong

5. **Tham van**
   - Cac ben lien quan noi bo
   - Ky duyet DPO
   - Tham van PDPC (tuy chon, duoc khuyen nghi cho cac truong hop moi)

**Lich trinh DPIA**: 4-6 tuan
**Chi phi DPIA**: 15.000-30.000 USD (tu van + thoi gian noi bo)
**Dau ra**: Bao cao 30-50 trang; co san theo yeu cau tu PDPC

**Khi nao thuc hien**: TRUOC khi trien khai, ly tuong la trong tuan 5-6 cua viec xay dung. Cac phat hien thong bao cau hinh bao mat cuoi cung.

**Tai lieu song**: Cap nhat DPIA khi:
- Nang cap mo hinh lon (vi du: Sonnet 4.5 -> 5.0)
- Nguon du lieu moi duoc them
- Tenant moi duoc tich hop (cap nhat nhe)
- Thay doi quy dinh

**Su dung thuc te**: Hau het cac benh vien se yeu cau DPIA nhu mot phan cua tham dinh nha cung cap. Hay chuan bi san.

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
