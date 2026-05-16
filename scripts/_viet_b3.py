import pathlib
f = pathlib.Path('docs/Client_QA_500_Tieng_Viet.md')
batch = '''

## 2. Chi phi & Dinh gia

### Q21. Tai sao bien the Claude dat hon bien the Nova (5.545 vs 2.805 USD)?

**A.** Gia suy luan mo hinh. Cu the:

**Claude Sonnet 4.5** (mo hinh lane phuc tap) tinh:
- 3,00 USD moi trieu token dau vao
- 15,00 USD moi trieu token dau ra

**Amazon Nova Pro** (doi thu canh tranh cua Sonnet) tinh:
- 0,80 USD moi trieu token dau vao
- 3,20 USD moi trieu token dau ra

Voi cac truy van phuc tap (noi bac si dat cau hoi sau):
`
Chi phi Claude Sonnet 4.5 moi truy van = ~0,013 USD
Chi phi Nova Pro moi truy van = ~0,0035 USD
`

Tren 420.000 truy van phuc tap/thang:
`
Claude: 420k x 0,013 = 5.460 USD
Nova:   420k x 0,0035 = 1.470 USD
Chenh lech: 3.990 USD/thang
`

Day la 73% khoang cach chi phi. 27% con lai la phi bao hiem nho tren Haiku 4.5 vs Nova Micro cho cap cuu.

**Tai sao ai chon Claude**: Chat luong suy luan lam sang tot hon tren cac truong hop bien. Trong PoC cua chung toi, Claude tu choi tra loi 9% cau hoi mot cach phu hop (nghia la no biet no khong biet); Nova Pro ao giac nhieu hon tren cac truong hop bien. Doi voi su dung chu luu, Nova la on. Doi voi cac cau hoi chuyen khoa rui ro cao, Claude an toan hon.

---

### Q22. "Bedrock Model Distillation sang Nova Lite" la gi va tai sao no giam chi phi?

**A.** Distillation la ky thuat ban dao tao mot mo hinh nho hon de bat chuoc mot mo hinh lon hon.

**Truc giac**: Sonnet 4.5 la mo hinh 200B+ tham so dat tien de chay. Nova Lite la ~8B tham so, re hon ~30 lan. Chung ta co the dung Sonnet de day Nova Lite tra loi nhu Sonnet tren cac cau hoi lam sang cu the cua Nova.

**Quy trinh**:
1. Lay 10.000-50.000 cau hoi mau tu linh vuc cua Nova
2. De Sonnet tra loi tat ca chung voi ly luan day du + trich dan
3. Dao tao Nova Lite tren cac dau ra Sonnet do (day la "distillation training")
4. Ket qua: Nova Lite co the tra loi cac cau hoi lam sang cua Nova o chat luong Sonnet 95%+ tren phan phoi duoc dao tao

**Tai sao no giam chi phi**:
- Sonnet tinh 15 USD/trieu token dau ra
- Nova Lite tinh ~0,50 USD/trieu token dau ra (re hon 30 lan)
- Doi voi 40% luong phuc tap ma sinh vien xu ly, ban nhan duoc cau tra loi chat luong Sonnet o chi phi Nova Lite

**Phep tinh** (trong bang chi phi cua chung toi):
`
Khong co sinh vien: 700k truy van phuc tap x 0,013 = 9.100 USD/thang (Sonnet thuan tuy)
Voi sinh vien: 280k Sonnet + 420k sinh vien
            = 280k x 0,013 + 420k x 0,0005
            = 3.640 + 210 = 3.850 USD
Tiet kiem: 5.250 USD/thang
`

**Chi phi distillation**: 670 USD/thang phan bo (dao tao lai hang quy). Tiet kiem rong: 4.580 USD/thang.

---

### Q23. Neu khoi luong truy van cua chung toi cao hon hoac thap hon nhieu thi sao?

**A.** Chi phi co hai thanh phan: co dinh va bien doi.

**Chi phi co dinh** (khong thay doi nhieu theo khoi luong):
- OpenSearch Serverless / OpenSearch Vector Search: 350-500 USD/thang toi thieu
- Neptune Analytics / AnalyticDB GraphRAG: 115-300 USD/thang toi thieu
- ElastiCache Redis / Tair: 80-100 USD/thang toi thieu
- VPN, mang, giam sat: 230 USD/thang toi thieu
- **Tong co dinh**: ~775-1.180 USD/thang/tenant

**Chi phi bien doi** (thay doi theo khoi luong):
- Suy luan LLM (Claude hoac Nova): ty le thuan voi truy van
- Nhung: ty le thuan voi kich thuoc corpus va truy van
- Luu tru: ty le thuan voi corpus + nhat ky kiem toan

**Cong thuc chi phi** (bien the Claude):
`
Chi phi hang thang = 1.800 USD (co dinh) + (truy van x 0,0058 USD trung binh moi truy van)
`

**Chi phi o cac khoi luong khac nhau**:

| Khoi luong/thang | Co dinh | Bien doi | Tong | Moi truy van |
|---|---|---|---|---|
| 100k | 1.800 | 580 | 2.380 | 0,024 |
| 300k | 1.800 | 1.740 | 3.540 | 0,012 |
| 600k (co so) | 1.800 | 3.480 | 5.280 | 0,0088 |
| 1,2M | 1.800 | 6.960 | 8.760 | 0,0073 |
| 3M | 1.800 | 17.400 | 19.200 | 0,0064 |

**Kinh te quy mo**: Chi phi moi truy van giam khi khoi luong tang vi chi phi co dinh duoc phan bo. O 3M/thang, chi phi moi truy van thap hon 73% so voi 100k/thang.

---

### Q24. Co giam gia theo khoi luong tu AWS hoac Alibaba khong?

**A.** Co, theo nhieu hinh thuc:

**Giam gia khoi luong AWS**:
- **Bedrock Reserved Tier**: cam ket token toi thieu hang thang, nhan giam gia 20-40%.
- **Enterprise Discount Program (EDP)**: o muc chi tieu AWS 50k+/thang, dinh gia tuy chinh thuong giam 15-30% so voi gia niem yet.
- **Solution Provider Program**: Nova voi tu cach la doi tac nhan duoc ~10% giam gia doi tac tren cac dich vu AWS ban lai.

**Giam gia khoi luong Alibaba Cloud**:
- **Reserved Instances** (RI) cho tinh toan: giam gia 30-50% voi cam ket 1-3 nam.
- **Cloud Solution Partner discount**: ~15-25% so voi gia niem yet.
- **Chuong trinh nganh y te**: giam gia theo tung truong hop cho cac linh vuc y te.

**Huong dan thuc te**:
- 6 thang dau: dung theo yeu cau (ban chua biet khoi luong on dinh cua minh)
- Thang 6: xem xet su dung thuc te, cam ket Reserved capacity cho phan on dinh (~70%), giu 30% theo yeu cau de co tinh linh hoat
- Nam 2+: dam phan thoa thuan doanh nghiep voi ca AWS va Alibaba de tan dung don bay danh muc

**Don bay dam phan**:
- Ca hai nhom ban hang AWS va Alibaba deu biet gia cua nhau.
- De cap den lua chon thay the khi dam phan: "Chung toi dang danh gia Alibaba, vui long phu hop voi gia cua ho cho y te."
- Singapore la thi truong canh tranh cho ca hai nha cung cap; ky vong giam 15-25% so voi gia niem yet voi lua chon thay the dang tin cay.

---

### Q25. Chi phi thay doi nhu the nao neu chung toi trien khai o Viet Nam, Indonesia hoac Thai Lan?

**A.** Boi canh quan trong: AWS khong co vung Viet Nam hoac Indonesia; Alibaba co Indonesia (Jakarta).

**Singapore vs cac vung ASEAN khac**:

| Vung | AWS co san? | Alibaba co san? | Chi phi vs SG |
|---|---|---|---|
| Singapore | Co (ap-southeast-1) | Co (ap-southeast-1) | Co so |
| Indonesia | Co (ap-southeast-3) | Co | +5-10% (vung nho hon) |
| Thai Lan | Co (ap-southeast-7) | Han che | +10-15% |
| Viet Nam | Khong co vung | Han che | Dung SG (van de tuan thu) |
| Philippines | Khong co vung | Han che | Dung SG |
| Malaysia | Co (ap-southeast-5) | Co | ~Giong SG |

**Phuc tap cu the cua Viet Nam**:
- Nghi dinh 53/2022 yeu cau noi dia hoa du lieu cho mot so danh muc du lieu suc khoe
- Nghi dinh 356/2025 cung co cho ho tro quyet dinh lam sang
- Giai phap: kien truc lai (du lieu benh nhan va nhat ky kiem toan luu tru tai Viet Nam; suy luan LLM xay ra tai Singapore qua du lieu da duoc ma hoa)
- Chi phi: +30% cho co so ha tang data plane

**Khuyen nghi cho mo rong khu vuc cua Nova**:
1. Tenant Singapore: AWS hoac Alibaba SG (co so)
2. Tenant Indonesia: AWS Jakarta hoac Alibaba Indonesia (+5-10% chi phi)
3. Tenant Viet Nam: lai SG + trung tam du lieu VN cuc bo (+30% chi phi, trien khai phuc tap)
4. ASEAN khac: dinh tuyen qua SG voi cac thoa thuan luu luong du lieu theo hop dong

---

'''
f.write_text(f.read_text(encoding='utf-8') + batch, encoding='utf-8')
print('Done, size:', f.stat().st_size)
