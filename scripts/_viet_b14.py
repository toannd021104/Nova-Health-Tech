import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 14. Van hanh dai han

### Q106. "Van hanh Ngay 2" co nghia la gi va tai sao no quan trong?

**A.** "Ngay 1" = ra mat, "Ngay 2" = van hanh lien tuc.

Ngay 2 bao gom: giam sat hieu suat, giai quyet van de, cai tien lien tuc, duy tri tuan thu, xu ly phan hoi nguoi dung, toi uu hoa chi phi, lap ke hoach nang luc, van hanh bao mat.

**Tai sao Ngay 2 quan trong hon Ngay 1**:
- Ngay 1: su kien 1 lan
- Ngay 2: 6 nam (luu giu HCSA) va hon nua
- Hau het chi phi: Ngay 2
- Hau het gia tri: Ngay 2

**Nang luc Ngay 2 Nova cung cap**:
- Giam sat 24/7 (SRE)
- Kiem tra suc khoe hang ngay
- Xem xet hieu suat hang tuan
- Bao cao tuan thu hang thang
- Cap nhat he thong hang quy
- Kiem toan bao mat hang nam

**Cam ket Ngay 2 cua benh vien**:
- Ho tro nguoi dung
- Tuan thu noi bo
- Duy tri su tham gia
- Phu hop chien luoc

**Chat luong Ngay 2 = chat luong dich vu tong the**.

---

### Q107. Loai giam sat nao chay lien tuc tren he thong?

**A.** Stack giam sat toan dien:

**Giam sat theo thoi gian thuc** (moi giay):
- Thoi gian phan hoi API
- Ti le loi
- Suc khoe dich vu
- Ti le hit cache
- Chi phi moi truy van

**Giam sat chat luong** (moi phut):
- Do chinh xac trich dan
- Diem grounding
- Ti le tu choi
- Chat luong phan hoi

**Giam sat tuan thu** (moi gio):
- Tinh toan ven cua nhat ky kiem toan
- Luu tru du lieu
- Thanh cong che giau PHI
- Cac mo hinh truy cap

**Giam sat kinh doanh** (hang ngay):
- Nguoi dung hoat dong
- Ti le ap dung
- Phan bo theo khoa
- Xu huong chi phi

**Cong cu cu the**:
- ARMS LLM Trace Explorer (Alibaba) / X-Ray (AWS): theo doi phan tan, phan tich do tre moi yeu cau, phan bo loi, toi uu hoa hieu suat
- SLS / CloudWatch Logs: nhat ky ung dung, su kien he thong, nhat ky kiem toan, co the tim kiem
- Giam sat ung dung ARMS: bang dieu khien theo thoi gian thuc, nguong canh bao, theo doi SLO
- Bang dieu khien tuy chinh: KPI cu the cua benh vien, phan tich theo khoa, phan tich xu huong

**Minh bach giam sat**:
- Benh vien thay cung bang dieu khien chung toi thay
- Truy cap theo thoi gian thuc
- Chi so chi tiet co san

---

### Q108. Ai chiu trach nhiem giu he thong cap nhat va hien tai?

**A.** Trach nhiem chung:

**Trach nhiem cua Nova**:
- **Cap nhat phan mem**: sua loi (lien tuc), va lap bao mat (trong vong 24 gio ke tu CVE), phat hanh tinh nang (hang thang), nang cap phien ban chinh (hang quy)
- **Co so kien thuc**: WHO ICD-11 hang ngay, huong dan WHO hang thang, dong bo thu nghiem noi bo hang tuan, them nguon moi (khi can)
- **Cap nhat mo hinh**: dao tao lai mo hinh sinh vien hang quy, phien ban chinh hang nam (Sonnet/Plus), tinh chinh prompt lien tuc
- **Tuan thu**: theo doi quy dinh moi, chung nhan duoc cap nhat, duy tri nhat ky kiem toan

**Trach nhiem cua benh vien**:
- **Du lieu noi bo**: cung cap bao cao thu nghiem duoc cap nhat, cap nhat giao thuc benh vien, noi dung cu the theo khoa
- **Quan ly nguoi dung**: onboarding bac si moi, thu hoi quyen truy cap khi roi, thay doi vai tro
- **Cau hinh**: tuy chinh theo khoa, tuy chon chuyen khoa, chinh sach noi bo
- **Su tham gia**: ap dung nguoi dung, tham gia dao tao, cung cap phan hoi

