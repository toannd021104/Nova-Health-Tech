import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
content = f.read_text(encoding='utf-8')

addendum = '''

---

## Phu luc Tuan thu: Cap nhat Quy dinh Singapore (Thang 5 nam 2026)

*Phan nay chinh sua va bo sung cac cau tra loi tuan thu trong tai lieu nay dua tren cac phat trien quy dinh nam 2024-2026.*

---

### CAP NHAT 1: AIHGle 2.0 - Huong dan AI trong Y te (MOH + HSA, 10 thang 3 nam 2026)

**La gi**: MOH va HSA cong bo chung Huong dan AI trong Y te phien ban 2.0 (AIHGle 2.0), thay the phien ban 2021. Day la **tai lieu quan tri chinh** cho AI trong y te Singapore.

**Ap dung cho 3 nhom**:
- **Nha phat trien** (nha san xuat nhu Nova): chiu trach nhiem thiet ke an toan, tai lieu, giam sat sau thi truong
- **Nha trien khai** (to chuc y te, cac benh vien khach hang cua Nova): chiu trach nhiem quan tri, danh gia rui ro, dao tao nhan vien
- **Nguoi dung** (bac si): chiu trach nhiem su dung phu hop, duy tri phan xet chuyen mon

**Hai danh muc truong hop su dung AI**:
- **Lam sang**: AI tac dong truc tiep den ket qua cham soc benh nhan (chan doan, theo doi, dieu tri). He thong cua chung toi thuoc danh muc nay.
- **Van hanh lam sang**: AI trong quy trinh lam viec lam sang nhung khong tac dong truc tiep den quyet dinh lam sang (vi du: phien am, lap lich).

**Bay nguyen tac dao duc cot loi** (tat ca phai duoc giai quyet):
1. An toan
2. Cong bang
3. Minh bach
4. Giai thich duoc
5. Manh me
6. Bao mat va bao ve du lieu
7. AI phu hop voi gia tri/muc tieu cua con nguoi

**Phan AI tao sinh**: AIHGle 2.0 giai quyet ro rang AI tao sinh (he thong cua chung toi su dung Claude/Qwen), bao gom cac chien luoc giam thieu rui ro cu the cho LLM.

**Phu hop cua he thong chung toi**: Tat ca 7 nguyen tac duoc giai quyet trong kien truc cua chung toi. Grounding trich dan bao gom minh bach/giai thich duoc. Guardrails bao gom an toan/manh me. KMS + nhat ky kiem toan bao gom bao mat/bao ve du lieu.

> Tham khao: https://www.bakermckenzie.com/en/insight/publications/2026/03/singapore-moh-and-hsa-launch-refreshed-ai-in-healthcare-guidelines

---

### CAP NHAT 2: Luat Thong tin Y te (HIA) - Thong qua thang 1 nam 2026, Hieu luc dau nam 2027

**La gi**: Luat Thong tin Y te (HIA) duoc Quoc hoi thong qua vao thang 1 nam 2026. No thay the khung NEHR tu nguyen truoc day bang **chia se du lieu y te bat buoc**.

**Yeu cau chinh**:
- Tat ca nguoi duoc cap phep HCSA (benh vien, phong kham) **phai** dong gop thong tin y te chinh vao NEHR
- Thong tin bao gom: di ung, tiem chung, chan doan, thuoc, ket qua xet nghiem, hinh anh X-quang, tom tat xuat vien
- Cac cong cu AI truy cap du lieu NEHR yeu cau su dong y cu the cua benh nhan va nhat ky kiem toan
- Tieu chuan an ninh mang va bao mat du lieu la bat buoc (xem Cap nhat 4)

**Ngay hieu luc**: Dau nam 2027 (MOH cho cac nha cung cap dich vu y te thoi gian chuan bi)

**Tac dong den he thong cua chung toi**:
- Trien khai hien tai KHONG su dung du lieu NEHR (chi du lieu noi bo benh vien)
- Khi HIA co hieu luc, cac benh vien co the muon tich hop du lieu NEHR vao cac truy van AI
- Dieu nay yeu cau: su dong y cu the cua benh nhan, nhat ky kiem toan den co quan dang ky NEHR trung uong, giam thieu du lieu
- Chung toi da lap ke hoach bo noi ket NEHR-Pro cho trien khai Nam 2 (~80.000-150.000 USD ky thuat mot lan)

**Nhung gi thay doi so voi Q&A truoc do cua chung toi**: Truoc day chung toi mo ta day la "Du luat HIE (dang cho)." Bay gio no la **luat da ban hanh** (HIA 2026), hieu luc dau nam 2027.

> Tham khao: https://www.bakermckenzie.com/en/insight/publications/2026/01/singapore-health-information-bill-passed-in-parliament

---

### CAP NHAT 3: Huong dan Tu van PDPC ve AI (1 thang 3 nam 2024)

**La gi**: Uy ban Bao ve Du lieu Ca nhan (PDPC) cong bo Huong dan Tu van ve viec su dung du lieu ca nhan trong cac he thong khuyen nghi va quyet dinh AI.

**Huong dan chinh**:
- Bao gom 3 giai doan: **phat trien** (dao tao AI), **trien khai** (B2C), **mua sam** (B2B)
- To chuc co the su dung du lieu ca nhan cho AI khi co su dong y co y nghia, HOAC dua vao cac ngoai le PDPA (vi du: cai thien kinh doanh, muc dich nghien cuu)
- Yeu cau minh bach: nguoi dung nen duoc thong bao khi du lieu ca nhan duoc su dung de dao tao he thong AI
- Luu y: Cac huong dan nay ap dung cho **AI phan biet** (he thong khuyen nghi/quyet dinh). Huong dan AI tao sinh duoc mong doi rieng biet.

**Tac dong den he thong cua chung toi**:
- Fine-tuning cua chung toi chi su dung du lieu da duoc an danh (khong co PHI) - tuan thu
- Chung toi khong dao tao tren du lieu benh nhan ma khong co su dong y ro rang - tuan thu
- Minh bach: chung toi cong bo viec su dung AI trong mau dong thuan benh nhan - tuan thu
- Mua sam: cac benh vien mua he thong cua chung toi nen xem xet cac huong dan nay de tham dinh nha cung cap

> Tham khao: https://www.pdpc.gov.sg/media-events/advisory-guidelines-on-use-of-personal-data-in-ai-recommendation-and-decision-systems-now-available

---

### CAP NHAT 4: Yeu cau Thiet yeu ve An ninh mang va Bao mat Du lieu cua MOH (Thang 4 nam 2026)

**La gi**: MOH cong bo Huong dan Yeu cau Thiet yeu ve An ninh mang va Bao mat Du lieu theo khung HIA, duoc phat trien voi su tu van cua CSA, IMDA va PDPC.

**Ap dung cho**: Tat ca cac thuc the HIA, bao gom nguoi duoc cap phep HCSA (cac benh vien khach hang cua chung toi) va cac nha dong gop NEHR.

**Ba linh vuc duoc bao gom**:

**An ninh mang (CNTT va phan mem)**:
- Cai dat cap nhat phan mem kip thoi
- Bien phap bao ve phan cung va phan mem
- Giao thuc sao luu va luu tru
- Nhan dang va bao ve tai san

**Bao mat Du lieu (thuc hanh lien quan den du lieu)**:
- Chinh sach nhan dang va bao ve thong tin y te
- Thoi han luu giu co gioi han muc dich
- Cong bo duoc uy quyen theo nguyen tac can biet
- Ngan chan chuyen giao khong dung cach

**Thuc hanh Chung (to chuc)**:
- Dao tao nhan vien
- Trach nhiem quan ly nha cung cap
- Kiem toan noi bo va xem xet bao mat dinh ky
- Xu ly dung cach
- Lap ke hoach khan cap va ung pho su co

**Tac dong den he thong cua chung toi**:
- Kien truc cua chung toi da dap ung tat ca cac yeu cau
- Quan ly nha cung cap: cac benh vien phai danh gia Nova la nha cung cap theo cac huong dan nay
- Chung toi cung cap: tai lieu bao mat, nhat ky kiem toan, bao cao kiem tra xam nhap, ISO 27001 (ke thua)
- Ung pho su co: runbooks va bao phu SRE 24/7 cua chung toi dap ung yeu cau lap ke hoach khan cap

> Tham khao: https://www.bakermckenzie.com/en/insight/publications/2026/04/singapore-moh-publishes-cybersecurity-and-data-security

---

### CAP NHAT 5: Nen tang SHARE cua HSA (Thang 7 nam 2025)

**La gi**: HSA chuyen tu MEDICS sang SHARE (Submission for Harmonized Evaluation and Registration) cho cac ho so thiet bi y te vao thang 7 nam 2025.

**Tac dong den he thong cua chung toi**:
- Tat ca cac ho so SaMD (Phan mem la Thiet bi Y te) moi phai su dung SHARE
- Dang ky HSA Hang B cua chung toi nen duoc nop qua SHARE
- Khong co thay doi ve tieu chi phan loai hoac yeu cau - chi co cong thong tin nop don thay doi

---

### CAP NHAT 6: Singapore Dat Hang Cao Nhat cua WHO ve Quy dinh Thiet bi Y te (Thang 3 nam 2026)

**Y nghia**: Singapore tro thanh Quoc gia Thanh vien WHO dau tien dat duoc phan loai cao nhat ve quy dinh thiet bi y te. Dieu nay bao hieu:
- Khung quy dinh cua Singapore duoc cong nhan quoc te la hang dau the gioi
- Huong dan SaMD cua HSA phu hop voi thuc hanh tot nhat toan cau
- De dang hon trong viec cong nhan lan nhau voi cac quoc gia hang cao khac (FDA My, EU, TGA Uc)
- Uy tin manh me hon cho cac thiet bi y te duoc dang ky tai Singapore tren toan cau

**Tac dong den he thong cua chung toi**:
- Dang ky HSA Hang B cua chung toi co gia tri quoc te cao hon
- De dang mo rong sang cac thi truong khac su dung dang ky Singapore lam tham chieu
- Chung to cam ket cua Singapore doi voi giam sat thiet bi y te AI nghiem ngat

---

### TOM TAT: Danh sach Kiem tra Tuan thu (Cap nhat Thang 5 nam 2026)

| Quy dinh | Trang thai | Vi tri cua chung toi |
|---|---|---|
| PDPA (2012, sua doi 2020) | Hieu luc | Tuan thu: che giau PHI, KMS, nhat ky kiem toan, DPO |
| HCSA 2020 | Hieu luc | Tuan thu: benh vien trien khai can giay phep HCSA |
| AIHGle 2.0 (Thang 3 nam 2026) | Hieu luc | Tuan thu: tat ca 7 nguyen tac duoc giai quyet trong kien truc |
| HIA 2026 | Da ban hanh, hieu luc dau 2027 | Da lap ke hoach: bo noi ket NEHR cho Nam 2 |
| Huong dan AI PDPC (Thang 3 nam 2024) | Hieu luc | Tuan thu: du lieu dao tao da duoc an danh, minh bach |
| Yeu cau Thiet yeu An ninh mang MOH (Thang 4 nam 2026) | Hieu luc | Tuan thu: tat ca yeu cau duoc dap ung |
| HSA SaMD Hang B | Bat buoc | Da lap ke hoach: nop qua nen tang SHARE |
| Luat An ninh mang 2018 (CII) | Hieu luc cho benh vien CII | Tuan thu: Anti-DDoS, WAF, nhat ky kiem toan, ung pho su co |
| IMDA AI Verify | Tu nguyen (thuc te bat buoc cho hop dong chinh phu) | Da lap ke hoach: tu danh gia vao Thang 5 |
| ISO 27001 / SOC 2 | Hieu luc | Ke thua tu AWS/Alibaba |

'''

f.write_text(content + addendum, encoding='utf-8')
print('Addendum written, new size:', f.stat().st_size)
