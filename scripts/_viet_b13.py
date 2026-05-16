import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 13. So sanh & Lua chon thay the

### Q101. He thong nay so sanh nhu the nao voi viec su dung ChatGPT truc tiep?

**A.** Su khac biet dang ke:

**ChatGPT** (AI tieu dung chung):
- Kien thuc rong
- Co the rat huu ich
- Re hoac mien phi cho su dung ca nhan

**AI cua chung toi** (cu the cho y te):
- Tap trung vao y te
- Duoc can cu trich dan
- Ho tro quyet dinh lam sang cu the

**Tai sao ChatGPT khong phu hop cho su dung lam sang**:
1. **Khong bao ve PHI**: ChatGPT ghi lai cac cuoc tro chuyen, co the dao tao tren dau vao. Rui ro quyen rieng tu. Khong tuan thu HIPAA.
2. **Khong co grounding trich dan**: Nghe co ve hop ly nhung khong the xac minh. Rui ro ao giac cao.
3. **Khong duoc quy dinh**: Khong duoc dang ky HSA. Khong duoc cap phep HCSA. Khong the su dung hop phap cho cac quyet dinh lam sang.
4. **Khoang trong cu the Singapore**: Khong biet cac huong dan MOH cu the. Co the khong phan anh thuc hanh dia phuong. Thuoc Singapore khong co trong danh muc thuoc.
5. **Khong co nhat ky kiem toan**: Cac cuoc tro chuyen khong duoc bao ton de tuan thu. Khong the ho tro bao cao HCSA. Khong the tai tao cac phien.
6. **Khong co tich hop EHR**: Nhap context thu cong. Khong co du lieu benh nhan. Khong the su dung FHIR.

**So sanh chi phi**:
- ChatGPT Pro: 20 USD/nguoi dung/thang = 10.000 USD/thang cho 500 bac si
- AI cua chung toi: 5.500 USD/thang cho 500 bac si
- Cong them AI cua chung toi duoc xay dung co muc dich va tuan thu

**Khi ChatGPT co the chap nhan duoc**:
- Giao duc lien tuc ca nhan (khong phai cham soc benh nhan)
- Cac cau hoi nghien cuu (khong phai cac quyet dinh lam sang)
- Cac nhiem vu hanh chinh (khong phai lam sang)
- Chi tham khao phu (khong phai lam sang)

**Ket luan**: ChatGPT la cong cu cho ca nhan; AI cua chung toi la AI y te cap doanh nghiep.

---

### Q102. Su khac biet giua he thong nay va Microsoft Copilot hoac Google Gemini la gi?

**A.** Cac truong hop su dung khac nhau:

**Microsoft Copilot cho Y te** (duoc thong bao 2024):
- AI nang suat chung
- Tich hop Microsoft Office
- Tom tat email
- Soan thao tai lieu
- Ho tro quyet dinh lam sang han che

**Google Gemini cho Y te**:
- Tuong tu Copilot
- Tich hop Google Workspace
- Tap trung hon vao nghien cuu
- Ho tro quyet dinh lam sang han che

**AI cua chung toi**:
- Duoc xay dung co muc dich cho ho tro quyet dinh lam sang
- Chuyen khoa tu ngay dau
- Tuan thu Singapore duoc tich hop san
- Thiet ke nhan thuc chuyen khoa

**So sanh**:

| Khia canh | Copilot/Gemini | AI cua chung toi |
|---|---|---|
| Muc dich su dung chinh | Nang suat | Quyet dinh lam sang |
| Cu the cho y te | Mot so | Co |
| Tuan thu Singapore | Chung | Duoc tich hop san |
| Trich dan lam sang | Mot so | Bat buoc |
| Dang ky HSA | Khong | Co |
| Tich hop EHR | Dua tren Office | FHIR truc tiep |
| Nhan thuc chuyen khoa | Khong | Co |

**Cac truong hop su dung so sanh**:

**Nhiem vu nang suat** (Copilot/Gemini tot hon):
- Soan thao thu lam sang
- Tom tat email
- Ghi chu cuoc hop
- Tao tai lieu

**Ho tro quyet dinh lam sang** (AI cua chung toi tot hon):
- Suy luan chan doan
- Khuyen nghi dieu tri
- Tuong tac thuoc
- Tu van chuyen khoa

**Phuong phap lai**:
- Dung Copilot cho nang suat
- Dung AI cua chung toi cho lam sang
- Ca hai co the cung ton tai

**So sanh chi phi**:
- Microsoft Copilot: 30 USD/nguoi dung/thang + 30 USD/nguoi dung/thang cho tinh nang Y te
- Cho 500 bac si: 30.000 USD/thang
- AI cua chung toi: 5.500 USD/thang cho 500 bac si
- Ti le chi phi: 5x dat hon cho Copilot

**Khuyen nghi**:
- AI cua chung toi cho cac quyet dinh lam sang
- Copilot/Gemini cho nang suat (giay phep rieng biet)
- Khong thay the cai nay bang cai kia

---

### Q103. Dieu gi xay ra neu chung toi muon chuyen sang nha cung cap khac?

**A.** Tinh linh hoat thap, co the quan ly:

**Cac kich ban chuyen doi**:

**Chuyen tu AWS sang Alibaba (hoac nguoc lai)**:
- Code ung dung co the chuyen: cung Python, cung mo hinh RAG
- Nhap lai: 2-4 tuan de nhung lai corpus tren vector store moi
- Chi phi chuyen doi: ~50-100k USD ky thuat
- Khong co khoa du lieu: corpus la cua ban; cac nhung co the duoc tao lai

**Chuyen sang nha cung cap AI khac hoan toan**:
- Ke hoach di cu
- Xuat du lieu o dinh dang tieu chuan
- Trien khai lai: 6-12 thang
- Chi phi: 300.000-800.000 USD