**Nhip do cap nhat**:
- **Hang ngay**: dong bo ICD-11
- **Hang tuan**: dong bo SharePoint
- **Hang thang**: lam moi WHO, trien khai tinh nang
- **Hang quy**: dao tao lai mo hinh, kiem toan bao mat
- **Hang nam**: phien ban chinh, kiem toan tuan thu

**Giao tiep ve cap nhat**:
- Ban tin (Nova -> Benh vien)
- Trang trang thai (truc tiep)
- Hoi thao web (hang quy)
- Xem xet 1:1 (moi tenant)

---

### Q109. He thong co bao gio ngung hoat dong de bao tri khong?

**A.** Duoc thiet ke de giam thieu thoi gian ngung hoat dong:

**Cua so bao tri**:
- Co lich: Thu 7 dau tien 2-6 SA SGT (4 gio)
- Thong bao: 7 ngay truoc
- Tan suat: ~2 lan moi nam (dien hinh)

**Hau het cap nhat: khong co thoi gian ngung hoat dong**:
- Trien khai cuon
- Phat hanh canary
- Trien khai xanh-xanh la
- Khong gian doan dich vu

**Cac kich ban bao tri cu the**:
1. **Cap nhat phan mem (thuong xuyen)**: Khong co thoi gian ngung hoat dong qua trien khai cuon. Duoc xac minh lien tuc. Tu dong rollback neu co van de.
2. **Di cu co so du lieu**: Di cu truc tuyen. Cac ban sao doc trong khi di cu. Duoc xac minh sau di cu.
3. **Nang cap co so ha tang**: Co lich truoc. Thong bao benh vien. Gian doan ngan (5-30 phut).
4. **Nang cap phien ban chinh**: Hang quy. Duoc kiem tra truoc. Phoi hop voi benh vien. Thoi gian ngung hoat dong ngan chap nhan duoc.

**Tac dong SLA**:
- Bao tri co lich: bi loai tru khoi SLA
- Ngung hoat dong khong co lich: SLA ap dung
- Tin dung dich vu theo SLA

**Giao tiep benh vien**:
- **Truoc bao tri**: thong bao 7 ngay, ke hoach chi tiet, huong dan quy trinh lam viec thay the
- **Trong bao tri**: cap nhat trang trang thai, tien do theo thoi gian thuc, FAQ nhanh
- **Sau bao tri**: bao cao xac minh, xac nhan suc khoe dich vu, cac van de neu co

**Lich su thuc te**:
- Dat duoc thoi gian hoat dong 99,9%+
- <5 gio tong thoi gian ngung hoat dong hang nam
- Hau het bao tri co lich: khong co tac dong

---

### Q110. Dieu gi xay ra neu Nova phat trien mot tinh nang moi anh huong den cach chung toi su dung he thong?

**A.** Quan ly tinh nang:

**Vong doi tinh nang**:
1. **Khai niem**: Duoc xac dinh tu phan hoi. Duoc xac thuc voi cac ben lien quan. Xem xet lo trinh.
2. **Phat trien**: Xay dung ky thuat. Kiem tra noi bo. 4-12 tuan dien hinh.
3. **Beta**: Cac benh vien duoc chon. Kiem tra thuc te. Phan hoi duoc thu thap.
4. **GA (Tinh san sang chung)**: Phat hanh cho tat ca. Duoc ghi lai. Duoc dao tao.
5. **Ap dung**: Benh vien danh gia. Quyet dinh su dung. Trien khai khi san sang.

**Kiem soat benh vien doi voi cac tinh nang**:
- **Bat buoc vs Tuy chon**: Bat buoc: cap nhat bao mat, tuan thu. Tuy chon: hau het cac tinh nang moi. Benh vien chon.
- **Cai dat moi tenant**: Bat tat moi tinh nang. Tuy chinh moi khoa. Trien khai dan.
- **Co hieu tinh nang**: Kiem soat chi tiet. Thi diem tren mot phan nguoi dung. Rollback neu co van de.

**Giao tiep ve cac tinh nang moi**:
- **Truoc khi phat hanh**: Hien thi lo trinh, bai dang blog, ban tin
- **Beta**: Hoi dong tu van khach hang, cac benh vien duoc chon, tai lieu chi tiet
- **GA**: Thong bao email, bai viet ban tin, hoi thao web duoc cung cap

