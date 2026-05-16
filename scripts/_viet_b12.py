import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 12. Quan ly rui ro

### Q91. Diem that bai don le lon nhat cua chung toi la gi?

**A.** Danh gia trung thuc:

**SPOF 1: Vung nha cung cap dam may** (cao nhat)
- AWS/Alibaba Singapore vung bi ngung hoat dong
- Tat ca cac dich vu khong co san
- Giam thieu: chuyen doi du phong xuyen vung (chu dong-bi dong)
- Rui ro: 1-2 gio ngung hoat dong moi nam (uoc tinh)

**SPOF 2: Bedrock/Model Studio**
- Dich vu LLM khong co san
- Chuc nang cot loi bi mat
- Giam thieu: mo hinh du phong + phan hoi da cache
- Rui ro: 0,5-1 gio dich vu bi suy giam moi nam

**SPOF 3: OpenSearch / Vector Search**
- Truy xuat kien thuc bi ngung
- Khong the can cu cau tra loi
- Giam thieu: ket qua da cache
- Rui ro: ngung hoat dong ngan han co the xay ra

**SPOF 4: Trien khai cua Nova**
- Loi code trong duong dan quan trong
- Trien khai that bai
- Giam thieu: phat hanh canary, rollback
- Rui ro: han che; trien khai co kiem soat

**SPOF 5: API ben ngoai (WHO, ICD-11)**
- Du lieu nguon khong co san
- Cap nhat bi tri hoan
- Giam thieu: du lieu da cache
- Rui ro: khong anh huong den dich vu (chi tinh moi du lieu)

**Rui ro SPOF tong hop**:
- Tong thoi gian ngung hoat dong hang nam ket hop: <1% (8,76 gio)
- Hau het ngung hoat dong: <30 phut
- Ngung hoat dong nghiem trong: hiem

**Tuy chon cua benh vien**:
- Chap nhan SLA tieu chuan (99,9%)
- Mua SLA cao hon: 99,95% hoac 99,99% (cao cap)
- Trang web DR rieng: tinh san sang cao nhat, chi phi cao nhat

---

### Q92. Kich ban ngung hoat dong xau nhat la gi?

**A.** Lich su thuc te:

**Kich ban: Ngung hoat dong hoan toan vung AWS Singapore**

**Xac suat**: Rat thap (su co lon cuoi cung: ~5 nam truoc)

**Tac dong**:
- Dich vu khong co san
- Tat ca bac si mat quyen truy cap AI
- Chi quy trinh lam viec thu cong
- Nhat ky kiem toan co the bi tri hoan hoac mat

**Uoc tinh thoi gian**:
- Hau het ngung hoat dong: <30 phut
- Ngung hoat dong vung (hiem): 2-6 gio
- Ngung hoat dong nghiem trong (rat hiem): 12-24 gio

**Ung pho cua benh vien**:
- Kich hoat quy trinh lam viec thu cong
- Thong bao Nova (trang trang thai)
- Ghi lai bat ky tac dong lam sang nao
- Tiep tuc khi dich vu duoc khoi phuc

**Ung pho cua Nova**:
- Cap nhat trang thai theo thoi gian thuc
- Tin dung dich vu theo SLA
- Bao cao sau su co
- Cac cai tien duoc thuc hien

**Chi phi ngung hoat dong xau nhat**:
- Truc tiep: khong (quy trinh lam viec thu cong tiep tuc)
- Nang suat: benh vien chiu (duoc bao hiem)
- Tin dung SLA: ap dung
- Danh tieng: toi thieu (ngung hoat dong toan nganh)

**Bao hiem**:
- Bao hiem gian doan kinh doanh: ~10.000 USD/nam cho bao hiem 500k USD
- Bao gom: mat doanh thu trong thoi gian ngung hoat dong keo dai
- Quyet dinh cua benh vien

**Lich su su co thuc te** (cac he thong tuong tu):
- Ngung hoat dong AWS S3 2017: 4 gio
- Ngung hoat dong AWS Singapore 2023: 3 gio
- Su co Bedrock: <30 phut dien hinh

