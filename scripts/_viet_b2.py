import pathlib
f = pathlib.Path("docs/Client_QA_500_Tieng_Viet.md")
batch = """
### Q11. Thời gian hoàn vốn là bao lâu?

**A.** Dùng giả định bảo thủ:

**Chi phí** (Variant A1+ Nova trên AWS): 2.805 USD/tháng/bệnh viện = 33.660 USD/năm.
**Thời gian tiết kiệm bảo thủ**: giả sử 50% truy vấn thực sự thay thế tra cứu tài liệu.

```
Thời gian phục hồi bảo thủ:
= 600.000 truy vấn x 50% x 5 phút x (80 USD/giờ / 60 phút)
= 2.000.000 USD/tháng

Hoàn vốn:
= 33.660 USD chi phí hàng năm / 2.000.000 USD/tháng giá trị
= 0,017 tháng = ~12 giờ
```

Hệ thống hoàn vốn năm đầu tiên trong vòng 12 giờ sử dụng bác sĩ ở quy mô. Điều này bất thường; hầu hết phần mềm doanh nghiệp có thời gian hoàn vốn 6-18 tháng. Lý do nhanh như vậy: thời gian bác sĩ là chi phí vận hành đắt nhất trong bệnh viện, và bất kỳ khoản tiết kiệm năng suất nào cũng tích lũy.

**Kịch bản bảo thủ hơn**: Ngay cả khi chỉ 10% truy vấn tiết kiệm 5 phút, hoàn vốn vẫn dưới 3 ngày.

---

### Q12. Chúng tôi đo lường thành công như thế nào? Nên theo dõi KPI nào?

**A.** Sáu KPI cấp điều hành:

| KPI | Mục tiêu | Lý do quan trọng |
|---|---|---|
| **Bác sĩ hoạt động hàng ngày** (% tổng số) | 70%+ vào tháng 3 | Chiều sâu áp dụng |
| **Truy vấn mỗi bác sĩ hoạt động/ngày** | 25+ | Mức độ gắn kết |
| **Tỉ lệ click vào trích dẫn** | 25-40% | Duy trì tư duy phản biện |
| **Tỉ lệ thumbs-up** | 90%+ | Sự hài lòng về chất lượng |
| **Tỉ lệ từ chối** | 2-8% | Hệ thống biết mình không biết gì |
| **TTFT cấp cứu** | ≤2s p95 | Tuân thủ SLA |

Cộng thêm 4 KPI an toàn lâm sàng được Giám đốc Y khoa xem xét:

| KPI | Mục tiêu |
|---|---|
| **Tỉ lệ chặn Guardrails** | <3% |
| **Điểm grounding p50** | ≥0,82 |
| **Sự kiện bất lợi có thể quy cho hệ thống** | 0 |
| **Thời gian phản hồi kiểm toán** | <4 giờ từ yêu cầu đến phát lại phiên đầy đủ |

---

### Q13. Làm sao giải thích chi phí cho các bệnh viện đối tác?

**A.** Chi phí tính theo bệnh viện-tenant, và bạn có thể cấu trúc định giá theo nhiều cách:

**Phương án 1: Chuyển qua với biên lợi nhuận**
- Chi phí AWS: 2.800 USD/tháng, tính 4.500 USD/tháng (~60% biên lợi nhuận)
- Lý do: Nova cung cấp tích hợp, đào tạo, tùy chỉnh và bảo hiểm SRE 24/7.

**Phương án 2: Theo ghế bác sĩ**
- 20 USD/bác sĩ/tháng -> 500 bác sĩ = 10.000 USD/tháng mỗi tenant
- Dễ lập ngân sách; mở rộng theo quy mô bệnh viện; biên lợi nhuận cao với bệnh viện nhỏ.

**Phương án 3: Tính theo truy vấn**
- 0,005 USD mỗi truy vấn (5x chi phí suy luận thô 0,001 USD)
- Phù hợp với tăng trưởng sử dụng của bệnh viện.

**Nói với bệnh viện**: "Mỗi bác sĩ của bạn lấy lại ~3 giờ/tuần thời gian tra cứu tài liệu. Với chi phí bác sĩ 80 USD/giờ, đó là ~5.000 USD/bác sĩ/tháng giá trị phục hồi. Chúng tôi tính bạn một phần nhỏ của điều đó (20 USD/bác sĩ/tháng), phần còn lại tích lũy cho bệnh viện của bạn."

---

### Q14. Nếu chúng tôi muốn bắt đầu nhỏ, chỉ một khoa, trước khi triển khai toàn bệnh viện thì sao?

**A.** Được khuyến nghị mạnh mẽ. Nền tảng hỗ trợ triển khai theo từng khoa một cách gọn gàng:

**Cấu hình thí điểm** (ví dụ: chỉ Khoa Cấp cứu):
- Cùng cơ sở hạ tầng, nhưng bộ lọc tenant_id giới hạn truy xuất và phân tích cho dữ liệu ED.
- Chi phí: giống như triển khai đầy đủ vì OpenSearch/Neptune có kích thước tối thiểu bất kể.
- Giá trị thí điểm: cán bộ an toàn lâm sàng xem xét 30 ngày sử dụng thực tế, ký duyệt trước khi triển khai rộng hơn.

**Lộ trình thí điểm điển hình**:
```
Tuần 1-2:    Chỉ ED + ICU (rủi ro cao nhất, xác nhận nhanh nhất)
Tuần 3-6:    Thêm Tim mạch, Hô hấp, Bệnh truyền nhiễm
Tuần 7-10:   Thêm 6 khoa nữa
Tuần 11+:    Toàn bệnh viện
```

**Chi phí trong thí điểm**: Giống như sản xuất (cơ sở hạ tầng được chia sẻ). Thí điểm giảm **rủi ro**, không giảm chi phí.

---

### Q15. Làm sao trình bày điều này với Hội đồng quản trị?

**A.** Bài thuyết trình 90 giây:

> "Các bác sĩ của chúng ta dành khoảng 1 giờ mỗi ngày tìm kiếm tài liệu y khoa. Với 500 bác sĩ, đó là 11.000 giờ mỗi tháng, tương đương 60 nhà nghiên cứu toàn thời gian. Chúng ta có thể phục hồi phần lớn thời gian đó bằng trợ lý AI lâm sàng được căn cứ trong hướng dẫn WHO, ICD-11 và thử nghiệm nội bộ của chúng ta, tất cả được lưu trữ tại Singapore trên AWS [hoặc Alibaba] với đầy đủ tuân thủ PDPA và HCSA.
>
> Chi phí khoảng 35.000-65.000 USD mỗi năm mỗi tenant. Thời gian phục hồi có giá trị 2-4 triệu USD mỗi tháng theo tỉ lệ bác sĩ tiêu chuẩn. Hệ thống hoạt động trong 6-10 tuần. Ba cố vấn bác sĩ và Giám đốc Y khoa đã xác nhận bằng chứng khái niệm; 100% câu trả lời kiểm tra được căn cứ trong nguồn được trích dẫn, với thời gian phản hồi dưới 5 giây cho các truy vấn cấp cứu.
>
> Hồ sơ rủi ro thuận lợi: hỗ trợ quyết định lâm sàng, không phải AI tự chủ; bác sĩ giữ toàn bộ phán xét lâm sàng; nhật ký kiểm toán đầy đủ cho báo cáo HCSA; từ chối theo mặc định khi không chắc chắn. Quyết định là liệu có dẫn đầu thị trường Đông Nam Á về điều này hay theo sau."

---

### Q16. Cạnh tranh trông như thế nào?

**A.** Ba danh mục đối thủ cạnh tranh:

**Đối thủ trực tiếp (nhà cung cấp AI lâm sàng)**:
- Glass Health (Mỹ): suy luận lâm sàng chung, không được bản địa hóa Singapore
- Hippocratic AI (Mỹ): tập trung vào bệnh nhân, trường hợp sử dụng khác
- Suki AI (Mỹ): tập trung vào ghi chép/tài liệu, không phải hỗ trợ quyết định
- Bot M.D. (Singapore): chatbot cho y tế, ít nghiêm ngặt về trích dẫn hơn

**Đối thủ gián tiếp (cơ sở dữ liệu tham khảo)**:
- UpToDate: tiêu chuẩn ngành, nhưng không tạo sinh; bác sĩ tìm kiếm và đọc
- DynaMed: tương tự UpToDate
- Cả hai đều tốn 400-600 USD/bác sĩ/năm; không tích hợp dữ liệu nội bộ

**Lợi thế khác biệt của Nova**:
1. Tích hợp thử nghiệm nội bộ (chỉ Nova có dữ liệu của Nova)
2. Tuân thủ bản địa Singapore (PDPA + HCSA + IMDA trong một stack)
3. Sẵn sàng đa tenant (bán cho nhiều bệnh viện)
4. Hai đường mô hình (AWS Claude hoặc Alibaba Qwen) cho khách hàng lựa chọn

---

### Q17. Nếu điều này hoạt động, chúng tôi có thể bán nó cho các bệnh viện khác không?

**A.** Có, và đây có thể là cơ hội dài hạn lớn hơn. Ba con đường:

**Con đường 1: SaaS cho bệnh viện đối tác**
- Mỗi bệnh viện mới là một tenant. Chi phí cơ sở hạ tầng biên: ~2.500-5.500 USD/tháng mỗi tenant.
- Tính 10.000-25.000 USD/tháng mỗi tenant (~70-80% biên lợi nhuận).

**Con đường 2: OEM nhãn trắng**
- Hệ thống y tế lớn hơn thích gắn nhãn riêng. Tính phí thiết lập + giấy phép mỗi tenant.
- Giá cao hơn (30k-100k USD/tháng) nhưng chu kỳ bán hàng dài hơn.

**Con đường 3: Nhúng vào quan hệ đối tác EHR**
- Epic, Cerner, Allscripts tại Singapore có thể nhúng trợ lý của Nova vào ứng dụng FHIR của họ.
- Chia sẻ doanh thu, giao dịch nhỏ hơn nhưng khối lượng lớn.

**Tổng thị trường có thể tiếp cận** ở Đông Nam Á: ~250 bệnh viện vừa và lớn ở mức trung bình 15k USD/tháng = ~45 triệu USD ARR trong 3 năm nếu Nova chiếm 40% thị phần.

---

### Q18. Chi phí định kỳ so với một lần là gì?

**A.** Hai danh mục chi phí:

**Chi phí một lần** (chỉ Năm 1):

| Hạng mục | Chi phí |
|---|---|
| Triển khai ban đầu (kỹ thuật) | 80.000-150.000 USD |
| Tích hợp EHR mỗi bệnh viện | 15.000-40.000 USD |
| Kiểm toán chứng nhận tuân thủ | 20.000-50.000 USD |
| Đào tạo bác sĩ ban đầu | 10.000-25.000 USD |
| **Tổng một lần Năm 1** | **125.000-265.000 USD** |

**Chi phí định kỳ** (mỗi năm):

| Hạng mục | Hàng năm |
|---|---|
| Cơ sở hạ tầng đám mây (mỗi tenant) | 34.000-66.000 USD |
| Phân bổ kỹ thuật SRE | 80.000 USD |
| Xem xét an toàn lâm sàng | 20.000 USD/tenant/năm |
| Báo cáo tuân thủ + chuẩn bị kiểm toán | 15.000 USD/tenant/năm |
| Chương trình phản hồi bác sĩ | 10.000 USD/tenant/năm |
| **Tổng định kỳ mỗi tenant** | **159.000-191.000 USD** |

**Hình dạng chi phí theo thời gian**:
```
Năm 1: ~284.000-456.000 USD (một lần + định kỳ)
Năm 2+: ~159.000-191.000 USD/năm/tenant
```

---

### Q19. Điều này ảnh hưởng đến bảo hiểm trách nhiệm y tế của chúng tôi như thế nào?

**A.** Ba điểm cần thảo luận với công ty bảo hiểm:

**1. Cập nhật chính sách cho "hỗ trợ quyết định tăng cường AI"**
Hầu hết chính sách trách nhiệm y tế năm 2026 có điều khoản bổ sung cho hỗ trợ quyết định tăng cường AI. Chi phí: thường tăng phí bảo hiểm 5-12%.

**2. Tranh luận để giảm phí bảo hiểm dựa trên tài liệu tốt hơn**
Nhật ký kiểm toán toàn diện hơn tài liệu lâm sàng thông thường. Một số công ty bảo hiểm (Chubb, Howden Singapore) cung cấp giảm giá cho bệnh viện có nhật ký kiểm toán AI có thể xác minh vì:
- Các vụ kiện dễ bào chữa hơn (chuỗi lý luận đầy đủ được bảo tồn)
- Trễ chẩn đoán giảm (câu trả lời nhanh hơn)
- Suy luận lâm sàng được tiêu chuẩn hóa (ít biến động giữa các bác sĩ hơn)

**3. Phân bổ bồi thường với nhà cung cấp công nghệ**
Trong hợp đồng với nhà cung cấp đám mây và với Nova:
- Nhà cung cấp chịu trách nhiệm về lỗi công nghệ (ví dụ: ngừng dịch vụ, rò rỉ dữ liệu từ cơ sở hạ tầng)
- Bệnh viện/bác sĩ chịu trách nhiệm về quyết định lâm sàng được đưa ra dựa trên câu trả lời

**Tác động chi phí ròng**: Thường là hòa vốn hoặc giảm ròng 5-10% sau khi kiểm toán viên thấy một năm hồ sơ thực tế.

---

### Q20. Nếu bác sĩ sao chép câu trả lời của AI vào hồ sơ bệnh nhân thì có vấn đề không?

**A.** Đây là câu hỏi quy trình làm việc thực tế. Trả lời theo 3 lớp:

**Hướng dẫn tài liệu**:
- Có, bác sĩ có thể sao chép câu trả lời của AI vào hồ sơ, nhưng nên ghi nguồn: "Tham khảo hỗ trợ quyết định: [ID tham chiếu truy vấn AI #ABC123, ngày 2026-05-15]."
- Hệ thống tạo ID tham chiếu truy vấn cho mục đích này. Click vào ID sẽ tái tạo lại phiên chính xác để kiểm toán.

**Khung trách nhiệm pháp lý**:
- Sao chép-dán **không** giống như chấp nhận trách nhiệm lâm sàng. Chữ ký của bác sĩ trên hồ sơ vẫn mang thẩm quyền quyết định lâm sàng.
- Nhật ký kiểm toán cho thấy bác sĩ đã xem gợi ý AI VÀ đưa ra phán xét lâm sàng độc lập. Đây là tài liệu **tốt hơn** so với ghi chú dựa trên trí nhớ.

**Quy trình làm việc tốt nhất** (được khuyến nghị trong đào tạo bác sĩ):
```
1. Hỏi trợ lý AI
2. Đọc câu trả lời + ít nhất một trích dẫn
3. Hình thành ý kiến lâm sàng của riêng bạn
4. Ghi lại Ý KIẾN CỦA BẠN + tham chiếu AI như hỗ trợ quyết định
```

**Mô hình chống**: Sao chép-dán câu trả lời AI như thể đó là suy luận lâm sàng gốc. Điều này không phù hợp về mặt chuyên môn và tạo ra sự mơ hồ kiểm toán.

---

"""
f.write_text(f.read_text(encoding="utf-8") + batch, encoding="utf-8")
print("Batch 2 written, total size:", f.stat().st_size)
