# Nova Health Tech · Trợ lý AI Lâm sàng
## 500 Câu hỏi & Trả lời · Dành cho Lãnh đạo Bệnh viện (Không chuyên kỹ thuật)

**Đối tượng**: CEO, COO, CFO, CMO, Giám đốc Y khoa, Trưởng khoa, Cán bộ Tuân thủ, Quản lý Bệnh viện.

**Phong cách**: Ngôn ngữ đơn giản, ví dụ cụ thể, con số thực tế, liên kết với tác động kinh doanh, công thức khi cần.

**Số liệu cơ sở**:
- 500 bác sĩ mỗi bệnh viện
- 40 truy vấn/bác sĩ/ngày
- 22 ngày làm việc/tháng
- 30% cấp cứu / 70% phức tạp
- Chi phí bác sĩ: ~80 USD/giờ
- Khối lượng cơ sở: 600.000 truy vấn/tháng/bệnh viện

---

## 1. Lợi ích kinh doanh & ROI

> *Xem thêm phiên bản tiếng Anh: `docs/Client_QA_500_Questions.md`*

### Q1. Tại sao bệnh viện cần trợ lý AI lâm sàng? Bác sĩ đã có UpToDate rồi.

**A.** UpToDate là công cụ tra cứu tuyệt vời nhưng cần bác sĩ biết tìm gì và đọc nhiều bài. Trợ lý AI khác ở 3 điểm:

1. **Tổng hợp nhiều nguồn trong vài giây.** Thay vì mất 5 phút đọc chương WHO, bài PubMed và báo cáo thử nghiệm nội bộ, trợ lý trả về 1 đoạn văn có trích dẫn trong 2 giây.
2. **Hoạt động ngay trong khi khám bệnh.** Bác sĩ đang có bệnh nhân trước mặt không thể dừng lại 5 phút. Phản hồi 2 giây cho phép dùng ngay trong phòng khám.
3. **Biết dữ liệu thử nghiệm nội bộ.** UpToDate không biết báo cáo thử nghiệm nội bộ của bệnh viện. Trợ lý index cả hai cùng với WHO và ICD-11.

**Tính toán kinh doanh**:
```
500 bác sĩ × 10 phút/ngày × 22 ngày = 110.000 phút/tháng
= 1.833 giờ/tháng × 80 USD/giờ = 146.640 USD/tháng tiết kiệm
```
Hệ thống chi phí 2.800–5.500 USD/tháng. Hoàn vốn trong khoảng 1 tuần.

---

### Q2. ROI thực sự là bao nhiêu?

**A.** Ba nguồn lợi nhuận đo lường được:

1. **Thời gian tiết kiệm mỗi truy vấn**: Bác sĩ mất trung bình 6 phút tra cứu tài liệu. Trợ lý trả lời trong 2–12 giây. Tiết kiệm: ~5 phút/truy vấn.
2. **Mật độ sử dụng**: 40 truy vấn/bác sĩ/ngày × 500 bác sĩ = 20.000 truy vấn/ngày, 600.000/tháng.
3. **Giá trị hàng năm** (chi phí bác sĩ 80 USD/giờ):

```
600.000 truy vấn/tháng × 5 phút × (80 USD/giờ ÷ 60 phút) = 4.000.000 USD/tháng
× 12 tháng = 48.000.000 USD/năm mỗi bệnh viện
```

**Chi phí**: 2.800–5.500 USD/tháng × 12 = 33.600–66.000 USD/năm.
**Tỉ lệ ROI**: ~360x đến 1.400x trong kịch bản bảo thủ.

Lợi ích lớn hơn, khó định lượng hơn: giảm trễ chẩn đoán trong cấp cứu và ít bỏ sót điều trị dựa trên bằng chứng.

---

### Q3. Làm sao biết hệ thống có được sử dụng thực sự không?

**A.** Mỗi truy vấn được ghi lại với metadata (không có thông tin nhận dạng bệnh nhân). Báo cáo hàng tháng bao gồm:

- **Tổng số truy vấn** theo khoa, theo lane (cấp cứu vs phức tạp)
- **Bác sĩ hoạt động**: bao nhiêu trong 500 người thực sự sử dụng tháng này
- **Top 20 loại câu hỏi**: tổng hợp, ẩn danh, hữu ích cho đào tạo
- **Thời gian phản hồi trung bình** theo lane
- **Tỉ lệ click vào trích dẫn**: bác sĩ có click vào nguồn để xác minh không?
- **Tỉ lệ thumbs-up / thumbs-down**

Ví dụ: "Khoa Tim mạch sử dụng trợ lý 12.400 lần tháng này, 94% thumbs up."

Nếu một khoa có tỉ lệ sử dụng thấp, đó là tín hiệu cần xem xét: quy trình làm việc không phù hợp, phản hồi không hữu ích, hoặc cần đào tạo thêm.

---

### Q4. Nếu bác sĩ không tin tưởng AI và từ chối sử dụng thì sao?

**A.** Niềm tin được xây dựng qua 3 cơ chế thiết kế sẵn:

1. **Mỗi câu trả lời đều có trích dẫn nguồn.** Bác sĩ có thể click vào [1] và xem đúng đoạn văn WHO, số trang, ngày cập nhật. Minh bạch hơn khuyến nghị bằng miệng của đồng nghiệp.
2. **Hệ thống nói "tôi không biết" khi không có dữ liệu.** Nếu context không hỗ trợ câu trả lời, hệ thống từ chối. PoC của chúng tôi đo lường 100% trích dẫn và 0% ảo giác.
3. **Được định vị là hỗ trợ quyết định, không phải người ra quyết định.** Bác sĩ giữ toàn bộ phán xét lâm sàng. Trợ lý gợi ý; bác sĩ quyết định.

**Mô hình áp dụng thực tế**: Tuần 1: 20% bác sĩ thử, Tuần 4: 60% dùng hàng tuần, Tuần 12: 85%+ dùng hàng tuần.

---

### Q5. Hệ thống này có thể thay thế nhân viên thư viện y khoa không?

**A.** Không, và chúng tôi khuyến nghị không nên định vị theo hướng đó. Lý do:

- Trợ lý **tăng cường** bác sĩ không có thời gian tra cứu nguồn. Tác động lớn nhất là bác sĩ cấp cứu lúc 3 giờ sáng, không phải thư viện viên đã làm việc cẩn thận.
- Thư viện viên và chuyên viên CDS thực hiện **giám tuyển sâu**: quyết định nguồn nào cần index, kiểm tra chất lượng truy xuất, đào tạo bác sĩ mới. Trợ lý tạo ra nhu cầu cho các vai trò này, không giảm.
- Dùng AI để cắt giảm nhân sự tạo ra vấn đề quan hệ lao động và hiếm khi hiệu quả.

**Trường hợp kinh doanh trung thực**: Không phải "sa thải 5 thư viện viên, tiết kiệm 500k USD/năm." Mà là "cho mỗi bác sĩ có thư viện viên cá nhân, tiết kiệm 500k USD/tháng trong thời gian bác sĩ."

---

### Q6. Bác sĩ có trở nên lười biếng và ngừng tư duy phản biện vì AI trả lời sẵn không?

**A.** Đây là mối lo ngại hợp lệ trong tin học lâm sàng, đôi khi gọi là "automation bias." Chúng tôi giải quyết qua 3 cách:

1. **Định dạng đầu ra buộc bác sĩ phải đọc.** Mỗi câu trả lời có cấu trúc "Khuyến nghị: ..." với bằng chứng trích dẫn. Bác sĩ phải đọc ít nhất phần khuyến nghị.
2. **Trích dẫn có thể click.** Nghiên cứu cho thấy ~30–40% bác sĩ click để xác minh trong các trường hợp mới. Cao hơn xác minh tư vấn bằng miệng (~5%).
3. **Kiểm tra mù định kỳ.** Hàng quý, chạy 50 câu hỏi với trường hợp khó, kết quả được xem xét bởi cán bộ an toàn lâm sàng.

Mối lo ngại tương tự đã được đặt ra với máy tính, hồ sơ bệnh án điện tử, công cụ chẩn đoán hình ảnh. Mô hình nhất quán: công cụ nâng cao công việc, không làm giảm kỹ năng.

---

### Q7. Nếu AI đưa ra câu trả lời sai và bệnh nhân bị tổn hại thì sao?

**A.** Đây là câu hỏi quan trọng nhất. Chúng tôi trả lời qua 3 khía cạnh:

**Pháp lý**:
- Hệ thống được cấp phép và vận hành như **hỗ trợ quyết định lâm sàng** theo HCSA, không phải bác sĩ điều trị.
- Mỗi câu trả lời có tuyên bố rõ ràng: "Chỉ hỗ trợ quyết định. Phán xét lâm sàng cuối cùng thuộc về bác sĩ có phép hành nghề."
- Nhật ký kiểm toán ghi lại: câu hỏi chính xác, bằng chứng truy xuất, câu trả lời, phiên bản mô hình, phiên bản prompt, dấu thời gian.

**Biện pháp kỹ thuật**:
- Xác thực trích dẫn: mỗi khẳng định phải có nguồn thực sự có thể truy xuất.
- Điểm grounding ≥ 0,7: chặn đầu ra không có cơ sở trước khi đến bác sĩ.
- Bedrock Guardrails: chặn các mô hình nguy hiểm đã biết.
- Hành vi từ chối: khi không chắc chắn, hệ thống nói "Tôi không thể trả lời từ context hiện tại."

**Thực tế**: PubMed có bài báo sai. Bài UpToDate bị thu hồi. Đồng nghiệp đưa ra lời khuyên sai. Tiêu chuẩn không phải "AI phải hoàn hảo"; mà là "AI phải tốt ít nhất bằng các lựa chọn thay thế, với khả năng truy xuất tốt hơn."

---

### Q8. Hệ thống này so sánh thế nào với việc thuê thêm bác sĩ?

**A.** Không phải thay thế bác sĩ, nhưng như một **nhân số thời gian**, phép tính rất ấn tượng:

**Chi phí thuê 1 bác sĩ bổ sung (Singapore)**: ~200.000–300.000 USD/năm (lương, phúc lợi, bảo hiểm, đào tạo, văn phòng).

**Trợ lý AI thêm vào**: 5 phút × 600.000 truy vấn/tháng = 50.000 giờ/năm, tương đương ~25 bác sĩ toàn thời gian.

**So sánh**:
```
25 bác sĩ bổ sung × 250.000 USD = 6.250.000 USD/năm
Chi phí trợ lý                   = ~50.000 USD/năm
Tỉ lệ tương đương năng suất      = ~125x
```

Trợ lý không thay thế bác sĩ bạn sẽ thuê để khám thêm bệnh nhân. Nó giải phóng bác sĩ bạn đã có để dành nhiều thời gian **với** bệnh nhân thay vì **nghiên cứu** cho họ.

---

### Q9. Sự khác biệt giữa Nova tự xây dựng hệ thống nội bộ và thuê nhà cung cấp như Alibaba hoặc AWS là gì?

**A.** Đây là câu hỏi build-vs-buy. Ba lớp:

**Nền tảng đám mây** (AWS, Alibaba): Không ai tự xây trung tâm dữ liệu cho việc này nữa. Chi phí vốn rất lớn. Dịch vụ đám mây trả theo sử dụng là lựa chọn hợp lý duy nhất.

**Mô hình AI** (Claude, Qwen): Đào tạo mô hình lâm sàng hàng đầu từ đầu tốn 50–200 triệu USD và mất 12–18 tháng. Anthropic và Alibaba đã làm điều này. Thuê mô hình của họ qua API chỉ tốn vài cent mỗi truy vấn.

**Lớp ứng dụng** (chính trợ lý): Đây là nơi Nova xây dựng. Giá trị gia tăng của Nova là tích hợp WHO + ICD-11 + thử nghiệm nội bộ, đào tạo giọng văn, tích hợp EHR, tư thế tuân thủ.

**So sánh chi phí (ước tính)**:
```
Tự xây dựng:
- Đội kỹ sư (10 người × 200k)     = 2.000.000 USD/năm
- Đội ML/AI (5 người × 250k)      = 1.250.000 USD/năm
- Đội tuân thủ/bảo mật (3 × 150k) = 450.000 USD/năm
- Đám mây + GPU (30% trên)        = 1.100.000 USD/năm
- Tổng                            = 4.800.000 USD/năm
- Cộng thêm: 18 tháng để ra mắt

Dùng dịch vụ quản lý AWS/Alibaba:
- 2–3 kỹ sư tích hợp (Nova hiện có) = ~500.000 USD/năm
- AI + truy xuất quản lý            = 34.000–66.000 USD/năm
- Tổng                              = ~550.000 USD/năm
- Thời gian ra mắt: 6–10 tuần
```

Phương pháp cloud-native **rẻ hơn ~9 lần** với **nhanh hơn ~10 lần**.

---

### Q10. Nếu nó có giá trị như vậy, tại sao tất cả các bệnh viện chưa làm điều này?

**A.** Ba lý do, và Nova có lợi thế ở mỗi điểm:

1. **Hầu hết bệnh viện không có lãnh đạo kỹ thuật.** Xây dựng điều này đòi hỏi hiểu biết về LLM, RAG, cơ sở dữ liệu vector, quy định y tế, tích hợp EHR và kiến trúc bảo mật, tất cả cùng một lúc. Nova Health Tech với tư cách là nhà cung cấp sức khỏe kỹ thuật số có chuyên môn này; một bệnh viện điển hình thì không.

2. **Tuân thủ chưa rõ ràng cho đến gần đây.** PDPA đã rõ ràng; HCSA 2020 chính thức thêm "hỗ trợ quyết định lâm sàng" là danh mục dịch vụ được cấp phép, giải quyết sự mơ hồ quy định. Trước cuối năm 2024, việc triển khai có rủi ro. Bây giờ có thể kiểm toán được.

3. **Ngưỡng chất lượng mô hình đã vượt qua vào 2024–2025.** Claude 3.5/4.5 và Qwen 3.5/3 đạt được suy luận cấp lâm sàng mà GPT-3.5/4 trước đây đơn giản là không có. Grounding trích dẫn qua RAG trưởng thành đến ~98% trong nghiên cứu và ~95% trong triển khai sản xuất.

Các bệnh viện ĐANG triển khai AI lâm sàng vào năm 2026 là: Mayo Clinic, Cleveland Clinic, Singapore SGH (với NUS), Mount Elizabeth. Nova là sớm ở Đông Nam Á — đây là lợi thế cạnh tranh đáng bảo vệ.

---


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



## 3. Tuan thu & Quy dinh Singapore