**Danh gia moi benh vien**:
- **Tinh nang tieu chuan**: Duoc bao gom trong dang ky. Su dung theo y muon. Khong co chi phi bo sung.
- **Tinh nang cao cap**: Chi phi bo sung. Benh vien quyet dinh. Thanh toan rieng.
- **Tinh nang tuy chinh**: Cu the cho benh vien. Phat trien tuy chinh. Gia theo du an.

---

## 15. Tuong lai & Kha nang mo rong

### Q111. Tiem nang tang truong cua chung toi la gi? Chung toi co the mo rong len 50 benh vien khong?

**A.** Lo trinh kha nang mo rong:

**Nang luc hien tai**:
- Moi tenant: 500-1000 bac si
- Da tenant: mo rong tuyen tinh
- Ly thuyet: hang nghin tenant

**Cac kich ban tang truong**:
- Nam 1: 1-3 tenant (thiet lap nen tang)
- Nam 2: 5-10 tenant (truong thanh van hanh)
- Nam 3: 15-30 tenant (mo rong thi truong)
- Nam 4: 30-50 tenant (mo rong ASEAN)
- Nam 5+: 50-100 tenant (doanh nghiep truong thanh)

**Kinh te van hanh**:
- Chi phi bien moi tenant bo sung: ~30.000-50.000 USD/nam
- Doanh thu moi tenant: 100.000-400.000 USD/nam
- Bien loi nhuan: 60-80% o quy mo

**Bao hoa thi truong Singapore**:
- ~60 benh vien tai Singapore
- Chiem duoc thuc te: 15-30 benh vien
- Benh vien lon: 5-10 toi da
- Hang trung: 10-20

**Mo rong ASEAN**:
- Indonesia: 200+ benh vien
- Thai Lan: 150+
- Viet Nam: 100+
- Tong: 1.000+ benh vien
- Chiem duoc thuc te: 100-300 trong 10 nam

**Cac can nhac chien luoc**:
- Giao duc thi truong
- Dia phuong hoa quy dinh
- Thich ung van hoa
- Ung pho canh tranh

---

### Q112. Tam nhin dai han cho AI trong y te la gi?

**A.** Trien vong chien luoc:

**Tam nhin 5 nam**:
1. **Tieu chuan y te duoc tang cuong AI**: Hau het bac si su dung AI hang ngay. Tieu chuan duoc can cu trich dan. Ket qua benh nhan duoc cai thien. Chi phi cham soc suc khoe giam.
2. **Xuat sac chuyen khoa cu the**: AI chuyen biet moi chuyen khoa. Chuyen mon linh vuc sau. Tich hop voi quy trinh lam viec lam sang.
3. **AI lay benh nhan lam trung tam**: Cac cong cu huong den benh nhan (voi cac bien phap bao ve). Giao duc benh nhan. Dong y co thong tin. Quyet dinh duoc trao quyen.
4. **Suc khoe cong dong**: AI cho suc khoe cong cong. Phat hien dich benh. Phan bo nguon luc. Cai thien chat luong.
5. **Tich hop nghien cuu**: Thu nghiem lam sang duoc ho tro boi AI. Tao bang chung the gioi thuc. Y hoc ca nhan hoa. Kham pha dieu tri moi.

**Tam nhin 10 nam**:
1. **Cham soc suc khoe hoc lien tuc**: Tich hop ket qua theo thoi gian thuc. Huong dan thich ung. Phan tich du doan. Thuc su ca nhan hoa.
2. **Tri tue da phuong thuc**: Van ban + hinh anh + giong noi. Du lieu gen. Du lieu cam bien. Goc nhin toan dien.
3. **Cong bang suc khoe toan cau**: AI dan chu hoa chuyen mon. Co san moi noi. Nhieu ngon ngu. Nhan cam van hoa.
4. **Y hoc phong ngua**: Du doan rui ro. Can thiep som. Toi uu hoa loi song. Mo rong suc khoe.