---

### Q93. Dieu gi xay ra neu chung toi dot ngot can mo rong len 10 lan so bac si?

**A.** Kha nang mo rong:

**Nang luc hien tai**:
- Moi tenant: 500-1000 bac si
- Da tenant: mo rong tuyen tinh
- Ly thuyet: hang nghin tenant

**Cac kich ban tang truong**:

**Trong 1 gio**: Tang truong 10% (tu dong mo rong)
**Trong 1 ngay**: Tang truong 50% (mo rong thu cong)
**Trong 1 tuan**: Tang truong 100% (xem xet kien truc)
**Trong 1 thang**: Tang truong 5x (cap phep nang luc)
**Trong 3 thang**: Tang truong 10x (lap ke hoach + mua sam)

**Kinh te mo rong**:

| Bac si | Chi phi/thang | Chi phi/bac si/thang |
|---|---|---|
| 100 | 2.500-4.000 USD | 25-40 USD |
| 500 (dien hinh) | 5.500 USD | 11 USD |
| 1.000 | 8.000-12.000 USD | 8-12 USD |
| 5.000 | 25.000-40.000 USD | 5-8 USD |

**Kinh te quy mo**: Chi phi moi bac si giam khi mo rong vi chi phi co dinh duoc phan bo.

**Tac dong hieu suat**:
- Trong kien truc hien tai: cung muc tieu do tre
- O quy mo rat cao (10x+): co the can kien truc khac nhau
- Dung luong danh rieng
- Toi uu hoa chuyen biet

**Khuyen nghi**:
- Bat dau voi 500 bac si
- Lap ke hoach cho 1.000 trong 12 thang
- Thao luan 5.000+ neu mo rong duoc ky vong

---

### Q94. Dieu gi xay ra neu AI dua ra khuyen nghi trai voi giao thuc cua benh vien?

**A.** Xu ly xung dot giao thuc:

**Tai sao xung dot xay ra**:
1. **WHO vs giao thuc benh vien**: WHO: tieu chuan toan cau. Benh vien: bien the dia phuong. Ca hai co the co bang chung.
2. **Cac quan diem chuyen khoa khac nhau**: AI trich dan huong dan chung. Chuyen gia chuyen khoa khong dong y. Ca hai co gia tri.
3. **Cac su khac biet dua tren tai nguyen**: Giao thuc tieu chuan: thuoc A. Benh vien dung: thuoc B (danh muc thuoc). Hieu qua tuong duong.
4. **Bang chung moi vs thuc hanh da thiet lap**: Nghien cuu moi nhat: thay doi khuyen nghi. Benh vien chua cap nhat giao thuc. AI biet bang chung moi.

**Xu ly xung dot**:

**Mo hinh 1: Uu tien benh vien**
- AI tuan theo giao thuc benh vien khi biet
- Ghi chu bang chung thay the
- Banner: "Giao thuc benh vien duoc uu tien"

**Mo hinh 2: Minh bach xung dot**
- AI hien thi ca hai
- Ghi nhan ro rang
- Bac si quyet dinh

**Mo hinh 3: Dua tren bang chung**
- AI hien thi bang chung manh nhat
- Giao thuc benh vien duoc hien thi
- Bat dong duoc ghi lai

**Trien khai**:
- Giao thuc benh vien duoc nhap vao KB
- Uu tien truy xuat cao hon
- Phat hien xung dot
- Hien thi minh bach

**Quan tri benh vien**:
- Quy trinh cap nhat giao thuc
- Xem xet bang chung hang quy
- Lam moi giao thuc benh vien
- AI nhap cac cap nhat

**Thuc hanh tot nhat**:
- Giu giao thuc cap nhat
- Tham gia voi phan hoi AI
- Ghi lai ly luan khi ghi de
- Cai thien lien tuc

---

### Q95. Chung toi co "cong tat" neu co gi do xay ra nghiem trong khong?