### Q26. PDPA la gi va tai sao chung toi phai quan tam?

**A.** PDPA = Personal Data Protection Act (Luat Bao ve Du lieu Ca nhan Singapore, 2012, sua doi 2020).

**Nhung gi no yeu cau**:
1. **Lay su dong y** truoc khi thu thap du lieu ca nhan, hoac co co so phap ly ro rang
2. **Thong bao cho moi nguoi** ve du lieu ban thu thap va ly do ("Nghia vu Thong bao")
3. **Chi su dung du lieu cho muc dich da neu**
4. **Giu du lieu chinh xac**
5. **Bao ve du lieu** voi bao mat hop ly
6. **Cho phep moi nguoi truy cap va chinh sua** du lieu cua ho
7. **Thong bao cho co quan quan ly (PDPC) trong vong 72 gio** ve vi pham du lieu anh huong den 500+ ca nhan hoac gay hai dang ke
8. **Bo nhiem Can bo Bao ve Du lieu (DPO)** cho to chuc cua ban

**Doi voi he thong cua chung toi**:
- Du lieu benh nhan la "Du lieu Ca nhan" theo PDPA. Cac quy tac bao ve nghiem ngat ap dung.
- Comprehend Medical / DataWorks SDDP che giau PHI truoc khi no den AI. AI khong bao gio thay ten that, MRN, NRIC.
- Nhat ky kiem toan luu giu dang token da che giau, khong bao gio PHI thu.
- Vi pham (vi du: ai do danh cap co so du lieu) cua cac token da che giau it nghiem trong hon nhieu so voi PHI thu.

**Phat tien vi pham**:
- Len den 1.000.000 SGD HOAC 10% doanh thu hang nam (tuy theo so nao cao hon)
- Cac truong hop thuc te: Singtel bi phat 1 trieu SGD+ vao nam 2020; Marina Bay Sands bi phat 74.000 SGD

**Doi voi Nova**:
- Bo nhiem DPO (trach nhiem 1 FTE, khong nhat thiet phai toan thoi gian)
- Duy tri quy trinh thong bao vi pham
- Dao tao tuan thu PDPA hang nam cho tat ca nhan vien
- Danh gia Tac dong Quyen rieng tu cho viec trien khai AI

**Ket luan**: PDPA la lanh tho quen thuoc. Viec trien khai AI phu hop voi PDPA **vi** no giam thieu phoi nhiem PHI, khong phai bat chap no.

---

### Q27. HCSA la gi va no ap dung cho chung toi nhu the nao?

**A.** HCSA = Healthcare Services Act 2020 (Luat Dich vu Cham soc Suc khoe Singapore).

**Nhung gi thay doi vao nam 2020**:
- HCSA thay the Luat Benh vien Tu nhan va Phong kham Y te (PHMC) cu nam 1980
- Cap nhat cho viec cung cap dich vu cham soc suc khoe hien dai: y te tu xa, suc khoe di dong, **ho tro quyet dinh lam sang dua tren AI**

**Danh muc dich vu theo HCSA**:
- Dich vu benh vien
- Dich vu chuyen khoa
- Dich vu y te lien minh
- **Dich vu Ho tro Quyet dinh Lam sang (CDS)**: lien quan den tro ly AI cua chung toi
- Dich vu y te tu xa

**Doi voi ho tro quyet dinh lam sang cu the**:
- Yeu cau giay phep tu MOH (Bo Y te)
- Dich vu phai dua tren bang chung (yeu cau trich dan phu hop voi HCSA)
- Cac su kien bat loi phai bao cao cho MOH
- Phai hoat dong duoi su giam sat cua bac si co phep hanh nghe duoc neu ten
- Giay phep gia han hang nam voi kiem tra cua MOH

**Tac dong thuc te doi voi Nova**:
- Neu Nova phuc vu benh vien CII: phai chiu danh gia an ninh mang nha cung cap
- Nova nen co chung nhan Cybersecurity Code of Practice (CCoP)
- Kiem tra xam nhap hang nam (~30.000-50.000 USD)
- Giam sat SOC 24/7 (da la phan cua SRE tieu chuan)

**Kien truc cua chung toi vs yeu cau CSA**:
- Anti-DDoS: Co (AWS Shield Advanced / Alibaba Anti-DDoS)
- WAF: Co (AWS WAF / Alibaba WAF)
- Nhat ky kiem toan bat bien: Co (S3 Object Lock / OSS WORM)
- Ma hoa: Co (KMS BYOK)
- Nhat ky truy cap: Co (CloudTrail / ActionTrail)
- Ung pho su co: Co (runbooks + truc ban)

---

### Q28. PDPA, HIPAA va GDPR khac nhau nhu the nao?

**A.** Tat ca deu la luat quyen rieng tu, voi pham vi dia ly va noi dung khac nhau:

**PDPA (Singapore, 2012/2020)**:
- Pham vi: du lieu ca nhan cua ca nhan tai Singapore
- Linh vuc: lien nganh (khong cu the cho y te)
- Phat tien: len den 1 trieu SGD hoac 10% doanh thu
- Chuyen du lieu xuyen bien gioi: yeu cau bao ve tuong duong
- Thong bao vi pham: 72 gio den PDPC

**HIPAA (Hoa Ky, 1996)**:
- Pham vi: Thong tin Suc khoe Duoc Bao ve (PHI) cua benh nhan My
- Linh vuc: cu the cho y te
- Phat tien: len den 1,5 trieu USD moi cap vi pham
- Chuyen du lieu xuyen bien gioi: yeu cau BAA voi tat ca cac nha xu ly phu
- Thong bao vi pham: 60 ngay

**GDPR (Lien minh Chau Au, 2018)**:
- Pham vi: du lieu ca nhan cua cu dan EU
- Linh vuc: lien nganh voi cac quy tac bo sung cho du lieu "danh muc dac biet" (suc khoe)
- Phat tien: len den 20 trieu EUR hoac 4% doanh thu toan cau
- Chuyen du lieu xuyen bien gioi: yeu cau quyet dinh tuong duong hoac SCC
- Thong bao vi pham: 72 gio

**Doi voi Nova**:
- **Luon ap dung PDPA** (trien khai Singapore)
- **Ap dung HIPAA** khi xu ly du lieu benh nhan My (vi du: neu mot cong ty bao hiem My hop tac)
- **Ap dung GDPR** khi xu ly du lieu cu dan EU (vi du: benh nhan la nguoi nuoc ngoai EU tai Singapore)
- **Quy tac nghiem ngat nhat thang**: khi cac quy tac mau thuan, tuan theo quy tac nghiem ngat nhat ap dung

**He thong cua chung toi dap ung ca ba** vi no duoc thiet ke cho tap hop sieu nghiem ngat nhat.

---

### Q29. Chung toi co can phe duyet tu MOH (Bo Y te) truoc khi trien khai khong?

**A.** Co dieu kien. Hai con duong:

**Con duong 1: Giay phep HCSA cho ho tro quyet dinh lam sang**
- Bat buoc neu AI duoc su dung cho cac quyet dinh chan doan hoac dieu tri
- Benh vien nop don; Nova cung cap tai lieu ho tro
- Quy trinh 3-4 thang, bat buoc truoc khi ra mat