**Thach thuc dai han**:
- Ky thuat: bao mat khang luong tu, hoc bao ton quyen rieng tu, hieu biet da phuong thuc, cai thien lien tuc
- Quy dinh: tien hoa AI Verify, hoa hop quoc te, mo rong quyen benh nhan, khung trach nhiem phap ly
- Dao duc: trach nhiem giai trinh thuat toan, giam thieu thien vi, yeu cau minh bach, giam sat cua con nguoi
- Kinh te: chi phi vs gia tri, bat binh dang cham soc suc khoe, mo hinh bao hiem, cau truc boi thuong

**Dinh vi cua Nova**:
- Nen tang: chuyen mon ky thuat sau, tap trung vao y te Singapore, lanh dao tuan thu, thanh cong khach hang
- Doi moi: ap dung cong nghe moi noi, phat trien truong hop su dung moi, quan he doi tac nghien cuu, cai thien lien tuc
- Mo rong thi truong: tang truong dia ly, chieu sau chuyen khoa, huong den benh nhan (can than), suc khoe cong dong

---

### Q113. AI co bao gio thay the bac si khong?

**A.** Khong, mo hinh tang cuong:

**Tai sao AI se khong thay the bac si**:
1. **Phan xet lam sang la khong the giam thieu**: Context benh nhan quan trong. Can nhan cam van hoa. Tri tue cam xuc la thiet yeu. Ly luan dao duc can thiet.
2. **Kham benh ly**: AI khong the soi. AI khong the nghe phoi. AI khong the kham. Can cham soc truc tiep.
3. **Moi quan he bac si-benh nhan**: Niem tin mat nhieu nam de xay dung. Phong cach giuong benh khong the thay the. Su dong cam la bat buoc. Tiep noi cham soc.
4. **Trach nhiem phap ly va trach nhiem giai trinh**: Trach nhiem phap ly thuoc ve bac si. Khung bao hiem. Uy quyen quy dinh. Cap phep nghe nghiep.
5. **Tuy chon cua benh nhan**: Hau het benh nhan thich ket noi con nguoi. AI nhu cong cu, khong phai nguoi thay the. Phan cap niem tin ro rang.

**Nhung gi AI co the lam**:
1. **Tang cuong truy cap kien thuc**: Truy xuat bang chung tuc thi. Tham khao cheo nhieu nguon. Cap nhat voi tai lieu.
2. **Giam ganh nang nhan thuc**: Tim kiem thong tin thuong xuyen. Ho tro tai lieu. Cac quyet dinh thuong xuyen.
3. **Cai thien tinh nhat quan**: Tieu chuan hoa tren thuc hanh tot nhat. Giam bien thien. Dam bao chat luong.
4. **Mo rong nang luc**: Tiet kiem thoi gian. Xu ly khoi luong. Bao phu ngoai gio.
5. **Ho tro giao duc**: Hoc lien tuc. Phat trien ky nang. Chuyen giao kien thuc.

**Vai tro cua bac si phat trien**:
- **It thoi gian hon cho**: Ghi nho su kien, truy xuat thong tin, tai lieu thuong xuyen, phan tich lap di lap lai
- **Nhieu thoi gian hon cho**: Tuong tac benh nhan, ra quyet dinh phuc tap, ky nang thu thuat, giang day va co van, nghien cuu va doi moi, tu duy chien luoc

**Tac dong viec lam**:
- **Nhu cau tang**: Nhieu benh nhan duoc phuc vu, nhieu bac si duoc phuc vu, cac loai thuc hanh moi (tin hoc lam sang AI)
- **Nhan manh ky nang**: Tu duy phan bien, giao tiep benh nhan, phan xet lam sang, ky nang thu thuat, tu duy chien luoc
- **Boi thuong**: Khong nen giam. Co the tang khi cac nhiem vu chuyen biet.

**Ket luan**: May tinh khong thay the nha toan hoc. Ho so benh an dien tu khong thay the bac si. Tro ly AI: cung mo hinh. Cong cu tang cuong, khong thay the.

---

### Q114. Chung toi co the mo rong sang cac ngon ngu hoac quoc gia khac khong?

**A.** Mo rong quoc te:

**Cac ngon ngu hien duoc ho tro**:
- Tieng Anh (chinh)
- Tieng Trung Quoc pho thong
- Bahasa Malaysia
- Tieng Viet
- Bahasa Indonesia

**Sap co**:
- Tieng Tamil
- Tieng Thai
- Tieng Han Quoc

