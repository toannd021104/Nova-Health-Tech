import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')

qa_list = [
    ("Q141", "AI co the xu ly nhap bang giong noi trong moi truong phong mo hoac vo trung khong?", "Xem xet quy trinh lam viec: Nhap bang giong noi (ranh tay) duoc khuyen nghi cho phong mo. Kich hoat bang ban dap chan co the. Giao dien than thien voi cam ung. Tich hop may tinh bang tuong thich voi moi truong vo trung. Quy trinh lam viec phong mo cu the: Truoc phau thuat: tu van AI ben ngoai truong vo trung. Trong phau thuat: ho tro bang giong noi cho cac giao thuc. Sau phau thuat: AI cho tai lieu. Chi phi: tieu chuan. Benh vien cung cap phan cung tuong thich voi moi truong vo trung."),
    ("Q142", "AI co the xu ly cac dieu kien man tinh phuc tap khong?", "Quan ly benh man tinh: tieu duong, suy tim, COPD, tang huyet ap, sot ung thu. Toi uu hoa cham soc dai han. AI giup giam sat, goi y dieu chinh dieu tri, xac dinh bien chung. Dac biet co gia tri cho: benh nhan da thuoc, benh nhan cao tuoi, benh nhan co nhieu benh kem theo. Tich hop voi: chuong trinh quan ly benh, cham soc suc khoe cong dong."),
    ("Q143", "Lam the nao de AI xu ly cac ket qua xet nghiem?", "Ho tro giai thich xet nghiem: nhan thuc pham vi tham chieu, phan tich xu huong, danh dau gia tri nguy kich, chan doan phan biet, khuyen nghi theo doi. Vi du: 'Glucose 350. Nguyen nhan co the: X, Y, Z. Xet nghiem duoc khuyen nghi: A, B. Boi canh benh nhan: trang thai insulin, che do an, v.v.' Tich hop voi he thong xet nghiem EHR."),
    ("Q144", "AI co the giup voi viec lap ke hoach xuat vien khong?", "Ho tro xuat vien toan dien: doi chieu thuoc, giao duc benh nhan, lap lich theo doi, nhu cau cham soc tai nha, thuoc sau xuat vien. Giup giam tai nhap vien thong qua chuan bi xuat vien tot hon. Tich hop voi quan ly truong hop."),
    ("Q145", "Dieu gi xay ra khi AI khong co thong tin ve mot truong hop cu the?", "Da duoc tra loi o Q75. Xem chi tiet o do."),
    ("Q146", "AI co the xu ly cac truong hop nhi khoa phuc tap khong?", "Da duoc tra loi o Q122. Xem chi tiet o do."),
    ("Q147", "Lam the nao de AI xu ly cac truong hop cap cuu cu the?", "Tinh nang cap cuu: giao thuc ATLS, phan loai tham hoa hang loat, uu tien hoi suc, chuyen tiep cham soc cap cuu, phoi hop da chuyen khoa. Thoi gian quan trong: lane cap cuu duoc toi uu hoa. Phoi hop da chuyen khoa trong chan thuong."),
    ("Q148", "AI co the giup voi viec quan ly nhiem trung khong?", "Ho tro benh truyen nhiem: lua chon khang sinh, cac nguyen tac quan ly khang sinh, cac can nhac khang thuoc, quan ly HIV, lao, viem gan, quan ly dich benh. Quan trong cho: su dung khang sinh phu hop, kiem soat nhiem trung benh vien."),
    ("Q149", "Lam the nao de AI xu ly cac truong hop ung thu?", "Ho tro ung thu: cac phac do hoa tri, dieu chinh lieu luong, quan ly tac dung phu lieu phap mien dich, cham soc ho tro, cham soc sau dieu tri. Tich hop voi nhom ung thu. Dac biet co gia tri cho: cac quyet dinh hoa tri phuc tap."),
    ("Q150", "AI co the xu ly cac truong hop than hoc khong?", "Ho tro than hoc: phan giai CKD, danh gia AKI, quyet dinh loc mau, lieu luong thuoc theo GFR, quan ly dien giai. Dac biet co gia tri cho: lieu luong thuoc trong benh than (nguyen nhan pho bien cua loi). Tich hop voi ket qua xet nghiem."),
    ("Q151", "Lam the nao de AI xu ly cac truong hop than kinh?", "Ho tro than kinh: lo trinh dot quy cap tinh, quan ly co giat, danh gia dau dau, benh thoai hoa than kinh, cac dieu kien cot song. Thoi gian quan trong: lo trinh dot quy. AI huu ich cho: chan doan phan biet phuc tap, cac quyet dinh dieu tri."),
    ("Q152", "AI co the xu ly cac truong hop noi tiet khong?", "Ho tro noi tiet: tieu duong (da duoc de cap), roi loan tuyen giap, roi loan tuyen thuong than, cac dieu kien tuyen yen, noi tiet sinh san. Cac dieu kien pho bien: gia tri dang ke cho cham soc ban dau + noi tiet."),
    ("Q153", "Lam the nao de AI xu ly cac truong hop benh truyen nhiem?", "Ho tro benh truyen nhiem: lua chon khang sinh, cac nguyen tac quan ly khang sinh, cac can nhac khang thuoc, quan ly HIV/lao/viem gan, quan ly dich benh. Quan trong cho: su dung khang sinh phu hop, kiem soat nhiem trung benh vien."),
    ("Q154", "AI co the xu ly cac truong hop huyet hoc khong?", "Ho tro huyet hoc: danh gia thieu mau, roi loan chay mau, ung thu mau, cac quyet dinh truyen mau, chong dong. Tich hop voi chuyen khoa huyet hoc."),
    ("Q155", "Lam the nao de AI xu ly cac truong hop mien dich hoc?", "Ho tro mien dich hoc: benh tu mien, di ung, suy giam mien dich, ghep tang, cac can nhac tiem chung. Linh vuc chuyen biet. AI cung cap tham khao + huong dan."),
    ("Q156", "AI co the xu ly cac truong hop nhi khoa chuyen khoa khong?", "Cac chuyen khoa nhi khoa: tim mach nhi, ho hap nhi, tieu hoa nhi, than kinh nhi, ung thu nhi, v.v. Moi loai: cham soc dua tren can nang, phu hop theo tuoi phu hop."),
    ("Q157", "Lam the nao de AI xu ly suc khoe phu nu cu the?", "Suc khoe phu nu: suc khoe sinh san, thai ky, suc khoe vu, man kinh, sang loc ung thu, suc khoe tam than. Ho tro toan dien trong suot cuoc doi suc khoe phu nu."),
    ("Q158", "AI co the xu ly suc khoe nam gioi khong?", "Suc khoe nam gioi: rui ro tim mach, suc khoe tuyen tien liet, thieu hut testosterone, suc khoe tam than, sang loc ung thu. Cham soc duoc dieu chinh theo cac moi quan tam suc khoe nam gioi."),
    ("Q159", "Lam the nao de AI xu ly y hoc vi thanh nien?", "Y hoc vi thanh nien: cac can nhac bao mat, suc khoe tam than, su dung chat, suc khoe tinh duc, tu van loi song. Linh vuc nhan cam. Bao ve bao mat. Tich hop voi: nhi khoa, y hoc gia dinh."),
    ("Q160", "AI co the xu ly cham soc nguoi cao tuoi cu the khong?", "Cham soc lao khoa: danh gia nhan thuc, danh gia suy yeu, phong ngua nga, da thuoc, muc tieu cham soc. Ho tro danh gia lao khoa toan dien."),
]

content = f.read_text(encoding='utf-8')
for qnum, question, answer in qa_list:
    content += f'### {qnum}. {question}\n\n**A.** {answer}\n\n---\n\n'
f.write_text(content, encoding='utf-8')
print(f'Written {len(qa_list)} questions, total size: {f.stat().st_size}')