**Con duong 2: Phan loai thiet bi y te HSA**
- Co quan Khoa hoc Suc khoe quan ly cac thiet bi y te bao gom phan mem
- Phan loai phu thuoc vao muc do rui ro:
  - **Hang A** (rui ro thap): chi thong bao, khong can phe duyet chinh thuc
  - **Hang B**: phe duyet tieu chuan, ~3 thang
  - **Hang C**: phe duyet nang cao, ~6 thang
  - **Hang D** (rui ro cao nhat, vi du: chan doan tu dong): phe duyet truoc khi ra thi truong, ~12 thang

**Phan loai du kien cua he thong chung toi**: Hang B.

**Ly do Hang B**:
- Day la ho tro quyet dinh lam sang thong bao cho bac si
- Quyet dinh lam sang cuoi cung duoc dua ra boi bac si
- Dau ra la thong tin, khong phai chi thi
- Cau tra loi "sai" gay bat tien nhung yeu cau loi bac si de gay hai cho benh nhan

**Lich trinh phe duyet**: 3-6 thang
**Chi phi nop don**: ~5.000-15.000 SGD cho HSA + 25.000-75.000 USD tu van quy dinh

**Ghi chu thoi gian**: Dieu nay chong lap voi viec xay dung ky thuat, khong mo rong no theo thu tu.

---

### Q30. Khung AI Verify cua IMDA la gi? Chung toi co phai su dung no khong?

**A.** AI Verify la khung kiem tra AI Co trach nhiem cua Singapore duoc IMDA ra mat nam 2023.

**No la gi**:
- Bo cong cu + khung quan tri
- 11 nguyen tac dao duc AI duoc danh gia:
  1. Minh bach
  2. Giai thich duoc
  3. Lap lai duoc/Tai tao duoc
  4. An toan
  5. Bao mat
  6. Manh me
  7. Cong bang
  8. Quan tri Du lieu
  9. Trach nhiem giai trinh
  10. Quyen tu chu & Giam sat cua Con nguoi
  11. Tang truong Bao trum, Xa hoi & Moi truong

**Co bat buoc khong?**:
- **Tu nguyen** doi voi AI chung
- **Duoc khuyen nghi manh me** cho AI y te
- **Bat buoc tren thuc te** doi voi cac hop dong cham soc suc khoe cua chinh phu

**Tai sao chung toi su dung no du sao**:
- Kiem toan AI cua ban theo AI Verify la yeu to phan biet tin cay voi cac benh vien
- Quan he doi tac IMDA cho phep ban tiep thi "Duoc chung nhan AI Verify"
- Bo cong cu mien phi, ~10.000-30.000 USD tu van de chay kiem toan day du

**Anh xa AI Verify cho he thong cua chung toi**:

| Nguyen tac | Trien khai cua chung toi |
|---|---|
| Minh bach | Trich dan tren moi cau tra loi, phien ban mo hinh hien thi |
| Giai thich duoc | Cac chunk duoc truy xuat hien thi trong phan mo rong "Tai sao cau tra loi nay?" |
| Lap lai duoc | Nhat ky kiem toan cho phep tai tao chinh xac |
| An toan | Bedrock Guardrails + diem grounding |
| Bao mat | Ma hoa, IDaaS, nhat ky kiem toan |
| Manh me | Red team 200+ prompt doi nghich truoc khi ra mat |
| Cong bang | Nhat quan gion van giua cac khoa, khong co thien vi nhan khau hoc trong dinh tuyen |
| Quan tri Du lieu | Tuan thu PDPA + theo doi nguon goc |
| Trach nhiem giai trinh | Can bo an toan lam sang + chat_trace |
| Quyen tu chu | Bac si dua ra quyet dinh cuoi cung, AI tu van |
| Tang truong Bao trum | Ho tro da ngon ngu (tieng Anh + tieng Trung qua Cohere v3) |

**Khuyen nghi**: Hoan thanh danh gia ban than AI Verify vao thang 5 cua viec trien khai. Xuat ban bao cao tom tat cho cac benh vien doi tac. Su dung nhu yeu to phan biet thi truong.

---

### Q31. Luat An ninh mang 2018 la gi?

**A.** Luat An ninh mang Singapore thiet lap bao ve Co so Ha tang Thong tin Quan trong (CII).

**Ai la CII**:
- Cac nha khai thac dich vu thiet yeu trong 11 linh vuc:
  1. Ngan hang/tai chinh
  2. **Y te** (lien quan den chung toi)
  3. Nang luong
  4. Nuoc
  5. Vien thong
  6. Giao thong duong bo
  7. Hang khong
  8. Hang hai
  9. Dich vu Chinh phu
  10. Truyen thong
  11. Thong tin-truyen thong

**Chi dinh CII y te**:
- Cac benh vien lon (vi du: SGH, NUH, NTFH) la CII
- **He thong ho tro quyet dinh lam sang** cua ho co the duoc chi dinh la cac thanh phan CII
- Dieu nay them ganh nang tuan thu nhung cung them ho tro an ninh mang cua chinh phu

**Yeu cau doi voi CII (va nha cung cap CII nhu Nova)**:
- Kiem toan an ninh mang hang nam (kiem toan vien duoc CSA phe duyet)
- Bao cao su co trong vong 2 gio ke tu khi phat hien
- Cac bai tap an ninh mang bat buoc
- Cac kiem soat ky thuat cu the: ma hoa, nhat ky truy cap, du phong

**Tac dong thuc te doi voi Nova**:
- Neu Nova phuc vu benh vien CII: phai chiu danh gia an ninh mang nha cung cap
- Nova nen co chung nhan Cybersecurity Code of Practice (CCoP)
- Kiem tra xam nhap hang nam (~30.000-50.000 USD)
- Giam sat SOC 24/7 (da la phan cua SRE tieu chuan)

**Kien truc cua chung toi vs yeu cau CSA**:
- Anti-DDoS: Co (AWS Shield Advanced / Alibaba Anti-DDoS)
- WAF: Co (AWS WAF / Alibaba WAF)
- Nhat ky kiem toan bat bien: Co (S3 Object Lock / OSS WORM)
- Ma hoa: Co (KMS BYOK)
- Nhat ky truy cap: Co (CloudTrail / ActionTrail)
- Ung pho su co: Co (runbooks + truc ban)

---

### Q32. Chung toi co can phe duyet tu MOH truoc khi trien khai khong?

**A.** Da duoc tra loi o Q29. Xem them chi tiet o do.

---

### Q33. Benh nhan co quyen yeu cau du lieu cua ho KHONG duoc AI xu ly khong?

**A.** Theo PDPA, co. Ba co che tu choi:

**1. Rut lai su dong y (quyen PDPA)**
- Benh nhan co the rut lai su dong y cho viec su dung du lieu cu the
- Benh vien phai tuan thu trong thoi gian hop ly
- Doi voi AI: dung xu ly du lieu cua benh nhan nay qua tro ly AI

**2. Tu choi theo tung lan kham**
- Benh nhan co the tu choi su tham gia cua AI cho mot lan tu van cu the
- Bac si ghi chu "benh nhan tu choi tu van AI"
- Tro ly AI bi bo qua cho lan kham do
- Quyen tieu chuan theo dao duc y te

**3. Co hieu vinh vien trong EHR**
- Benh nhan danh dau "khong xu ly AI" trong ho so benh nhan cua ho
- EHR gui co hieu voi moi cuoc goi API
- Tro ly AI tra ve: "Benh nhan da tu choi; tu van AI khong co san cho truong hop nay"

