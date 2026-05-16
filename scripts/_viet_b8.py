import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 6. Do chinh xac & Tin cay

### Q61. AI chinh xac den muc nao? "Do chinh xac" co nghia la gi doi voi AI y te?

**A.** Do chinh xac da chieu:

**1. Do chinh xac trich dan**: Moi khang dinh trich dan nguon thuc su co the truy xuat. Do luong: 100% trong PoC. Nhi phan: co hoac khong.

**2. Do chinh xac grounding**: Cau tra loi nhat quan voi cac nguon duoc trich dan. Do luong boi diem grounding (0-1). Nguong: >=0,7. Trung binh PoC: 0,85.

**3. Do chinh xac thuc te**: Cau tra loi dung ve mat thuc te so voi tieu chuan vang. Do luong boi hoi dong bac si. Muc tieu: >=95% cho cac truong hop khong bien.

**4. Do lien quan lam sang**: Cau tra loi giai quyet cau hoi lam sang thuc te. Do luong boi thumbs up/down cua bac si. Muc tieu: >=90%.

**5. Tinh cap nhat**: Cau tra loi phan anh cac huong dan hien tai. Do luong boi kiem tra so voi WHO/MOH hien tai. Muc tieu: 100% cho cac cau hoi dua tren huong dan.

**Muc tieu do chinh xac cu the**:

| Loai truy van | Muc tieu do chinh xac | Ket qua PoC |
|---|---|---|
| Lieu luong thuoc | >=99% | 99,5% |
| Tieu chi chan doan | >=97% | 98% |
| Giao thuc dieu tri | >=95% | 96% |
| Chan doan phan biet | >=90% | 92% |
| Cac truong hop bien (benh hiem gap) | >=80% | 85% |

**Kiem soat chat luong**:
- Kiem tra truoc khi trien khai: 1000+ cau hoi duoc bac si kiem tra
- Giam sat san xuat: mau ngau nhien 100 truy van hang ngay
- Phan hoi bac si: thumbs up/down tren moi cau tra loi
- Kiem toan hang quy: xem xet ben ngoai

---

### Q62. Chung toi co the tin tuong AI hon UpToDate hoac cac co so du lieu tham khao khac khong?

**A.** Cac ho so tin cay khac nhau:

**Diem manh cua UpToDate**:
- Duoc giam tuyen thu cong boi cac bien tap vien bac si
- Bao thu, duoc kiem tra ky
- Tieu chuan nganh
- Lich su 25+ nam
- Toan dien

**Diem yeu cua UpToDate**:
- Khong theo thoi gian thuc (cap nhat hang thang)
- Khong tich hop voi du lieu benh nhan
- Chung, khong cu the cho benh nhan
- Cham de doc
- Khong co kien thuc thu nghiem noi bo

**Diem manh cua AI cua chung toi**:
- Theo thoi gian thuc (ICD-11 hang ngay, WHO hang thang)
- Suy luan cu the cho benh nhan (voi context EHR)
- Tich hop thu nghiem noi bo
- Toc do (2-3 giay vs 5+ phut)
- Tim kiem tren tat ca cac nguon dong thoi

**Diem yeu cua AI cua chung toi**:
- Cong nghe moi hon, it lich su nganh hon
- Rui ro ao giac (duoc giam thieu nhung khong bang khong)
- Do chinh xac trich dan phu thuoc vao chat luong truy xuat
- Co the bo lo cac chinh sua gan day

**Khung so sanh**:

| Khia canh | UpToDate | AI cua chung toi |
|---|---|---|
| Do chinh xac tren cac cau hoi tieu chuan | 99% | 95-98% |
| Do chinh xac tren cac truong hop phuc tap/bien | 95% | 85-92% |
| Toc do | 5-15 phut | 2-15 giay |
| Cu the cho benh nhan | Khong | Co |
| Tich hop du lieu noi bo | Khong | Co |
| Tan suat cap nhat | Hang thang | Hang ngay |
| Chi phi moi truy van | 0,05-0,15 USD | 0,001-0,013 USD |
| Lich su | 25+ nam | 1-2 nam |

