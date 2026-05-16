import pathlib

OUT = pathlib.Path("docs/Client_QA_500_Tieng_Viet.md")

QA = [
("Q1", "Tai sao benh vien can tro ly AI lam sang? Bac si da co UpToDate roi.",
"""UpToDate la cong cu tra cuu tot nhung can bac si biet tim gi va doc nhieu bai. Tro ly AI khac o 3 diem:

1. **Tong hop nhieu nguon trong vai giay.** Thay vi mat 5 phut doc chuong WHO, bai PubMed va bao cao thu nghiem noi bo, tro ly tra ve 1 doan van co trich dan trong 2 giay.
2. **Hoat dong ngay trong khi kham benh.** Bac si dang co benh nhan truoc mat khong the dung lai 5 phut. Phan hoi 2 giay cho phep dung ngay trong phong kham.
3. **Biet du lieu thu nghiem noi bo.** UpToDate khong biet bao cao thu nghiem noi bo cua benh vien. Tro ly index ca hai cung voi WHO va ICD-11.

**Tinh toan kinh doanh**:
```
500 bac si x 10 phut/ngay x 22 ngay = 110.000 phut/thang
= 1.833 gio/thang x 80 USD/gio = 146.640 USD/thang tiet kiem
```
He thong chi phi 2.800-5.500 USD/thang. Hoan von trong chung 1 tuan."""),

("Q2", "ROI thuc su la bao nhieu?",
"""Ba nguon loi nhuan do luong duoc:

1. **Thoi gian tiet kiem moi truy van**: Bac si mat trung binh 6 phut tra cuu tai lieu. Tro ly tra loi trong 2-12 giay. Tiet kiem: ~5 phut/truy van.
2. **Mat do su dung**: 40 truy van/bac si/ngay x 500 bac si = 20.000 truy van/ngay, 600.000/thang.
3. **Gia tri hang nam** (chi phi bac si 80 USD/gio):

```
600.000 truy van/thang x 5 phut x (80 USD/gio / 60 phut) = 4.000.000 USD/thang
x 12 thang = 48.000.000 USD/nam moi benh vien
```

**Chi phi**: 2.800-5.500 USD/thang x 12 = 33.600-66.000 USD/nam.
**Ti le ROI**: ~360x den 1.400x trong kich ban bao thu.

Loi ich lon hon, kho dinh luong hon: giam tre chan doan trong cap cuu va it bo sot dieu tri dua tren bang chung."""),

("Q3", "Lam sao biet he thong co duoc su dung thuc su khong?",
"""Moi truy van duoc ghi lai voi metadata (khong co thong tin nhan dang benh nhan). Bao cao hang thang bao gom:

- **Tong so truy van** theo khoa, theo lane (cap cuu vs phuc tap)
- **Bac si hoat dong**: bao nhieu trong 500 nguoi thuc su su dung thang nay
- **Top 20 loai cau hoi**: tong hop, an danh, huu ich cho dao tao
- **Thoi gian phan hoi trung binh** theo lane
- **Ti le click vao trich dan**: bac si co click vao nguon de xac minh khong?
- **Ti le thumbs-up / thumbs-down**

Vi du: "Khoa Tim mach su dung tro ly 12.400 lan thang nay, 94% thumbs up."

Neu mot khoa co ti le su dung thap, do la tin hieu can xem xet: quy trinh lam viec khong phu hop, phan hoi khong huu ich, hoac can dao tao them."""),

("Q4", "Neu bac si khong tin tuong AI va tu choi su dung thi sao?",
"""Niem tin duoc xay dung qua 3 co che thiet ke san:

1. **Moi cau tra loi deu co trich dan nguon.** Bac si co the click vao [1] va xem dung doan van WHO, so trang, ngay cap nhat. Minh bach hon khuyen nghi bang mieng cua dong nghiep.
2. **He thong noi "toi khong biet" khi khong co du lieu.** Neu context khong ho tro cau tra loi, he thong tu choi. PoC cua chung toi do luong 100% trich dan va 0% ao giac.
3. **Duoc dinh vi la ho tro quyet dinh, khong phai nguoi ra quyet dinh.** Bac si giu toan bo phan xet lam sang. Tro ly goi y; bac si quyet dinh.

**Mo hinh ap dung thuc te**: Tuan 1: 20% bac si thu, Tuan 4: 60% dung hang tuan, Tuan 12: 85%+ dung hang tuan."""),

("Q5", "He thong nay co the thay the nhan vien thu vien y khoa hoac chuyen vien tai lieu lam sang khong?",
"""Khong, va chung toi khuyen nghi khong nen dinh vi theo huong do. Ly do:

- Tro ly **tang cuong** bac si khong co thoi gian tra cuu nguon. Tac dong lon nhat la bac si cap cuu luc 3 gio sang, khong phai thu vien vien da lam viec can than.
- Thu vien vien va chuyen vien CDS thuc hien **giam tuyen sau**: quyet dinh nguon nao can index, kiem tra chat luong truy xuat, dao tao bac si moi. Tro ly tao ra nhu cau cho cac vai tro nay, khong giam.
- Dung AI de cat giam nhan su tao ra van de quan he lao dong va hiem khi hieu qua.

**Truong hop kinh doanh trung thuc**: Khong phai "sa thai 5 thu vien vien, tiet kiem 500k USD/nam." Ma la "cho moi bac si co thu vien vien ca nhan, tiet kiem 500k USD/thang trong thoi gian bac si.""""),

("Q6", "Bac si co tro nen luoi bieng va ngung tu duy phan bien vi AI tra loi san khong?",
"""Day la moi lo ngai hop le trong tin hoc lam sang, doi khi goi la "automation bias." Chung toi giai quyet qua 3 cach:

1. **Dinh dang dau ra buoc bac si phai doc.** Moi cau tra loi co cau truc "Khuyen nghi: ..." voi bang chung trich dan. Bac si phai doc it nhat phan khuyen nghi.
2. **Trich dan co the click.** Nghien cuu cho thay ~30-40% bac si click de xac minh trong cac truong hop moi. Cao hon xac minh tu van bang mieng (~5%).
3. **Kiem tra mu dinh ky.** Hang quy, chay 50 cau hoi voi truong hop kho, ket qua duoc xem xet boi can bo an toan lam sang.

Moi lo ngai tuong tu da duoc dat ra voi may tinh, ho so benh an dien tu, cong cu chan doan hinh anh. Mo hinh nhat quan: cong cu nang cao cong viec, khong lam giam ky nang."""),

("Q7", "Neu AI dua ra cau tra loi sai va benh nhan bi ton hai thi sao?",
"""Day la cau hoi quan trong nhat. Chung toi tra loi qua 3 khia canh:

**Phap ly**:
- He thong duoc cap phep va van hanh nhu **ho tro quyet dinh lam sang** theo HCSA, khong phai bac si dieu tri.
- Moi cau tra loi co tuyen bo ro rang: "Chi ho tro quyet dinh. Phan xet lam sang cuoi cung thuoc ve bac si co phep hanh nghe."
- Nhat ky kiem toan ghi lai: cau hoi chinh xac, bang chung truy xuat, cau tra loi, phien ban mo hinh, phien ban prompt, dau thoi gian.

**Bien phap ky thuat**:
- Xac thuc trich dan: moi khang dinh phai co nguon thuc su co the truy xuat.
- Diem grounding >= 0,7: chan dau ra khong co co so truoc khi den bac si.
- Bedrock Guardrails: chan cac mo hinh nguy hiem da biet.
- Hanh vi tu choi: khi khong chac chan, he thong noi "Toi khong the tra loi tu context hien tai."

**Thuc te**: PubMed co bai bao sai. Bai UpToDate bi thu hoi. Dong nghiep dua ra loi khuyen sai. Tieu chuan khong phai "AI phai hoan hao"; ma la "AI phai tot it nhat bang cac lua chon thay the, voi kha nang truy xuat tot hon.""""),

("Q8", "He thong nay so sanh the nao voi viec thue them bac si hoac mo rong doi ngu lam sang?",
"""Khong phai thay the bac si, nhung nhu mot **nhan so thoi gian**, phep tinh rat an tuong:

**Chi phi thue 1 bac si bo sung (Singapore)**: ~200.000-300.000 USD/nam (luong, phuc loi, bao hiem, dao tao, van phong).

**Tro ly AI them vao**: 5 phut x 600.000 truy van/thang = 50.000 gio/nam, tuong duong ~25 bac si toan thoi gian.

**So sanh**:
```
25 bac si bo sung x 250.000 USD = 6.250.000 USD/nam
Chi phi tro ly                   = ~50.000 USD/nam
Ti le tuong duong nang suat      = ~125x
```

Tro ly khong thay the bac si ban se thue de kham them benh nhan. No giai phong bac si ban da co de danh nhieu thoi gian **voi** benh nhan thay vi **nghien cuu** cho ho."""),

("Q9", "Su khac biet giua Nova tu xay dung he thong noi bo va thue nha cung cap nhu Alibaba hoac AWS la gi?",
"""Day la cau hoi build-vs-buy. Ba lop:

**Nen tang dam may** (AWS, Alibaba): Khong ai tu xay trung tam du lieu cho viec nay nua. Chi phi von rat lon. Dich vu dam may tra theo su dung la lua chon hop ly duy nhat.

**Mo hinh AI** (Claude, Qwen): Dao tao mo hinh lam sang hang dau tu dau ton 50-200 trieu USD va mat 12-18 thang. Anthropic va Alibaba da lam dieu nay. Thue mo hinh cua ho qua API chi ton vai cent moi truy van.

**Lop ung dung** (chinh tro ly): Day la noi Nova xay dung. Gia tri gia tang cua Nova la tich hop WHO + ICD-11 + thu nghiem noi bo, dao tao gion van, tich hop EHR, tu the tuan thu.

**So sanh chi phi (uoc tinh)**:
```
Tu xay dung:
- Doi ky su (10 nguoi x 200k)     = 2.000.000 USD/nam
- Doi ML/AI (5 nguoi x 250k)      = 1.250.000 USD/nam
- Doi tuan thu/bao mat (3 x 150k) = 450.000 USD/nam
- Dam may + GPU (30% tren)        = 1.100.000 USD/nam
- Tong                            = 4.800.000 USD/nam
- Cong them: 18 thang de ra mat

Dung dich vu quan ly AWS/Alibaba:
- 2-3 ky su tich hop (Nova hien co) = ~500.000 USD/nam
- AI + truy xuat quan ly            = 34.000-66.000 USD/nam
- Tong                              = ~550.000 USD/nam
- Thoi gian ra mat: 6-10 tuan
```

Phuong phap cloud-native **re hon ~9 lan** voi **nhanh hon ~10 lan**."""),

("Q10", "Neu no co gia tri nhu vay, tai sao tat ca cac benh vien chua lam dieu nay?",
"""Ba ly do, va Nova co loi the o moi diem:

1. **Hau het benh vien khong co lanh dao ky thuat.** Xay dung dieu nay doi hoi hieu biet ve LLM, RAG, co so du lieu vector, quy dinh y te, tich hop EHR va kien truc bao mat, tat ca cung mot luc. Nova Health Tech voi tu cach la nha cung cap suc khoe ky thuat so co chuyen mon nay; mot benh vien dien hinh thi khong.

2. **Tuan thu chua ro rang cho den gan day.** PDPA da ro rang; HCSA 2020 chinh thuc them "ho tro quyet dinh lam sang" la danh muc dich vu duoc cap phep, giai quyet su mo ho quy dinh. Truoc cuoi nam 2024, viec trien khai co rui ro. Bay gio co the kiem toan duoc.

3. **Nguong chat luong mo hinh da vuot qua vao 2024-2025.** Claude 3.5/4.5 va Qwen 3.5/3 dat duoc suy luan cap lam sang ma GPT-3.5/4 truoc day don gian la khong co. Grounding trich dan qua RAG truong thanh den ~98% trong nghien cuu va ~95% trong trien khai san xuat.

Cac benh vien DANG trien khai AI lam sang vao nam 2026 la: Mayo Clinic, Cleveland Clinic, Singapore SGH (voi NUS), Mount Elizabeth. Nova la som o Dong Nam A - day la loi the canh tranh dang bao ve."""),
]

content = pathlib.Path("docs/Client_QA_500_Tieng_Viet.md").read_text(encoding="utf-8")
for qnum, question, answer in QA:
    content += f"### {qnum}. {question}\n\n**A.** {answer}\n\n---\n\n"
pathlib.Path("docs/Client_QA_500_Tieng_Viet.md").write_text(content, encoding="utf-8")
print(f"Written {len(QA)} questions")