**A.** Ung pho khan cap nhieu cap:

**Cap 1: Tam dung cap bac si**
- Bac si ca nhan co the vo hieu hoa AI cho cac truong hop cua ho
- Nut "Vo hieu hoa AI" trong EHR
- Hieu qua: cac truy van cua ho bo qua AI, quy trinh lam viec thu cong duoc khoi phuc
- Tham quyen quyet dinh: bac si

**Cap 2: Tam dung cap khoa**
- Truong khoa co the vo hieu hoa cho toan khoa
- "Vo hieu hoa khoa" qua cong thong tin quan tri
- Hieu qua: tat ca cac truy van khoa bo qua AI
- Tham quyen quyet dinh: truong khoa

**Cap 3: Tam dung cap benh vien**
- Giam doc Y te co the vo hieu hoa AI cho toan benh vien
- Hieu qua: AI tra ve "Dich vu tam thoi khong co san" cho tat ca cac truy van
- Quy trinh lam viec thu cong chi
- Tham quyen quyet dinh: Giam doc Y te (voi su dong y cua VP/CMO)
- Thong bao: ngay lap tuc den Nova; 4 gio den tat ca bac si

**Cap 4: Tam dung xuyen tenant**
- Nova SRE co the vo hieu hoa cho tat ca cac tenant neu phat hien van de he thong
- Vi du: loi nghiem trong, su co bao mat
- Hieu qua: dich vu khong co san toan cau
- Tham quyen quyet dinh: VP Ky thuat + Can bo Tuan thu
- Thong bao: 1 gio den tat ca lanh dao benh vien

**Cap 5: Tat hoan toan**
- Van de quy dinh hoac an toan nghiem trong
- Hieu qua: dich vu hoan toan khong co san
- Tham quyen quyet dinh: CEO + Co van Phap ly
- Thong bao: co quan quan ly, tat ca benh vien, tuyen bo cong khai

**Tieu chi kich hoat** (duoc xac dinh trong ke hoach ung pho su co):
- Cap 1-2: tieu chuan/tuy chon cua bac si
- Cap 3: van de cu the cua benh vien hoac lo ngai tuan thu
- Cap 4: van de he thong, su co bao mat
- Cap 5: vi pham quy dinh nghiem trong, phan quyet CEO

**Quy trinh khoi dong lai**:
- Moi cap co quy trinh khoi dong lai duoc ghi lai
- Cac xac thuc bat buoc truoc khi khoi dong lai
- Xem xet sau su co bat buoc

---

### Q96. Ke hoach phuc hoi tham hoa cua chung toi la gi?

**A.** Chien luoc phuc hoi nhieu lop:

**Loi AZ don le (pho bien nhat)**:
- AWS co 3 vung kha dung (AZ) tai Singapore
- Trien khai cua chung toi su dung 2-3 AZ theo mac dinh
- Loi AZ don le: chuyen doi tu dong, ~30 giay gian doan
- RPO: 0 (sao chep dong bo)
- RTO: 1-2 phut

**Loi dich vu don le**:
- Bedrock bi ngung: Tu dong chuyen doi sang vung thay the (voi su dong y cua benh vien) HOAC suy giam nhe nhan
- OpenSearch bi ngung: Ket qua da cache + chuc nang giam
- Neptune bi ngung: Chi truy xuat vector (chap nhan duoc suy giam)
- RPO: 5 phut
- RTO: 10-30 phut

**Loi vung (hiem)**:
- Tat ca AWS Singapore khong co san (cuc ky hiem)
- Ung pho cua chung toi:
  - Phuong an A: Chuyen doi xuyen vung sang AWS Sydney (voi su dong y cua benh nhan, vi du du lieu roi Singapore)
  - Phuong an B: Dich vu khong co san cho den khi AWS phuc hoi
  - Benh vien chon chinh sach truoc
- RPO: 1 gio
- RTO: 2-4 gio (Phuong an A); thoi gian ngung hoat dong AWS (Phuong an B)