**Tac dong van hanh**:
- Ti le tu choi du kien: <5% dua tren cac trien khai tuong tu
- Thiet ke quy trinh lam viec: tu choi la "click de bo qua" khong phai su gian doan van hanh lon
- Chi phi ho tro tu choi: toi thieu (~5.000 USD ky thuat mot lan cho tich hop co hieu EHR)

**Nhat ky kiem toan**: Moi truy van AI ghi lai trang thai dong y. Neu benh nhan sau do phan doi, kiem toan cho thay lieu viec su dung AI co duoc uy quyen vao thoi diem do hay khong.

---

### Q34. Chung toi co nghia vu cong khai bao cao cac su kien bat loi do AI gay ra khong?

**A.** Nhieu nghia vu bao cao:

**1. Bao cao Su kien Bat loi Bat buoc cua HSA**
- Thiet bi y te Hang B (he thong cua chung toi): cac su kien nghiem trong trong vong 7 ngay
- "Nghiem trong" = tu vong, benh de doa tinh mang, nhap vien, ton thuong vinh vien
- Nop qua he thong MEDDR truc tuyen cua HSA

**2. Bao cao Su co Nghiem trong cua MOH**
- Bao cao cap benh vien cho cac su co lam sang
- Cac su kien co the quy cho AI di qua bao cao su co benh vien tieu chuan
- Du lieu tong hop hang nam duoc bao cao cho MOH

**3. Bao cao Ky luat SMC**
- Neu mot bac si bi cao buoc da phu thuoc qua muc vao AI gay hai
- Benh vien bao cao cho Uy ban Ky luat SMC
- Doc lap voi bao cao he thong

**4. Cong bo cong khai**
- Khong co bao cao cong khai bat buoc o Singapore (khac voi mot so nuoc EU)
- Thuc hanh tot nhat duoc khuyen nghi: bao cao tong hop hang nam cho cong dong benh vien
- Cac an pham thuong mai thuong yeu cau cong bo tu nguyen

**Lich bao cao thuc te**:

| Tan suat | Bao cao |
|---|---|
| Trong vong 2 gio | Kich hoat ung pho su co noi bo |
| Trong vong 24 gio | Uy ban an toan benh vien duoc thong bao |
| Trong vong 7 ngay | Bao cao su kien nghiem trong HSA (neu ap dung) |
| Trong vong 30 ngay | Bao cao phan tich nguyen nhan goc |
| Hang quy | Xu huong tong hop cho lanh dao dieu hanh |
| Hang nam | Bao cao tom tat cong khai (duoc khuyen nghi) |

---

### Q35. Chung toi co can Danh gia Tac dong Quyen rieng tu (DPIA) truoc khi trien khai khong?

**A.** Co, duoc khuyen nghi manh me.

**Khi nao DPIA duoc yeu cau (PDPA Muc 16)**:
- Xu ly du lieu ca nhan nhay cam (suc khoe la nhay cam)
- Xu ly quy mo lon
- Cong nghe moi voi cac tac dong quyen rieng tu

**Ca ba dieu kien ap dung** cho viec trien khai cua chung toi.

**Cac thanh phan DPIA**:

1. **Mo ta xu ly**
   - Du lieu nao duoc thu thap
   - Cach xu ly (che giau PHI, suy luan AI, kiem toan)
   - Ai co quyen truy cap

2. **Su can thiet va tinh tuong xung**
   - Tai sao can ho tro AI
   - Lieu cac lua chon thay the it xam pham hon co the dat duoc cung muc tieu
   - Cac buoc giam thieu du lieu

3. **Danh gia rui ro**
   - Rui ro doi voi chu the du lieu (quyen rieng tu, do chinh xac du lieu, quyen tu chu)
   - Diem xac suat va muc do nghiem trong

4. **Bien phap giam thieu**
   - Ky thuat: che giau PHI, ma hoa, kiem toan
   - To chuc: dao tao, quan tri, hop dong

5. **Tham van**
   - Cac ben lien quan noi bo
   - Ky duyet DPO
   - Tham van PDPC (tuy chon, duoc khuyen nghi cho cac truong hop moi)

**Lich trinh DPIA**: 4-6 tuan
**Chi phi DPIA**: 15.000-30.000 USD (tu van + thoi gian noi bo)
**Dau ra**: Bao cao 30-50 trang; co san theo yeu cau tu PDPC

**Khi nao thuc hien**: TRUOC khi trien khai, ly tuong la trong tuan 5-6 cua viec xay dung. Cac phat hien thong bao cau hinh bao mat cuoi cung.

**Tai lieu song**: Cap nhat DPIA khi:
- Nang cap mo hinh lon (vi du: Sonnet 4.5 -> 5.0)
- Nguon du lieu moi duoc them
- Tenant moi duoc tich hop (cap nhat nhe)
- Thay doi quy dinh

**Su dung thuc te**: Hau het cac benh vien se yeu cau DPIA nhu mot phan cua tham dinh nha cung cap. Hay chuan bi san.

---



### Q36. Dieu gi xay ra trong mot cuoc kiem toan quy dinh boi PDPC, MOH hoac HSA?

**A.** Ba loai kiem toan khac nhau, moi loai co the quan ly duoc:

**Kiem toan PDPC (quyen rieng tu)**:
- Duoc kich hoat boi khieu nai, thong bao vi pham, hoac lua chon ngau nhien
- Thong bao: thuong 2-4 tuan truoc
- Thoi gian: 2-5 ngay tai cho, nhieu tuan theo doi
- Tai lieu yeu cau: DPIA, so do luong du lieu, quy trinh quan ly dong y, ke hoach ung pho vi pham, hop dong nha cung cap, nhat ky kiem toan (mau ngau nhien)

**Kiem toan MOH (giay phep HCSA)**:
- Hang nam theo lich hoac duoc kich hoat boi su kien bat loi
- Thong bao: 4-6 tuan truoc
- Thoi gian: 1-3 ngay tai cho
- Tai lieu yeu cau: mo ta dich vu, ke hoach quan tri lam sang, nhat ky su kien bat loi, bao cao dam bao chat luong, trinh do nhan su, du lieu ket qua benh nhan (da duoc an danh)

**Kiem toan HSA (thiet bi y te)**:
- Dinh ky (moi 1-3 nam doi voi Hang B)
- Thong bao: 6-8 tuan truoc
- Thoi gian: 2-4 ngay tai cho
- Tai lieu yeu cau: Ho so Quan ly Rui ro, Bao cao Danh gia Lam sang, bao cao Giam sat Sau thi truong, nhat ky thay doi phan mem, bao cao su kien bat loi, Hoa don Vat lieu An ninh mang

**Su chuan bi cua chung toi**:
- Tat ca tai lieu bat buoc duoc duy tri lien tuc (khong duoc tap hop vao thoi diem kiem toan)
- Xem xet tuan thu noi bo hang quy (phat hien van de truoc co quan quan ly)
- Nguoi lien lac duoc chi dinh cho moi co quan (Can bo Tuan thu, Giam doc Y te, Quan ly Chat luong)

**Ket qua kiem toan thuong**:
- 70%: Dat voi cac khuyen nghi nho
- 25%: Dat voi cac cai tien bat buoc (thoi han ~3 thang)
- 4%: Dat co dieu kien yeu cau kiem toan theo doi
- 1%: Dinh chi giay phep/dang ky (cac van de nghiem trong)

---

### Q37. Chung toi co the tin tuong rang du lieu benh nhan khong roi khoi Singapore khong?