**Phuong phap lai (duoc khuyen nghi)**:
- Dung ca hai
- AI cho truy cap nhanh + cu the cho benh nhan
- UpToDate cho nghien cuu sau va xac minh
- Bac si hoc khi nao nen dung cai nao

---

### Q63. Loi lon nhat AI co the mac trong thuc hanh lam sang la gi?

**A.** Kiem ke rui ro thuc te:

**Danh muc rui ro**:

**1. Trich dan huong dan loi thoi**
- Nguyen nhan: cache cu hoac huong dan duoc cap nhat sau cache
- Tac dong: bac si hanh dong theo thong tin loi thoi
- Xac suat: thap (vo hieu hoa cache hoat dong)
- Giam thieu: kiem tra huong dan theo thoi gian thuc

**2. Lieu luong thuoc sai**
- Nguyen nhan: ao giac hoac loi truy xuat
- Tac dong: loi thuoc
- Xac suat: rat thap (du lieu thuoc duoc giam tuyen ky)
- Giam thieu: kiem tra cheo voi co so du lieu duoc phe duyet

**3. Bo sot chong chi dinh**
- Nguyen nhan: AI khong co lich su benh nhan day du
- Tac dong: phan ung bat loi tiem nang
- Xac suat: trung binh (phu thuoc vao tich hop du lieu)
- Giam thieu: kiem tra chong chi dinh ro rang, tich hop lich su benh nhan

**4. Giai thich trieu chung sai**
- Nguyen nhan: cach dien dat cua bac si mo ho
- Tac dong: chan doan phan biet sai
- Xac suat: thap (AI yeu cau lam ro)
- Giam thieu: cac mau truy van co cau truc

**5. Khuyen nghi trai voi huong dan**
- Nguyen nhan: dao tao loi thoi, truy xuat sai
- Tac dong: bac si bi dan dat sai
- Xac suat: thap (trich dan buoc grounding)
- Giam thieu: kiem tra kep so voi huong dan hien tai

**Cac su co thuc te co kha nang nhat**:
- Tu choi khi cau tra loi co san (am tinh gia): phien phuc nhung an toan
- Cau tra loi da cache loi thoi (hiem): duoc giam thieu boi vo hieu hoa
- Van de dien dat nho (chu quan): tac dong thap

**Cac su co co hau qua nhat**:
- Bo sot tuong tac thuoc hiem (hiem, nghiem trong)
- Khuyen nghi trai voi huong dan hien tai (trung binh)
- Ro PHI (hiem nhung rat nghiem trong)

**Thuc te**: Bac si con nguoi cung mac loi. Nghien cuu cho thay: bac si dung ~80-90% tren cac truong hop phuc tap. Tro ly AI co the giam loi chan doan ~10-15%. Rong: ket qua tot hon, khong hoan hao.

---

### Q64. Lam the nao de biet neu AI dang cho ket qua khac nhau cho cung mot cau hoi?

**A.** Giam sat nhat quan:

**Tai sao cau tra loi co the khac nhau**:

**1. Tao ngau nhien (nhiet do)**
- AI co cai dat nhiet do
- Mac dinh: 0,1 (thap; hau het nhat quan)
- 0 = xac dinh (luon cung mot cau tra loi)
- 0,5+ = sang tao (thay doi)

**Cai dat cua chung toi**: nhiet do = 0,1, ban xac dinh.

**2. Trang thai cache**
- Truy van dau tien: tao moi
- Truy van thu hai (trong TTL cache): da cache, giong het
- Sau khi cache het han: duoc tao lai, co the khac mot chut

**3. Cap nhat co so kien thuc**
- WHO xuat ban huong dan moi luc 02:00 SGT
- Cau hoi luc 01:50: huong dan cu duoc trich dan
- Cau hoi luc 02:10: huong dan moi duoc trich dan
- Day la hanh vi chinh xac