**Mo rong quoc gia**:

**Singapore**: Nen tang
**Malaysia**: Moi truong quy dinh tuong tu, de dang hon
**Indonesia**: Can dia phuong hoa, thi truong lon
**Viet Nam**: Dia phuong hoa nghiem ngat hon, thi truong nho hon
**Thai Lan**: Thich ung van hoa, thi truong lon

**Moi quoc gia mo rong bao gom**:
1. **Dia phuong hoa quy dinh**: Tuan thu cu the theo quoc gia. Luat y te dia phuong. Khung bao ve du lieu. Khung quan tri AI.
2. **Dia phuong hoa ngon ngu**: Thuat ngu y te. Sac thai van hoa. Thanh ngu dia phuong. Dam bao chat luong.
3. **Dia phuong hoa lam sang**: Huong dan dia phuong (tuong duong MOH). Danh muc thuoc dia phuong. Du lieu thu nghiem dia phuong. Thuc hanh cham soc suc khoe van hoa.
4. **Dia phuong hoa co so ha tang**: Cac vung dam may dia phuong. Luu tru du lieu. Do tre mang. Ho tro dia phuong.
5. **Dia phuong hoa van hanh**: Nhom dia phuong. Quan he doi tac dia phuong. Ban hang dia phuong. Ho tro dia phuong.

**Chi phi moi quoc gia**:
- Thiet lap ban dau: 200.000-500.000 USD
- Van hanh hang nam: 200.000-500.000 USD
- Gia moi tenant: 80-90% gia Singapore

**Khuyen nghi**: Bat dau voi Singapore. Mo rong sang Malaysia (de nhat). Sau do Indonesia/Viet Nam (nam 2-3). Cac quoc gia khac dua tren co hoi.

---

### Q115. Cac tinh nang moi nao chung toi co the mong doi trong nhung nam toi?

**A.** Hien thi lo trinh:

**Nam 1 (nen tang)**:
- Nang cao ho tro da ngon ngu
- Ung dung di dong (ban de)
- Mo rong nhap bang giong noi
- Cai thien tich hop quy trinh lam viec

**Nam 2 (chieu sau chuyen khoa)**:
- **AI chuyen khoa**: Chuyen mon chuyen khoa sau hon. Suy luan cap nghien cuu. Cac agent chuyen khoa phu.
- **Tich hop lam sang**: Nhieu he thong EHR hon. Cac cong cu quy trinh lam viec tuy chinh. Ho tro tai lieu tu dong.
- **Giam sat chat luong**: Theo doi do chinh xac tot hon. Phat hien troi. Hoc thich ung.

**Nam 3 (tinh nang nang cao)**:
- **AI da phuong thuc**: Phan tich hinh anh tot hon. Phan tich am thanh (tim, phoi). Tich hop du lieu cam bien.
- **Phan tich du doan**: Du doan rui ro. Du bao ket qua. Lap ke hoach nguon luc.
- **Y hoc ca nhan hoa**: Tich hop gen. Cac yeu to loi song. Phu hop dieu tri.

**Nam 4-5 (doi moi)**:
- **Tich hop nghien cuu**: Thiet ke thu nghiem duoc ho tro boi AI. Bang chung the gioi thuc. Nghien cuu ket qua.
- **Suc khoe cong dong**: Thong tin chi tiet tong hop. Xu huong suc khoe cong cong. Chuan mo chat luong.
- **Cong cu huong den benh nhan**: Chatbot giao duc. Ho tro tu quan ly. Ho tro phan loai.

**Nam 5+ (bien gioi)**:
- **Kha nang AI nang cao**: Suy luan o cap chuyen gia. Thich ung lien tuc. Phoi hop da agent.
- **Mo hinh trien khai moi**: Tinh toan bien. Hoc lien ket. Dao tao bao ton quyen rieng tu.
- **Cong nghe moi noi**: Ung dung tinh toan luong tu. Sinh trac hoc nang cao. Hop nhat cam bien.

**Lo trinh duoc thuc day boi khach hang**:
- Phan hoi khach hang: 60% uu tien
- Xu huong nganh: 30%
- Kham pha chien luoc: 10%

**Giao tiep**:
- Lo trinh hang nam (cap cao)
- Xem truoc hang quy
- Chuong trinh beta
- Hoi dong tu van khach hang

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