**A.** Co, voi bao dam hop dong va ky thuat:

**Ma trix vi tri du lieu**:

**Du lieu benh nhan (khi duoc xu ly)**:
- **Luu tru**: ap-southeast-1 (Singapore)
- **Trong qua trinh truyen**: TLS 1.3 trong vung Singapore
- **Trong xu ly LLM**: dang token hoa, duoc xu ly tai Singapore
- **Trong nhat ky kiem toan**: dang token hoa, ap-southeast-1, OSS WORM

**Du lieu van hanh**:
- **Chi so he thong**: ap-southeast-1
- **Nhat ky ung dung**: ap-southeast-1
- **Cau hinh**: ap-southeast-1

**Luong du lieu xuyen bien gioi** (han che):

| Dich vu | Vung | Loai du lieu |
|---|---|---|
| Claude API (Bedrock) | ap-southeast-1 (Singapore) | Prompt da token hoa, hoan thanh |
| Qwen API (Model Studio) | Singapore International | Prompt da token hoa, hoan thanh |
| Ghi nhat ky Anthropic | Khong co (voi cau hinh dung) | Khong co |
| Ghi nhat ky Alibaba | Khong co (voi cau hinh dung) | Khong co |
| Thanh toan AWS | us-east-1 (an danh) | Chi chi so su dung |
| Anti-DDoS | Bien toan cau | Chi metadata moi de doa |

**Bao dam luu tru du lieu**:
- AWS Bedrock: cam ket hop dong voi xu ly ap-southeast-1
- Alibaba Model Studio: cam ket hop dong voi Singapore International
- Ca hai deu cung cap chung nhan luu tru du lieu theo yeu cau

**Xac minh kiem toan**:
- Kiem toan luu tru du lieu hang quy
- Bao cao co san cho cac tenant benh vien
- Nhat ky mang cho thay luong du lieu
- Khoa KMS bi khoa theo vung
- Bucket S3/OSS bi khoa theo vung

**Bang chung thuc te ve luu tru**: Co quan quan ly hoi "Chung minh du lieu benh nhan khong roi Singapore." Chung toi co the cho thay: khoa KMS bi khoa theo vung, bucket S3 bi khoa theo vung, kiem toan egress mang, khong co sao chep xuyen vung duoc kich hoat.

---

### Q38. Dieu gi xay ra neu co vi pham bao mat?

**A.** Lich trinh ung pho vi pham PDPA Singapore duoc xac dinh ro rang:

**Lich trinh (PDPA Muc 26B)**:

| Lich trinh | Hanh dong |
|---|---|
| Gio 1 | Phat hien vi pham, kich hoat nhom ung pho su co |
| Gio 4 | Xac dinh pham vi ban dau (tac dong, ca nhan bi anh huong) |
| Gio 24 | Thong bao noi bo: lanh dao, DPO, cac tenant benh vien |
| Ngay 3 | Phan tich phap y chi tiet dang tien hanh |
| Ngay 3 (72 gio) | **Thong bao PDPC bat buoc** neu vi pham anh huong den 500+ ca nhan hoac gay hai dang ke |
| Ngay 7 | Thong bao cho cac ca nhan bi anh huong |
| Ngay 30 | Bao cao khac phuc chi tiet cho PDPC |
| Ngay 90 | Tuyen bo cong khai (neu ap dung) |

**Phan loai muc do nghiem trong**:

**Cap 1 (Nghiem trong)**: PHI bi lo, >500 ca nhan
- Thong bao PDPC bat buoc trong 72 gio
- Thong bao cho cac ca nhan bi anh huong
- Cong bo cong khai neu truyen thong dua tin
- Phat tien tiem nang: 1 trieu SGD

**Cap 2 (Lon)**: Phoi nhiem PHI han che, <500 ca nhan HOAC khong gay hai ca nhan nhung du lieu bi truy cap
- Thong bao PDPC tuy chon nhung duoc khuyen nghi
- Thong bao cho cac tenant benh vien
- Khac phuc noi bo

**Cap 3 (Nho)**: Khong co PHI bi lo (vi du: chi so he thong bi ro, token da che giau)
- Khac phuc noi bo
- Thong bao PDPC khong bat buoc

**Uoc tinh cap vi pham cua he thong chung toi**:
- Vi pham co kha nang nhat: Cap 3 (he thong chay tren du lieu da token hoa; truy cap PHI thu kho)
- Vi pham nhat ky kiem toan: Cap 3 (nhat ky duoc token hoa)
- Vi pham bucket OSS thu chua PDF goc: Cap 1 (co the gay hai thuc su)

**Chi phi vi pham thuc te** (dien hinh):
- Dieu tra phap y: 50.000-200.000 USD
- Thong bao khach hang: 10.000-50.000 USD
- Phat tien quy dinh: 0-1.000.000 SGD (toi da PDPA)
- Sua chua danh tieng: 50.000-500.000 USD
- Tong: 100.000-2.000.000 USD tuy theo muc do nghiem trong

---

### Q39. Chung toi co can Danh gia Tac dong Quyen rieng tu (DPIA) truoc khi trien khai khong?

**A.** Da duoc tra loi o Q35. Xem chi tiet o do.

---

### Q40. Cac tieu chuan quoc te nao cho AI trong y te chung toi nen tuan theo?

**A.** Mot so tieu chuan lien quan:

**1. ISO 13485 (Quan ly Chat luong Thiet bi Y te)**
- Quan ly chat luong toan dien cho nha san xuat thiet bi y te
- Bat buoc cho thiet bi y te HSA Hang B+
- ~50.000-150.000 USD de chung nhan; ~25.000 USD/nam de duy tri

**2. ISO 14971 (Quan ly Rui ro Thiet bi Y te)**
- Khung quan ly rui ro cu the
- Thanh phan bat buoc cua ho so nop HSA
- Danh gia rui ro lien tuc duoc yeu cau

**3. IEC 62304 (Vong doi Phan mem Thiet bi Y te)**
- Quy trinh vong doi cu the cho phan mem
- Yeu cau tai lieu: thiet ke, kiem tra, quan ly thay doi
- Hau het nha phat trien SaMD My/EU tuan theo dieu nay

**4. ISO 27001 (Bao mat Thong tin)**
- Da yeu cau doi voi AWS/Alibaba (chung toi ke thua)
- Cac benh vien thuong yeu cau Nova duy tri

**5. SOC 2 Type II (Bao mat/Tinh san sang)**
- Nguon goc My, nhung ngay cang duoc yeu cau
- AWS/Alibaba duoc chung nhan o lop dam may

**Duoc khuyen nghi cho Nova**:
- ISO 13485 + IEC 62304: bat buoc cho HSA Hang B
- ISO 27001 + 27018: ke thua tu nha cung cap dam may (khong can chung nhan Nova rieng biet)
- HITRUST CSF: chi neu theo duoi thi truong My

**Tong chi phi chung nhan**: ~200.000-400.000 USD nam dau. Xung dang cho viec ban hang benh vien cao cap.

---

### Q41. Bao mat du lieu benh nhan duoc xu ly nhu the nao?

**A.** Hai lop bao ve:

**Lop 1: Che giau PHI tai thoi diem nhap**
- DataWorks SDDP / Comprehend Medical quet voi cac goi quy tac PHI y te
- Phat hien: ten, MRN, NRIC/FIN, ngay sinh, so dien thoai, email
- Hanh dong: cach ly den /raw/_quarantine/, thong bao quan tri vien, tai lieu bi loai tru khoi chi muc

