import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')

# Q201-300: Cac chu de bo sung
qa_list = [
    ("Q201", "AI co the xu ly cac truong hop cap cuu nhi khoa khong?", "Cap cuu nhi khoa: nhiem trung huyet nhi, cham soc NICU, lieu luong dua tren can nang, cap cuu nhi khoa, phoi hop da chuyen khoa. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu, giao tiep voi cha me."),
    ("Q202", "Lam the nao de AI xu ly cac truong hop cap cuu san khoa?", "Cap cuu san khoa: tien san giat, xuat huyet sau sinh, tieu duong thai ky, cham soc truoc sinh, cac dieu kien nguy co cao. Tich hop voi nhom san khoa. Dac biet co gia tri cho: thai ky nguy co cao."),
    ("Q203", "AI co the xu ly cac truong hop cap cuu than kinh khong?", "Da duoc tra loi o Q177. Xem chi tiet o do."),
    ("Q204", "Lam the nao de AI xu ly cac truong hop cap cuu tim mach?", "Da duoc tra loi o Q162. Xem chi tiet o do."),
    ("Q205", "AI co the xu ly cac truong hop cap cuu ho hap khong?", "Cap cuu ho hap: suy ho hap cap, ARDS, thuyen tac phoi, tran khi mang phoi, cap cuu hen phe quan. Thoi gian quan trong. Tich hop voi: ED, ICU, ho hap."),
    ("Q206", "Lam the nao de AI xu ly cac truong hop cap cuu tieu hoa?", "Cap cuu tieu hoa: xuat huyet tieu hoa, viem tuy cap, viem ruot thua, tac ruot, suy gan cap. Thoi gian quan trong. Tich hop voi: ED, phau thuat, tieu hoa."),
    ("Q207", "AI co the xu ly cac truong hop cap cuu than hoc khong?", "Cap cuu than hoc: AKI cap tinh, tang kali mau, nhiem toan chuyen hoa, cap cuu loc mau, cap cuu ghep than. Thoi gian quan trong. Tich hop voi: ED, than hoc, ICU."),
    ("Q208", "Lam the nao de AI xu ly cac truong hop cap cuu noi tiet?", "Cap cuu noi tiet: nhiem toan ceton do tieu duong, hon me tang thau, con bao, suy tuyen thuong than cap, cap cuu tuyen yen. Thoi gian quan trong. Tich hop voi: ED, noi tiet, ICU."),
    ("Q209", "AI co the xu ly cac truong hop cap cuu nhiem trung khong?", "Cap cuu nhiem trung: nhiem trung huyet, soc nhiem trung, viem mang nao, viem phoi nang, nhiem trung o benh nhan suy giam mien dich. Thoi gian quan trong. Tich hop voi: ED, benh truyen nhiem, ICU."),
    ("Q210", "Lam the nao de AI xu ly cac truong hop cap cuu than kinh?", "Da duoc tra loi o Q177. Xem chi tiet o do."),
    ("Q211", "AI co the xu ly cac truong hop cap cuu tam than khong?", "Cap cuu tam than: danh gia rui ro tu tu, kich dong cap tinh, loan tam than cap, cap cuu nghien chat, cap cuu suc khoe tam than. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than."),
    ("Q212", "Lam the nao de AI xu ly cac truong hop cap cuu mat khong?", "Cap cuu mat: mat thi luc, chan thuong mat, tang nhan ap cap tinh, bong mat, cap cuu mat khac. Chuyen biet. AI cung cap phan loai + gioi thieu chuyen khoa."),
    ("Q213", "AI co the xu ly cac truong hop cap cuu tai mui hong khong?", "Cap cuu tai mui hong: chay mau mui nang, tat nghen duong tho, nhiem trung nang, chan thuong, cap cuu tai mui hong khac. Tich hop voi: ED, tai mui hong."),
    ("Q214", "Lam the nao de AI xu ly cac truong hop cap cuu rang mieng?", "Cap cuu rang mieng: nhiem trung rang mieng nang, chan thuong ham mat, xuat huyet sau phau thuat, cap cuu rang mieng khac. Tich hop voi: ED, rang mieng."),
    ("Q215", "AI co the xu ly cac truong hop cap cuu da lieu khong?", "Cap cuu da lieu: phan ung di ung nang, bong nang, nhiem trung da nang, cap cuu da lieu khac. Tich hop voi: ED, da lieu."),
    ("Q216", "Lam the nao de AI xu ly cac truong hop cap cuu co xuong khop khong?", "Cap cuu co xuong khop: gay xuong, trai khop, chan thuong day chang, cap cuu co xuong khop khac. Tich hop voi: ED, chinh hinh."),
    ("Q217", "AI co the xu ly cac truong hop cap cuu mach mau khong?", "Cap cuu mach mau: phinh dong mach chu, thieu mau chi cap tinh, huyet khoi tinh mach sau, cap cuu mach mau khac. Thoi gian quan trong. Tich hop voi: ED, phau thuat mach mau."),
    ("Q218", "Lam the nao de AI xu ly cac truong hop cap cuu ung thu?", "Da duoc tra loi o Q178. Xem chi tiet o do."),
    ("Q219", "AI co the xu ly cac truong hop cap cuu ghep tang khong?", "Cap cuu ghep tang: thai ghet cap tinh, nhiem trung sau ghep, tac dung phu uc che mien dich, cap cuu ghep tang khac. Chuyen biet. Tich hop voi: ghep tang, benh truyen nhiem, ICU."),
    ("Q220", "Lam the nao de AI xu ly cac truong hop cap cuu tram cam?", "Cap cuu tram cam: danh gia rui ro tu tu, kich dong cap tinh, cap cuu suc khoe tam than, cap cuu nghien chat. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than."),
    ("Q221", "AI co the xu ly cac truong hop cap cuu tre em khong?", "Cap cuu tre em: nhiem trung huyet nhi, cap cuu NICU, cap cuu nhi khoa, phoi hop da chuyen khoa. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu."),
    ("Q222", "Lam the nao de AI xu ly cac truong hop cap cuu nguoi cao tuoi?", "Cap cuu nguoi cao tuoi: nga, suy giam nhan thuc cap tinh, nhiem trung, cap cuu da thuoc, cap cuu nguoi cao tuoi khac. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc."),
    ("Q223", "AI co the xu ly cac truong hop cap cuu phu nu mang thai khong?", "Cap cuu phu nu mang thai: tien san giat, xuat huyet, nhau bong non, cap cuu san khoa khac. Thoi gian quan trong. Tich hop voi: ED, san khoa, ICU."),
    ("Q224", "Lam the nao de AI xu ly cac truong hop cap cuu sau phau thuat?", "Cap cuu sau phau thuat: chay mau, nhiem trung, huyet khoi, cap cuu sau phau thuat khac. Tich hop voi: phau thuat, ICU, ED."),
    ("Q225", "AI co the xu ly cac truong hop cap cuu ICU khong?", "Cap cuu ICU: toi uu hoa huyet dong, quan ly may tho, quan ly an than, giao thuc nhiem trung huyet, giao tiep voi gia dinh. Bac si ICU: nguoi dung AI nang nhat. Thoi gian quan trong, quyet dinh rui ro cao."),
    ("Q226", "Lam the nao de AI xu ly cac truong hop cap cuu phong mo?", "Cap cuu phong mo: danh gia truoc phau thuat, quan ly gay me, cap cuu trong phau thuat, cap cuu phong mo khac. Tich hop voi: phau thuat, gay me, ICU."),
    ("Q227", "AI co the xu ly cac truong hop cap cuu phong cap cuu khong?", "Cap cuu phong cap cuu: phan loai, on dinh, cac giao thuc cap cuu, phoi hop da chuyen khoa, chuyen tiep. Bac si cap cuu: nguoi dung AI nang nhat. Thoi gian quan trong."),
    ("Q228", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham ngoai tru?", "Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED."),
    ("Q229", "AI co the xu ly cac truong hop cap cuu phong kham tu nhan khong?", "Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED."),
    ("Q230", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham chuyen khoa?", "Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED."),
    ("Q231", "AI co the xu ly cac truong hop cap cuu phong kham da khoa khong?", "Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED."),
    ("Q232", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham gia dinh?", "Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED."),
    ("Q233", "AI co the xu ly cac truong hop cap cuu phong kham noi khoa khong?", "Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED."),
    ("Q234", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham ngoai khoa?", "Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED."),
    ("Q235", "AI co the xu ly cac truong hop cap cuu phong kham nhi khoa khong?", "Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu."),
    ("Q236", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham san khoa?", "Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED."),
    ("Q237", "AI co the xu ly cac truong hop cap cuu phong kham tam than khong?", "Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than."),
    ("Q238", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham mat?", "Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED."),
    ("Q239", "AI co the xu ly cac truong hop cap cuu phong kham tai mui hong khong?", "Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED."),
    ("Q240", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham rang mieng?", "Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED."),
    ("Q241", "AI co the xu ly cac truong hop cap cuu phong kham da lieu khong?", "Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED."),
    ("Q242", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham co xuong khop?", "Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED."),
    ("Q243", "AI co the xu ly cac truong hop cap cuu phong kham mach mau khong?", "Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED."),
    ("Q244", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham ung thu?", "Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED."),
    ("Q245", "AI co the xu ly cac truong hop cap cuu phong kham ghep tang khong?", "Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED."),
    ("Q246", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham tram cam?", "Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than."),
    ("Q247", "AI co the xu ly cac truong hop cap cuu phong kham tre em khong?", "Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu."),
    ("Q248", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham nguoi cao tuoi?", "Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc."),
    ("Q249", "AI co the xu ly cac truong hop cap cuu phong kham phu nu mang thai khong?", "Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED."),
    ("Q250", "Lam the nao de AI xu ly cac truong hop cap cuu phong kham sau phau thuat?", "Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED."),
]

content = f.read_text(encoding='utf-8')
for qnum, question, answer in qa_list:
    content += f'### {qnum}. {question}\n\n**A.** {answer}\n\n---\n\n'
f.write_text(content, encoding='utf-8')
print(f'Written {len(qa_list)} questions, total size: {f.stat().st_size}')
