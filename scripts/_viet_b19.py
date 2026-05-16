import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')

qa_list = [
    ("Q161", "AI co the xu ly cac truong hop phau thuat khong?", "Ho tro phau thuat: danh gia truoc phau thuat, phan tang rui ro, cac can nhac thu thuat, lap ke hoach gay me, cham soc sau phau thuat. Tich hop voi quy trinh phau thuat. Huu ich cho: cac bac si phau thuat noi tru, cac truong hop phuc tap, lap ke hoach da chuyen khoa."),
    ("Q162", "Lam the nao de AI xu ly cac truong hop cap cuu tim mach?", "Cap cuu tim mach: cac giao thuc ACS, quan ly suy tim, cham soc loan nhip, tang huyet ap, quan ly lipid, huong dan hinh anh. Mot trong nhung chuyen khoa co gia tri nhat cho ho tro AI."),
    ("Q163", "AI co the xu ly cac truong hop ho hap phuc tap khong?", "Ho hap phuc tap: hen phe quan/COPD nang, dot cap COPD, thuyen tac phoi, ung thu phoi, ngu ngon. Quan trong cho: cac can thiep kip thoi."),
    ("Q164", "Lam the nao de AI xu ly cac truong hop tieu hoa?", "Tieu hoa: IBS/IBD, xuat huyet tieu hoa, benh gan, cac dieu kien tuy, cac can nhac noi soi. Tich hop voi quy trinh lam viec chuyen khoa tieu hoa."),
    ("Q165", "AI co the xu ly cac truong hop ung thu khong?", "Da duoc tra loi o Q149. Xem chi tiet o do."),
    ("Q166", "Lam the nao de AI xu ly cac truong hop than hoc?", "Da duoc tra loi o Q150. Xem chi tiet o do."),
    ("Q167", "AI co the xu ly cac truong hop san khoa khong?", "Ho tro san khoa: quan ly thai ky, cham soc truoc sinh, cac can nhac sinh, cham soc sau sinh, thai ky nguy co cao. Tich hop voi nhom san khoa. Dac biet co gia tri cho: thai ky nguy co cao."),
    ("Q168", "Lam the nao de AI xu ly cac truong hop nhi khoa so sinh/NICU?", "Cham soc so sinh: danh gia Apgar, on dinh ban dau, cac dieu kien pho bien, cham soc NICU cu the, ho tro cha me. Tich hop voi quy trinh lam viec NICU, tu van neonatologist."),
    ("Q169", "AI co the xu ly cac truong hop da lieu khong?", "Da lieu: danh gia ton thuong da, chan doan phan biet, khuyen nghi dieu tri, huong dan gioi thieu chuyen khoa. Tot nhat ket hop voi: cong cu phan tich hinh anh. AI xu ly boi canh lam sang, AI hinh anh xu ly hinh anh."),
    ("Q170", "Lam the nao de AI xu ly cac truong hop nhan khoa?", "Nhan khoa: danh gia trieu chung thi giac, cac dieu kien pho bien, khuyen nghi dieu tri, phoi hop chuyen khoa. Kha nang dua tren hinh anh han che ma khong co cong cu phan tich hinh anh chuyen biet. Tot nhat cho: ly luan lam sang, huong dan dieu tri."),
    ("Q171", "AI co the xu ly cac truong hop tai mui hong khong?", "Tai mui hong: danh gia trieu chung, cac dieu kien pho bien, khuyen nghi dieu tri, gioi thieu chuyen khoa. Ho tro toan dien."),
    ("Q172", "Lam the nao de AI xu ly cac truong hop rang mieng?", "Rang mieng: sang loc thuong xuyen, benh rang mieng, cac lua chon dieu tri, giao duc benh nhan. Pham vi han che nhung co san. Tich hop voi khoa rang."),
    ("Q173", "AI co the xu ly cac truong hop phuc hoi khong?", "Phuc hoi: khuyen nghi lieu phap, danh gia tien do, lap ke hoach xuat vien, muc tieu dai han, giao duc gia dinh. Tich hop tren: PT, OT, Lieu phap Ngon ngu, Phuc hoi Tim/Phoi."),
    ("Q174", "Lam the nao de AI xu ly cac truong hop tam than cu the?", "Da duoc tra loi o Q127. Xem chi tiet o do."),
    ("Q175", "AI co the xu ly cac truong hop quan ly dau khong?", "Quan ly dau: cac phuong phap da phuong thuc, nhan manh khong opioid, danh gia rui ro, cac lua chon khong duoc pham, tu van benh nhan. Linh vuc nhan cam. Cau hinh bao thu. Tich hop voi chuyen khoa dau."),
    ("Q176", "Lam the nao de AI xu ly cac truong hop cap cuu phau thuat?", "Cap cuu phau thuat: danh gia ATLS, phan loai tham hoa hang loat, uu tien hoi suc, chuyen tiep cham soc cap cuu, phoi hop da chuyen khoa. Thoi gian quan trong. Tich hop voi: ED, phau thuat, ICU."),
    ("Q177", "AI co the xu ly cac truong hop cap cuu than kinh khong?", "Cap cuu than kinh: lo trinh dot quy cap tinh, quan ly co giat, cac dau hieu nguy hiem dau dau, benh thoai hoa than kinh, cac dieu kien cot song. Thoi gian quan trong: lo trinh dot quy. Tich hop voi: ED, than kinh, ICU."),
    ("Q178", "Lam the nao de AI xu ly cac truong hop cap cuu ung thu?", "Cap cuu ung thu: hoi chung ly giai khoi u, ep tuy song, tang do nho mau, nhiem trung nang o benh nhan suy giam mien dich, cac cap cuu khac. Thoi gian quan trong. Tich hop voi: ED, ung thu, ICU."),
    ("Q179", "AI co the xu ly cac truong hop loan nhip tim khong?", "Quan ly loan nhip: cac can nhac chan doan, lua chon dieu tri, tinh hop le cat dot, chong dong, giao duc benh nhan. Chuyen biet trong tim mach."),
    ("Q180", "Lam the nao de AI xu ly cac dieu kien ho hap phuc tap?", "Ho hap phuc tap: hen phe quan nang, dot cap COPD, thuyen tac phoi, ung thu phoi, ngu ngon. Quan trong cho: cac can thiep kip thoi."),
    ("Q181", "AI co the xu ly cac dieu kien tu mien khong?", "Tu mien: cac khung chan doan, cac dieu tri bien doi benh, quan ly dot cap, cac can nhac benh kem theo, gioi thieu chuyen khoa. Tich hop voi: thap khop, mien dich hoc."),
    ("Q182", "Lam the nao de AI xu ly y hoc ghep tang?", "Ghep tang: danh gia truoc ghep, uc che mien dich, quan ly thai ghet, cham soc dai han, cac can nhac nguoi hien song. Chuyen biet. AI cung cap tham khao + huong dan."),
    ("Q183", "AI co the xu ly cac truong hop nhiem trung benh vien khong?", "Nhiem trung benh vien (HAC): nhan dang, cac chien luoc phong ngua, dieu tri khi xay ra, cac yeu cau bao cao, cac co hoi cai thien. Tich hop voi: kiem soat nhiem trung, dich te hoc benh vien."),
    ("Q184", "Lam the nao de AI xu ly cac truong hop hoi nghi da chuyen khoa?", "Hoi nghi da chuyen khoa: nghien cuu truoc hoi nghi, tu van da chuyen khoa, cac khung quyet dinh, tai lieu, lap ke hoach theo doi. Ho tro hop tac nhieu bac si."),
    ("Q185", "AI co the ho tro doi moi giao duc y khoa khong?", "Giao duc y khoa: cac lo trinh hoc tap ca nhan hoa, kham pha chu de, tai lieu moi nhat, cap nhat lien quan den thuc hanh, cac cau hoi thuc hanh. Dac biet co gia tri trong cac benh vien giang day."),
    ("Q186", "Lam the nao de AI xu ly tich hop nghien cuu lam sang?", "Tich hop nghien cuu: ho tro xem xet tai lieu, sang loc thu nghiem, ho tro phan tich, ho tro xuat ban, cac cong cu hop tac. Nhieu ung dung cap do nghien cuu."),
    ("Q187", "AI co the ho tro cac chuong trinh suc khoe cong dong khong?", "Suc khoe cong dong: quan ly suc khoe dan so, phat hien dich benh, phan bo nguon luc, cac chuong trinh suc khoe, do luong tac dong. Tich hop voi: dich te hoc benh vien."),
    ("Q188", "Lam the nao de AI xu ly cac truong hop y te tu xa cu the?", "Da duoc tra loi o Q47. Xem chi tiet o do."),
    ("Q189", "AI co the xu ly cac truong hop giam sat tu xa khong?", "Giam sat tu xa: thiet ke chuong trinh, lua chon benh nhan, tich hop cong nghe, theo doi ket qua, gia tri chien luoc. Ho tro chuong trinh RPM."),
    ("Q190", "Lam the nao de AI xu ly cac chuong trinh benh man tinh?", "Quan ly benh man tinh: quan ly suc khoe dan so, dang ky benh nhan, phoi hop cham soc, do luong ket qua, phu hop chien luoc. Cac chuong trinh quan ly benh."),
    ("Q191", "AI co the ho tro cac chuong trinh suc khoe khong?", "Suc khoe: suc khoe dan so, cham soc phong ngua, giao duc benh nhan, su tham gia, ket qua. Cac sang kien suc khoe benh vien."),
    ("Q192", "Lam the nao de AI xu ly cac chuong trinh suc khoe cong dong?", "Suc khoe cong dong: danh gia nhu cau, thiet ke chuong trinh, phat trien quan he doi tac, trien khai, do luong tac dong. Ho tro quan he doi tac cong dong."),
    ("Q193", "AI co the ho tro cac chuong trinh suc khoe truong hoc khong?", "Suc khoe truong hoc: ho tro giao duc, cac chuong trinh tiem chung, sang loc suc khoe, quan he doi tac cong dong, phu hop chien luoc. Cac chuong trinh suc khoe truong hoc."),
    ("Q194", "Lam the nao de AI xu ly suc khoe noi lam viec?", "Suc khoe noi lam viec: cac chuong trinh suc khoe nhan vien, suc khoe nghe nghiep, ho tro suc khoe tam than, cac sang kien chien luoc, do luong ROI. Suc khoe luc luong lao dong benh vien."),
    ("Q195", "AI co the ho tro cac cap nhat quy dinh khong?", "Cap nhat quy dinh: giam sat thong tu MOH Singapore, ban tin PDPC, cap nhat IMDA, thong bao HSA, ho tro trien khai. Giam sat quy dinh lien tuc."),
    ("Q196", "Lam the nao de AI xu ly truyen thong chien luoc?", "Truyen thong chien luoc: nhan tin cac ben lien quan, quan ly thuong hieu, truyen thong khung hoang, truyen thong noi bo, truyen thong ben ngoai. Ho tro truyen thong toan dien."),
    ("Q197", "AI co the ho tro quan ly thay doi khong?", "Quan ly thay doi: phat trien chien luoc, trien khai, su tham gia cac ben lien quan, quan ly su khang cu, tinh ben vung. Ho tro thay doi chien luoc."),
    ("Q198", "Lam the nao de AI xu ly phat trien van hoa?", "Van hoa: danh gia van hoa, phu hop gia tri, truyen thong, cong nhan, cai thien lien tuc. Ho tro van hoa benh vien."),
    ("Q199", "AI co the ho tro chuyen tiep lanh dao khong?", "Chuyen tiep lanh dao: lap ke hoach ke nhiem, ho tro onboarding, chuyen giao kien thuc, tiep noi, phu hop chien luoc. Ho tro chuyen tiep quan trong."),
    ("Q200", "Lam the nao de AI xu ly quan tri benh vien?", "Quan tri: bao cao hoi dong, phat trien chinh sach, tuan thu, phu hop chien luoc, quan ly rui ro. Ho tro quan tri benh vien."),
]

content = f.read_text(encoding='utf-8')
for qnum, question, answer in qa_list:
    content += f'### {qnum}. {question}\n\n**A.** {answer}\n\n---\n\n'
f.write_text(content, encoding='utf-8')
print(f'Written {len(qa_list)} questions, total size: {f.stat().st_size}')