**Thiet lap phuc hoi tham hoa**:

**Chu dong-bi dong (duoc khuyen nghi)**:
- Vung chinh: Singapore
- Vung sao luu: Sydney (hoac lua chon cua benh vien)
- Sao chep hang ngay
- Thoi gian chuyen doi: 2-4 gio
- Chi phi: +500-1.500 USD/thang/tenant co so ha tang

**Chu dong-chu dong (tinh san sang cao nhat)**:
- Cung tai trong chay tren ca hai vung
- Chuyen doi tuc thi
- Chi phi: 2x co so ha tang
- Truong hop su dung: chi cho cac benh vien yeu cau 99,99%+ thoi gian hoat dong

**Khong co DR (don gian nhat)**:
- Chi mot vung
- Chap nhan thoi gian ngung hoat dong trong khi ngung hoat dong vung
- Chi phi: 1x co so ha tang
- Chap nhan duoc chi cho cac truong hop su dung khong quan trong

**Lich kiem tra DR**:
- Bai tap DR hang quy
- Mo phong loi vung
- Do RPO va RTO thuc te
- Cai thien runbook dua tren cac phat hien

**Chi phi DR**:
- Thiet lap chu dong-bi dong: +500-1.500 USD/thang/tenant
- Bai tap DR hang quy: 5.000 USD/bai tap
- Kiem toan DR hang nam ben ngoai: 15.000 USD

---

### Q97. Dieu gi xay ra neu AI dua ra khuyen nghi sai va benh nhan bi ton hai?

**A.** Da duoc tra loi o Q7. Xem chi tiet o do.

---

### Q98. Lam the nao de xu ly tinh trang bac si phu thuoc qua muc vao AI?

**A.** Cac chien luoc chong phu thuoc:

**Rui ro phu thuoc**:
1. **Giam ky nang bac si**: Phu thuoc vao AI ma khong suy nghi. Giam thieu: AI yeu cau xem xet trich dan; giao duc.
2. **Khoa vao quy trinh lam viec**: Quy trinh lam viec phu thuoc vao AI. Giam thieu: quy trinh lam viec thu cong song song duoc duy tri.
3. **Khoang trong kien thuc lam sang**: Bac si khong hoc sau. Giam thieu: AI giai thich ly luan; che do giao duc.
4. **Phan xet lam sang**: Bac si khong phat trien phan xet. Giam thieu: AI la ho tro quyet dinh; bac si quyet dinh.

**Thiet ke chong phu thuoc**:
- **Xem xet trich dan bat buoc**: AI hien thi "Dua tren [nguon]". Bac si phai doc it nhat phan khuyen nghi.
- **Mo hinh tu choi**: AI tu choi khi KB thieu du lieu. Bac si phai phat trien phan xet.
- **Chi bao do tin cay**: AI hien thi muc do chac chan. Bac si hoc khi nao nen tin tuong.
- **Kiem tra mu dinh ky**: Hang quy: 50 cau hoi, ket qua duoc xem xet boi can bo an toan lam sang. Neu bac si chap nhan cau tra loi AI ma khong co tu duy phan bien, siet chat guardrails hoac them banner "day la bat thuong, vui long xac minh".

**Quan tri benh vien**:
- Tiep tuc cac chuong trinh giao duc
- Dao tao quy trinh lam viec thu cong
- AI la cong cu, khong phai nguoi thay the
- Phan xet lam sang la toi cao

**Ket qua dai han**:
- Cac bac si tot hon (nhieu kien thuc truy cap hon)
- Hieu qua hon (tiet kiem thoi gian)
- Ket qua tot hon (dua tren bang chung)
- Thuc hanh ben vung

---

### Q99. Dieu gi xay ra neu co su kien bao chi tieu cuc lien quan den AI y te?

**A.** Ke hoach truyen thong khung hoang:

**Cac kich ban co the xay ra**:
1. **Su kien bat loi lien quan den AI**: Ton hai benh nhan bi cao buoc do AI. Truyen thong dua tin. Kiem tra quy dinh.
2. **Moi lo ngai AI toan nganh**: Nha cung cap khac that bai. Phan ung tieu cuc chung. Co quan quan ly phan hoi.
3. **Van de tuan thu**: Phat hien kiem toan duoc cong bo. Vi pham quyen rieng tu bi cao buoc. Tac dong den co phieu/danh tieng.
4. **Van de nha cung cap**: Scandal Anthropic/Alibaba. Lo ngai ve du lieu dao tao. Moi lo ngai dia chinh tri.

**Khung ung pho**:

**Hanh dong ngay lap tuc** (trong vong 1 gio):
1. Kich hoat nhom khung hoang
2. Thu thap thong tin
3. Bao ton bang chung
4. Giam sat truyen thong

**Trong vong 4 gio**:
5. Truyen thong noi bo: tat ca nhan vien
6. Thong bao khach hang: cac tenant benh vien
7. Canh bao cac ben lien quan: lanh dao, nha dau tu

**Trong vong 24 gio**:
8. Tuyen bo cong khai (thuc te)
9. Q&A voi truyen thong
10. Thong bao co quan quan ly (neu bat buoc)

**Ngay 2-7**:
11. Bao cao dieu tra chi tiet
12. Tiep tuc truyen thong
13. Cac hanh dong khac phuc

**Phuc hoi dai han**:
14. Cai thien duoc chung minh
15. Kiem toan doc lap
16. Bao cao cong khai
17. Xay dung lai niem tin

**Vat lieu duoc chuan bi san**:
- Cac tuyen bo giu cho (mau)
- Tai lieu FAQ
- Nguoi phat ngon duoc xac dinh
- Dao tao truyen thong da hoan thanh

**Chi phi**:
- Chuan bi khung hoang: 50.000-100.000 USD mot lan
- Ung pho khung hoang: 100.000-500.000 USD moi su co
- Bao hiem: 10.000-30.000 USD/nam cho bao hiem 5 trieu USD

---

### Q100. Cau hoi cuoi cung: Dieu quan trong nhat can hieu ve AI nay la gi?

**A.** AI la ho tro quyet dinh, khong phai nguoi ra quyet dinh.

**Cac nguyen tac chinh**:

**1. Tang cuong, khong thay the**:
- Bac si van la nguoi chinh
- AI ho tro suy nghi cua ho
- Quyet dinh cuoi cung: con nguoi

**2. Duoc can cu trich dan**:
- Moi khang dinh duoc trich dan
- Nguon co the xac minh
- Niem tin qua minh bach

**3. Tu choi khi khong chac chan**:
- AI tu choi khi KB thieu du lieu
- Trung thuc ve han che
- Bao ton cho an toan

**4. Ban dia Singapore**:
- Tuan thu PDPA
- Phu hop HCSA
- Nhan thuc boi canh dia phuong
- Luu tru du lieu duoc dam bao

**5. ROI tich cuc**:
- Tiet kiem thoi gian dang ke
- Ket qua tot hon
- Chi phi hop ly
- Gia tri dai han

**6. Lien tuc phat trien**:
- Bang chung moi nhat
- Huong dan duoc cap nhat
- Kha nang cai thien
- Hoc lien tuc

**7. Lay con nguoi lam trung tam**:
- Than thien voi bac si
- An toan cho benh nhan
- Khung dao duc
- Nhan cam van hoa

**Ket luan**: Duoc thuc hien dung, AI nay giup cac bac si gioi tro nen tot hon, nhanh hon va tu tin hon. Duoc thuc hien sai, no co the tao ra rui ro. Kien truc, tuan thu va giam sat lien tuc cua chung toi duoc thiet ke de thuc hien dung.

Quyet dinh khong phai la "chung toi co nen ap dung AI khong?" ma la "chung toi ap dung AI tot nhu the nao?"

Chung toi cam ket giup ban thuc hien tot.

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