**Lop 2: Token hoa tai thoi diem chay**
- FC /chat preflight chay SDDP tren tin nhan den va bat ky phan du lieu benh nhan nao tu EHR
- PHI duoc phat hien tro thanh cac token KMS co the dao nguoc: <TEN_0>, <MRN_0>, <NGAY_SINH_0>, <DIEN_THOAI_0>, <EMAIL_0>, <NRIC_0>
- LLM chi thay cac token. Cau tra loi duoc de-token hoa trong giao dien nguoi dung chi.
- Nhat ky kiem toan luu giu dang da token hoa.

**Tai sao token hoa tot hon chi ma hoa**:
- Ma hoa: du lieu bi khoa toan hoc voi mot khoa. Voi khoa, ban co the phuc hoi ban goc.
- Token hoa: du lieu duoc thay the bang mot token ngau nhien. Khong co bang anh xa rieng biet, ban khong the dao nguoc.
- Ngay ca khi AI bi xam pham: no se noi "<TEN_0>", khong phai ten that
- Ngay ca khi nhat ky kiem toan bi xam pham: chi co token, khong co PHI

**Noi bang anh xa song**:
- Kho an toan co han che cao, tach biet khoi he thong chinh
- Yeu cau phe duyet hai nguoi cho bat ky truy cap nao
- Khong the truy cap tu cac he thong san xuat bi xam pham
- Ngay ca khi tin tac co du lieu san xuat + nhat ky kiem toan, ho khong the lay ten benh nhan cho den khi pha vo kho rieng biet

---

### Q42. Bac si co the xem lich su cuoc tro chuyen AI cua ho khong?

**A.** Co, nhieu cap do truy cap:

**Truy cap ca nhan** (moi bac si):
- Lich su cua rieng ho
- Quyen rieng tu: chi du lieu cua rieng ho
- Xu huong va thong tin chi tiet

**Truy cap khoa** (truong khoa):
- Du lieu khoa tong hop
- So sanh voi dong nghiep (an danh)
- Hieu suat khoa

**Truy cap benh vien** (Giam doc Y te):
- Tat ca chi so
- Xem xuyen khoa
- Goc do chien luoc

**Truy cap kiem toan** (Can bo Tuan thu):
- Phat lai phien day du
- Tim kiem theo ngay, bac si, benh nhan, chu de
- Ho tro kiem toan quy dinh

**Luu giu du lieu**:
- Phien hoat dong: du lieu truc tiep
- Phien gan day: luu tru nong 30 ngay
- Phien cu hon: luu tru 6 nam (yeu cau HCSA)
- Xoa tu dong sau 6 nam

---

### Q43. Dieu gi xay ra neu mot bac si roi benh vien?

**A.** Quy trinh offboarding ro rang:

**Ngay 1 (ngay roi)**:
- Thu hoi quyen truy cap ngay lap tuc
- Vo hieu hoa tai khoan IDaaS
- Xoa phien hoat dong
- Xac nhan thu hoi phan cung (neu co)

**Ngay 1-7**:
- Xac minh tat ca quyen truy cap da bi thu hoi
- Kiem tra nhat ky kiem toan cho bat ky hoat dong bat thuong nao truoc khi roi
- Luu giu nhat ky kiem toan (6 nam theo HCSA)

**Dai han**:
- Nhat ky kiem toan cua bac si duoc luu giu theo yeu cau quy dinh
- Khong co truy cap sau khi roi
- Bao mat du lieu benh nhan duoc duy tri

**Lich su cuoc tro chuyen**:
- Cac cuoc tro chuyen cua bac si duoc luu giu trong nhat ky kiem toan
- Khong the truy cap boi bac si sau khi roi
- Co the truy cap boi quan tri vien benh vien cho muc dich kiem toan
- Bao ve quyen rieng tu duoc duy tri

**Tiep nhan bac si moi**:
- Onboarding tu phuc vu: 15 phut
- Phien demo tuy chon: 30 phut
- Khong can dao tao ky thuat
- Truy cap ngay lap tuc sau khi IDaaS duoc cau hinh

---

### Q44. Lam the nao de biet he thong AI dang hoat dong tot hay dang suy giam?

**A.** Giam sat theo thoi gian thuc va xu huong:

**Chi so hieu suat duoc theo doi**:

**1. Toc do**:
- Do tre (p50, p95, p99)
- Thoi gian den token dau tien
- Tong thoi gian phan hoi

**2. Chat luong**:
- Do chinh xac (so voi tieu chuan vang)
- Ti le trich dan
- Ti le tu choi
- Phat hien ao giac

**3. Do tin cay**:
- Thoi gian hoat dong
- Ti le loi
- Thanh cong chuyen doi du phong
- Thoi gian phuc hoi

**4. Su hai long nguoi dung**:
- Thumbs up/down
- Chat luong phan hoi
- Chi so ap dung

**5. Chi so kinh doanh**:
- Chi phi moi truy van
- Su dung tai nguyen
- Lap ke hoach nang luc

**Phat hien suy giam**:

**Canh bao theo thoi gian thuc**:
- Do tre p95 > 2s trong 5 phut
- Ti le loi > 1% trong 10 phut
- Diem chat luong giam > 5% trong tuan

**Phan tich xu huong**:
- So sanh tuan-qua-tuan
- Thang-qua-thang
- Quy-qua-quy

**Phat hien bat thuong**:
- Ngoai le thong ke
- Nhan dang mo hinh
- Phat hien bat thuong dua tren ML

**Kich hoat hanh dong**:

**Ngay lap tuc**:
- Goi bac si truc ban SRE
- Canh bao nhom ky thuat
- Leo thang len chi huy su co

**Ngan han**:
- Dieu tra nguyen nhan goc
- Thuc hien sua chua
- Ngan chan tai phat

**Dai han**:
- Cai tien kien truc
- Thay doi quy trinh
- Cap nhat dao tao

---

### Q45. Chung toi co the kiem tra cac tuyen bo nay mot cach doc lap khong?

**A.** Co, nhieu tuy chon xac minh:

**1. Bao cao Trung tam Tin tuong AWS/Alibaba**
- AWS Artifact: tai xuong SOC 2, ISO 27001, bao cao PCI-DSS
- Trung tam Tin tuong Alibaba: goi tuong tu
- Tat ca chung nhan co the xac minh cong khai

**2. Kiem toan code doc lap**
- Benh vien co the thue cong ty bao mat ben thu ba
- Nova cung cap quyen truy cap code (theo NDA)
- Chi phi dien hinh: 30.000-80.000 USD
- Cac benh vien hop ly da lam dieu nay

**3. Xem xet kien truc**
- Nhom CISO/bao mat cua benh vien xem xet tai lieu kien truc
- Phien hoi dap voi ky thuat cua Nova
- Bao cao kiem tra xam nhap duoc chia se

**4. Demo truc tiep**
- Cho thay luong du lieu thuc te: dat cau hoi -> xem che giau -> xem truy xuat -> xem cau tra loi
- Cho thay muc nhat ky kiem toan duoc tao ra
- Cho thay du lieu KHONG roi khoi vung Singapore

**5. Tai lieu tuan thu**
- DPIA (Q35): tai lieu day du co san
- Bao cao kiem tra xam nhap: duoc chia se theo yeu cau
- Chung chi ISO 27001 (ke thua tu dam may)
- Bao cao SOC 2 Type II