**4. Bien thien truy xuat ngau nhien**
- Tim kiem vector co tinh ngau nhien nho
- Top 5 chunk co the khac nhau tren cac truong hop bien
- Cac chunk khac nhau -> cau tra loi khac nhau mot chut

**5. Cap nhat phien ban mo hinh**
- Hang quy: nang cap mo hinh
- Truoc/sau nang cap: cau tra loi co the phat trien

**Bien thien chap nhan duoc**:
- Khuyen nghi lam sang nhat quan
- Cach dien dat co the khac nhau
- Trich dan phai tuong tu (cung cac nguon chinh)
- Bat dong ve khuyen nghi chinh: dieu tra

**Giam sat nhat quan**:
- Cac cap ngau nhien: cung cau hoi duoc hoi cach nhau 24 gio
- Xem xet thu cong cac su khac biet
- Theo doi: ~5% cap co su khac biet nho (chap nhan duoc)
- Theo doi: ~0,5% co su khac biet co y nghia (dieu tra)

**Kha nang tai tao**:
- De kiem toan/phap ly: phien chinh xac co the duoc tai tao
- "AI da noi gi voi Bac si Linh luc 14:32 SGT ngay 15 thang 5?"
- 100% co the tai tao tu nhat ky kiem toan

---

### Q65. Lam the nao de kiem tra AI truoc khi trien khai cho benh nhan thuc su?

**A.** Xac thuc nhieu giai doan:

**Giai doan 1: Kiem tra don vi (ky thuat)**
- Kiem tra cap thanh phan
- Bao gom: che giau PHI, truy xuat, xac thuc trich dan
- 1000+ truong hop kiem tra
- Chay tren moi thay doi code
- Ti le dat: 100% bat buoc

**Giai doan 2: Kiem tra tich hop**
- Kich ban kiem tra dau cuoi
- Bao gom: lane cap cuu, lane phuc tap, cache, kiem toan
- 200+ kich ban
- Chay hang dem
- Ti le dat: 100% bat buoc

**Giai doan 3: Kiem tra do chinh xac lam sang**
- Cac cau hoi y te tieu chuan vang
- Duoc giam tuyen boi hoi dong tu van lam sang
- Bao gom: 12 khoa, 1000+ cau hoi
- Ti le dat: >=95% bat buoc de trien khai

**Giai doan 4: Kiem tra doi nghich**
- Red team co gang pha vo he thong
- Tiem nhap prompt, kich hoat ao giac
- Ti le dat: >=98% thanh cong phong thu

**Giai doan 5: Trien khai thi diem**
- Nhom nho bac si (vi du: 20)
- Cac truong hop han che (goi y chi doc)
- Kiem tra thuc te trong 30 ngay
- Phan hoi duoc tich hop

**Giai doan 6: Trien khai theo giai doan**
- Tung khoa mot
- Moi giai doan: on dinh 30 ngay
- Cac van de duoc giai quyet truoc giai doan tiep theo

**Giai doan 7: San xuat**
- Trien khai toan benh vien
- Giam sat lien tuc
- Kiem toan do chinh xac hang quy

**Danh muc kiem tra cu the**:

**Lien quan den thuoc**:
- Lieu luong cho cac thuoc pho bien
- Tuong tac thuoc
- Lieu luong than/gan
- An toan thai ky/cho con bu

**Lien quan den chan doan**:
- Chan doan phan biet
- Tieu chi chan doan
- Huong dan hinh anh
- Giai thich ket qua xet nghiem

**Lien quan den dieu tri**:
- Khuyen nghi dieu tri hang dau
- Dieu tri hang hai khi that bai dieu tri
- Lieu phap ket hop
- Cac quan the dac biet

**Lien quan den tuan thu**:
- Tu choi cac yeu cau khong phu hop
- Khong tiet lo PHI
- Tuan theo huong dan
- Cung cap trich dan

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