**Mang ve noi bo**:
- Tu luu tru tren Kubernetes cua benh vien
- Thay the cac dich vu quan ly AWS bang nguon mo: Qdrant cho vector, Neo4j cho do thi, vLLM cho phuc vu
- Thoi gian chuyen doi 6 thang voi van hanh song song
- Chi phi: 200.000-500.000 USD thiet lap

**Muc do khoa nha cung cap**: Thap. IP quan trong (to chuc corpus, prompt, khai thac danh gia) nam trong code Nova so huu. Cac bit cu the cho dam may (Bedrock, Model Studio) co cac tuong duong hang hoa.

**Cac dieu khoan hop dong bao ve**:
- Quyen xuat du lieu (dinh dang tieu chuan)
- Quyen so huu code (lop ung dung)
- Kha nang chuyen doi (su dung giao dien tuong thich OSS khi co the)
- Thong bao ket thuc 90 ngay

**Chi phi chuyen doi thuc te**:
- Chuyen doi AWS-Alibaba: 50-100k USD, 2-4 tuan
- Chuyen doi sang nha cung cap khac: 300-800k USD, 6-12 thang
- Mang ve noi bo: 200-500k USD, 6 thang
- Chuyen doi gian doan: 500-1.200k USD, 12 thang

**Khuyen nghi**: Chon nha cung cap de quan he doi tac, khong chi vi gia. Chi phi chuyen doi thuong thap. Gia tri quan he dai han thuong cao hon.

---

### Q104. Chung toi nen chon AWS hay Alibaba?

**A.** Ca hai deu co the cung cap giai phap. Cac yeu to quyet dinh:

**Chon AWS neu**:
- Benh vien uu tien Claude cua Anthropic (chat luong suy luan cao cap)
- Can phu hop quy dinh My/EU (HIPAA BAA, HITRUST)
- Doi ngu CNTT hien co quen thuoc voi AWS
- Uu tien thuong hieu cao cap

**Chon Alibaba neu**:
- Uu tien chi phi (re hon ~10-20%)
- Ho tro ngon ngu chau A manh hon (Qwen duoc dao tao tren du lieu chau A)
- Tich hop Singapore International tot hon
- Uu tien mo hinh Qwen

**So sanh chi phi** (cung tai trong):

| Thanh phan | AWS (A1+ Nova) | Alibaba (Qwen) |
|---|---|---|
| Mo hinh cap cuu | 70 USD | 47 USD |
| Mo hinh phuc tap | 1.470 USD | 1.160 USD |
| Nhung | 10 USD | 35 USD |
| Vector store | 350 USD | 180 USD |
| GraphRAG | 115 USD | 300 USD |
| Tong | **2.805 USD** | **~2.272 USD** |

**Chenh lech**: Alibaba re hon ~500 USD/thang (~6.000 USD/nam).

**Thuc te Singapore**: Hau het cac benh vien Singapore: AWS chiem uu the. Doi moi AI y te: Alibaba dang tang truong. Xu huong: da dam may pho bien.

**Khuyen nghi**: Chon dua tren uu tien mo hinh (Claude vs Qwen), moi quan he dam may hien co, va nhu cau tuan thu. Chenh lech chi phi hiem khi la yeu to quyet dinh.

---

### Q105. Chung toi co nen su dung ca AWS va Alibaba dong thoi khong?

**A.** Da dam may: cac can nhac:

**Tai sao da dam may**:
1. **Giam rui ro nha cung cap**: Khong co diem that bai don le. Don bay dam phan voi nha cung cap. Doc lap chien luoc.
2. **Tot nhat trong loai**: AWS cho cot loi. Alibaba cho cac dich vu cu the chau A. Su dung diem manh cua moi nha cung cap.
3. **Phuc hoi tham hoa**: Chu dong-bi dong xuyen nha cung cap. Tinh san sang toi da.
4. **Toi uu hoa dia ly**: Cac nha cung cap khac nhau manh o cac vung khac nhau. Chau A: Alibaba. My: AWS.

**Tai sao khong da dam may**:
1. **Phuc tap van hanh**: Hai bo dich vu de quan ly. Hai API de duy tri. Gap doi chi phi van hanh.
2. **Tang chi phi**: Mot so dich vu bi nhan doi. Egress mang giua cac dam may. Tong: 1,5-2x dam may don.
3. **Thoi gian ky thuat**: Nhieu cong viec tich hop. Nhieu kiem tra. Nhieu tai lieu.
4. **Phuc tap tuan thu**: Hai bo kiem toan. Hai bo chung nhan. Nhieu tai lieu.

**Cac mo hinh da dam may pho bien**:

**Chu dong-chu dong** (chi phi cao nhat, tinh san sang toi da):
- Cung tai trong chay tren ca hai
- Can bang tai
- Chi phi: 2x dam may don

**Chu dong-bi dong** (duoc khuyen nghi):
- Chinh tren mot dam may
- Sao luu tren dam may kia
- Chuyen doi cho DR
- Chi phi: 1,3-1,5x

**Lai** (su dung moi nha cung cap cho diem manh):
- AWS cho tinh toan cot loi
- Alibaba cho cac dich vu cu the
- Trien khai hon hop
- Chi phi: thay doi

**Mot dam may** (don gian nhat):
- Chon mot
- Tich hop sau
- Chi phi thap hon
- Phu thuoc nha cung cap cao hon

**Khuyen nghi**:
- Hau het benh vien: Mot dam may (AWS hoac Alibaba)
- Benh vien e ngai rui ro: Chu dong-bi dong da dam may
- Nghien cuu cap: Lai cho tot nhat trong loai
- Chi phi khoi dau: Mot dam may, mo rong sau

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