**6. Giam sat cua rieng benh vien**
- SIEM cua benh vien co the nhap nhat ky kiem toan cua chung toi
- Benh vien thay cung du lieu chung toi thay
- Khong can "tin tuong chung toi"

**7. Quyen kiem toan**
- Dieu khoan hop dong tieu chuan: benh vien co the kiem toan Nova mot lan moi nam
- Thong bao 30 ngay
- Pham vi hop ly

---

### Q46. Dieu gi xay ra khi chung toi ket thuc hop dong?

**A.** Quy trinh ket thuc ro rang:

**Ngay 1-30 sau khi ket thuc**:
- Dich vu tiep tuc (giai doan giam dan)
- Benh vien xuat du lieu
- Nha cung cap moi tich hop (neu ap dung)

**Ngay 30**:
- Dich vu bi vo hieu hoa
- Du lieu bi xoa khoi cac he thong hoat dong
- Nhat ky kiem toan duoc luu giu theo quy dinh (6 nam HCSA)

**Ngay 30-90**:
- Hoa don cuoi cung duoc thanh toan
- Bao mat tiep tuc (5 nam sau khi ket thuc)

**Nghia vu dai han**:
- Nhat ky kiem toan: 6 nam (yeu cau HCSA)
- Bao mat: 5 nam sau khi ket thuc
- Cac yeu cau boi thuong: 1 nam sau su co

**Xuat du lieu**:
- Dinh dang tieu chuan (JSON, CSV)
- Nhat ky kiem toan trong dinh dang co the doc duoc
- Tai lieu kien truc
- Cau hinh (khong co bi mat)

**Ho tro di cu**:
- Tai lieu xuat
- Phien hoi dap ky thuat
- Thoi gian an toan 30 ngay cho cac van de

**Khoa nha cung cap**:
- Thap. IP quan trong (corpus, prompt, khai thac) la trong code Nova so huu.
- Cac bit cu the cho dam may (Bedrock, Model Studio) co cac tuong duong hang hoa.
- Chi phi di cu: ~50-100k USD ky thuat, 2-4 tuan.

---

### Q47. Chung toi co the su dung he thong nay cho y te tu xa khong?

**A.** Co, voi dieu chinh. Y te tu xa co cac quy tac cu the:

**Huong dan Y te Tu xa MOH Singapore (2015, cap nhat 2022)**:
- Tu van y te tu xa phai bao gom bac si truc tiep theo thoi gian thuc
- Khong dong bo (luu tru va chuyen tiep) yeu cau phe duyet MOH cu the
- AI co the ho tro ca hai che do

**Doi voi he thong cua chung toi trong y te tu xa**:

**Dong bo (tu van video truc tiep)**:
- Tro ly AI duoc truy cap boi bac si trong khi tu van
- Benh nhan chi thay bac si
- Goi y AI duoc bac si xem xet truoc khi thao luan
- Giong nhu quy trinh lam viec tai cho

**Khong dong bo (vi du: xem xet hinh anh da khoa)**:
- Benh nhan gui hinh anh
- AI pre-screen de phan loai
- Bac si xem xet (voi goi y AI la mot dau vao)
- Quyet dinh duoc ghi lai

**Cau hinh duoc khuyen nghi cho trien khai y te tu xa**:
- Nguong grounding: 0,85 (so voi 0,7 tai cho)
- Mac dinh tu choi: tich cuc hon
- Trich dan bat buoc trong moi cau tra loi (khong co phan hoi chi co tu su)

---

### Q48. Dieu gi xay ra neu co thay doi lon trong quy dinh?

**A.** Quy trinh thich ung quy dinh:

**Cap 1: Chi cap nhat tai lieu**
- Vi du: thong tu MOH moi nhan manh cac quy tac hien co
- Quy trinh: Cap nhat tai lieu noi bo, dao tao nhan vien, khong thay doi he thong
- Lich trinh: 1-2 tuan
- Chi phi: ~2.000 USD thoi gian noi bo

**Cap 2: Thay doi cau hinh**
- Vi du: chu de bi cam moi trong Guardrails (vi du: "khong thao luan ve tinh trang thieu thuoc cu the")
- Quy trinh: Cap nhat chinh sach Guardrails, trien khai qua CI/CD, giam sat
- Lich trinh: 1 tuan
- Chi phi: ~5.000 USD ky thuat + kiem toan

**Cap 3: Thay doi kien truc**
- Vi du: yeu cau luu tru du lieu moi (vi du: "ten benh nhan phai duoc ma hoa voi khoa do benh vien kiem soat")
- Quy trinh: Xem xet thiet ke, thay doi ky thuat, xem xet quy dinh, trien khai, kiem toan
- Lich trinh: 4-12 tuan
- Chi phi: 25.000-100.000 USD tuy theo pham vi

**Theo doi thay doi tuan thu**:
- Can bo tuan thu dang ky: thong tu MOH, ban tin PDPC, cap nhat IMDA, thong bao HSA
- Xem xet tuan thu hang quy
- Kiem toan ben ngoai hang nam bao gom tat ca cac thay doi

**Giao tiep**:
- Thay doi lon: email tat ca cac tenant benh vien 30 ngay truoc
- Thay doi nho: ban tin hang thang
- Thay doi quan trong theo thoi gian thuc: chuoi dien thoai cho cac can bo an toan lam sang

---

### Q49. Chung toi co can bao hiem dac biet cho viec trien khai AI nay khong?

**A.** Co, mot so loai bao hiem:

**1. Bao hiem Trach nhiem Mang (Cyber Liability)**
- Bao gom: dieu tra phap y, thong bao khach hang, phat tien quy dinh
- Pham vi khuyen nghi: 5-10 trieu USD
- Phi bao hiem: 20.000-80.000 USD/nam
- Khau tru: 1-2% chi phi su co

**2. Bao hiem Loi va Thieu sot (E&O)**
- Bao gom: loi phan mem, dich vu khong dap ung mong doi
- Pham vi khuyen nghi: 5-10 trieu USD
- Phi bao hiem: 15.000-40.000 USD/nam

**3. Bao hiem Trach nhiem Nghe nghiep (Benh vien)**
- Cap nhat cho "ho tro quyet dinh tang cuong AI"
- Chi phi: thuong tang phi bao hiem 5-12%
- Mot so cong ty bao hiem giam gia cho nhat ky kiem toan AI co the xac minh

**4. Bao hiem Gian doan Kinh doanh**
- Bao gom: mat doanh thu trong thoi gian ngung hoat dong
- Pham vi: 500k-2 trieu USD
- Phi bao hiem: 10.000-20.000 USD/nam

**Tong phi bao hiem khuyen nghi cho Nova**: ~80.000-150.000 USD/nam

**Thi truong bao hiem tai Singapore**:
- Cac nha cung cap chinh: AIG, Chubb, Howden, Zurich
- Thi truong y te cu the: dang noi len
- Moi gioi chuyen biet: AON Healthcare, Marsh Healthcare

**Meo dam phan**:
- Tong hop chung nhan tuan thu
- Chuan bi ke hoach ung pho su co
- Ket qua kiem tra xam nhap
- So do kien truc (voi trong tam bao mat)
- Tai chinh 3 nam

---

### Q50. Lam the nao de chung toi biet he thong AI dang hoat dong tot hay dang suy giam?

**A.** Da duoc tra loi o Q44. Xem chi tiet o do.

---

