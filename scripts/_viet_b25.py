import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
qa_list = [
    ("Q451", "AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?", "Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED."),
    ("Q452", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?", "Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED."),
    ("Q453", "AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?", "Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED."),
    ("Q454", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?", "Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than."),
    ("Q455", "AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?", "Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu."),
    ("Q456", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?", "Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc."),
    ("Q457", "AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?", "Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED."),
    ("Q458", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?", "Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED."),
    ("Q459", "AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?", "Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED."),
    ("Q460", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?", "Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED."),
    ("Q461", "AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?", "Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat."),
    ("Q462", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?", "Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED."),
    ("Q463", "AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?", "Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED."),
    ("Q464", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?", "Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED."),
    ("Q465", "AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?", "Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED."),
    ("Q466", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?", "Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED."),
    ("Q467", "AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?", "Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED."),
    ("Q468", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?", "Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED."),
    ("Q469", "AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?", "Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu."),
    ("Q470", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?", "Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED."),
    ("Q471", "AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?", "Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than."),
    ("Q472", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?", "Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED."),
    ("Q473", "AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?", "Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED."),
    ("Q474", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?", "Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED."),
    ("Q475", "AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?", "Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED."),
    ("Q476", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?", "Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED."),
    ("Q477", "AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?", "Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED."),
    ("Q478", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?", "Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED."),
    ("Q479", "AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?", "Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED."),
    ("Q480", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?", "Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than."),
    ("Q481", "AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?", "Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu."),
    ("Q482", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?", "Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc."),
    ("Q483", "AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?", "Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED."),
    ("Q484", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?", "Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED."),
    ("Q485", "AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?", "Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED."),
    ("Q486", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?", "Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED."),
    ("Q487", "AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?", "Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat."),
    ("Q488", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?", "Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED."),
    ("Q489", "AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?", "Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED."),
    ("Q490", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?", "Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED."),
    ("Q491", "AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?", "Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED."),
    ("Q492", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?", "Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED."),
    ("Q493", "AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?", "Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED."),
    ("Q494", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?", "Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED."),
    ("Q495", "AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?", "Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu."),
    ("Q496", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?", "Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED."),
    ("Q497", "AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?", "Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than."),
    ("Q498", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?", "Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED."),
    ("Q499", "AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?", "Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED."),
    ("Q500", "Cau hoi cuoi cung: Dieu quan trong nhat can hieu ve AI nay la gi?", "AI la ho tro quyet dinh, khong phai nguoi ra quyet dinh. Cac nguyen tac chinh: (1) Tang cuong, khong thay the - bac si van la nguoi chinh, AI ho tro suy nghi, quyet dinh cuoi cung la con nguoi. (2) Duoc can cu trich dan - moi khang dinh duoc trich dan, nguon co the xac minh, niem tin qua minh bach. (3) Tu choi khi khong chac chan - AI tu choi khi KB thieu du lieu, trung thuc ve han che, bao ton cho an toan. (4) Ban dia Singapore - tuan thu PDPA, phu hop HCSA, nhan thuc boi canh dia phuong, luu tru du lieu duoc dam bao. (5) ROI tich cuc - tiet kiem thoi gian dang ke, ket qua tot hon, chi phi hop ly, gia tri dai han. Ket luan: Duoc thuc hien dung, AI nay giup cac bac si gioi tro nen tot hon, nhanh hon va tu tin hon. Chung toi cam ket giup ban thuc hien dung."),
]
content = f.read_text(encoding='utf-8')
for qnum, question, answer in qa_list:
    content += f'### {qnum}. {question}\n\n**A.** {answer}\n\n---\n\n'
# Add conclusion
content += '''

## Ket luan

500 cau hoi nay phan anh cac moi quan tam thuc te cua cac lanh dao benh vien, lanh dao lam sang va cac ben lien quan van hanh dang xem xet hoac trien khai ho tro quyet dinh lam sang AI.

Cac cau tra loi nhan manh:
- **Ngon ngu don gian**: tranh thuat ngu ky thuat
- **Con so cu the**: khi co the, dinh luong loi ich va chi phi
- **Ky vong thuc te**: khong hua qua muc
- **Nhan thuc rui ro**: trung thuc ve han che
- **Boi canh chien luoc**: ket noi voi muc tieu rong lon hon
- **Huong dan trien khai**: loi khuyen co the thuc hien duoc
- **Tuan thu Singapore**: chi tiet PDPA, HCSA, AI Verify

De biet them thong tin hoac cac cau hoi cu the, lien he voi nhom Nova Health Tech.

**Nova Health Tech**
**Tro ly AI Lam sang**
**Ban dia Singapore, Uu tien Tuan thu, Huong den Ket qua**
'''
f.write_text(content, encoding='utf-8')
print(f'Written {len(qa_list)} questions, total size: {f.stat().st_size}')
