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



## 4. Bao mat & Quyen rieng tu

### Q51. Dieu gi xay ra khi mot bac si hoi AI ve mot benh nhan cu the?

**A.** Tung buoc bang ngon ngu don gian:

**Thiet lap**: Bac si Linh dang xem xet ho so benh nhan Nguyen Van A trong Epic. Benh nhan bi dau nguc, nghi ngo NMCT.

**Buoc 1: Bac si go cau hoi**
- Bac si Linh click nut "Hoi Nova" trong Epic
- Go: "Benh nhan Nguyen Van A, nam 58 tuoi, dau nguc, ECG cho thay ST elevation. Cac lua chon dieu tri?"
- Nhan Enter

**Buoc 2: Xac thuc & uy quyen**
- Trinh duyet gui cau hoi den cong API voi JWT cua Bac si Linh (duoc phat hanh boi IdP cua Epic qua lien ket Cognito)
- Cong API xac minh: Bac si Linh co duoc uy quyen khong? Co (vai tro bac si)
- Dinh tuyen den trinh xu ly chat Nova

**Buoc 3: Che giau PHI** (trong vong 50ms)
- Trinh xu ly chat Nova nhan: "Benh nhan Nguyen Van A, nam 58 tuoi..."
- Comprehend Medical / DataWorks SDDP quet PHI
- Phat hien: "Nguyen Van A" -> thay the bang <TEN_0>
- Van ban moi: "Benh nhan <TEN_0>, nam 58 tuoi, dau nguc, ECG cho thay ST elevation."

**Buoc 4: Kiem tra cache** (trong vong 50ms)
- Bam cau hoi da che giau
- Kiem tra ElastiCache Redis: co truy van tuong tu truoc do khong?
- Cau hoi pho bien (STEMI la thuong gap): co the co cache hit
- Gia su bo lo: tiep tuc truy xuat

**Buoc 5: Truy xuat** (trong vong 1 giay)
- Tim kiem vector tren OpenSearch: tim cac chunk tuong tu "STEMI ST elevation dau nguc dieu tri"
- Top 3 ket qua: huong dan cap cuu tim mach WHO, giao thuc tim mach noi bo, cap nhat ACC/AHA STEMI 2023
- Tim kiem do thi tren Neptune: tim cac thuc the lien quan (thuoc, chong chi dinh, thu thuat)
- Top 2 ket qua do thi: giao thuc aspirin + heparin, PCI chinh vs tieu huyet khoi

**Buoc 6: Tao LLM** (TTFT trong vong 1 giay, tong 3 giay)
- Soan prompt: system prompt + cac chunk duoc truy xuat + cau hoi da che giau
- Gui den Claude Haiku 4.5 (lane cap cuu) qua API streaming
- Nhan cac token streaming: "Khan cap thoi gian..."
- Tung tu, phan hoi xuat hien trong giao dien nguoi dung cua Bac si Linh

**Buoc 7: Xac thuc** (trong vong 100ms)
- Xac thuc trich dan: moi [1], [2] trich dan cac chunk thuc su? Co
- Diem grounding: duoc tinh la 0,91 (tren nguong 0,7) Co
- Bo loc PHI: co PHI nao trong dau ra khong? Khong (chung toi khong bao gio gui PHI den mo hinh) Co

**Buoc 8: Hien thi cho bac si**
- Bac si Linh thay: "Khan cap thoi gian: Benh nhan STEMI. Khuyen nghi:..."
- Trich dan [1], [2], [3] co the click den cac chunk nguon
- Tong thoi gian da qua: ~3,8 giay

**Buoc 9: Nhat ky kiem toan** (song song, khong dong bo)
- Ghi lai phien: ai hoi, khi nao, cai gi duoc hoi (da che giau), cai gi duoc truy xuat, cai gi duoc tra loi
- Luu tru trong S3 Object Lock / OSS WORM, bat bien trong 6 nam

**Tom tat quyen rieng tu**:
- Ten benh nhan "Nguyen Van A" da duoc che giau truoc bat ky xu ly mo hinh nao
- Dich vu LLM Anthropic / Alibaba KHONG BAO GIO thay "Nguyen Van A"
- Nhat ky kiem toan hien thi <TEN_0> khong phai ten that
- Neu kiem toan duoc xem xet, ten that chi duoc tiet lo qua quy trinh tai nhan dang rieng biet, co han che cao

---

### Q52. Neu mot hacker xam nhap vao tai khoan dam may cua chung toi va co gang tai xuong tat ca du lieu thi sao?

**A.** Nhieu lop phong thu:

**Lop 1: Kiem soat truy cap tai khoan**
- Tai khoan root AWS/Alibaba: MFA phan cung, khong bao gio duoc su dung truc tiep
- Nguoi dung IAM voi truy cap dua tren vai tro
- Lien ket voi Entra ID cua Nova (xac thuc tap trung)
- Khong co khoa API ton tai lau; chi co token STS ngan han

**Lop 2: Kiem soat mang**
- Cach ly VPC: cac dich vu du lieu khong the truy cap internet
- Nhom bao mat: mac dinh tu choi, danh sach cho phep ro rang
- Diem cuoi VPC: cac dich vu duoc truy cap qua PrivateLink, khong phai internet cong cong
- Egress cong NAT: chi den cac IP cu the

**Lop 3: Ma hoa**
- Du lieu luu tru: KMS BYOK (benh vien co the thu hoi khoa)
- Du lieu trong qua trinh truyen: TLS 1.3
- Sao luu duoc ma hoa voi khoa rieng biet
- Xoay vong khoa: 90 ngay

**Lop 4: Kiem toan & Phat hien**
- CloudTrail: moi cuoc goi API duoc ghi lai
- GuardDuty: phat hien bat thuong (cac mo hinh API bat thuong)
- Macie: phat hien PHI trong S3 (canh bao neu PHI di chuyen den bucket cong cong)
- ARMS LLM Trace Explorer: cac mo hinh cuoc goi AI

**Lop 5: Sao luu / Bat bien**
- S3 Object Lock: nhat ky kiem toan bat bien trong 6 nam
- Khong the xoa ngay ca boi quan tri vien Nova
- Sao chep xuyen vung

**Lop 6: Bao ve moi de doa noi bo**
- Khong co quan tri vien Nova don le nao co quyen truy cap day du (phan cong trach nhiem)
- Quy tac hai nguoi cho truy cap du lieu san xuat
- Cong cu Quan ly Truy cap Dac quyen (PAM)
- Xem xet truy cap hang quy

**Kich ban xau nhat**:
- Tin tac xam pham tai khoan AWS san xuat cua Nova
- Tai xuong tat ca bucket S3 va chi muc OpenSearch
- Ket qua: IP Nova bi lo (kien truc he thong, prompt), nhung **KHONG CO PHI BENH NHAN BI LO**
- Nova doi mat voi thiet hai danh tieng kinh doanh va co the thong bao khach hang
- Benh nhan KHONG the duoc nhan dang tu du lieu vi pham

**Tai sao kien truc cua chung toi chong vi pham tot hon**:
- Token hoa tai thoi diem nhap (PHI khong bao gio duoc luu tru vinh vien)
- Tach biet kho anh xa
- Phong thu theo chieu sau
- Mac dinh tu choi mang

---

### Q53. Kich ban vi pham xau nhat la gi? Co ai co the danh cap du lieu benh nhan khong?

**A.** Phan tich theo danh muc du lieu:

**Du lieu chung toi luu giu**:
1. **Nhat ky kiem toan** (da token hoa, khong co PHI)
2. **Nhung** (bieu dien toan hoc, khong phai van ban)
3. **Cac chunk cua WHO/ICD-11** (du lieu cong cong du sao)
4. **Bao cao thu nghiem noi bo** (nhay cam, nhung da duoc an danh)
5. **Du lieu cau hinh** (cai dat he thong)

**Du lieu chung toi KHONG luu giu** (sau khi che giau PHI):
- Ten benh nhan
- MRN
- So NRIC/FIN
- Ngay sinh
- So dien thoai
- Dia chi email

**Muc do nghiem trong vi pham theo loai du lieu**:

| Du lieu | Muc do nghiem trong vi pham | Tin tac co the lam gi |
|---|---|---|
| Nhat ky kiem toan (da token hoa) | Thap | Cac mo hinh thong ke, khong co PHI |
| Nhung | Rat thap | Cac vector toan hoc, khong the dao nguoc thanh van ban |
| Cac chunk tri thuc | Khong co | Du lieu cong cong |
| Bao cao thu nghiem (da an danh) | Trung binh | Chi tiet thu nghiem, khong nhan dang benh nhan |
| Cau hinh | Thap | Kien thuc kien truc he thong |
| Khoa KMS | Nghiem trong (nhung can xam pham rieng biet) | Co the giai ma neu cac lop khac cung bi xam pham |

**Dao nguoc token hoa**:
- Bang anh xa tu token tro lai PHI nam trong kho rieng biet, co han che cao
- Truy cap kho yeu cau phe duyet hai nguoi dac biet
- Kho KHONG the truy cap tu cac he thong san xuat bi xam pham
- Ngay ca khi tin tac co du lieu san xuat + nhat ky kiem toan, ho khong the lay ten benh nhan cho den khi pha vo kho rieng biet

**Kich ban xau nhat thuc te**:
- Tin tac xam pham tai khoan san xuat AWS cua Nova
- Tai xuong tat ca bucket S3 va chi muc OpenSearch
- Ket qua: IP Nova bi lo (kien truc he thong, prompt), nhung **KHONG CO PHI BENH NHAN BI LO**
- Nova doi mat voi thiet hai danh tieng kinh doanh va co the thong bao khach hang
- Benh nhan KHONG the duoc nhan dang tu du lieu vi pham

**So sanh voi vi pham dien hinh**:
- SingHealth 2018: ~1,5 trieu ho so benh nhan, PHI day du bi lo (vi pham cap may chu)
- Singtel 2022: Du lieu khach hang bao gom thong tin nhan dang
- Kien truc nay: ngay ca khi toan bo he thong bi xam pham, khong co PHI bi lo

**Rui ro dinh luong**:
- Xac suat xam pham tai khoan day du: <0,1% moi nam (co so nganh cho dam may duoc bao mat tot)
- Thiet hai trong truong hop xau nhat: han che (khong co PHI bi lo)
- Bao hiem bao gom: 5-10 trieu USD (du cho cac kich ban co the xay ra)

---

### Q54. Giai thich cac thuc hanh ma hoa cua chung toi bang ngon ngu don gian.

**A.** Ba loai ma hoa:

**1. Ma hoa luu tru (khi du lieu duoc luu tru)**
- Giong nhu ket an tai ngan hang: du lieu bi khoa trong cac tep duoc ma hoa tren dia
- Ngay ca khi ai do danh cap o cung, ho khong the doc du lieu ma khong co khoa
- Duoc thuc hien boi: AWS KMS / Alibaba KMS

**2. Ma hoa trong qua trinh truyen (khi du lieu di chuyen)**
- Giong nhu phong bi kin: du lieu duoc ma hoa trong khi di chuyen giua cac he thong
- Ngay ca khi ai do nghe trom cap mang, ho chi thay ky tu vo nghia
- Duoc thuc hien boi: TLS 1.3 (HTTPS hien dai)

**3. Ma hoa trong khi su dung (trong khi xu ly)**
- Kho nhat trong ba loai: du lieu can duoc giai ma de xu ly
- Duoc giam thieu boi: thoi gian giai ma toi thieu, bo nho quy trinh co lap, mo-dun bao mat phan cung

**Quan ly khoa**:

**Khoa la gi?** Mot chuoi ngau nhien dai khoa/mo khoa du lieu duoc ma hoa.

**BYOK (Mang Khoa Cua Rieng Ban)**:
- Benh vien tao khoa ma hoa trong tai khoan AWS/Alibaba cua rieng ho
- Chia se voi dich vu ma hoa cua Nova
- Benh vien co the thu hoi bat ky luc nao -> ngay lap tuc ngan Nova truy cap du lieu
- Cung cap cho benh vien quyen kiem soat toi thuong

**Xoay vong khoa**:
- Khoa moi duoc tao moi 90 ngay
- Du lieu cu duoc ma hoa lai voi khoa moi
- Cac khoa cu duoc giu lai de giai ma sao luu (cung duoc xoay vong)

**Nhat ky truy cap khoa**:
- Moi lan su dung khoa duoc ghi lai
- "Ai giai ma cai gi, khi nao"
- Duong dan ho tro kiem toan tuan thu

**Vi du thuc te**:
Tuong tuong ket an ngan hang:
- Ma hoa = cac buc tuong thep va cua
- Khoa = ma so ket hop
- Nhat ky kiem toan = camera ghi lai moi lan vao

Trong he thong cua chung toi:
- AWS KMS / Alibaba KMS = nha cung cap ket an
- BYOK = benh vien so huu ma so ket hop
- CloudTrail / ActionTrail = camera

Neu ke cuop danh cap ket an: van bi khoa.
Neu ke cuop lay duoc ma so: camera cho thay chung vao.
Neu benh vien thay doi ma so: Nova khong the vao cho den khi duoc dat lai.

---

### Q55. Token hoa PHI la gi va tai sao no tot hon chi ma hoa?

**A.** Su khac biet quan trong:

**Ma hoa**: Du lieu bi xao tron toan hoc voi mot khoa. Voi khoa, ban co the phuc hoi ban goc.

**Token hoa**: Du lieu duoc thay the bang mot token ngau nhien. Khong co bang anh xa rieng biet, ban khong the phuc hoi ban goc.

**Vi du voi ten benh nhan**:

**Phuong phap ma hoa**:
`
Goc: "Nguyen Van A"
Da ma hoa: "x7K9pQ2..." (phu thuoc vao khoa)
Voi khoa: co the phuc hoi thanh "Nguyen Van A"
`

**Phuong phap token hoa**:
`
Goc: "Nguyen Van A"
Token: "<TEN_BENH_NHAN_001>"
Bang anh xa (he thong rieng biet): {001: "Nguyen Van A"}
Khong co bang anh xa: token khong the dao nguoc
`

**Tai sao token hoa tot hon cho AI**:
1. **AI khong bao gio thay PHI that**: mo hinh chi thay <TEN_BENH_NHAN_001>, khong phai "Nguyen Van A"
2. **Ngay ca khi dau ra AI bi ro**: no se noi <TEN_BENH_NHAN_001>, khong phai ten that
3. **Token khong can duoc ma hoa**: no da ngau nhien; ma hoa danh cho bang anh xa

**Noi bang anh xa song**:
- Kho co han che cao, tach biet khoi he thong chinh
- Yeu cau phe duyet hai nguoi cho bat ky truy cap nao
- Duoc ma hoa KMS voi khoa rieng biet
- Duoc ghi nhat ky kiem toan

**Cac truong hop loi**:
- Dau ra AI vo tinh bi ro: "<TEN_BENH_NHAN_001>" - KHONG the nhan dang, muc do nghiem trong thap
- Nhat ky kiem toan bi xam pham: cac token, khong phai PHI - KHONG the nhan dang, muc do nghiem trong thap
- CA HAI bi xam pham + kho bi xam pham: yeu cau xam pham nhieu lop - cuc ky kho xay ra

**So sanh voi chi ma hoa**:
- Chi ma hoa: "giai ma voi khoa, thay tat ca PHI"
- Token hoa + ma hoa: ngay ca voi tat ca cac khoa, chi thay cac token

**Vi du thuc te**:
- Ma hoa: khoa nha cua ban voi khoa. Mat khoa, mat quyen truy cap.
- Token hoa: giu so dia chi trong ket an rieng biet. Ngay ca khi ai do vao nha ban, ho khong biet ai song o do cho den khi pha vo ket an so dia chi rieng biet.

---



## 5. Hieu suat & Toc do

### Q56. Tai sao thoi gian phan hoi cap cuu la 2 giay? Con so do den tu dau?

**A.** Nghien cuu nhan thuc va phan hoi cua bac si.

**Co so khoa hoc nhan thuc**:
- Tuong tac "tuc thi" cua con nguoi: ~1 giay
- Tuong tac "phan hoi nhanh" chap nhan duoc: ~2 giay
- Vuot qua 2 giay, duoc cam nhan la "dang cho"
- Vuot qua 5 giay, su chu y cua bac si chuyen sang noi khac

**Nghien cuu quy trinh lam viec lam sang**:
- Bac si cap cuu dua ra ~50 quyet dinh/gio
- Moi gian doan 2+ giay lam gian doan dong chay nhan thuc
- Mot lan cho 5 giay moi quyet dinh: mat 10% nang suat
- Nhieu lan cho tich luy

**Tac dong den benh nhan**:
- Thoi gian cua-den-kim cho STEMI: <90 phut (moi phut tiet kiem = cuoc song)
- Thoi gian den tieu huyet khoi cho dot quy: <60 phut
- Thoi gian den khang sinh cho nhiem trung huyet: <60 phut
- Cac quyet dinh ca nhan can phai nhanh de ho tro tong the

**SLA cua chung toi**:
- p50: 1 giay (hau het cac truy van)
- p95: 2 giay (95% trong 2 giay)
- p99: 3 giay (hiem khi >3 giay)
- p99,9: 5 giay (cuc ky hiem khi >5 giay)

**Ket qua PoC**:
- Dat duoc p50: 1,0 giay, p95: 2,5 giay tren on-demand
- Voi Reserved Tier (san xuat): du kien p50: 0,6 giay, p95: 1,8 giay

**Tai sao khong phai 1 giay?**:
- Co the thuc hien vat ly voi phan cung tuy chinh, dat tien
- 2 giay mang lai 99% gia tri lam sang o 30% chi phi
- Loi ich bien toi thieu vuot qua 2 giay

---

### Q57. Dieu gi xay ra neu mot truy van mat hon 2 giay?

**A.** Nhieu du phong:

**Trong vong 2 giay (95% truy van)**:
- Phan hoi binh thuong, day du chuc nang
- Tat ca cac nguon duoc trich dan, chuoi ly luan day du

**2-3 giay (4% truy van)**:
- Phan hoi mot phan: phan dau tien duoc tra ve qua streaming
- Cac token con lai duoc stream khi co san
- Bac si thay: "Khan cap thoi gian: ..." xuat hien tung tu mot
- Co the hanh dong lam sang tu token dau tien

**3-5 giay (0,9% truy van)**:
- Du phong den phan hoi da cache neu co san
- Du phong den mo hinh don gian hon (Haiku thay vi Sonnet)
- Chat luong giam nhung chap nhan duoc cho cap cuu

**>5 giay (0,1% truy van)**:
- Hien thi chi bao "Dang tim kiem..."
- Bac si co the huy va su dung quy trinh thu cong
- Hoac cho neu thoi gian cho phep

**Chien luoc suy giam thich ung**:
Neu tai trong tong the cao:
- Giam kich thuoc context: 3 chunk thay vi 5
- Bo qua GraphRAG (tiet kiem 1+ giay)
- Su dung mo hinh nho hon cho cac quyet dinh dinh tuyen
- Cache tich cuc hon

**Phat tien SLA** (voi benh vien):
- p95 > 2 giay trong >1 gio: tin dung dich vu 5%
- p99 > 5 giay trong >1 gio: tin dung dich vu 10%
- Ngung hoat dong keo dai >24 gio: tin dung dich vu 25%

---

### Q58. Thoi gian phan hoi thay doi nhu the nao theo loai truy van?

**A.** Thay doi dua tren:

**Yeu to 1: Lane (cap cuu vs phuc tap)**
- Cap cuu: ~1-2,5 giay p95 (Haiku 4.5, it chunk hon)
- Phuc tap: ~9-12 giay p95 (Sonnet 4.5, nhieu chunk hon, guardrails)

**Yeu to 2: Cache hit vs miss**
- Cache hit: <500ms (chi truy xuat va tra ve)
- Cache miss: toan bo pipeline chay

**Yeu to 3: Do phuc tap cau hoi**
- Don gian ("lieu luong la gi?"): nhanh hon
- Phuc tap ("so sanh thuoc A vs B trong suy than voi..."): cham hon
- Cau hoi nhieu phan: cham nhat

**Yeu to 4: Do phu cua tai lieu**
- Cau hoi voi pham vi KB phong phu: truy xuat nhanh
- Cau hoi yeu cau tim kiem sau: cham hon
- Cau hoi can duyet do thi: cham nhat

**Thoi gian phan hoi duoc do** (tu PoC):

| Loai truy van | Trung vi | p95 | Pham vi pho bien |
|---|---|---|---|
| Thuc te don gian (da cache) | 0,3 giay | 0,6 giay | 0,2-0,8 giay |
| Thuc te don gian (chua cache) | 1,2 giay | 1,8 giay | 1,0-2,0 giay |
| Phan loai cap cuu | 1,5 giay | 2,5 giay | 1,2-3,0 giay |
| Chan doan phan biet phuc tap | 4,8 giay | 9,5 giay | 3,0-12 giay |
| Giao thuc nhieu buoc | 6,2 giay | 11,0 giay | 4,0-15 giay |
| Dua tren hinh anh (X-quang) | 8,5 giay | 15 giay | 5,0-20 giay |

---

### Q59. Tai sao lane phuc tap mat nhieu thoi gian (9,7 giay trong PoC)?

**A.** Phan tich chi tiet:

**Phan tich thoi gian lane phuc tap** (tu PoC):
1. Xac thuc + che giau PHI: 100ms
2. Kiem tra cache: 50ms
3. Quyet dinh dinh tuyen (Nova Micro): 400ms
4. Truy xuat tu Vector KB (top 15): 800ms
5. Truy xuat tu GraphRAG (top 3): 600ms
6. Tong chuan bi: ~1.950ms
7. Thoi gian suy nghi Sonnet 4.5: ~7.200ms
8. Streaming + xac thuc: 600ms

**Tong**: ~9.700ms

**Thoi gian dang di dau?**:
- ~75% trong suy luan mo hinh (Sonnet 4.5 suy nghi)
- ~20% trong truy xuat (vector + do thi)
- ~5% trong xu ly truoc/sau

**Tai sao Sonnet 4.5 mat 7+ giay**:
- Xu ly 18 chunk duoc truy xuat (~10.000 token dau vao)
- Tao cau tra loi 800 token voi trich dan
- Chuoi ly luan noi bo (giong chuoi suy nghi)
- Kiem tra Guardrails sau moi chunk

**Muc tieu san xuat voi Reserved Tier**:
- Suy nghi Sonnet: ~3-4 giay (voi dung luong danh rieng)
- Tong: ~5-6 giay dau cuoi

**Cac tuy chon toi uu hoa** (khong co Reserved Tier):

1. **Giam kich thuoc context**
   - Top 10 chunk thay vi 15: tiet kiem ~1 giay
   - Danh doi: it context hon, co the it chinh xac hon

2. **Dung Sonnet chi de tong hop**
   - Dung Haiku cho ly luan ban dau
   - Sonnet chi cho cau tra loi cuoi cung
   - Tiet kiem ~2-3 giay
   - Tac dong chat luong: toi thieu cho hau het cac truy van

3. **Tien tinh toan cac mo hinh pho bien**
   - Cache theo loai cau hoi
   - Tang ti le hit: 35% -> 50%
   - Giam trung binh rong: ~1 giay

4. **Truy xuat song song**
   - Vector + Do thi + Kiem tra Cache song song
   - Tiet kiem ~400ms

**So sanh voi cac lua chon thay the**:
- Tim kiem UpToDate thu cong: 5-15 phut
- Tu van dong nghiep bang mieng: 5-30 phut
- Lane phuc tap cua chung toi o 10 giay: nhanh hon dang ke so voi cac lua chon thay the
- Ngay ca o 15 giay: van nhanh hon 10 lan so voi cac lua chon thay the

---

### Q60. He thong xu ly tai trong cao nhu the nao? Dieu gi xay ra neu 200 bac si truy van cung luc?

**A.** Tu dong mo rong va quan ly tai trong:

**Nang luc o tai trong cao**:
- Tai trong cao nhat moi tenant: ~200 truy van/phut
- Nang luc co so moi tenant: 50 truy van/phut
- Tu dong mo rong len: 500 truy van/phut
- Vuot qua do: hang doi voi uu tien

**Cac thanh phan va kha nang mo rong cua chung**:

**Function Compute / Lambda (trinh xu ly chat)**:
- Tu dong mo rong theo ty le yeu cau
- Cac instance duoc lam am truoc: 16 (tranh khoi dong lanh)
- Toi da: 1000+ dong thoi
- Chi phi: tra theo yeu cau

**Bedrock / Model Studio**:
- Duoc quan ly boi AWS/Alibaba
- Gioi han TPM moi tai khoan: 50k-500k token/phut
- Vuot qua gioi han: hang doi (thuong <30 giay)
- Dung luong danh rieng: bao dam cho benh vien cu the

**OpenSearch / Vector Search**:
- Tu dong mo rong OCU dua tren tai trong
- Co so: 2 OCU
- Cao diem: mo rong len 8 OCU
- Thoi gian truy van duoi 1 giay ngay ca duoi tai trong

**Neptune / GraphRAG**:
- Mo rong theo chieu doc
- Da vung
- Thong luong: 5.000+ truy van/phut co so

**Cache (Redis / Tair)**:
- Bo nho duoc phan bo truoc
- Doc: 100.000+ QPS
- Ghi: 50.000+ QPS

**Ket qua kiem tra tai trong**:
- Kiem tra tai trong duy tri: 500 QPS trong 1 gio
- Do tre p95 duoi tai trong: 3,5 giay (so voi 2,0 giay co so)
- Ti le hit cache tang len 45% duoi tai trong
- Khong co loi, khong co timeout

**Kich hoat mo rong**:
- p95 > 2 giay: canh bao, khong hanh dong tu dong
- p95 > 3 giay trong 2 phut: tu dong mo rong OpenSearch len
- p95 > 5 giay trong 5 phut: goi SRE truc ban

**Chi phi mo rong thuc te**:
- Co so: 600k truy van/thang o 5.500 USD/tenant
- Dot tang (vi du: dai dich): ~2 trieu truy van/thang o 11.000 USD/tenant
- Giam gia Reserved Tier: ~25% tiet kiem o cao diem
- Rong: ~8.250 USD/tenant trong thang cao diem

---



## 6. Do chinh xac & Tin cay

### Q61. AI chinh xac den muc nao? "Do chinh xac" co nghia la gi doi voi AI y te?

**A.** Do chinh xac da chieu:

**1. Do chinh xac trich dan**: Moi khang dinh trich dan nguon thuc su co the truy xuat. Do luong: 100% trong PoC. Nhi phan: co hoac khong.

**2. Do chinh xac grounding**: Cau tra loi nhat quan voi cac nguon duoc trich dan. Do luong boi diem grounding (0-1). Nguong: >=0,7. Trung binh PoC: 0,85.

**3. Do chinh xac thuc te**: Cau tra loi dung ve mat thuc te so voi tieu chuan vang. Do luong boi hoi dong bac si. Muc tieu: >=95% cho cac truong hop khong bien.

**4. Do lien quan lam sang**: Cau tra loi giai quyet cau hoi lam sang thuc te. Do luong boi thumbs up/down cua bac si. Muc tieu: >=90%.

**5. Tinh cap nhat**: Cau tra loi phan anh cac huong dan hien tai. Do luong boi kiem tra so voi WHO/MOH hien tai. Muc tieu: 100% cho cac cau hoi dua tren huong dan.

**Muc tieu do chinh xac cu the**:

| Loai truy van | Muc tieu do chinh xac | Ket qua PoC |
|---|---|---|
| Lieu luong thuoc | >=99% | 99,5% |
| Tieu chi chan doan | >=97% | 98% |
| Giao thuc dieu tri | >=95% | 96% |
| Chan doan phan biet | >=90% | 92% |
| Cac truong hop bien (benh hiem gap) | >=80% | 85% |

**Kiem soat chat luong**:
- Kiem tra truoc khi trien khai: 1000+ cau hoi duoc bac si kiem tra
- Giam sat san xuat: mau ngau nhien 100 truy van hang ngay
- Phan hoi bac si: thumbs up/down tren moi cau tra loi
- Kiem toan hang quy: xem xet ben ngoai

---

### Q62. Chung toi co the tin tuong AI hon UpToDate hoac cac co so du lieu tham khao khac khong?

**A.** Cac ho so tin cay khac nhau:

**Diem manh cua UpToDate**:
- Duoc giam tuyen thu cong boi cac bien tap vien bac si
- Bao thu, duoc kiem tra ky
- Tieu chuan nganh
- Lich su 25+ nam
- Toan dien

**Diem yeu cua UpToDate**:
- Khong theo thoi gian thuc (cap nhat hang thang)
- Khong tich hop voi du lieu benh nhan
- Chung, khong cu the cho benh nhan
- Cham de doc
- Khong co kien thuc thu nghiem noi bo

**Diem manh cua AI cua chung toi**:
- Theo thoi gian thuc (ICD-11 hang ngay, WHO hang thang)
- Suy luan cu the cho benh nhan (voi context EHR)
- Tich hop thu nghiem noi bo
- Toc do (2-3 giay vs 5+ phut)
- Tim kiem tren tat ca cac nguon dong thoi

**Diem yeu cua AI cua chung toi**:
- Cong nghe moi hon, it lich su nganh hon
- Rui ro ao giac (duoc giam thieu nhung khong bang khong)
- Do chinh xac trich dan phu thuoc vao chat luong truy xuat
- Co the bo lo cac chinh sua gan day

**Khung so sanh**:

| Khia canh | UpToDate | AI cua chung toi |
|---|---|---|
| Do chinh xac tren cac cau hoi tieu chuan | 99% | 95-98% |
| Do chinh xac tren cac truong hop phuc tap/bien | 95% | 85-92% |
| Toc do | 5-15 phut | 2-15 giay |
| Cu the cho benh nhan | Khong | Co |
| Tich hop du lieu noi bo | Khong | Co |
| Tan suat cap nhat | Hang thang | Hang ngay |
| Chi phi moi truy van | 0,05-0,15 USD | 0,001-0,013 USD |
| Lich su | 25+ nam | 1-2 nam |

**Phuong phap lai (duoc khuyen nghi)**:
- Dung ca hai
- AI cho truy cap nhanh + cu the cho benh nhan
- UpToDate cho nghien cuu sau va xac minh
- Bac si hoc khi nao nen dung cai nao

---

### Q63. Loi lon nhat AI co the mac trong thuc hanh lam sang la gi?

**A.** Kiem ke rui ro thuc te:

**Danh muc rui ro**:

**1. Trich dan huong dan loi thoi**
- Nguyen nhan: cache cu hoac huong dan duoc cap nhat sau cache
- Tac dong: bac si hanh dong theo thong tin loi thoi
- Xac suat: thap (vo hieu hoa cache hoat dong)
- Giam thieu: kiem tra huong dan theo thoi gian thuc

**2. Lieu luong thuoc sai**
- Nguyen nhan: ao giac hoac loi truy xuat
- Tac dong: loi thuoc
- Xac suat: rat thap (du lieu thuoc duoc giam tuyen ky)
- Giam thieu: kiem tra cheo voi co so du lieu duoc phe duyet

**3. Bo sot chong chi dinh**
- Nguyen nhan: AI khong co lich su benh nhan day du
- Tac dong: phan ung bat loi tiem nang
- Xac suat: trung binh (phu thuoc vao tich hop du lieu)
- Giam thieu: kiem tra chong chi dinh ro rang, tich hop lich su benh nhan

**4. Giai thich trieu chung sai**
- Nguyen nhan: cach dien dat cua bac si mo ho
- Tac dong: chan doan phan biet sai
- Xac suat: thap (AI yeu cau lam ro)
- Giam thieu: cac mau truy van co cau truc

**5. Khuyen nghi trai voi huong dan**
- Nguyen nhan: dao tao loi thoi, truy xuat sai
- Tac dong: bac si bi dan dat sai
- Xac suat: thap (trich dan buoc grounding)
- Giam thieu: kiem tra kep so voi huong dan hien tai

**Cac su co thuc te co kha nang nhat**:
- Tu choi khi cau tra loi co san (am tinh gia): phien phuc nhung an toan
- Cau tra loi da cache loi thoi (hiem): duoc giam thieu boi vo hieu hoa
- Van de dien dat nho (chu quan): tac dong thap

**Cac su co co hau qua nhat**:
- Bo sot tuong tac thuoc hiem (hiem, nghiem trong)
- Khuyen nghi trai voi huong dan hien tai (trung binh)
- Ro PHI (hiem nhung rat nghiem trong)

**Thuc te**: Bac si con nguoi cung mac loi. Nghien cuu cho thay: bac si dung ~80-90% tren cac truong hop phuc tap. Tro ly AI co the giam loi chan doan ~10-15%. Rong: ket qua tot hon, khong hoan hao.

---

### Q64. Lam the nao de biet neu AI dang cho ket qua khac nhau cho cung mot cau hoi?

**A.** Giam sat nhat quan:

**Tai sao cau tra loi co the khac nhau**:

**1. Tao ngau nhien (nhiet do)**
- AI co cai dat nhiet do
- Mac dinh: 0,1 (thap; hau het nhat quan)
- 0 = xac dinh (luon cung mot cau tra loi)
- 0,5+ = sang tao (thay doi)

**Cai dat cua chung toi**: nhiet do = 0,1, ban xac dinh.

**2. Trang thai cache**
- Truy van dau tien: tao moi
- Truy van thu hai (trong TTL cache): da cache, giong het
- Sau khi cache het han: duoc tao lai, co the khac mot chut

**3. Cap nhat co so kien thuc**
- WHO xuat ban huong dan moi luc 02:00 SGT
- Cau hoi luc 01:50: huong dan cu duoc trich dan
- Cau hoi luc 02:10: huong dan moi duoc trich dan
- Day la hanh vi chinh xac

**4. Bien thien truy xuat ngau nhien**
- Tim kiem vector co tinh ngau nhien nho
- Top 5 chunk co the khac nhau tren cac truong hop bien
- Cac chunk khac nhau -> cau tra loi khac nhau mot chut

**5. Cap nhat phien ban mo hinh**
- Hang quy: nang cap mo hinh
- Truoc/sau nang cap: cau tra loi co the phat trien

**Bien thien chap nhan duoc**:
- Khuyen nghi lam sang nhat quan
- Cach dien dat co the khac nhau
- Trich dan phai tuong tu (cung cac nguon chinh)
- Bat dong ve khuyen nghi chinh: dieu tra

**Giam sat nhat quan**:
- Cac cap ngau nhien: cung cau hoi duoc hoi cach nhau 24 gio
- Xem xet thu cong cac su khac biet
- Theo doi: ~5% cap co su khac biet nho (chap nhan duoc)
- Theo doi: ~0,5% co su khac biet co y nghia (dieu tra)

**Kha nang tai tao**:
- De kiem toan/phap ly: phien chinh xac co the duoc tai tao
- "AI da noi gi voi Bac si Linh luc 14:32 SGT ngay 15 thang 5?"
- 100% co the tai tao tu nhat ky kiem toan

---

### Q65. Lam the nao de kiem tra AI truoc khi trien khai cho benh nhan thuc su?

**A.** Xac thuc nhieu giai doan:

**Giai doan 1: Kiem tra don vi (ky thuat)**
- Kiem tra cap thanh phan
- Bao gom: che giau PHI, truy xuat, xac thuc trich dan
- 1000+ truong hop kiem tra
- Chay tren moi thay doi code
- Ti le dat: 100% bat buoc

**Giai doan 2: Kiem tra tich hop**
- Kich ban kiem tra dau cuoi
- Bao gom: lane cap cuu, lane phuc tap, cache, kiem toan
- 200+ kich ban
- Chay hang dem
- Ti le dat: 100% bat buoc

**Giai doan 3: Kiem tra do chinh xac lam sang**
- Cac cau hoi y te tieu chuan vang
- Duoc giam tuyen boi hoi dong tu van lam sang
- Bao gom: 12 khoa, 1000+ cau hoi
- Ti le dat: >=95% bat buoc de trien khai

**Giai doan 4: Kiem tra doi nghich**
- Red team co gang pha vo he thong
- Tiem nhap prompt, kich hoat ao giac
- Ti le dat: >=98% thanh cong phong thu

**Giai doan 5: Trien khai thi diem**
- Nhom nho bac si (vi du: 20)
- Cac truong hop han che (goi y chi doc)
- Kiem tra thuc te trong 30 ngay
- Phan hoi duoc tich hop

**Giai doan 6: Trien khai theo giai doan**
- Tung khoa mot
- Moi giai doan: on dinh 30 ngay
- Cac van de duoc giai quyet truoc giai doan tiep theo

**Giai doan 7: San xuat**
- Trien khai toan benh vien
- Giam sat lien tuc
- Kiem toan do chinh xac hang quy

**Danh muc kiem tra cu the**:

**Lien quan den thuoc**:
- Lieu luong cho cac thuoc pho bien
- Tuong tac thuoc
- Lieu luong than/gan
- An toan thai ky/cho con bu

**Lien quan den chan doan**:
- Chan doan phan biet
- Tieu chi chan doan
- Huong dan hinh anh
- Giai thich ket qua xet nghiem

**Lien quan den dieu tri**:
- Khuyen nghi dieu tri hang dau
- Dieu tri hang hai khi that bai dieu tri
- Lieu phap ket hop
- Cac quan the dac biet

**Lien quan den tuan thu**:
- Tu choi cac yeu cau khong phu hop
- Khong tiet lo PHI
- Tuan theo huong dan
- Cung cap trich dan

---



## 7. Trien khai & Lo trinh

### Q66. Mat bao lau de trien khai tu "quyet dinh duoc dua ra" den "bac si dau tien su dung"?

**A.** Lich trinh thuc te: 6-10 tuan cho tenant benh vien dau tien.

**Phan tich tung tuan**:

**Tuan 1-2: Nen tang**
- Ky hop dong voi Nova
- Cap phep tai khoan AWS/Alibaba
- Thiet lap VPC, IAM, mang
- Ket noi voi IdP benh vien (xac thuc bac si)
- Trien khai OpenSearch va Neptune ban dau

**Tuan 3-4: Nhap du lieu**
- Nhap huong dan WHO
- Tich hop API ICD-11
- Tai len PDF bao cao thu nghiem noi bo (benh vien cung cap)
- Tao nhung vector
- Trich xuat thuc the GraphRAG

**Tuan 5-6: Cau hinh AI**
- Thiet lap cac agent khoa (12 khoa)
- Tuy chinh system prompt
- Cau hinh chinh sach Guardrails
- Khoi tao cache
- Thu thap du lieu fine-tuning (neu ap dung)

**Tuan 7-8: Tich hop & Bao mat**
- Tich hop EHR (FHIR R4)
- Thiet lap webhook SharePoint
- Hoan thien tai lieu tuan thu
- Kiem toan bao mat

**Tuan 9-10: Thi diem & Ra mat**
- Thi diem noi bo (nhan vien Nova): 1 tuan
- Thi diem han che (10-20 bac si): 1 tuan
- Trien khai tung khoa
- Ra mat day du

**Con duong quan trong**:
- Tich hop IdP benh vien: thuong mat 2-3 tuan rieng
- Phe duyet thiet bi y te HSA (neu chua co): 3-6 thang (song song)
- Xem xet an toan lam sang: 2-3 tuan

**Con duong nhanh hon** (neu Nova da lam truoc):
- 4-6 tuan cho cac tenant lap lai
- Cac mau co the tai su dung
- Cac tich hop duoc phe duyet truoc

**Con duong cham hon** (benh vien phuc tap):
- 12-16 tuan neu tich hop EHR la moi
- Nhieu vong tuan thu
- Tuy chinh rong lon yeu cau

---

### Q67. Nhom cua chung toi can lam gi trong qua trinh trien khai?

**A.** Trach nhiem cua benh vien:

**Truoc khi khoi dong** (chuan bi benh vien):
1. Xac dinh nha tai tro du an (CMIO hoac tuong duong)
2. Lap nhom du an benh vien
3. Phe duyet ngan sach ban dau
4. Ky Thoa thuan Dich vu Chu

**Khoi dong den Tuan 2**:

**Trach nhiem nhom benh vien**:
- Chi dinh chuyen gia lam sang (1-2 bac si)
- Thiet lap quyen truy cap cho cac ky su Nova (han che, co pham vi)
- Cung cap chi tiet tich hop IdP
- Xac dinh lien he EHR

**Nova cung cap**:
- Quan ly du an
- Ky su truong
- Can bo tuan thu
- Tu van lam sang

**Tuan 3-4 (nhap du lieu)**:

**Benh vien cung cap**:
- PDF bao cao thu nghiem lam sang noi bo
- Giao thuc cu the cua benh vien
- Tai lieu tham khao theo khoa
- Logo, thuong hieu cho giao dien nguoi dung

**Nova thuc hien**:
- Nhap noi dung
- Cau hinh truy xuat
- Thiet lap cac thuc the GraphRAG

**Tuan 5-6 (cau hinh)**:

**Benh vien cung cap**:
- Tuy chon gion van theo khoa
- Cac chu de bi cam (vi du: cac lieu phap thu nghiem)
- Cac mau tu choi
- Cac mau tin nhan duoc phe duyet

**Nova thuc hien**:
- Cau hinh 12 agent khoa
- Dieu chinh truy xuat theo khoa
- Thiet lap chinh sach Guardrails

**Tuan 7-8 (tich hop)**:

**Benh vien cung cap**:
- Chi tiet diem cuoi FHIR EHR
- Thong tin xac thuc SMART App Launch
- Ngoai le bao mat mang
- Thiet lap duong ham VPN

**Nova thuc hien**:
- Code tich hop FHIR
- Cau hinh SMART
- Thiet lap data plane VPN

**Tuan 9-10 (ra mat)**:

**Benh vien cung cap**:
- Phan hoi bac si
- Lua chon nhom (nhom thi diem)
- Truyen thong den bac si
- Tham du buoi dao tao

**Nova cung cap**:
- Dao tao onboarding
- Ho tro truc tiep trong thi diem
- Giai quyet van de

**Tong no luc benh vien**:
- Nha tai tro du an: ~5 gio/tuan x 10 tuan = 50 gio
- Chuyen gia lam sang: ~10 gio/tuan x 4 tuan = 40 gio
- CNTT benh vien: ~20 gio/tuan x 4 tuan = 80 gio
- Can bo tuan thu: ~5 gio/tuan x 6 tuan = 30 gio
- Tong: ~200 gio thoi gian benh vien

**Chi phi thoi gian benh vien**:
- ~200 gio x 200 USD/gio ty le pha tron = 40.000 USD
- Day la dau tu cho benh vien
- Duoc hoan von trong 2 tuan dau tien van hanh

---

### Q68. Chung toi co the bat dau voi chuong trinh thi diem nho hon truoc khong?

**A.** Duoc khuyen nghi manh me:

**Cac cau truc thi diem**:

**Phuong an 1: Mot khoa, 30 ngay**
- Chon: Khoa Cap cuu (tac dong cao nhat)
- 20-30 bac si
- Che do chi doc ban dau (goi y, khong co hanh dong lam sang)
- Chi phi: giong nhu trien khai day du co so ha tang
- Gia tri: xac thuc truoc khi trien khai day du

**Phuong an 2: Mot loai chuyen khoa, 60 ngay**
- Chon: Noi khoa tren cac khoa
- 50-100 bac si
- Ket hop che do chi doc va su dung tich cuc
- Nhieu du lieu, nhieu su tu tin

**Phuong an 3: Thi diem toan benh vien 90 ngay**
- Tat ca cac khoa, nhung voi khung "thi diem" ro rang
- De ket thuc neu khong hoat dong
- Dat tien nhung thuc te

**Chi phi trong thi diem**:
- Cung co so ha tang nhu san xuat (2.800-5.500 USD/thang)
- Cong them chi phi trien khai benh vien (40.000 USD)
- Tru cac khoang tiet kiem tiem nang trong thi diem

**Tieu chi thanh cong thi diem**:

**Bat buoc**:
- 70%+ bac si thi diem su dung hang tuan
- 90%+ do chinh xac (duoc xac minh boi can bo an toan lam sang)
- 100% tuan thu luu tru du lieu
- Khong co su co bao mat
- <=5% ti le tu choi (tin hieu-nhieu)

**Mong muon**:
- 80% thoi gian tiet kiem tren cac chu de duoc tu van
- 90%+ thumbs up
- 50%+ ap dung trich dan
- Top 5 truong hop su dung duoc xac dinh

**Cac tuy chon ket thuc thi diem**:

**Thi diem thanh cong**:
- Tiep tuc trien khai day du
- Them cac khoa
- Mo rong quy mo

**Thi diem khong ket luan**:
- Gia han them 60 ngay
- Giai quyet cac van de cu the
- Danh gia lai

**Thi diem that bai**:
- Ngung
- Giai doan giam dan 30 ngay
- Nhat ky kiem toan duoc bao ton (quy dinh)

**Khung thi diem duoc khuyen nghi**:
- Thang 1: trien khai + chuan bi thi diem
- Thang 2: van hanh thi diem (30-60 ngay)
- Thang 3: danh gia + quyet dinh
- Thang 4-6: trien khai day du (neu thanh cong)

---

### Q69. Ai tu phia chung toi can tham gia vao viec trien khai?

**A.** Ban do cac ben lien quan:

**Nha tai tro dieu hanh**:
- CEO/COO: trach nhiem cuoi cung, phe duyet ngan sach
- CFO: giam sat ngan sach, theo doi ROI
- CMO: giam sat an toan lam sang

**Lanh dao du an**:
- Giam doc Thong tin Y te Truong (CMIO): nha tai tro du an chinh
- Quan ly Du an: phoi hop hang ngay
- Giam doc Lam sang: ky duyet lam sang

**Chuyen gia lam sang** (1-2 moi khoa):
- Cac bac si chuyen gia ung ho
- Cung cap dau vao lam sang
- Kiem tra thi diem
- Dao tao dong nghiep

**Nhom CNTT**:
- Giam doc CNTT: lanh dao phia CNTT
- Ky su truong: thuc hien ky thuat
- Ky su Bao mat: xem xet bao mat
- Ky su Mang: VPN, tich hop

**Tuan thu**:
- Can bo Tuan thu: giam sat quy dinh
- DPO: bao ve du lieu
- Co van Phap ly: xem xet hop dong

**Tuong duong phia Nova**:
- Giam doc Tai khoan: lanh dao quan he
- Quan ly Du an: phoi hop
- Ky su truong: lanh dao ky thuat
- Tu van Lam sang: lien lac lam sang
- Can bo Tuan thu: ho tro quy dinh

**Nhip do giao tiep**:

**Hang tuan trong trien khai**:
- Quan ly du an (benh vien) <-> Quan ly du an (Nova)
- Cuoc hop trang thai 30 phut
- Cac hang muc hanh dong, cac van de can giai quyet

**Hai tuan mot lan trong trien khai**:
- CMIO <-> Giam doc Tai khoan
- Xem xet 60 phut
- Thao luan chien luoc

**Hang thang sau trien khai**:
- Xem xet nhom day du
- Chi so hieu suat
- Cai tien lien tuc

**Hang quy sau trien khai**:
- Xem xet dieu hanh
- Phan tich ROI
- Lap ke hoach lo trinh

**Cam ket thoi gian uoc tinh**:

| Vai tro | Gio/tuan trong trien khai | Sau trien khai |
|---|---|---|
| Nha tai tro dieu hanh | 1 | <1 |
| CMIO | 5 | 2 |
| Chuyen gia lam sang | 5-10 | 2-3 |
| Truong CNTT | 10-15 | 2-5 |
| Tuan thu | 5 | 1-2 |
| Bac si nguoi dung cuoi | 0 (trong phat trien) | 0,5 (su dung he thong) |

---

### Q70. Chung toi co the tuy chinh he thong theo nhu cau cu the cua benh vien khong?

**A.** Co, nhieu cap do tuy chinh:

**Cap 1: Cau hinh** (khong co code)
- Cai dat theo khoa
- Tuy chon gion van (trang trong hon, tro chuyen hon)
- Muc do chi tiet (ngan gon vs toan dien)
- Dinh dang (dau dong vs van xuoi)
- Phong cach trich dan (noi tuyen vs cuoi)
- Ngon ngu (tieng Anh, tieng Trung, v.v.)
- Thuong hieu benh vien

**Chi phi**: Bao gom trong thiet lap tieu chuan
**Lich trinh**: 1-2 tuan

**Cap 2: Prompt tuy chinh** (it code)
- System prompt theo khoa
- Huong dan cu the cua benh vien
- Cac tinh chinh chuyen khoa

**Chi phi**: 5.000-10.000 USD thiet lap
**Lich trinh**: 2-3 tuan

**Cap 3: Quy trinh lam viec tuy chinh** (it code)
- Cac luong phe duyet cu the cua benh vien
- Cac quy tac dinh tuyen tuy chinh
- Xu ly dac biet cho cac dieu kien nhat dinh

**Chi phi**: 15.000-30.000 USD
**Lich trinh**: 4-6 tuan

**Cap 4: Tich hop tuy chinh** (code)
- Tich hop cac he thong cu the cua benh vien
- Nguon du lieu tuy chinh
- API benh vien

**Chi phi**: 40.000-100.000 USD
**Lich trinh**: 8-12 tuan

**Cap 5: Tinh nang tuy chinh** (code dang ke)
- Giao dien nguoi dung cu the cua benh vien
- Tinh nang chi danh cho benh vien
- Tuy chinh nang cao

**Chi phi**: 100.000-300.000 USD
**Lich trinh**: 6-9 thang

**Cac tuy chinh pho bien**:

**Cau hinh chuyen khoa**:
- Lieu luong dua tren can nang nhi khoa
- Cac can nhac lao khoa
- Cac quy tac an toan thai ky/cho con bu

**Boi canh dia phuong**:
- Danh muc thuoc cua benh vien
- Nhan thuoc Singapore
- Cac lua chon thuoc generic dia phuong

**Tich hop quy trinh lam viec**:
- SSO cu the cua benh vien
- Cac lo trinh phan loai tuy chinh
- Cac luong ban giao noi bo

**Bao cao tuy chinh**:
- Chi so cu the cua benh vien
- Bang dieu khien theo khoa
- Dinh dang bao cao tuan thu

**Danh doi**:

**Nhieu tuy chinh hon**:
- Phu hop hon voi benh vien
- Chi phi cao hon
- Trien khai lau hon
- Ganh nang bao tri nhieu hon

**It tuy chinh hon**:
- Nhanh hon, re hon
- Chat luong tieu chuan
- De nang cap hon
- Co the khong phu hop hoan hao

**Khuyen nghi**:
- Nam 1: tuy chinh toi thieu (Cap 1-2)
- Nam 2: xac dinh khoang trong, tuy chinh Cap 3
- Nam 3+: dua tren nhu cau duoc chung minh

---



## 8. Du lieu & Nguon tri thuc

### Q71. AI lay kien thuc y te tu dau?

**A.** Nhieu nguon duoc giam tuyen:

**Nguon chinh**:
- **Huong dan WHO** (~300 tai lieu): huong dan song, giao thuc benh, cap nhat hang thang
- **API WHO ICD-11** (~120.000 thuc the): phan loai benh quoc te, cap nhat hang ngay
- **Bao cao thu nghiem noi bo** (cu the theo benh vien): du lieu thu nghiem da duoc an danh, giao thuc dieu tri
- **Giao thuc dieu tri** (cu the theo benh vien): SOP, tai lieu lo trinh, cong cu ho tro quyet dinh lam sang
- **PubMed E-utilities** (cong cu thoi gian chay): tim kiem PubMed theo thoi gian thuc, cac bai bao nghien cuu moi nhat

**Nguon tuy chon** (theo benh vien):
- Tich hop giay phep UpToDate (chi phi bo sung)
- Tich hop DynaMed
- Huong dan hoi chuyen khoa (ACC/AHA, ESC, v.v.)
- Tap chi cu the cua benh vien

**Nhung gi chung toi KHONG su dung**:
- Wikipedia (khong dang tin cay)
- Tim kiem internet chung (rui ro ao giac)
- Mang xa hoi benh nhan
- Tai lieu quang cao duoc phe duyet boi cong ty duoc pham (co the co thien vi)

**Kiem soat chat luong nguon**:
- Tat ca cac nguon duoc kiem tra boi hoi dong tu van lam sang
- Co so tham khao khi co the
- Cac to chuc co tham quyen duoc uu tien
- Tan suat cap nhat duoc theo doi

---

### Q72. Du lieu moi nhat la khi nao? Khi nao cap nhat gan nhat?

**A.** Nhip do cap nhat da nguon:

**Cap nhat hang ngay** (02:00 SGT): API WHO ICD-11 - phan anh cac ban phat hanh hang ngay cua WHO, trong vong 24 gio ke tu khi WHO xuat ban.

**Cap nhat hang thang + RSS**: PDF huong dan WHO - Dinh ky: Ngay 1 hang thang 02:30 SGT. Thoi gian thuc: thong bao RSS kich hoat nhap ngay lap tuc.

**Cap nhat hang tuan + webhook**: Bao cao thu nghiem noi bo - Dinh ky: Chu nhat 03:00 SGT. Thoi gian thuc: webhook SharePoint khi co file moi.

**Vo hieu hoa cache**: Khi KB duoc cap nhat, cac cau tra loi da cache lien quan duoc xoa tu dong. Vo hieu hoa dua tren the, chi xoa cac chunk phu hop.

**Hien thi tinh moi trong giao dien nguoi dung**:
- "Cap nhat [ngay]" tren moi trich dan
- Banner tren cac tai lieu cu (>ngay_xem_xet)
- AI co the canh bao: "Luu y: khuyen nghi nay co the loi thoi"

**So sanh voi cac lua chon thay the**:
- UpToDate: ~6 thang tre cho cac bai viet
- Sach giao khoa thu cong: 2-5 nam tre
- Bai bao tap chi truc tiep: thoi gian thuc nhung chua duoc xac minh

**Loi the cua chung toi**: Trong so nhanh nhat trong AI y te. Nguon goc co the xac minh. Vo hieu hoa tu dong.

---

### Q73. Chung toi co the them huong dan lam sang cua rieng minh vao co so kien thuc khong?

**A.** Co, duoc thiet ke cho dieu do.

**Nhung gi benh vien co the them**:
- Giao thuc cu the cua benh vien
- Cac bo lenh chuan
- Chinh sach quan ly khang sinh
- Cac giao thuc cai thien chat luong
- Cac tai lieu giang day
- Cac bien the dia phuong cua huong dan WHO/MOH

**Quy trinh tai len**:
1. Benh vien xuat PDF (da duoc an danh)
2. Gan the voi metadata (khoa, phien ban, ngay)
3. Tai len qua cong thong tin an toan hoac dong bo SharePoint
4. Phe duyet quy trinh lam viec (Giam doc Lam sang phe duyet)
5. Uu tien truy xuat duoc thiet lap
6. Co san trong vong 24 gio

**Cac loai tai lieu duoc ho tro**:
- PDF (pho bien nhat)
- Word/DOCX
- HTML
- Van ban thuan
- Markdown

**Yeu cau chat luong tai lieu**:
- Van ban co the tim kiem (khong phai hinh anh quet)
- Cau truc hop ly (tieu de, doan van)
- Noi dung chat luong (co tham khao khi co the)
- Ngay xuat ban ro rang

**Chi phi**: Tieu chuan: bao gom. Tuy chinh nang cao: 5.000-15.000 USD. Di cu hang loat: 10.000-30.000 USD.

---

### Q74. Dieu gi xay ra khi WHO cap nhat mot khuyen nghi?

**A.** Quy trinh toan dien de dam bao tinh moi:

**Phat hien**: Cac trang huong dan WHO duoc craw hang tuan. So sanh voi phien ban truoc. Canh bao khac biet den nhom tuan thu.

**Quy trinh cap nhat**:
`
1. Phat hien (tu dong): "WHO da cap nhat khuyen nghi corticosteroid COVID-19"
2. Phan loai (trong vong 4 gio): can bo an toan lam sang xem xet
3. Phan loai:
   a. Nho (loi chinh ta, dinh dang): uu tien thap, cap nhat theo lo
   b. Trung binh (thay doi thu tuc): xem xet tieu chuan va nhap
   c. Lon (thay doi khuyen nghi dieu tri): UU TIEN CAO
4. Nhap (trong vong 24 gio doi voi lon):
   a. Phan tich lai PDF WHO
   b. Phan khuc va nhung lai
   c. Cap nhat OpenSearch + Neptune
   d. Vo hieu hoa cache (chi nguon bi anh huong)
5. Giao tiep (trong vong 48 gio doi voi lon):
   a. Thong bao email den tat ca cac tenant benh vien
   b. Banner trong giao dien nguoi dung: "Cap nhat [ngay]: WHO da sua doi khuyen nghi"
   c. Cac cau tra loi truoc day bi anh huong duoc danh dau de danh gia lai
`

**Giai quyet xung dot** (vi du: WHO khong dong y voi MOH):
- AI hien thi ca hai voi ghi nhan
- Banner giai thich su khac biet
- Can bo an toan lam sang xem xet cac truong hop bien

**Chi phi**: Chi phi co so ha tang toi thieu (da duoc xay dung); ~10 gio/thang thoi gian can bo an toan lam sang.

---

### Q75. Dieu gi xay ra khi AI khong co thong tin ve mot truong hop cu the?

**A.** Tu choi trung thuc voi huong dan co ich.

**Cac mau tu choi**:

**Mau 1: KB thieu thong tin**:
> "Toi khong the tra loi dieu nay tu context hien tai. Co so kien thuc hien co khong chua thong tin cu the ve [chu de]. Cac tai nguyen duoc goi y: [danh sach cac lua chon thay the]."

**Mau 2: Cau hoi qua cu the**:
> "Toi khong co thong tin ve truong hop cu the nay. Cach tiep can chung cho cac truong hop tuong tu la [cach tiep can chung]. Doi voi benh nhan cu the: [khuyen nghi tu van chuyen khoa]."

**Mau 3: Chu de gan day khong co nhap**:
> "Day co ve la mot phat trien gan day. Huong dan moi nhat toi co la ngay [ngay]. De cap nhat moi nhat, tham khao [PubMed/UpToDate/hoi chuyen khoa]."

**Nhung gi AI KHONG lam**:
- Khong bịa dat cau tra loi
- Khong ngoai suy tu du lieu han che
- Khong xin loi qua muc
- Khong tuyen bo chuyen mon ma no khong co

**Ti le tu choi**: Muc tieu 5-10% (mot so tu choi la hanh vi chinh xac)
- <5%: AI co the qua tu tin
- >15%: Khoang trong KB dang ke

**Theo doi mo hinh**:
- Theo doi cac tu choi thuong xuyen
- Xac dinh khoang trong KB
- Them noi dung con thieu
- Cai tien lien tuc

---

## 9. Tich hop & Quy trinh lam viec

### Q76. AI tich hop voi EHR hien co cua chung toi nhu the nao?

**A.** Tich hop dua tren tieu chuan:

**Tich hop qua SMART on FHIR**:
- HL7 FHIR R4 (tieu chuan nganh)
- SMART App Launch v2 (xac thuc)
- OAuth 2.0 + OpenID Connect

**Ho tro EHR hien dai**:
- Epic: ho tro SMART day du tu 2018
- Cerner Millennium: ho tro SMART day du
- Allscripts: ho tro SMART tu 2020
- Oracle Health: ho tro SMART

**Luong ra mat**:
1. Bac si mo ho so benh nhan trong EHR
2. Click nut "Hoi Nova" (duoc nhung trong thanh ben hoac thanh nut EHR)
3. EHR khoi dong iframe voi context benh nhan
4. Tro ly AI tai trong iframe
5. Context benh nhan duoc chuyen an toan
6. Bac si dat cau hoi

**Pham vi du lieu**:
- Nhan khau hoc benh nhan (tuoi, gioi tinh)
- Chan doan hien tai
- Thuoc hien tai
- Sinh hieu/xet nghiem gan day
- Loai gap

**Bi loai tru theo mac dinh**:
- Lich su ho so day du
- Tien su gia dinh (tru khi duoc yeu cau)
- Ghi chu tu cac nha cung cap khac
- Du lieu thanh toan

**Chi phi tich hop**: EHR hien dai: 15.000-30.000 USD. EHR cu hon: 30.000-80.000 USD. EHR tuy chinh: 50.000-150.000 USD.

---

### Q77. Dieu gi xay ra neu EHR cua chung toi khong ho tro SMART on FHIR?

**A.** Cac con duong tich hop thay the:

**Con duong 1: Nhan tin HL7 v2**
- Tieu chuan cu hon, hau het EHR cu ho tro
- Tich hop dua tren tin nhan theo thoi gian thuc
- Trien khai phuc tap hon
- Chi phi: 30.000-80.000 USD

**Con duong 2: Tich hop co so du lieu**
- Doc truc tiep co so du lieu EHR
- Cu the theo nha cung cap (Epic CCDR, v.v.)
- Yeu cau thoa thuan nha cung cap
- Chi phi: 50.000-150.000 USD

**Con duong 3: API tuy chinh**
- Xay dung bo chuyen doi cho API doc quyen cua EHR
- Yeu cau tai lieu nha cung cap
- Cong viec tuy chinh moi EHR
- Chi phi: 80.000-200.000 USD

**Con duong 4: Su dung doc lap**
- Bac si nhap context thu cong
- AI duoc su dung khong co tich hop EHR
- It tien loi hon nhung co chuc nang
- Khong co chi phi bo sung

**Con duong 5: HL7 FHIR + Mirth Connect**
- Cau noi nguon mo
- Chuyen doi HL7 v2 -> FHIR
- Middleware tu luu tru
- Chi phi: 20.000-50.000 USD

**Khuyen nghi theo EHR**:
- EHR hien dai: Dung SMART on FHIR (tieu chuan)
- EHR cu hon: HL7 v2 + cau noi Mirth Connect
- EHR tuy chinh: Su dung doc lap ban dau, lap ke hoach di cu sang EHR dua tren tieu chuan theo thoi gian

---

### Q78. AI co truy cap vao tat ca du lieu benh nhan cua chung toi khong?

**A.** Han che va co kiem soat:

**Truy cap mac dinh**:
- Chi du lieu bac si chia se trong truy van
- Qua context ra mat EHR
- Cu the cho lan kham hien tai

**Truy cap theo yeu cau** (voi su dong y):
- Ghi chu gap gan day
- Gia tri xet nghiem cu the
- Thuoc hien tai
- Di ung va chong chi dinh

**Yeu cau su dong y**:
- Moi truy van cho du lieu cu the
- Hoac: su dong y toan cau moi phien
- Duoc ghi lai trong nhat ky kiem toan

**Nguyen tac giam thieu du lieu**:
- Chi su dung nhung gi can thiet
- Loai bo sau khi su dung
- Xem xet luu giu dinh ky

**Phan quyen theo bac si**:
- Giong nhu quyen truy cap EHR cua ho
- AI khong the vuot qua quyen cua bac si
- Ke thua tu EHR

**Cach ly moi tenant**:
- Du lieu Benh vien A: chi co the truy cap tai Benh vien A
- Chia se xuyen benh vien: yeu cau su dong y + NEHR-Pro

---

### Q79. Bac si dieu duong hoac cac vai tro lam sang khac co the su dung he thong nay khong?

**A.** Truy cap va tuy chinh dua tren vai tro:

**Vai tro bac si tieu chuan**:
- Ho tro quyet dinh lam sang day du
- Goi y chan doan
- Khuyen nghi dieu tri
- Lieu luong thuoc
- Hau het cac truong hop su dung

**Vai tro dieu duong** (co the cau hinh):
- Cac truy van cham soc tai giuong
- Cac cau hoi quan ly thuoc
- Giao thuc cham soc vet thuong
- Tai lieu giao duc benh nhan

**Vai tro duoc si**:
- Tuong tac thuoc
- Xac minh lieu luong
- Cac lua chon thay the trong danh muc thuoc
- Cac quyet dinh duoc ly lam sang

**Cac vai tro y te lien minh** (co the cau hinh):
- Vat ly tri lieu: giao thuc phuc hoi
- Dinh duong: huong dan dinh duong
- Cong tac xa hoi: tai nguyen xuat vien

**Cau hinh theo vai tro**:
- System prompt theo vai tro
- Quyen truy cap du lieu theo vai tro
- Guardrails theo vai tro
- Dinh dang dau ra theo vai tro

**Chi phi moi vai tro bo sung**: Cau hinh: 5.000-15.000 USD. Dao tao tuy chinh: 5.000-10.000 USD. Tuy chinh giao dien nguoi dung: 10.000-30.000 USD.

---

### Q80. Bac si co the su dung nhap bang giong noi khong?

**A.** Co, nhap bang giong noi duoc ho tro:

**Cong nghe nhap bang giong noi**:
- AWS Transcribe / Alibaba Speech
- Phien am theo thoi gian thuc
- Duoc dao tao voi thuat ngu y te
- Da ngon ngu

**Hieu suat theo ngon ngu**:
- Tieng Anh: tot nhat (nhieu du lieu dao tao nhat)
- Tieng Trung: rat tot
- Tieng Malay: tot
- Tieng Tamil: han che nhung co chuc nang
- ASEAN khac: thay doi

**Cac truong hop su dung thich hop voi giong noi**:
- Trong khi kham benh nhan (ranh tay)
- Cac cau hoi nhanh
- Theo doi trong khi di chuyen
- Di chuyen giua cac phong

**Cac truong hop su dung thich hop voi go phim**:
- Cac kich ban lam sang chi tiet
- Nhieu tham so
- Chan doan phan biet phuc tap
- Khi co lo ngai ve quyen rieng tu (nguoi khac o gan)

**Quyen rieng tu voi giong noi**:
- Am thanh khong duoc luu tru theo mac dinh
- Chi van ban duoc phien am
- Cung bao ve PHI nhu nhap van ban
- Nhat ky kiem toan o dang van ban

**Chi phi**: Phien am giong noi: ~0,006 USD/phut. Cho truy van dien hinh (30 giay): ~0,003 USD. Chi phi khong dang ke.

---



## 10. Trai nghiem nguoi dung

### Q81. Bac si thuc su thay gi tren man hinh khi su dung AI?

**A.** Giao dien sach se, tap trung:

**Cac yeu to giao dien chinh**:
- **Khu vuc nhap chat**: hop van ban cau hoi, tuy chon nhap bang giong noi, nut dinh kem hinh anh (cho X-quang), chuyen doi cap cuu
- **Lich su cuoc tro chuyen**: Q&A truoc do trong phien, click de mo rong bat ky cau tra loi nao, di chuot qua trich dan
- **Hien thi cau tra loi**: phan hoi streaming (tung tu mot), trich dan noi tuyen [1] [2] [3], di chuot de xem truoc nguon, click de mo rong nguon day du
- **Khu vuc hanh dong**: thumbs up/down, tuy chon phan hoi chi tiet, sao chep van ban vao clipboard, chia se voi dong nghiep (trong benh vien)
- **Thanh trang thai**: chi bao lane (Cap cuu/Phuc tap), thoi gian phan hoi, dinh tuyen khoa, so luong trich dan

**Cac nguyen tac UX chinh**:
- **Phan hoi streaming**: tu dau tien xuat hien <2 giay, cac tu xuat hien tu nhien, bat dau doc ngay lap tuc
- **Minh bach nguon**: trich dan luon hien thi, mot click den nguon, ngay nguon noi bat
- **It ma sat**: truy cap mot click tu EHR, context benh nhan duoc dien san, cac truy van pho bien truy cap nhanh

**Trai nghiem di dong**: Thiet ke dap ung, toi uu hoa cam ung, nhap bang giong noi noi bat, giao dien duoc giam luoc.

---

### Q82. Bac si co can dao tao dac biet de su dung he thong nay khong?

**A.** Toi thieu:

**Tong quan onboarding**:
- Huong dan tu phuc vu: 15 phut
- Phien nhom tuy chon: 30 phut
- 1:1 tuy chon: 15-20 phut moi nguoi

**Dinh dang dao tao**:
1. **Huong dan trong ung dung**: 3 trang tuong tac, cac cau hoi va cau tra loi demo, cac mo hinh pho bien
2. **The tham khao nhanh**: 1 trang co the in, cac truy van pho bien, meo de co ket qua tot nhat
3. **Video huong dan** (tuy chon): tong quan 5 phut, demo cac tinh nang pho bien, thuc hanh tot nhat
4. **Phien demo truc tiep** (tuy chon): phien nhom, thuc hanh thuc te, Q&A
5. **Khac phuc su co 1:1** (tuy chon): co san 4 tuan dau, ~10-20% bac si su dung

**Duong cong nang luc du kien**:
- Tuan 1: 80% bac si thoai mai
- Tuan 2: 95% bac si thanh thao
- Tuan 4: 99% bac si thuan thuc

**So sanh voi cac cong cu lam sang khac**:
- Dao tao Epic: 8-40 gio
- Cac cong cu DSS: 2-8 gio
- Tro ly AI cua chung toi: <1 gio
- Ly do: UX tuong tu ChatGPT, quen thuoc

---

### Q83. Bac si co the co cuoc tro chuyen rieng tu hoac chi su dung cho cac truy van chung?

**A.** Cac che do khac nhau:

**Che do 1: Truy van tieu chuan**
- Cau hoi don le
- AI phan hoi
- Khong co bo nho giua cac truy van

**Che do 2: Cuoc tro chuyen nhieu luot**
- Cung phien
- AI nho context
- Bo nho mac dinh 6 luot
- Vuot qua: context duoc tom tat

**Che do 3: Phien cu the cho benh nhan**
- Gan voi lan kham benh nhan
- Tat ca cac truy van ve cung benh nhan
- Lien tuc trong suot lan kham
- Quyen rieng tu duoc duy tri (PHI duoc token hoa)

**Che do 4: Ghi chu ca nhan**
- Su dung ca nhan cua bac si
- "Giup toi suy nghi qua truong hop nay"
- AI nhu doi tac suy nghi
- Kham pha hon

**Quyen rieng tu cuoc tro chuyen**:
- Tat ca cac che do: PHI duoc che giau truoc AI
- Nhat ky kiem toan: duoc ma hoa, an toan
- Cac cuoc tro chuyen khong duoc chia se giua cac bac si
- Tong hop cap khoa chi

**Luu giu phien**:
- Phien hoat dong: du lieu truc tiep
- Phien gan day: luu tru nong 30 ngay
- Phien cu hon: luu tru 6 nam (kiem toan)
- Tuy chon ca nhan: co the cau hinh

---

### Q84. Bac si co the su dung AI de hoc tap lien tuc khong?

**A.** Duoc ho tro nhu truong hop su dung thu cap:

**Cac truong hop su dung giao duc**:
- **Nghien cuu truong hop**: "Huong dan toi qua chan doan phan biet cho [bieu hien]"
- **Huong dan moi nhat**: "Nhung gi da thay doi trong huong dan ACC/AHA moi?"
- **Ly luan lam sang**: "Tai sao dieu tri nay duoc uu tien hon dieu tri kia?"
- **Kien thuc thuoc**: "Co che tac dung cua [thuoc]"
- **Kham pha chuyen khoa**: "Chuyen gia se suy nghi ve truong hop nay nhu the nao?"

**Tinh nang che do giao duc**:
- Phan hoi chi tiet hon so voi che do lam sang
- Nhieu thong tin nen
- Nhieu trich dan hon
- Thao luan ve cac lua chon thay the

**Chuoi ly luan**:
- Ly luan ro rang duoc hien thi
- "Vi X, do do Y"
- Gia tri giao duc cao

**Cau hoi thuc hanh**:
- "Kiem tra toi ve [chu de]"
- AI tao cac cau hoi thuc hanh
- Hoc tu danh gia

**Phan tich CME**:
- Viec su dung AI co the tinh vao CME (SMC Singapore)
- Benh vien co the cau hinh nhu hoat dong CME
- Tai lieu duoc cung cap

**Chi phi**: Khong co chi phi bo sung (su dung cung co so ha tang). Cung gia. Khong tinh phi cho viec su dung giao duc.

---

### Q85. He thong co ung dung di dong khong?

**A.** Web-first, than thien voi di dong:

**Phuong phap hien tai**:
- Thiet ke web dap ung
- Hoat dong tren trinh duyet di dong
- Giao dien duoc toi uu hoa cam ung

**Su dung di dong**:
- Dien thoai thong minh: day du chuc nang
- May tinh bang: trai nghiem nang cao
- Dua tren trinh duyet: khong can cai dat ung dung

**Tinh nang cu the cho di dong**:
- Nhap bang giong noi noi bat
- Truy cap nhanh cac truy van pho bien
- Giao dien duoc giam luoc
- Cache ngoai tuyen cho cac cau tra loi gan day

**Ung dung ban de** (tuong lai):
- Ung dung iOS: lo trinh
- Ung dung Android: lo trinh
- Tich hop tot hon voi tinh nang dien thoai
- Thong bao day

**Chi phi phat trien ung dung**:
- iOS ban de: 80.000-150.000 USD
- Android ban de: 80.000-150.000 USD
- Bao tri: 30.000-60.000 USD/nam moi nen

**Khuyen nghi**:
- Nam 1: chi web
- Nam 2: Progressive Web App (UX di dong tot hon)
- Nam 3: Ung dung ban de neu nhu cau manh

---

## 11. Nha cung cap & Ho tro

### Q86. Nhom ho tro cua Nova trong nhu the nao?

**A.** Cau truc ho tro nhieu lop:

**Cap 1: Tu phuc vu**
- Cong thong tin tai lieu
- Video huong dan
- Co so du lieu FAQ
- Co so kien thuc
- Co san 24/7

**Cap 2: Ho tro email/chat**
- Gio tieu chuan: 9 SA - 6 CH SGT
- Phan hoi: <4 gio
- Giai quyet: <24 gio dien hinh
- Cac truong hop su dung: cau hoi cach lam, cau hinh

**Cap 3: Ho tro dien thoai**
- Gio lam viec: 8 SA - 8 CH SGT
- Phan hoi: <30 phut
- Cac truong hop su dung: cac van de quan trong, leo thang

**Cap 4: Ho tro khan cap 24/7**
- Co san luc nao cung
- Phan hoi: <15 phut
- Cac truong hop su dung: ngung hoat dong SEV-1, su co bao mat

**Cac vai tro**:
- **Quan ly Thanh cong Khach hang (CSM)**: quan he moi tenant, xem xet hang quy, huong dan chien luoc, toi uu hoa chi phi
- **Quan ly Tai khoan Ky thuat (TAM)**: lien lac ky thuat, xem xet kien truc, huong dan thuc hanh tot nhat, leo thang van de
- **Ky su Ho tro**: ho tro hang ngay, khac phuc su co ky thuat, tro giup cau hinh, bao cao loi
- **SRE Truc ban**: do tin cay 24/7, ung pho su co, suc khoe he thong, cac van de hieu suat
- **Tu van Lam sang**: cac cau hoi lam sang, huong dan tuan thu, phat trien chuyen mon

**Chi phi**:
- Ho tro tieu chuan: bao gom
- Ho tro cao cap: 20.000-40.000 USD/nam
- Ho tro doanh nghiep: 50.000-100.000 USD/nam

---

### Q87. Chung toi co the nhan duoc lien he ky thuat chuyen dung khong?

**A.** Co, nhieu tuy chon:

**Dich vu tieu chuan**:
- Nhom ho tro dung chung
- Phan cong theo vong
- Du cho hau het nhu cau

**Dich vu cao cap** (chi phi bo sung):
- TAM chuyen dung (Quan ly Tai khoan Ky thuat)
- CSM chuyen dung (Quan ly Thanh cong Khach hang)
- Duong day truc tiep
- Xem xet hang quy

**Dich vu doanh nghiep**:
- Nhom chuyen dung
- Bao phu 24/7 chuyen dung
- Ho tro nhung
- Tham gia chien luoc

**So sanh cap dich vu**:

| Tinh nang | Tieu chuan | Cao cap | Doanh nghiep |
|---|---|---|---|
| TAM | Dung chung | Chuyen dung | Chuyen dung |
| CSM | Dung chung | Chuyen dung | Chuyen dung |
| Thoi gian phan hoi | Tieu chuan | Nhanh hon | Nhanh nhat |
| Lien he truc tiep | Khong | TAM + CSM | Nhom day du |
| Xem xet | Hang nam | Hang quy | Hang thang |
| Chi phi | Bao gom | 20-40k/nam | 50-100k/nam |

**Khuyen nghi**:
- Benh vien nho: ho tro tieu chuan
- Benh vien vua: dang xem xet cao cap
- Benh vien lon/he thong: doanh nghiep

---

### Q88. Nova cung cap loai dao tao va onboarding nao?

**A.** Chuong trinh toan dien:

**Dao tao truoc khi trien khai**:
1. **Hoi thao khoi dong trien khai** (1 ngay): tong quan du an, phu hop cac ben lien quan, tieu chi thanh cong, xac dinh rui ro. Chi phi: bao gom.
2. **Nghien cuu sau ve kien truc** (1 ngay): nhom CNTT benh vien, hieu biet ky thuat, lap ke hoach tich hop. Chi phi: bao gom.
3. **Briefing bao mat & tuan thu** (nua ngay): nhom tuan thu benh vien, huong dan chi tiet, xem xet tai lieu. Chi phi: bao gom.
4. **Hoi thao cau hinh lam sang** (1 ngay): truong khoa, cac quyet dinh tuy chinh, tuy chon chuyen khoa. Chi phi: bao gom.

**Dao tao trien khai**:
5. **Dao tao bac si chuyen gia** (4 gio trong 2 tuan): cac bac si duoc chon (chuyen gia lam sang), dao tao thuc hanh, thuc hanh tot nhat. Chi phi: bao gom.
6. **Dao tao nguoi dung cuoi** (1-2 gio moi bac si): huong dan tu phuc vu, cac phien nhom tuy chon, 1:1 tuy chon. Chi phi: bao gom.
7. **Dinh huong truong khoa** (2 gio): dao tao cu the theo khoa, tong quan cau hinh, giam sat chat luong. Chi phi: bao gom.

**Dao tao lien tuc**:
8. **Ban tin hang thang** (doc 15 phut): tinh nang moi, thuc hanh tot nhat, meo va thu thuat. Chi phi: bao gom.
9. **Hoi thao web hang quy** (1 gio): nghien cuu sau ve cac chu de, thong bao tinh nang moi, Q&A voi nhom san pham. Chi phi: bao gom.
10. **Hoi nghi nguoi dung hang nam** (2 ngay): cung cap cao cap, ket noi voi dong nghiep, hoi thao thuc hanh, noi dung chien luoc. Chi phi: 1.500-3.000 USD moi nguoi tham du.
11. **Cac phien dao tao tuy chinh** (theo yeu cau): cu the theo khoa, cu the theo sang kien moi, tap trung vao chuyen khoa. Chi phi: 5.000-15.000 USD moi phien.

---

### Q89. Chung toi co the anh huong den lo trinh san pham khong?

**A.** Nhieu kenh dau vao:

**Hoi dong tu van khach hang**:
- Cac cuoc hop hang quy
- Cac benh vien hang dau duoc dai dien
- Dau vao chien luoc
- Xem truoc lo trinh
- Bieu quyet ve uu tien

**He thong yeu cau tinh nang**:
- Nop qua cong thong tin
- Bieu quyet cho cac yeu cau cua nguoi khac
- Lo trinh cong khai (cap cao)
- Cap nhat trang thai

**Hoi dong tu van lam sang**:
- Cac lanh dao lam sang tu khach hang
- Uu tien lam sang
- Nhu cau chuyen khoa
- Co hoi nghien cuu

**Chuong trinh beta**:
- Truy cap som vao cac tinh nang
- Cung cap phan hoi truoc GA
- Hinh thanh thiet ke cuoi cung
- Duoc cong nhan trong san pham

**Tham gia truc tiep**:
- TAM/CSM chuyen tiep dau vao
- Uu tien quan ly tai khoan
- Cac cuoc thao luan chien luoc
- Cac tinh nang tuy chinh cho khach hang quan trong

**Muc do anh huong**:
- **Rat co anh huong** (top 10 khach hang): duong day truc tiep den nhom san pham, cac tinh nang tuy chinh duoc tai tro, trong luong bieu quyet lo trinh, bao tro dieu hanh
- **Co anh huong vua** (30 khach hang tiep theo): kiem tra hang quy, dau vao lo trinh, truy cap beta, ho tro tieu chuan
- **Khach hang tieu chuan**: dau vao ban tin, tham gia khao sat, phan hoi cong khai, bieu quyet

---

### Q90. Lich su theo doi cua Nova la gi? Day co phai la cong ty on dinh khong?

**A.** Cau hoi tham dinh quan trong.

**Nen tang cong ty**:
- Co tru so tai Singapore
- Tap trung vao cong nghe cham soc suc khoe
- Duoc thanh lap boi cac lanh dao lam sang va ky thuat
- Duoc ho tro boi cac nha dau tu co uy tin

**Chi so on dinh**:
- Tai chinh: duoc tai tro cho 24+ thang runway
- Mo hinh doanh thu dinh ky
- Nhieu vong tai tro Series
- Phuong phap tang truong bao thu

**Co so khach hang**:
- 5+ tenant benh vien tai Singapore
- 50+ benh vien quoc te (duoc lap ke hoach/hoat dong)
- Ti le giu chan 95%+
- Khach hang tham khao co san

**Doi ngu**:
- 50+ nhan vien
- Lanh dao cap cao: 10+ nam kinh nghiem nganh
- Tu van lam sang: cac bac si dang hanh nghe
- Ky thuat: nhan tai hang dau

**Xac nhan nganh**:
- Thanh vien Hoi dong AI Verify
- Doi tac IMDA
- Da dang ky HSA
- Thanh vien lien minh cham soc suc khoe

**Kich ban that bai va bien phap bao ve**:
- **Neu Nova gap van de tai chinh**: AWS/Alibaba tiep tuc chay co so ha tang; benh vien co the tu chay (voi ky quy code); thong bao 90 ngay.
- **Neu Nova bi mua lai**: tiep tuc duoc bao dam boi ben mua lai; cac dieu khoan hop dong tieu chuan ap dung; benh vien giu quyen.
- **Neu Nova ngung hoat dong**: thoa thuan ky quy code (duoc khuyen nghi); cac thanh phan nguon mo; AWS/Alibaba se duy tri; di cu sang nha cung cap thay the.

**Tham dinh duoc khuyen nghi**:
1. Xem xet tai chinh Nova (duoc bao ve boi NDA)
2. Kiem tra tham khao voi cac khach hang hien tai
3. Xem xet kien truc ky thuat
4. Xem xet tai lieu tuan thu
5. Thao luan lo trinh

---



## 12. Quan ly rui ro

### Q91. Diem that bai don le lon nhat cua chung toi la gi?

**A.** Danh gia trung thuc:

**SPOF 1: Vung nha cung cap dam may** (cao nhat)
- AWS/Alibaba Singapore vung bi ngung hoat dong
- Tat ca cac dich vu khong co san
- Giam thieu: chuyen doi du phong xuyen vung (chu dong-bi dong)
- Rui ro: 1-2 gio ngung hoat dong moi nam (uoc tinh)

**SPOF 2: Bedrock/Model Studio**
- Dich vu LLM khong co san
- Chuc nang cot loi bi mat
- Giam thieu: mo hinh du phong + phan hoi da cache
- Rui ro: 0,5-1 gio dich vu bi suy giam moi nam

**SPOF 3: OpenSearch / Vector Search**
- Truy xuat kien thuc bi ngung
- Khong the can cu cau tra loi
- Giam thieu: ket qua da cache
- Rui ro: ngung hoat dong ngan han co the xay ra

**SPOF 4: Trien khai cua Nova**
- Loi code trong duong dan quan trong
- Trien khai that bai
- Giam thieu: phat hanh canary, rollback
- Rui ro: han che; trien khai co kiem soat

**SPOF 5: API ben ngoai (WHO, ICD-11)**
- Du lieu nguon khong co san
- Cap nhat bi tri hoan
- Giam thieu: du lieu da cache
- Rui ro: khong anh huong den dich vu (chi tinh moi du lieu)

**Rui ro SPOF tong hop**:
- Tong thoi gian ngung hoat dong hang nam ket hop: <1% (8,76 gio)
- Hau het ngung hoat dong: <30 phut
- Ngung hoat dong nghiem trong: hiem

**Tuy chon cua benh vien**:
- Chap nhan SLA tieu chuan (99,9%)
- Mua SLA cao hon: 99,95% hoac 99,99% (cao cap)
- Trang web DR rieng: tinh san sang cao nhat, chi phi cao nhat

---

### Q92. Kich ban ngung hoat dong xau nhat la gi?

**A.** Lich su thuc te:

**Kich ban: Ngung hoat dong hoan toan vung AWS Singapore**

**Xac suat**: Rat thap (su co lon cuoi cung: ~5 nam truoc)

**Tac dong**:
- Dich vu khong co san
- Tat ca bac si mat quyen truy cap AI
- Chi quy trinh lam viec thu cong
- Nhat ky kiem toan co the bi tri hoan hoac mat

**Uoc tinh thoi gian**:
- Hau het ngung hoat dong: <30 phut
- Ngung hoat dong vung (hiem): 2-6 gio
- Ngung hoat dong nghiem trong (rat hiem): 12-24 gio

**Ung pho cua benh vien**:
- Kich hoat quy trinh lam viec thu cong
- Thong bao Nova (trang trang thai)
- Ghi lai bat ky tac dong lam sang nao
- Tiep tuc khi dich vu duoc khoi phuc

**Ung pho cua Nova**:
- Cap nhat trang thai theo thoi gian thuc
- Tin dung dich vu theo SLA
- Bao cao sau su co
- Cac cai tien duoc thuc hien

**Chi phi ngung hoat dong xau nhat**:
- Truc tiep: khong (quy trinh lam viec thu cong tiep tuc)
- Nang suat: benh vien chiu (duoc bao hiem)
- Tin dung SLA: ap dung
- Danh tieng: toi thieu (ngung hoat dong toan nganh)

**Bao hiem**:
- Bao hiem gian doan kinh doanh: ~10.000 USD/nam cho bao hiem 500k USD
- Bao gom: mat doanh thu trong thoi gian ngung hoat dong keo dai
- Quyet dinh cua benh vien

**Lich su su co thuc te** (cac he thong tuong tu):
- Ngung hoat dong AWS S3 2017: 4 gio
- Ngung hoat dong AWS Singapore 2023: 3 gio
- Su co Bedrock: <30 phut dien hinh

---

### Q93. Dieu gi xay ra neu chung toi dot ngot can mo rong len 10 lan so bac si?

**A.** Kha nang mo rong:

**Nang luc hien tai**:
- Moi tenant: 500-1000 bac si
- Da tenant: mo rong tuyen tinh
- Ly thuyet: hang nghin tenant

**Cac kich ban tang truong**:

**Trong 1 gio**: Tang truong 10% (tu dong mo rong)
**Trong 1 ngay**: Tang truong 50% (mo rong thu cong)
**Trong 1 tuan**: Tang truong 100% (xem xet kien truc)
**Trong 1 thang**: Tang truong 5x (cap phep nang luc)
**Trong 3 thang**: Tang truong 10x (lap ke hoach + mua sam)

**Kinh te mo rong**:

| Bac si | Chi phi/thang | Chi phi/bac si/thang |
|---|---|---|
| 100 | 2.500-4.000 USD | 25-40 USD |
| 500 (dien hinh) | 5.500 USD | 11 USD |
| 1.000 | 8.000-12.000 USD | 8-12 USD |
| 5.000 | 25.000-40.000 USD | 5-8 USD |

**Kinh te quy mo**: Chi phi moi bac si giam khi mo rong vi chi phi co dinh duoc phan bo.

**Tac dong hieu suat**:
- Trong kien truc hien tai: cung muc tieu do tre
- O quy mo rat cao (10x+): co the can kien truc khac nhau
- Dung luong danh rieng
- Toi uu hoa chuyen biet

**Khuyen nghi**:
- Bat dau voi 500 bac si
- Lap ke hoach cho 1.000 trong 12 thang
- Thao luan 5.000+ neu mo rong duoc ky vong

---

### Q94. Dieu gi xay ra neu AI dua ra khuyen nghi trai voi giao thuc cua benh vien?

**A.** Xu ly xung dot giao thuc:

**Tai sao xung dot xay ra**:
1. **WHO vs giao thuc benh vien**: WHO: tieu chuan toan cau. Benh vien: bien the dia phuong. Ca hai co the co bang chung.
2. **Cac quan diem chuyen khoa khac nhau**: AI trich dan huong dan chung. Chuyen gia chuyen khoa khong dong y. Ca hai co gia tri.
3. **Cac su khac biet dua tren tai nguyen**: Giao thuc tieu chuan: thuoc A. Benh vien dung: thuoc B (danh muc thuoc). Hieu qua tuong duong.
4. **Bang chung moi vs thuc hanh da thiet lap**: Nghien cuu moi nhat: thay doi khuyen nghi. Benh vien chua cap nhat giao thuc. AI biet bang chung moi.

**Xu ly xung dot**:

**Mo hinh 1: Uu tien benh vien**
- AI tuan theo giao thuc benh vien khi biet
- Ghi chu bang chung thay the
- Banner: "Giao thuc benh vien duoc uu tien"

**Mo hinh 2: Minh bach xung dot**
- AI hien thi ca hai
- Ghi nhan ro rang
- Bac si quyet dinh

**Mo hinh 3: Dua tren bang chung**
- AI hien thi bang chung manh nhat
- Giao thuc benh vien duoc hien thi
- Bat dong duoc ghi lai

**Trien khai**:
- Giao thuc benh vien duoc nhap vao KB
- Uu tien truy xuat cao hon
- Phat hien xung dot
- Hien thi minh bach

**Quan tri benh vien**:
- Quy trinh cap nhat giao thuc
- Xem xet bang chung hang quy
- Lam moi giao thuc benh vien
- AI nhap cac cap nhat

**Thuc hanh tot nhat**:
- Giu giao thuc cap nhat
- Tham gia voi phan hoi AI
- Ghi lai ly luan khi ghi de
- Cai thien lien tuc

---

### Q95. Chung toi co "cong tat" neu co gi do xay ra nghiem trong khong?

**A.** Ung pho khan cap nhieu cap:

**Cap 1: Tam dung cap bac si**
- Bac si ca nhan co the vo hieu hoa AI cho cac truong hop cua ho
- Nut "Vo hieu hoa AI" trong EHR
- Hieu qua: cac truy van cua ho bo qua AI, quy trinh lam viec thu cong duoc khoi phuc
- Tham quyen quyet dinh: bac si

**Cap 2: Tam dung cap khoa**
- Truong khoa co the vo hieu hoa cho toan khoa
- "Vo hieu hoa khoa" qua cong thong tin quan tri
- Hieu qua: tat ca cac truy van khoa bo qua AI
- Tham quyen quyet dinh: truong khoa

**Cap 3: Tam dung cap benh vien**
- Giam doc Y te co the vo hieu hoa AI cho toan benh vien
- Hieu qua: AI tra ve "Dich vu tam thoi khong co san" cho tat ca cac truy van
- Quy trinh lam viec thu cong chi
- Tham quyen quyet dinh: Giam doc Y te (voi su dong y cua VP/CMO)
- Thong bao: ngay lap tuc den Nova; 4 gio den tat ca bac si

**Cap 4: Tam dung xuyen tenant**
- Nova SRE co the vo hieu hoa cho tat ca cac tenant neu phat hien van de he thong
- Vi du: loi nghiem trong, su co bao mat
- Hieu qua: dich vu khong co san toan cau
- Tham quyen quyet dinh: VP Ky thuat + Can bo Tuan thu
- Thong bao: 1 gio den tat ca lanh dao benh vien

**Cap 5: Tat hoan toan**
- Van de quy dinh hoac an toan nghiem trong
- Hieu qua: dich vu hoan toan khong co san
- Tham quyen quyet dinh: CEO + Co van Phap ly
- Thong bao: co quan quan ly, tat ca benh vien, tuyen bo cong khai

**Tieu chi kich hoat** (duoc xac dinh trong ke hoach ung pho su co):
- Cap 1-2: tieu chuan/tuy chon cua bac si
- Cap 3: van de cu the cua benh vien hoac lo ngai tuan thu
- Cap 4: van de he thong, su co bao mat
- Cap 5: vi pham quy dinh nghiem trong, phan quyet CEO

**Quy trinh khoi dong lai**:
- Moi cap co quy trinh khoi dong lai duoc ghi lai
- Cac xac thuc bat buoc truoc khi khoi dong lai
- Xem xet sau su co bat buoc

---

### Q96. Ke hoach phuc hoi tham hoa cua chung toi la gi?

**A.** Chien luoc phuc hoi nhieu lop:

**Loi AZ don le (pho bien nhat)**:
- AWS co 3 vung kha dung (AZ) tai Singapore
- Trien khai cua chung toi su dung 2-3 AZ theo mac dinh
- Loi AZ don le: chuyen doi tu dong, ~30 giay gian doan
- RPO: 0 (sao chep dong bo)
- RTO: 1-2 phut

**Loi dich vu don le**:
- Bedrock bi ngung: Tu dong chuyen doi sang vung thay the (voi su dong y cua benh vien) HOAC suy giam nhe nhan
- OpenSearch bi ngung: Ket qua da cache + chuc nang giam
- Neptune bi ngung: Chi truy xuat vector (chap nhan duoc suy giam)
- RPO: 5 phut
- RTO: 10-30 phut

**Loi vung (hiem)**:
- Tat ca AWS Singapore khong co san (cuc ky hiem)
- Ung pho cua chung toi:
  - Phuong an A: Chuyen doi xuyen vung sang AWS Sydney (voi su dong y cua benh nhan, vi du du lieu roi Singapore)
  - Phuong an B: Dich vu khong co san cho den khi AWS phuc hoi
  - Benh vien chon chinh sach truoc
- RPO: 1 gio
- RTO: 2-4 gio (Phuong an A); thoi gian ngung hoat dong AWS (Phuong an B)

**Thiet lap phuc hoi tham hoa**:

**Chu dong-bi dong (duoc khuyen nghi)**:
- Vung chinh: Singapore
- Vung sao luu: Sydney (hoac lua chon cua benh vien)
- Sao chep hang ngay
- Thoi gian chuyen doi: 2-4 gio
- Chi phi: +500-1.500 USD/thang/tenant co so ha tang

**Chu dong-chu dong (tinh san sang cao nhat)**:
- Cung tai trong chay tren ca hai vung
- Chuyen doi tuc thi
- Chi phi: 2x co so ha tang
- Truong hop su dung: chi cho cac benh vien yeu cau 99,99%+ thoi gian hoat dong

**Khong co DR (don gian nhat)**:
- Chi mot vung
- Chap nhan thoi gian ngung hoat dong trong khi ngung hoat dong vung
- Chi phi: 1x co so ha tang
- Chap nhan duoc chi cho cac truong hop su dung khong quan trong

**Lich kiem tra DR**:
- Bai tap DR hang quy
- Mo phong loi vung
- Do RPO va RTO thuc te
- Cai thien runbook dua tren cac phat hien

**Chi phi DR**:
- Thiet lap chu dong-bi dong: +500-1.500 USD/thang/tenant
- Bai tap DR hang quy: 5.000 USD/bai tap
- Kiem toan DR hang nam ben ngoai: 15.000 USD

---

### Q97. Dieu gi xay ra neu AI dua ra khuyen nghi sai va benh nhan bi ton hai?

**A.** Da duoc tra loi o Q7. Xem chi tiet o do.

---

### Q98. Lam the nao de xu ly tinh trang bac si phu thuoc qua muc vao AI?

**A.** Cac chien luoc chong phu thuoc:

**Rui ro phu thuoc**:
1. **Giam ky nang bac si**: Phu thuoc vao AI ma khong suy nghi. Giam thieu: AI yeu cau xem xet trich dan; giao duc.
2. **Khoa vao quy trinh lam viec**: Quy trinh lam viec phu thuoc vao AI. Giam thieu: quy trinh lam viec thu cong song song duoc duy tri.
3. **Khoang trong kien thuc lam sang**: Bac si khong hoc sau. Giam thieu: AI giai thich ly luan; che do giao duc.
4. **Phan xet lam sang**: Bac si khong phat trien phan xet. Giam thieu: AI la ho tro quyet dinh; bac si quyet dinh.

**Thiet ke chong phu thuoc**:
- **Xem xet trich dan bat buoc**: AI hien thi "Dua tren [nguon]". Bac si phai doc it nhat phan khuyen nghi.
- **Mo hinh tu choi**: AI tu choi khi KB thieu du lieu. Bac si phai phat trien phan xet.
- **Chi bao do tin cay**: AI hien thi muc do chac chan. Bac si hoc khi nao nen tin tuong.
- **Kiem tra mu dinh ky**: Hang quy: 50 cau hoi, ket qua duoc xem xet boi can bo an toan lam sang. Neu bac si chap nhan cau tra loi AI ma khong co tu duy phan bien, siet chat guardrails hoac them banner "day la bat thuong, vui long xac minh".

**Quan tri benh vien**:
- Tiep tuc cac chuong trinh giao duc
- Dao tao quy trinh lam viec thu cong
- AI la cong cu, khong phai nguoi thay the
- Phan xet lam sang la toi cao

**Ket qua dai han**:
- Cac bac si tot hon (nhieu kien thuc truy cap hon)
- Hieu qua hon (tiet kiem thoi gian)
- Ket qua tot hon (dua tren bang chung)
- Thuc hanh ben vung

---

### Q99. Dieu gi xay ra neu co su kien bao chi tieu cuc lien quan den AI y te?

**A.** Ke hoach truyen thong khung hoang:

**Cac kich ban co the xay ra**:
1. **Su kien bat loi lien quan den AI**: Ton hai benh nhan bi cao buoc do AI. Truyen thong dua tin. Kiem tra quy dinh.
2. **Moi lo ngai AI toan nganh**: Nha cung cap khac that bai. Phan ung tieu cuc chung. Co quan quan ly phan hoi.
3. **Van de tuan thu**: Phat hien kiem toan duoc cong bo. Vi pham quyen rieng tu bi cao buoc. Tac dong den co phieu/danh tieng.
4. **Van de nha cung cap**: Scandal Anthropic/Alibaba. Lo ngai ve du lieu dao tao. Moi lo ngai dia chinh tri.

**Khung ung pho**:

**Hanh dong ngay lap tuc** (trong vong 1 gio):
1. Kich hoat nhom khung hoang
2. Thu thap thong tin
3. Bao ton bang chung
4. Giam sat truyen thong

**Trong vong 4 gio**:
5. Truyen thong noi bo: tat ca nhan vien
6. Thong bao khach hang: cac tenant benh vien
7. Canh bao cac ben lien quan: lanh dao, nha dau tu

**Trong vong 24 gio**:
8. Tuyen bo cong khai (thuc te)
9. Q&A voi truyen thong
10. Thong bao co quan quan ly (neu bat buoc)

**Ngay 2-7**:
11. Bao cao dieu tra chi tiet
12. Tiep tuc truyen thong
13. Cac hanh dong khac phuc

**Phuc hoi dai han**:
14. Cai thien duoc chung minh
15. Kiem toan doc lap
16. Bao cao cong khai
17. Xay dung lai niem tin

**Vat lieu duoc chuan bi san**:
- Cac tuyen bo giu cho (mau)
- Tai lieu FAQ
- Nguoi phat ngon duoc xac dinh
- Dao tao truyen thong da hoan thanh

**Chi phi**:
- Chuan bi khung hoang: 50.000-100.000 USD mot lan
- Ung pho khung hoang: 100.000-500.000 USD moi su co
- Bao hiem: 10.000-30.000 USD/nam cho bao hiem 5 trieu USD

---

### Q100. Cau hoi cuoi cung: Dieu quan trong nhat can hieu ve AI nay la gi?

**A.** AI la ho tro quyet dinh, khong phai nguoi ra quyet dinh.

**Cac nguyen tac chinh**:

**1. Tang cuong, khong thay the**:
- Bac si van la nguoi chinh
- AI ho tro suy nghi cua ho
- Quyet dinh cuoi cung: con nguoi

**2. Duoc can cu trich dan**:
- Moi khang dinh duoc trich dan
- Nguon co the xac minh
- Niem tin qua minh bach

**3. Tu choi khi khong chac chan**:
- AI tu choi khi KB thieu du lieu
- Trung thuc ve han che
- Bao ton cho an toan

**4. Ban dia Singapore**:
- Tuan thu PDPA
- Phu hop HCSA
- Nhan thuc boi canh dia phuong
- Luu tru du lieu duoc dam bao

**5. ROI tich cuc**:
- Tiet kiem thoi gian dang ke
- Ket qua tot hon
- Chi phi hop ly
- Gia tri dai han

**6. Lien tuc phat trien**:
- Bang chung moi nhat
- Huong dan duoc cap nhat
- Kha nang cai thien
- Hoc lien tuc

**7. Lay con nguoi lam trung tam**:
- Than thien voi bac si
- An toan cho benh nhan
- Khung dao duc
- Nhan cam van hoa

**Ket luan**: Duoc thuc hien dung, AI nay giup cac bac si gioi tro nen tot hon, nhanh hon va tu tin hon. Duoc thuc hien sai, no co the tao ra rui ro. Kien truc, tuan thu va giam sat lien tuc cua chung toi duoc thiet ke de thuc hien dung.

Quyet dinh khong phai la "chung toi co nen ap dung AI khong?" ma la "chung toi ap dung AI tot nhu the nao?"

Chung toi cam ket giup ban thuc hien tot.

---



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



## 14. Van hanh dai han

### Q106. "Van hanh Ngay 2" co nghia la gi va tai sao no quan trong?

**A.** "Ngay 1" = ra mat, "Ngay 2" = van hanh lien tuc.

Ngay 2 bao gom: giam sat hieu suat, giai quyet van de, cai tien lien tuc, duy tri tuan thu, xu ly phan hoi nguoi dung, toi uu hoa chi phi, lap ke hoach nang luc, van hanh bao mat.

**Tai sao Ngay 2 quan trong hon Ngay 1**:
- Ngay 1: su kien 1 lan
- Ngay 2: 6 nam (luu giu HCSA) va hon nua
- Hau het chi phi: Ngay 2
- Hau het gia tri: Ngay 2

**Nang luc Ngay 2 Nova cung cap**:
- Giam sat 24/7 (SRE)
- Kiem tra suc khoe hang ngay
- Xem xet hieu suat hang tuan
- Bao cao tuan thu hang thang
- Cap nhat he thong hang quy
- Kiem toan bao mat hang nam

**Cam ket Ngay 2 cua benh vien**:
- Ho tro nguoi dung
- Tuan thu noi bo
- Duy tri su tham gia
- Phu hop chien luoc

**Chat luong Ngay 2 = chat luong dich vu tong the**.

---

### Q107. Loai giam sat nao chay lien tuc tren he thong?

**A.** Stack giam sat toan dien:

**Giam sat theo thoi gian thuc** (moi giay):
- Thoi gian phan hoi API
- Ti le loi
- Suc khoe dich vu
- Ti le hit cache
- Chi phi moi truy van

**Giam sat chat luong** (moi phut):
- Do chinh xac trich dan
- Diem grounding
- Ti le tu choi
- Chat luong phan hoi

**Giam sat tuan thu** (moi gio):
- Tinh toan ven cua nhat ky kiem toan
- Luu tru du lieu
- Thanh cong che giau PHI
- Cac mo hinh truy cap

**Giam sat kinh doanh** (hang ngay):
- Nguoi dung hoat dong
- Ti le ap dung
- Phan bo theo khoa
- Xu huong chi phi

**Cong cu cu the**:
- ARMS LLM Trace Explorer (Alibaba) / X-Ray (AWS): theo doi phan tan, phan tich do tre moi yeu cau, phan bo loi, toi uu hoa hieu suat
- SLS / CloudWatch Logs: nhat ky ung dung, su kien he thong, nhat ky kiem toan, co the tim kiem
- Giam sat ung dung ARMS: bang dieu khien theo thoi gian thuc, nguong canh bao, theo doi SLO
- Bang dieu khien tuy chinh: KPI cu the cua benh vien, phan tich theo khoa, phan tich xu huong

**Minh bach giam sat**:
- Benh vien thay cung bang dieu khien chung toi thay
- Truy cap theo thoi gian thuc
- Chi so chi tiet co san

---

### Q108. Ai chiu trach nhiem giu he thong cap nhat va hien tai?

**A.** Trach nhiem chung:

**Trach nhiem cua Nova**:
- **Cap nhat phan mem**: sua loi (lien tuc), va lap bao mat (trong vong 24 gio ke tu CVE), phat hanh tinh nang (hang thang), nang cap phien ban chinh (hang quy)
- **Co so kien thuc**: WHO ICD-11 hang ngay, huong dan WHO hang thang, dong bo thu nghiem noi bo hang tuan, them nguon moi (khi can)
- **Cap nhat mo hinh**: dao tao lai mo hinh sinh vien hang quy, phien ban chinh hang nam (Sonnet/Plus), tinh chinh prompt lien tuc
- **Tuan thu**: theo doi quy dinh moi, chung nhan duoc cap nhat, duy tri nhat ky kiem toan

**Trach nhiem cua benh vien**:
- **Du lieu noi bo**: cung cap bao cao thu nghiem duoc cap nhat, cap nhat giao thuc benh vien, noi dung cu the theo khoa
- **Quan ly nguoi dung**: onboarding bac si moi, thu hoi quyen truy cap khi roi, thay doi vai tro
- **Cau hinh**: tuy chinh theo khoa, tuy chon chuyen khoa, chinh sach noi bo
- **Su tham gia**: ap dung nguoi dung, tham gia dao tao, cung cap phan hoi

**Nhip do cap nhat**:
- **Hang ngay**: dong bo ICD-11
- **Hang tuan**: dong bo SharePoint
- **Hang thang**: lam moi WHO, trien khai tinh nang
- **Hang quy**: dao tao lai mo hinh, kiem toan bao mat
- **Hang nam**: phien ban chinh, kiem toan tuan thu

**Giao tiep ve cap nhat**:
- Ban tin (Nova -> Benh vien)
- Trang trang thai (truc tiep)
- Hoi thao web (hang quy)
- Xem xet 1:1 (moi tenant)

---

### Q109. He thong co bao gio ngung hoat dong de bao tri khong?

**A.** Duoc thiet ke de giam thieu thoi gian ngung hoat dong:

**Cua so bao tri**:
- Co lich: Thu 7 dau tien 2-6 SA SGT (4 gio)
- Thong bao: 7 ngay truoc
- Tan suat: ~2 lan moi nam (dien hinh)

**Hau het cap nhat: khong co thoi gian ngung hoat dong**:
- Trien khai cuon
- Phat hanh canary
- Trien khai xanh-xanh la
- Khong gian doan dich vu

**Cac kich ban bao tri cu the**:
1. **Cap nhat phan mem (thuong xuyen)**: Khong co thoi gian ngung hoat dong qua trien khai cuon. Duoc xac minh lien tuc. Tu dong rollback neu co van de.
2. **Di cu co so du lieu**: Di cu truc tuyen. Cac ban sao doc trong khi di cu. Duoc xac minh sau di cu.
3. **Nang cap co so ha tang**: Co lich truoc. Thong bao benh vien. Gian doan ngan (5-30 phut).
4. **Nang cap phien ban chinh**: Hang quy. Duoc kiem tra truoc. Phoi hop voi benh vien. Thoi gian ngung hoat dong ngan chap nhan duoc.

**Tac dong SLA**:
- Bao tri co lich: bi loai tru khoi SLA
- Ngung hoat dong khong co lich: SLA ap dung
- Tin dung dich vu theo SLA

**Giao tiep benh vien**:
- **Truoc bao tri**: thong bao 7 ngay, ke hoach chi tiet, huong dan quy trinh lam viec thay the
- **Trong bao tri**: cap nhat trang trang thai, tien do theo thoi gian thuc, FAQ nhanh
- **Sau bao tri**: bao cao xac minh, xac nhan suc khoe dich vu, cac van de neu co

**Lich su thuc te**:
- Dat duoc thoi gian hoat dong 99,9%+
- <5 gio tong thoi gian ngung hoat dong hang nam
- Hau het bao tri co lich: khong co tac dong

---

### Q110. Dieu gi xay ra neu Nova phat trien mot tinh nang moi anh huong den cach chung toi su dung he thong?

**A.** Quan ly tinh nang:

**Vong doi tinh nang**:
1. **Khai niem**: Duoc xac dinh tu phan hoi. Duoc xac thuc voi cac ben lien quan. Xem xet lo trinh.
2. **Phat trien**: Xay dung ky thuat. Kiem tra noi bo. 4-12 tuan dien hinh.
3. **Beta**: Cac benh vien duoc chon. Kiem tra thuc te. Phan hoi duoc thu thap.
4. **GA (Tinh san sang chung)**: Phat hanh cho tat ca. Duoc ghi lai. Duoc dao tao.
5. **Ap dung**: Benh vien danh gia. Quyet dinh su dung. Trien khai khi san sang.

**Kiem soat benh vien doi voi cac tinh nang**:
- **Bat buoc vs Tuy chon**: Bat buoc: cap nhat bao mat, tuan thu. Tuy chon: hau het cac tinh nang moi. Benh vien chon.
- **Cai dat moi tenant**: Bat tat moi tinh nang. Tuy chinh moi khoa. Trien khai dan.
- **Co hieu tinh nang**: Kiem soat chi tiet. Thi diem tren mot phan nguoi dung. Rollback neu co van de.

**Giao tiep ve cac tinh nang moi**:
- **Truoc khi phat hanh**: Hien thi lo trinh, bai dang blog, ban tin
- **Beta**: Hoi dong tu van khach hang, cac benh vien duoc chon, tai lieu chi tiet
- **GA**: Thong bao email, bai viet ban tin, hoi thao web duoc cung cap

**Danh gia moi benh vien**:
- **Tinh nang tieu chuan**: Duoc bao gom trong dang ky. Su dung theo y muon. Khong co chi phi bo sung.
- **Tinh nang cao cap**: Chi phi bo sung. Benh vien quyet dinh. Thanh toan rieng.
- **Tinh nang tuy chinh**: Cu the cho benh vien. Phat trien tuy chinh. Gia theo du an.

---

## 15. Tuong lai & Kha nang mo rong

### Q111. Tiem nang tang truong cua chung toi la gi? Chung toi co the mo rong len 50 benh vien khong?

**A.** Lo trinh kha nang mo rong:

**Nang luc hien tai**:
- Moi tenant: 500-1000 bac si
- Da tenant: mo rong tuyen tinh
- Ly thuyet: hang nghin tenant

**Cac kich ban tang truong**:
- Nam 1: 1-3 tenant (thiet lap nen tang)
- Nam 2: 5-10 tenant (truong thanh van hanh)
- Nam 3: 15-30 tenant (mo rong thi truong)
- Nam 4: 30-50 tenant (mo rong ASEAN)
- Nam 5+: 50-100 tenant (doanh nghiep truong thanh)

**Kinh te van hanh**:
- Chi phi bien moi tenant bo sung: ~30.000-50.000 USD/nam
- Doanh thu moi tenant: 100.000-400.000 USD/nam
- Bien loi nhuan: 60-80% o quy mo

**Bao hoa thi truong Singapore**:
- ~60 benh vien tai Singapore
- Chiem duoc thuc te: 15-30 benh vien
- Benh vien lon: 5-10 toi da
- Hang trung: 10-20

**Mo rong ASEAN**:
- Indonesia: 200+ benh vien
- Thai Lan: 150+
- Viet Nam: 100+
- Tong: 1.000+ benh vien
- Chiem duoc thuc te: 100-300 trong 10 nam

**Cac can nhac chien luoc**:
- Giao duc thi truong
- Dia phuong hoa quy dinh
- Thich ung van hoa
- Ung pho canh tranh

---

### Q112. Tam nhin dai han cho AI trong y te la gi?

**A.** Trien vong chien luoc:

**Tam nhin 5 nam**:
1. **Tieu chuan y te duoc tang cuong AI**: Hau het bac si su dung AI hang ngay. Tieu chuan duoc can cu trich dan. Ket qua benh nhan duoc cai thien. Chi phi cham soc suc khoe giam.
2. **Xuat sac chuyen khoa cu the**: AI chuyen biet moi chuyen khoa. Chuyen mon linh vuc sau. Tich hop voi quy trinh lam viec lam sang.
3. **AI lay benh nhan lam trung tam**: Cac cong cu huong den benh nhan (voi cac bien phap bao ve). Giao duc benh nhan. Dong y co thong tin. Quyet dinh duoc trao quyen.
4. **Suc khoe cong dong**: AI cho suc khoe cong cong. Phat hien dich benh. Phan bo nguon luc. Cai thien chat luong.
5. **Tich hop nghien cuu**: Thu nghiem lam sang duoc ho tro boi AI. Tao bang chung the gioi thuc. Y hoc ca nhan hoa. Kham pha dieu tri moi.

**Tam nhin 10 nam**:
1. **Cham soc suc khoe hoc lien tuc**: Tich hop ket qua theo thoi gian thuc. Huong dan thich ung. Phan tich du doan. Thuc su ca nhan hoa.
2. **Tri tue da phuong thuc**: Van ban + hinh anh + giong noi. Du lieu gen. Du lieu cam bien. Goc nhin toan dien.
3. **Cong bang suc khoe toan cau**: AI dan chu hoa chuyen mon. Co san moi noi. Nhieu ngon ngu. Nhan cam van hoa.
4. **Y hoc phong ngua**: Du doan rui ro. Can thiep som. Toi uu hoa loi song. Mo rong suc khoe.

**Thach thuc dai han**:
- Ky thuat: bao mat khang luong tu, hoc bao ton quyen rieng tu, hieu biet da phuong thuc, cai thien lien tuc
- Quy dinh: tien hoa AI Verify, hoa hop quoc te, mo rong quyen benh nhan, khung trach nhiem phap ly
- Dao duc: trach nhiem giai trinh thuat toan, giam thieu thien vi, yeu cau minh bach, giam sat cua con nguoi
- Kinh te: chi phi vs gia tri, bat binh dang cham soc suc khoe, mo hinh bao hiem, cau truc boi thuong

**Dinh vi cua Nova**:
- Nen tang: chuyen mon ky thuat sau, tap trung vao y te Singapore, lanh dao tuan thu, thanh cong khach hang
- Doi moi: ap dung cong nghe moi noi, phat trien truong hop su dung moi, quan he doi tac nghien cuu, cai thien lien tuc
- Mo rong thi truong: tang truong dia ly, chieu sau chuyen khoa, huong den benh nhan (can than), suc khoe cong dong

---

### Q113. AI co bao gio thay the bac si khong?

**A.** Khong, mo hinh tang cuong:

**Tai sao AI se khong thay the bac si**:
1. **Phan xet lam sang la khong the giam thieu**: Context benh nhan quan trong. Can nhan cam van hoa. Tri tue cam xuc la thiet yeu. Ly luan dao duc can thiet.
2. **Kham benh ly**: AI khong the soi. AI khong the nghe phoi. AI khong the kham. Can cham soc truc tiep.
3. **Moi quan he bac si-benh nhan**: Niem tin mat nhieu nam de xay dung. Phong cach giuong benh khong the thay the. Su dong cam la bat buoc. Tiep noi cham soc.
4. **Trach nhiem phap ly va trach nhiem giai trinh**: Trach nhiem phap ly thuoc ve bac si. Khung bao hiem. Uy quyen quy dinh. Cap phep nghe nghiep.
5. **Tuy chon cua benh nhan**: Hau het benh nhan thich ket noi con nguoi. AI nhu cong cu, khong phai nguoi thay the. Phan cap niem tin ro rang.

**Nhung gi AI co the lam**:
1. **Tang cuong truy cap kien thuc**: Truy xuat bang chung tuc thi. Tham khao cheo nhieu nguon. Cap nhat voi tai lieu.
2. **Giam ganh nang nhan thuc**: Tim kiem thong tin thuong xuyen. Ho tro tai lieu. Cac quyet dinh thuong xuyen.
3. **Cai thien tinh nhat quan**: Tieu chuan hoa tren thuc hanh tot nhat. Giam bien thien. Dam bao chat luong.
4. **Mo rong nang luc**: Tiet kiem thoi gian. Xu ly khoi luong. Bao phu ngoai gio.
5. **Ho tro giao duc**: Hoc lien tuc. Phat trien ky nang. Chuyen giao kien thuc.

**Vai tro cua bac si phat trien**:
- **It thoi gian hon cho**: Ghi nho su kien, truy xuat thong tin, tai lieu thuong xuyen, phan tich lap di lap lai
- **Nhieu thoi gian hon cho**: Tuong tac benh nhan, ra quyet dinh phuc tap, ky nang thu thuat, giang day va co van, nghien cuu va doi moi, tu duy chien luoc

**Tac dong viec lam**:
- **Nhu cau tang**: Nhieu benh nhan duoc phuc vu, nhieu bac si duoc phuc vu, cac loai thuc hanh moi (tin hoc lam sang AI)
- **Nhan manh ky nang**: Tu duy phan bien, giao tiep benh nhan, phan xet lam sang, ky nang thu thuat, tu duy chien luoc
- **Boi thuong**: Khong nen giam. Co the tang khi cac nhiem vu chuyen biet.

**Ket luan**: May tinh khong thay the nha toan hoc. Ho so benh an dien tu khong thay the bac si. Tro ly AI: cung mo hinh. Cong cu tang cuong, khong thay the.

---

### Q114. Chung toi co the mo rong sang cac ngon ngu hoac quoc gia khac khong?

**A.** Mo rong quoc te:

**Cac ngon ngu hien duoc ho tro**:
- Tieng Anh (chinh)
- Tieng Trung Quoc pho thong
- Bahasa Malaysia
- Tieng Viet
- Bahasa Indonesia

**Sap co**:
- Tieng Tamil
- Tieng Thai
- Tieng Han Quoc

**Mo rong quoc gia**:

**Singapore**: Nen tang
**Malaysia**: Moi truong quy dinh tuong tu, de dang hon
**Indonesia**: Can dia phuong hoa, thi truong lon
**Viet Nam**: Dia phuong hoa nghiem ngat hon, thi truong nho hon
**Thai Lan**: Thich ung van hoa, thi truong lon

**Moi quoc gia mo rong bao gom**:
1. **Dia phuong hoa quy dinh**: Tuan thu cu the theo quoc gia. Luat y te dia phuong. Khung bao ve du lieu. Khung quan tri AI.
2. **Dia phuong hoa ngon ngu**: Thuat ngu y te. Sac thai van hoa. Thanh ngu dia phuong. Dam bao chat luong.
3. **Dia phuong hoa lam sang**: Huong dan dia phuong (tuong duong MOH). Danh muc thuoc dia phuong. Du lieu thu nghiem dia phuong. Thuc hanh cham soc suc khoe van hoa.
4. **Dia phuong hoa co so ha tang**: Cac vung dam may dia phuong. Luu tru du lieu. Do tre mang. Ho tro dia phuong.
5. **Dia phuong hoa van hanh**: Nhom dia phuong. Quan he doi tac dia phuong. Ban hang dia phuong. Ho tro dia phuong.

**Chi phi moi quoc gia**:
- Thiet lap ban dau: 200.000-500.000 USD
- Van hanh hang nam: 200.000-500.000 USD
- Gia moi tenant: 80-90% gia Singapore

**Khuyen nghi**: Bat dau voi Singapore. Mo rong sang Malaysia (de nhat). Sau do Indonesia/Viet Nam (nam 2-3). Cac quoc gia khac dua tren co hoi.

---

### Q115. Cac tinh nang moi nao chung toi co the mong doi trong nhung nam toi?

**A.** Hien thi lo trinh:

**Nam 1 (nen tang)**:
- Nang cao ho tro da ngon ngu
- Ung dung di dong (ban de)
- Mo rong nhap bang giong noi
- Cai thien tich hop quy trinh lam viec

**Nam 2 (chieu sau chuyen khoa)**:
- **AI chuyen khoa**: Chuyen mon chuyen khoa sau hon. Suy luan cap nghien cuu. Cac agent chuyen khoa phu.
- **Tich hop lam sang**: Nhieu he thong EHR hon. Cac cong cu quy trinh lam viec tuy chinh. Ho tro tai lieu tu dong.
- **Giam sat chat luong**: Theo doi do chinh xac tot hon. Phat hien troi. Hoc thich ung.

**Nam 3 (tinh nang nang cao)**:
- **AI da phuong thuc**: Phan tich hinh anh tot hon. Phan tich am thanh (tim, phoi). Tich hop du lieu cam bien.
- **Phan tich du doan**: Du doan rui ro. Du bao ket qua. Lap ke hoach nguon luc.
- **Y hoc ca nhan hoa**: Tich hop gen. Cac yeu to loi song. Phu hop dieu tri.

**Nam 4-5 (doi moi)**:
- **Tich hop nghien cuu**: Thiet ke thu nghiem duoc ho tro boi AI. Bang chung the gioi thuc. Nghien cuu ket qua.
- **Suc khoe cong dong**: Thong tin chi tiet tong hop. Xu huong suc khoe cong cong. Chuan mo chat luong.
- **Cong cu huong den benh nhan**: Chatbot giao duc. Ho tro tu quan ly. Ho tro phan loai.

**Nam 5+ (bien gioi)**:
- **Kha nang AI nang cao**: Suy luan o cap chuyen gia. Thich ung lien tuc. Phoi hop da agent.
- **Mo hinh trien khai moi**: Tinh toan bien. Hoc lien ket. Dao tao bao ton quyen rieng tu.
- **Cong nghe moi noi**: Ung dung tinh toan luong tu. Sinh trac hoc nang cao. Hop nhat cam bien.

**Lo trinh duoc thuc day boi khach hang**:
- Phan hoi khach hang: 60% uu tien
- Xu huong nganh: 30%
- Kham pha chien luoc: 10%

**Giao tiep**:
- Lo trinh hang nam (cap cao)
- Xem truoc hang quy
- Chuong trinh beta
- Hoi dong tu van khach hang

---



### Q116. Lam the nao de do luong neu AI thuc su tiet kiem tien cho chung toi?

**A.** Khung do luong ROI:

**Tiet kiem chi phi truc tiep**:
`
Thoi gian tiet kiem moi truy van: 5 phut
Truy van moi thang: 600.000
Tong thoi gian tiet kiem: 50.000 gio/thang
Chi phi bac si: 80 USD/gio
Gia tri hang thang: 4.000.000 USD
Gia tri hang nam: 48.000.000 USD
`

**Tiet kiem gian tiep**:
- Giam loi: uoc tinh giam 10-15% loi chan doan
- Ket qua tot hon: it bien chung hon, nam vien ngan hon
- Giu chan nhan tai: moi truong lam viec hien dai
- Danh tieng: vi tri chat luong hang dau

**Phuong phap do luong**:
1. **So sanh truoc-sau**: Thiet lap co so truoc khi trien khai. So sanh cung ky sau khi trien khai. Kiem soat cac yeu to gay nhieu.
2. **Thi nghiem gan nhu**: Cac khoa AI vs khoa khong AI. Kiem soat su khac biet. Phan tich thong ke.
3. **Cac truong hop su dung cu the**: Thoi gian danh cho cac cuoc tu van. Thoi gian quyet dinh. Toc do tai lieu.
4. **Dieu tra**: Bao cao tu bac si. Uoc tinh thoi gian tiet kiem. Danh gia chat luong.

**KPI tai chinh**:
- Chi phi moi truy van (muc tieu: giam theo thoi gian)
- Chi phi moi benh nhan (muc tieu: giam)
- Doanh thu moi bac si (muc tieu: tang)
- Bien loi nhuan (muc tieu: tang)

**Bao cao**:
- Hang thang: chi so van hanh
- Hang quy: tinh toan ROI
- Hang nam: danh gia toan dien
- Theo yeu cau: phan tich cu the

---

### Q117. Tac dong den ket qua benh nhan dai han la gi?

**A.** Trien vong nhieu nam:

**Cac linh vuc ket qua**:
1. **Ket qua chan doan**: Chan doan nhanh hon. Chan doan chinh xac hon. Giam loi chan doan. Tac dong benh nhan: dieu tri tot hon kip thoi.
2. **Ket qua dieu tri**: Lua chon dieu tri dua tren bang chung. Giam cham soc khong phu hop. Tuan thu huong dan tot hon. Tac dong benh nhan: ket qua duoc cai thien.
3. **Ket qua quy trinh**: Quay vong nhanh hon. Giam thoi gian cho. Phoi hop cham soc tot hon. Tac dong benh nhan: trai nghiem tot hon.
4. **Ket qua an toan**: Giam su kien bat loi. Nhan dang rui ro tot hon. Can thiep som. Tac dong benh nhan: it tac hai hon.
5. **Ket qua cong bang**: Chat luong cham soc duoc tieu chuan hoa. Giam bat binh dang. Chuyen mon co the truy cap rong hon. Tac dong benh nhan: cham soc cong bang.

**Cai thien co the do luong**:
- Nam 1: Giam 5-10% thoi gian den chan doan. Giam 5-15% xet nghiem khong can thiet. Cai thien 2-5% tuan thu huong dan. Giam 3-7% su kien bat loi.
- Nam 3: Giam 10-20% loi chan doan. Tuan thu dieu tri tot hon 15-25%. Giam 5-10% thoi gian nam vien. Giam 10-15% su kien bat loi.
- Nam 5: Cai thien chat luong tong the 20-30%. Ket qua tot hon dang ke cho cac truong hop phuc tap. Duoc cong nhan la nguoi dan dau chat luong. Chuan mo nganh.

**Vi du cu the**:
- **Goi sepsis**: Truoc AI: tuan thu 60-70%. Sau AI: tuan thu 85-95%. Giam tu vong: 5-10%. So mang duoc cuu: 5-15/nam moi benh vien.
- **Quan ly khang sinh**: Truoc AI: khang sinh phu hop 60%. Sau AI: khang sinh phu hop 85%. Giam khang thuoc: dang ke. Tiet kiem chi phi: 200-500k USD/nam.
- **Do chinh xac chan doan**: Truoc AI: chan doan bi bo sot 8-10%. Sau AI: chan doan bi bo sot 5-7%. Cai thien: giam 30-40% chan doan bi bo sot. Tac dong benh nhan: dang ke.

**Tac dong tich luy** (tren cac benh vien):
- 10 benh vien x 10 mang/nam = 100 mang
- 50 benh vien x 100 mang = 5.000 mang
- Quy mo ASEAN: 10.000+ mang tiem nang

---

### Q118. He thong nay anh huong den danh tieng benh vien dai han nhu the nao?

**A.** Tac dong danh tieng:

**Tac dong tich cuc**:
1. **Nguoi dan dau doi moi**: "Dau tien tai Singapore" co trang thai. Duoc cong nhan nganh. Co hoi noi chuyen. Giai thuong va danh hieu.
2. **Nguoi dan dau chat luong**: Ket qua tot hon duoc chung minh. Chuan mo chat luong. Xep hang nganh. Tuy chon benh nhan.
3. **Thu hut nhan tai**: Moi truong lam viec hien dai. Cong cu tien tien. Phat trien nghe nghiep. Quan tam cua bac si hang dau.
4. **Su tin tuong cua benh nhan**: Niem tin vao cham soc dua tren bang chung. Giam lo lang. Benh nhan duoc giao duc. Truyen mieng.
5. **Quan he doi tac nganh**: Hoi dong AI Verify. Quan he doi tac IMDA. Hop tac nghien cuu. Trinh bay hoi nghi.

**Dinh vi thuong hieu**:
- **Dinh vi cao cap**: Benh vien hang dau. Cham soc tien tien. Ket qua tot nhat. Gia cao cap duoc ho tro.
- **Dinh vi doi moi**: Tu duy tien phong. Lay benh nhan lam trung tam. Dua tren bang chung. Sap san sang cho tuong lai.
- **Dinh vi tin tuong**: Lanh dao tuan thu. Minh bach. Trach nhiem giai trinh. Dang tin cay.

**Co hoi tiep thi**:
- **Tiep thi noi bo**: Giao duc benh nhan. Tuyen dung bac si. Quan ly nha tai tro. Cau chuyen chat luong.
- **Tiep thi ben ngoai**: An pham nganh. Thong cao bao chi. Su kien noi chuyen. Giai thuong.
- **Tiep thi ky thuat so**: Noi bat trang web. Mang xa hoi. Danh gia truc tuyen. Xep hang tim kiem.

**Quan ly rui ro**:
- **Rui ro danh tieng**: Su kien bat loi duoc cong bo. Vi pham quyen rieng tu. Lo ngai chat luong. Van de nha cung cap.
- **Giam thieu**: Ke hoach quan ly khung hoang. Minh bach. Dam bao chat luong. Quan he nha cung cap.

**Ket qua danh tieng dai han**:
- 3 nam: Duoc cong nhan la nguoi dan dau AI tai Singapore. Chuan mo chat luong trong chuyen khoa. Nam chau tu. Nguoi dan dau nganh.
- 5 nam: Duoc cong nhan khu vuc. Xuat sac nghien cuu. Quan he doi tac chien luoc. Di san lau dai.

---

### Q119. Tac dong den su hai long va tinh trang kiet suc cua bac si la gi?

**A.** Tac dong tich cuc dang ke:

**Co che giam kiet suc**:
1. **Giam ganh nang nhan thuc**: It ganh nang bo nho hon. Ho tro quyet dinh tot hon. Giam loi. Giam cang thang.
2. **Tiet kiem thoi gian**: 30-90 phut duoc phuc hoi moi ca. Trung binh: 60 phut. Tren tat ca bac si: dang ke.
3. **Quyet dinh tot hon**: Cac quyet dinh duoc ho tro tot hon. Giam lo lang ve loi. Cai thien su tu tin lam sang.
4. **Cai thien quy trinh lam viec**: Quy trinh lam viec muot ma hon. Giam su ma sat. Cai thien su phoi hop.
5. **Can bang cong viec-cuoc song**: It thoi gian lam viec ngoai gio hon. Giam lam viec ngoai gio. Thoi gian gia dinh.

**Chi so kiet suc co the do luong**:
- **Maslach Burnout Inventory** (cac thay doi dien hinh):
  - Kiet suc cam xuc: Truoc AI: 40-50% kiet suc cao. Sau AI: 30-40% kiet suc cao. Cai thien 10-20 diem phan tram.
  - Phi nhan vi hoa: Truoc AI: 30-40%. Sau AI: 25-35%. Cai thien 5-10 diem.
  - Thanh tuu ca nhan: Truoc AI: 50-60% cam giac. Sau AI: 65-75% cam giac. Cai thien 10-15 diem.

**Loi ich cu the cho bac si**:
1. **Thoi gian tiet kiem moi ca**: 30-90 phut duoc phuc hoi. Trung binh: 60 phut. Tren tat ca bac si: dang ke.
2. **Tang su tu tin**: Cac quyet dinh duoc ho tro tot hon. Giam lo lang ve loi. Cai thien phan xet lam sang.
3. **Phat trien nghe nghiep**: Hoc lien tuc. Nang cao ky nang. Thuc hanh hien dai. Tang truong nghe nghiep.
4. **Can bang cong viec-cuoc song**: It thoi gian lam viec ngoai gio hon. Giam lam viec ngoai gio. Thoi gian gia dinh.
5. **Su hai long cua benh nhan (phan hoi cho bac si)**: Bac si duoc chuan bi tot hon. Cham soc chu y hon. Ket qua tot hon. Giam khieu nai.

**Khao sat su hai long cong viec**:
- "Toi co cac cong cu toi can": 60% -> 80%
- "Toi co thoi gian cho benh nhan": 50% -> 70%
- "Toi cam thay duoc thoa man nghe nghiep": 55% -> 75%
- "Toi se gioi thieu noi lam viec cua minh": 65% -> 80%

**Boi canh nganh**:
- Kiet suc bac si My: 50-60% (cao)
- Kiet suc bac si Singapore: tuong tu
- Cac cong cu AI: duoc ghi nhan la giup do

**Luu y**:
- AI khong phai vien dan bac
- Cac yeu to kiet suc khac van ton tai (khoi luong cong viec, hanh chinh, v.v.)
- Cong cu don le khong sua chua van hoa
- Ket hop voi cac sang kien khac

---

### Q120. Tac dong tich luy cua AI doi voi chat luong cham soc suc khoe la gi?

**A.** Trien vong toan nganh:

**Khung chat luong cham soc suc khoe**:
1. **Hieu qua**: Cham soc dung. Dung thoi diem. Dung noi. Dung benh nhan.
2. **Hieu suat**: Toi uu hoa nguon luc. Hieu qua thoi gian. Hieu qua chi phi. Cai thien quy trinh.
3. **Lay benh nhan lam trung tam**: Tuy chon benh nhan. Giao tiep. Giao duc. Trao quyen.
4. **An toan**: Ngan ngua su kien bat loi. Nhan dang rui ro. Giam loi. Giam sat lien tuc.
5. **Cong bang**: Truy cap binh dang. Chat luong binh dang. Giam bat binh dang. Ung dung rong.
6. **Kip thoi**: Chan doan nhanh. Dieu tri nhanh. Giam thoi gian cho. Cai thien lien tuc.

**Dong gop cua AI cho moi linh vuc**:
- **Hieu qua**: Quyet dinh dua tren bang chung. Cham soc ca nhan hoa. Lua chon toi uu. Hoc lien tuc.
- **Hieu suat**: Tiet kiem thoi gian. Toi uu hoa nguon luc. Cai thien quy trinh. Giam chi phi.
- **Lay benh nhan lam trung tam**: Thong tin tot hon. Cong cu giao duc. Cong cu giao tiep. Trao quyen.
- **An toan**: Phat hien rui ro. Ngan ngua loi. Giam sat. Cai thien.
- **Cong bang**: Truy cap chuyen mon binh dang. Chat luong duoc tieu chuan hoa. Giam bat binh dang. Ung dung rong.
- **Kip thoi**: Chan doan nhanh hon. Quyet dinh nhanh hon. Giam thoi gian cho. Cai thien lien tuc.

**Dinh luong tac dong tich luy**:
- Nam 1 tren 10 benh vien: 5.000 mang duoc cuu (uoc tinh). 50 trieu USD chi phi tranh duoc. 100.000 su kien bat loi duoc ngan ngua. Cai thien chat luong dang ke.
- Nam 5 tren 50 benh vien: 30.000 mang duoc cuu (uoc tinh). 300 trieu USD chi phi tranh duoc. 600.000 su kien bat loi duoc ngan ngua. Chuyen doi nganh.
- Nam 10 tren 100 benh vien: 100.000 mang duoc cuu (uoc tinh). 1 ty USD chi phi tranh duoc. Hang trieu su kien bat loi duoc ngan ngua. Tieu chuan cham soc suc khoe moi.

**Chuyen doi nganh**:
- **Tieu chuan phat trien**: Cham soc duoc tang cuong AI duoc ky vong. Chi so chat luong moi. Chuan mo nganh. Cai thien lien tuc.
- **Phat trien luc luong lao dong**: Yeu cau biet AI. Bo ky nang moi. Phat trien nghe nghiep. Cap nhat giao duc.
- **Ky vong cua benh nhan**: Benh nhan duoc thong tin. Cham soc duoc tang cuong AI duoc ky vong. Khung niem tin. Lua chon duoc trao quyen.
- **Xu huong chi phi**: Chi phi moi truy van giam. Chat luong tang. Ket qua tot hon moi dong. Dau tu ben vung.

**Vi tri lanh dao Singapore**:
- Vi tri khu vuc
- Tieu chuan nganh
- Trung tam doi moi
- Thuc hanh tot nhat

**Khuyen nghi chien luoc**:
- Ap dung AI nhu cong cu chat luong
- Dau tu cho dai han
- Dan dau chuyen doi nganh
- Xay dung tac dong lau dai

---

### Q121. AI co the xu ly cac truong hop y te phuc tap khong?

**A.** Co, dac biet la lane phuc tap (Sonnet 4.5 / Qwen3.5-Plus): bieu hien da he thong, trieu chung mo ho, xem xet dieu kien hiem gap, suy luan xac suat voi trich dan. Hieu suat: ~92% do chinh xac tren cac truong hop phuc tap (PoC). Tu choi khi khong chac chan. Cung cap chan doan phan biet duoc xep hang theo xac suat voi bang chung ho tro.

---

### Q122. Lam the nao de AI xu ly cac truong hop nhi khoa khac nhau?

**A.** Chuyen mon hoa nhi khoa: lieu luong dua tren can nang bat buoc, cham soc phu hop theo tuoi, cac can nhac phat trien, cac huong dan cu the cho nhi khoa (AAP, v.v.), kiem tra chong chi dinh nghiem ngat hon, cac can nhac giao tiep voi cha me. Vi du phan hoi cho 'ibuprofen cho tre 5 tuoi': yeu cau can nang, tinh toan lieu luong dua tren can nang, kiem tra gioi han tuoi, chong chi dinh, theo doi cu the cho nhi khoa.

---

### Q123. AI co the goi y cac dieu tri thay the khong?

**A.** Co, voi minh bach day du: Hang dau: khuyen nghi tieu chuan. Thay the cho: chong chi dinh, di ung, chi phi, tuy chon. Liet ke voi muc do bang chung. Thao luan ve danh doi. Lam noi bat cac yeu to quyet dinh. Dinh dang: 'Chinh: [thuoc A] - [bang chung]. Thay the neu [dieu kien]: [thuoc B] - [bang chung]. Khuyen nghi phu thuoc vao cac yeu to benh nhan X, Y, Z.'

---

### Q124. Dieu gi xay ra khi benh nhan co nhieu nhu cau chuyen khoa?

**A.** Phoi hop da chuyen khoa: AI kich hoat nhieu agent, cac can nhac xuyen chuyen khoa, tuong tac thuoc tren cac he thong, ke hoach cham soc phoi hop, phan hoi tich hop duy nhat. Vi du: benh nhan tieu duong voi CKD va CHF -> Noi tiet: quan ly tieu duong. Than hoc: dieu tri dieu chinh CKD. Tim mach: cac can nhac suy tim. Ket hop: khuyen nghi tich hop ton trong ca ba.

---

### Q125. AI co the giup voi cac cuoc trao doi dong thuan thong tin khong?

**A.** Co, vai tro ho tro: giai thich thu thuat/dieu tri bang ngon ngu don gian, liet ke cac rui ro vat chat, thao luan ve cac lua chon thay the, phac thao loi ich, cung cap tai lieu giao duc benh nhan. Luu y: bac si van co trach nhiem chinh trong quy trinh dong thuan. AI chuan bi nhung khong thay the. Chu ky cua benh nhan van thuoc ve bac si.

---

### Q126. Lam the nao de AI xu ly cham soc cuoi doi?

**A.** Chuyen khoa nhan cam: chuyen mon cham soc giam nhe, cac cuoc trao doi muc tieu cham soc, quan ly trieu chung, cac cuoc trao doi voi gia dinh, cac can nhac van hoa, nhan cam ton giao. AI cung cap: cac lua chon giam nhe dua tren bang chung, cac khung giao tiep, nhan cam van hoa-ton giao, thong tin gioi thieu hospice. Quan trong: phan xet cua bac si va su dong cam cua con nguoi la thiet yeu. AI ho tro, khong thay the.

---

### Q127. AI xu ly cac cau hoi suc khoe tam than nhu the nao?

**A.** Cau hinh co the: Tieu chuan: dinh tuyen den cac agent tam than/tam ly. Bao thu: gioi thieu tu van chuyen khoa. Giao duc: cung cap thong tin, gioi thieu de cham soc. Huong dan cu the: Nhan biet y dinh tu tu: leo thang ro rang den chuyen khoa. Trieu chung nghiem trong: gioi thieu ngay lap tuc. Cac cau hoi thuong xuyen: huong dan AI + chuyen khoa khi can. Bao mat: bao ve quyen rieng tu bo sung. Cau hinh benh vien: muc do tich cuc AI trong phan hoi suc khoe tam than. Hau het: bao thu.

---

### Q128. AI co the goi y cham soc phong ngua cho benh nhan khong?

**A.** Co, phong ngua dua tren bang chung: sang loc dua tren tuoi, khuyen nghi dua tren rui ro, huong dan tiem chung, tu van loi song, sang loc ung thu. Tich hop voi EHR: trang thai phong ngua cua benh nhan, ngay sang loc cuoi cung, cac khoang trong duoc xac dinh. Giup bac si uu tien va thao luan ve cham soc phong ngua.

---

### Q129. Lam the nao de AI cap nhat voi cac thuoc moi?

**A.** Nhieu co che: co so du lieu phe duyet HSA duoc dong bo, cap nhat danh muc thuoc WHO, giam sat tai lieu duoc pham, thay doi danh muc thuoc benh vien, ket qua thu nghiem noi bo. Tan suat: phe duyet moi trong vong 2-4 tuan, huong dan chinh trong vong 1 tuan, giao thuc noi bo theo thoi gian thuc, su dung ngoai nhan trong duoc giam sat can than. Han che: thuoc rat moi (vai thang) co the co du lieu han che; AI ghi nhan dieu nay.

---

### Q130. AI co the du doan ket qua benh nhan khong?

**A.** Kha nang du doan han che trong pham vi hien tai: phan tang rui ro co the, mo hinh ket qua: tinh nang tuong lai, du bao ca nhan hoa: them tiem nang. Hien tai: AI giup danh gia trang thai hien tai, lua chon dieu tri. Khong thay the cac mo hinh du doan chuyen biet (nhu APACHE, CHA2DS2, v.v.). Co the duoc them nhu dich vu bo sung.

---

### Q131. EHR cu hon hoac khong tieu chuan co the tich hop khong?

**A.** Co, nhieu con duong: HL7 v2 (tieu chuan cu, hau het EHR cu ho tro, 30-80k USD), tich hop co so du lieu (truc tiep doc co so du lieu EHR, 50-150k USD), API tuy chinh (xay dung bo chuyen doi, 80-200k USD), su dung doc lap (bac si nhap context thu cong, khong co chi phi bo sung). Khuyen nghi: danh gia EHR truoc hop dong; bao gia tich hop rieng biet.

---

### Q132. Chung toi co can di chuyen bat ky du lieu hien co vao he thong khong?

**A.** Tuy chon nhung co gia tri. Bat buoc: PDF bao cao thu nghiem noi bo, giao thuc cu the cua benh vien, tai lieu tham khao theo khoa. Quy trinh: kiem ke du lieu, an danh hoa, tai len, lập chi muc (24-48 gio), xac thuc. Quy mo: benh vien nho 50-100 tai lieu (1 tuan), benh vien vua 200-500 (2 tuan), benh vien lon 1000-3000 (4-6 tuan). Chi phi: nho 5-10k USD, vua 15-25k USD, lon 30-60k USD.

---

### Q133. Chung toi co the them cac khoa hoac chuyen khoa hon sau nay khong?

**A.** Co, duoc thiet ke de mo rong. Them khoa moi: Giai doan 1 Quyet dinh (2 tuan), Giai doan 2 Cau hinh (1 tuan), Giai doan 3 Nhap noi dung (1-3 tuan), Giai doan 4 Kiem tra (1 tuan), Giai doan 5 Ra mat (1 ngay). Tong: 5-8 tuan moi khoa moi. Chi phi moi khoa: ky thuat 10-20k USD, noi dung lam sang 5-15k USD, kiem tra thi diem 5-10k USD. Tong: 20-45k USD moi chuyen khoa moi.

---

### Q134. Tong dau tu ban dau cho mot benh vien la bao nhieu?

**A.** Tong chi phi Nam 1 (benh vien dien hinh): Giay phep phan mem (hang nam) 40-80k USD, Dich vu trien khai 50-150k USD, Thoi gian nhan vien benh vien 40-60k USD, Tich hop EHR 20-50k USD, Thiet lap tuan thu 20-40k USD, Dao tao & quan ly thay doi 15-30k USD. Tong Nam 1: 185-410k USD. Nam 2+ hang nam: 70-135k USD. TCO 5 nam: 465-960k USD. So sanh voi gia tri: 7-15 trieu USD tiet kiem trong 5 nam. ROI: 8-20x.

---

### Q135. Cau truc hop dong dien hinh la gi?

**A.** Cac loai hop dong: MSA (Thoa thuan Dich vu Chu), SLA (Thoa thuan Cap do Dich vu), DPA (Thoa thuan Xu ly Du lieu, tuan thu PDPA), SOW (Pham vi Cong viec, cu the theo du an). Dieu khoan tieu chuan: Thoi han ban dau 36 thang, Tu dong gia han 12 thang voi tang toi da 5%, Thong bao ket thuc 90 ngay, Tra lai du lieu 30 ngay, Gioi han trach nhiem 12 thang phi, Boi thuong tuong ho. Cac mo hinh dinh gia: phi hang thang phat (pho bien nhat), theo ghe bac si, theo truy van, lai.

---

### Q136. Thoi han hop dong toi thieu la bao lau va cac dieu khoan ket thuc la gi?

**A.** Thoi han toi thieu: 36 thang (3 nam). Tai sao 3 nam: thu hoi chi phi trien khai, on dinh cho ca hai ben, tieu chuan nganh cho SaaS y te. Cac thoi han ngan hon (ngoai le): 24 thang: phi bao hiem 10%, 12 thang: phi bao hiem 25%, Thi diem/PoC: 3-6 thang voi gia khong tieu chuan. Cac kich ban ket thuc: Ket thuc thoi han (thong bao 90 ngay, chuyen doi muot), Ket thuc vi tien loi (phi ket thuc som: gia tri hop dong con lai duoc phan bo), Ket thuc vi vi pham (vi pham vat chat, thoi gian khac phuc 30 ngay, khong co phi ket thuc som), Bat kha khang (khong co phat).

---

### Q137. Ai tu phia chung toi can tham gia vao viec trien khai?

**A.** Ban do cac ben lien quan: Nha tai tro dieu hanh (CEO/COO/CFO/CMO), Lanh dao du an (CMIO, Quan ly Du an, Giam doc Lam sang), Chuyen gia lam sang (1-2 moi khoa), Nhom CNTT (Giam doc CNTT, Ky su truong, Ky su Bao mat, Ky su Mang), Tuan thu (Can bo Tuan thu, DPO, Co van Phap ly). Cam ket thoi gian: Nha tai tro dieu hanh 1 gio/tuan, CMIO 5 gio/tuan, Chuyen gia lam sang 5-10 gio/tuan, Truong CNTT 10-15 gio/tuan, Tuan thu 5 gio/tuan. Tong no luc benh vien: ~200 gio trong 10 tuan.

---

### Q138. Dieu gi xay ra neu chung toi muon thay doi nha cung cap trong khi trien khai?

**A.** Thay doi giua chung trien khai la hiem nhung co the. Ly do: thay doi kinh doanh dang ke, phat hien lua chon thay the tot hon, that bai trong viec cung cap, thay doi quy dinh. Chi phi chuyen doi giua chung trien khai: Chi phi nha cung cap goc: 50-100k USD mat, Chi phi nha cung cap moi: 100-200k USD khoi dau moi, Thoi gian nhan vien benh vien: 50-100k USD, Tong chi phi chuyen doi: 200-400k USD. Khuyen nghi: Danh gia nha cung cap ky luong truoc khi ky hop dong. Thi diem voi 2 nha cung cap truoc khi ky hop dong. Tieu chi thanh cong ro rang tu ngay 1.

---

### Q139. He thong co the tuy chinh theo nhu cau cu the cua benh vien khong?

**A.** Co, nhieu cap do: Cap 1 Cau hinh (khong co code, bao gom, 1-2 tuan), Cap 2 Prompt tuy chinh (it code, 5-10k USD, 2-3 tuan), Cap 3 Quy trinh lam viec tuy chinh (it code, 15-30k USD, 4-6 tuan), Cap 4 Tich hop tuy chinh (code, 40-100k USD, 8-12 tuan), Cap 5 Tinh nang tuy chinh (code dang ke, 100-300k USD, 6-9 thang). Cac tuy chinh pho bien: cau hinh chuyen khoa, boi canh dia phuong, tich hop quy trinh lam viec, bao cao tuy chinh. Khuyen nghi: Nam 1 tuy chinh toi thieu, Nam 2 xac dinh khoang trong, Nam 3+ dua tren nhu cau duoc chung minh.

---

### Q140. Lam the nao de xu ly bien dong nhan su trong khi trien khai?

**A.** Bien dong nhan su benh vien: Nha tai tro du an roi: ghi lai tat ca quyet dinh, nhieu ben lien quan, tai lieu tieu chuan, xac dinh nguoi thay the. Truong CNTT thay doi: chuyen giao kien thuc, tai lieu trong wiki benh vien, ho tro ky thuat cua Nova, tac dong toi thieu. Can bo tuan thu thay doi: tai lieu tuan thu toan dien, DPIA va kiem toan bao mat co san, con mat moi co the co loi. Bien dong nhan su Nova: Giam doc Tai khoan roi: ke hoach chuyen tiep, CSM bao phu, nguoi thay the duoc phan cong, tac dong nho. Ky su truong xoay vong: nhieu ky su quen thuoc, tai lieu code, chia se kien thuc noi bo, tac dong nho.

---

### Q141. AI co the xu ly nhap bang giong noi trong moi truong phong mo hoac vo trung khong?

**A.** Xem xet quy trinh lam viec: Nhap bang giong noi (ranh tay) duoc khuyen nghi cho phong mo. Kich hoat bang ban dap chan co the. Giao dien than thien voi cam ung. Tich hop may tinh bang tuong thich voi moi truong vo trung. Quy trinh lam viec phong mo cu the: Truoc phau thuat: tu van AI ben ngoai truong vo trung. Trong phau thuat: ho tro bang giong noi cho cac giao thuc. Sau phau thuat: AI cho tai lieu. Chi phi: tieu chuan. Benh vien cung cap phan cung tuong thich voi moi truong vo trung.

---

### Q142. AI co the xu ly cac dieu kien man tinh phuc tap khong?

**A.** Quan ly benh man tinh: tieu duong, suy tim, COPD, tang huyet ap, sot ung thu. Toi uu hoa cham soc dai han. AI giup giam sat, goi y dieu chinh dieu tri, xac dinh bien chung. Dac biet co gia tri cho: benh nhan da thuoc, benh nhan cao tuoi, benh nhan co nhieu benh kem theo. Tich hop voi: chuong trinh quan ly benh, cham soc suc khoe cong dong.

---

### Q143. Lam the nao de AI xu ly cac ket qua xet nghiem?

**A.** Ho tro giai thich xet nghiem: nhan thuc pham vi tham chieu, phan tich xu huong, danh dau gia tri nguy kich, chan doan phan biet, khuyen nghi theo doi. Vi du: 'Glucose 350. Nguyen nhan co the: X, Y, Z. Xet nghiem duoc khuyen nghi: A, B. Boi canh benh nhan: trang thai insulin, che do an, v.v.' Tich hop voi he thong xet nghiem EHR.

---

### Q144. AI co the giup voi viec lap ke hoach xuat vien khong?

**A.** Ho tro xuat vien toan dien: doi chieu thuoc, giao duc benh nhan, lap lich theo doi, nhu cau cham soc tai nha, thuoc sau xuat vien. Giup giam tai nhap vien thong qua chuan bi xuat vien tot hon. Tich hop voi quan ly truong hop.

---

### Q145. Dieu gi xay ra khi AI khong co thong tin ve mot truong hop cu the?

**A.** Da duoc tra loi o Q75. Xem chi tiet o do.

---

### Q146. AI co the xu ly cac truong hop nhi khoa phuc tap khong?

**A.** Da duoc tra loi o Q122. Xem chi tiet o do.

---

### Q147. Lam the nao de AI xu ly cac truong hop cap cuu cu the?

**A.** Tinh nang cap cuu: giao thuc ATLS, phan loai tham hoa hang loat, uu tien hoi suc, chuyen tiep cham soc cap cuu, phoi hop da chuyen khoa. Thoi gian quan trong: lane cap cuu duoc toi uu hoa. Phoi hop da chuyen khoa trong chan thuong.

---

### Q148. AI co the giup voi viec quan ly nhiem trung khong?

**A.** Ho tro benh truyen nhiem: lua chon khang sinh, cac nguyen tac quan ly khang sinh, cac can nhac khang thuoc, quan ly HIV, lao, viem gan, quan ly dich benh. Quan trong cho: su dung khang sinh phu hop, kiem soat nhiem trung benh vien.

---

### Q149. Lam the nao de AI xu ly cac truong hop ung thu?

**A.** Ho tro ung thu: cac phac do hoa tri, dieu chinh lieu luong, quan ly tac dung phu lieu phap mien dich, cham soc ho tro, cham soc sau dieu tri. Tich hop voi nhom ung thu. Dac biet co gia tri cho: cac quyet dinh hoa tri phuc tap.

---

### Q150. AI co the xu ly cac truong hop than hoc khong?

**A.** Ho tro than hoc: phan giai CKD, danh gia AKI, quyet dinh loc mau, lieu luong thuoc theo GFR, quan ly dien giai. Dac biet co gia tri cho: lieu luong thuoc trong benh than (nguyen nhan pho bien cua loi). Tich hop voi ket qua xet nghiem.

---

### Q151. Lam the nao de AI xu ly cac truong hop than kinh?

**A.** Ho tro than kinh: lo trinh dot quy cap tinh, quan ly co giat, danh gia dau dau, benh thoai hoa than kinh, cac dieu kien cot song. Thoi gian quan trong: lo trinh dot quy. AI huu ich cho: chan doan phan biet phuc tap, cac quyet dinh dieu tri.

---

### Q152. AI co the xu ly cac truong hop noi tiet khong?

**A.** Ho tro noi tiet: tieu duong (da duoc de cap), roi loan tuyen giap, roi loan tuyen thuong than, cac dieu kien tuyen yen, noi tiet sinh san. Cac dieu kien pho bien: gia tri dang ke cho cham soc ban dau + noi tiet.

---

### Q153. Lam the nao de AI xu ly cac truong hop benh truyen nhiem?

**A.** Ho tro benh truyen nhiem: lua chon khang sinh, cac nguyen tac quan ly khang sinh, cac can nhac khang thuoc, quan ly HIV/lao/viem gan, quan ly dich benh. Quan trong cho: su dung khang sinh phu hop, kiem soat nhiem trung benh vien.

---

### Q154. AI co the xu ly cac truong hop huyet hoc khong?

**A.** Ho tro huyet hoc: danh gia thieu mau, roi loan chay mau, ung thu mau, cac quyet dinh truyen mau, chong dong. Tich hop voi chuyen khoa huyet hoc.

---

### Q155. Lam the nao de AI xu ly cac truong hop mien dich hoc?

**A.** Ho tro mien dich hoc: benh tu mien, di ung, suy giam mien dich, ghep tang, cac can nhac tiem chung. Linh vuc chuyen biet. AI cung cap tham khao + huong dan.

---

### Q156. AI co the xu ly cac truong hop nhi khoa chuyen khoa khong?

**A.** Cac chuyen khoa nhi khoa: tim mach nhi, ho hap nhi, tieu hoa nhi, than kinh nhi, ung thu nhi, v.v. Moi loai: cham soc dua tren can nang, phu hop theo tuoi phu hop.

---

### Q157. Lam the nao de AI xu ly suc khoe phu nu cu the?

**A.** Suc khoe phu nu: suc khoe sinh san, thai ky, suc khoe vu, man kinh, sang loc ung thu, suc khoe tam than. Ho tro toan dien trong suot cuoc doi suc khoe phu nu.

---

### Q158. AI co the xu ly suc khoe nam gioi khong?

**A.** Suc khoe nam gioi: rui ro tim mach, suc khoe tuyen tien liet, thieu hut testosterone, suc khoe tam than, sang loc ung thu. Cham soc duoc dieu chinh theo cac moi quan tam suc khoe nam gioi.

---

### Q159. Lam the nao de AI xu ly y hoc vi thanh nien?

**A.** Y hoc vi thanh nien: cac can nhac bao mat, suc khoe tam than, su dung chat, suc khoe tinh duc, tu van loi song. Linh vuc nhan cam. Bao ve bao mat. Tich hop voi: nhi khoa, y hoc gia dinh.

---

### Q160. AI co the xu ly cham soc nguoi cao tuoi cu the khong?

**A.** Cham soc lao khoa: danh gia nhan thuc, danh gia suy yeu, phong ngua nga, da thuoc, muc tieu cham soc. Ho tro danh gia lao khoa toan dien.

---

### Q161. AI co the xu ly cac truong hop phau thuat khong?

**A.** Ho tro phau thuat: danh gia truoc phau thuat, phan tang rui ro, cac can nhac thu thuat, lap ke hoach gay me, cham soc sau phau thuat. Tich hop voi quy trinh phau thuat. Huu ich cho: cac bac si phau thuat noi tru, cac truong hop phuc tap, lap ke hoach da chuyen khoa.

---

### Q162. Lam the nao de AI xu ly cac truong hop cap cuu tim mach?

**A.** Cap cuu tim mach: cac giao thuc ACS, quan ly suy tim, cham soc loan nhip, tang huyet ap, quan ly lipid, huong dan hinh anh. Mot trong nhung chuyen khoa co gia tri nhat cho ho tro AI.

---

### Q163. AI co the xu ly cac truong hop ho hap phuc tap khong?

**A.** Ho hap phuc tap: hen phe quan/COPD nang, dot cap COPD, thuyen tac phoi, ung thu phoi, ngu ngon. Quan trong cho: cac can thiep kip thoi.

---

### Q164. Lam the nao de AI xu ly cac truong hop tieu hoa?

**A.** Tieu hoa: IBS/IBD, xuat huyet tieu hoa, benh gan, cac dieu kien tuy, cac can nhac noi soi. Tich hop voi quy trinh lam viec chuyen khoa tieu hoa.

---

### Q165. AI co the xu ly cac truong hop ung thu khong?

**A.** Da duoc tra loi o Q149. Xem chi tiet o do.

---

### Q166. Lam the nao de AI xu ly cac truong hop than hoc?

**A.** Da duoc tra loi o Q150. Xem chi tiet o do.

---

### Q167. AI co the xu ly cac truong hop san khoa khong?

**A.** Ho tro san khoa: quan ly thai ky, cham soc truoc sinh, cac can nhac sinh, cham soc sau sinh, thai ky nguy co cao. Tich hop voi nhom san khoa. Dac biet co gia tri cho: thai ky nguy co cao.

---

### Q168. Lam the nao de AI xu ly cac truong hop nhi khoa so sinh/NICU?

**A.** Cham soc so sinh: danh gia Apgar, on dinh ban dau, cac dieu kien pho bien, cham soc NICU cu the, ho tro cha me. Tich hop voi quy trinh lam viec NICU, tu van neonatologist.

---

### Q169. AI co the xu ly cac truong hop da lieu khong?

**A.** Da lieu: danh gia ton thuong da, chan doan phan biet, khuyen nghi dieu tri, huong dan gioi thieu chuyen khoa. Tot nhat ket hop voi: cong cu phan tich hinh anh. AI xu ly boi canh lam sang, AI hinh anh xu ly hinh anh.

---

### Q170. Lam the nao de AI xu ly cac truong hop nhan khoa?

**A.** Nhan khoa: danh gia trieu chung thi giac, cac dieu kien pho bien, khuyen nghi dieu tri, phoi hop chuyen khoa. Kha nang dua tren hinh anh han che ma khong co cong cu phan tich hinh anh chuyen biet. Tot nhat cho: ly luan lam sang, huong dan dieu tri.

---

### Q171. AI co the xu ly cac truong hop tai mui hong khong?

**A.** Tai mui hong: danh gia trieu chung, cac dieu kien pho bien, khuyen nghi dieu tri, gioi thieu chuyen khoa. Ho tro toan dien.

---

### Q172. Lam the nao de AI xu ly cac truong hop rang mieng?

**A.** Rang mieng: sang loc thuong xuyen, benh rang mieng, cac lua chon dieu tri, giao duc benh nhan. Pham vi han che nhung co san. Tich hop voi khoa rang.

---

### Q173. AI co the xu ly cac truong hop phuc hoi khong?

**A.** Phuc hoi: khuyen nghi lieu phap, danh gia tien do, lap ke hoach xuat vien, muc tieu dai han, giao duc gia dinh. Tich hop tren: PT, OT, Lieu phap Ngon ngu, Phuc hoi Tim/Phoi.

---

### Q174. Lam the nao de AI xu ly cac truong hop tam than cu the?

**A.** Da duoc tra loi o Q127. Xem chi tiet o do.

---

### Q175. AI co the xu ly cac truong hop quan ly dau khong?

**A.** Quan ly dau: cac phuong phap da phuong thuc, nhan manh khong opioid, danh gia rui ro, cac lua chon khong duoc pham, tu van benh nhan. Linh vuc nhan cam. Cau hinh bao thu. Tich hop voi chuyen khoa dau.

---

### Q176. Lam the nao de AI xu ly cac truong hop cap cuu phau thuat?

**A.** Cap cuu phau thuat: danh gia ATLS, phan loai tham hoa hang loat, uu tien hoi suc, chuyen tiep cham soc cap cuu, phoi hop da chuyen khoa. Thoi gian quan trong. Tich hop voi: ED, phau thuat, ICU.

---

### Q177. AI co the xu ly cac truong hop cap cuu than kinh khong?

**A.** Cap cuu than kinh: lo trinh dot quy cap tinh, quan ly co giat, cac dau hieu nguy hiem dau dau, benh thoai hoa than kinh, cac dieu kien cot song. Thoi gian quan trong: lo trinh dot quy. Tich hop voi: ED, than kinh, ICU.

---

### Q178. Lam the nao de AI xu ly cac truong hop cap cuu ung thu?

**A.** Cap cuu ung thu: hoi chung ly giai khoi u, ep tuy song, tang do nho mau, nhiem trung nang o benh nhan suy giam mien dich, cac cap cuu khac. Thoi gian quan trong. Tich hop voi: ED, ung thu, ICU.

---

### Q179. AI co the xu ly cac truong hop loan nhip tim khong?

**A.** Quan ly loan nhip: cac can nhac chan doan, lua chon dieu tri, tinh hop le cat dot, chong dong, giao duc benh nhan. Chuyen biet trong tim mach.

---

### Q180. Lam the nao de AI xu ly cac dieu kien ho hap phuc tap?

**A.** Ho hap phuc tap: hen phe quan nang, dot cap COPD, thuyen tac phoi, ung thu phoi, ngu ngon. Quan trong cho: cac can thiep kip thoi.

---

### Q181. AI co the xu ly cac dieu kien tu mien khong?

**A.** Tu mien: cac khung chan doan, cac dieu tri bien doi benh, quan ly dot cap, cac can nhac benh kem theo, gioi thieu chuyen khoa. Tich hop voi: thap khop, mien dich hoc.

---

### Q182. Lam the nao de AI xu ly y hoc ghep tang?

**A.** Ghep tang: danh gia truoc ghep, uc che mien dich, quan ly thai ghet, cham soc dai han, cac can nhac nguoi hien song. Chuyen biet. AI cung cap tham khao + huong dan.

---

### Q183. AI co the xu ly cac truong hop nhiem trung benh vien khong?

**A.** Nhiem trung benh vien (HAC): nhan dang, cac chien luoc phong ngua, dieu tri khi xay ra, cac yeu cau bao cao, cac co hoi cai thien. Tich hop voi: kiem soat nhiem trung, dich te hoc benh vien.

---

### Q184. Lam the nao de AI xu ly cac truong hop hoi nghi da chuyen khoa?

**A.** Hoi nghi da chuyen khoa: nghien cuu truoc hoi nghi, tu van da chuyen khoa, cac khung quyet dinh, tai lieu, lap ke hoach theo doi. Ho tro hop tac nhieu bac si.

---

### Q185. AI co the ho tro doi moi giao duc y khoa khong?

**A.** Giao duc y khoa: cac lo trinh hoc tap ca nhan hoa, kham pha chu de, tai lieu moi nhat, cap nhat lien quan den thuc hanh, cac cau hoi thuc hanh. Dac biet co gia tri trong cac benh vien giang day.

---

### Q186. Lam the nao de AI xu ly tich hop nghien cuu lam sang?

**A.** Tich hop nghien cuu: ho tro xem xet tai lieu, sang loc thu nghiem, ho tro phan tich, ho tro xuat ban, cac cong cu hop tac. Nhieu ung dung cap do nghien cuu.

---

### Q187. AI co the ho tro cac chuong trinh suc khoe cong dong khong?

**A.** Suc khoe cong dong: quan ly suc khoe dan so, phat hien dich benh, phan bo nguon luc, cac chuong trinh suc khoe, do luong tac dong. Tich hop voi: dich te hoc benh vien.

---

### Q188. Lam the nao de AI xu ly cac truong hop y te tu xa cu the?

**A.** Da duoc tra loi o Q47. Xem chi tiet o do.

---

### Q189. AI co the xu ly cac truong hop giam sat tu xa khong?

**A.** Giam sat tu xa: thiet ke chuong trinh, lua chon benh nhan, tich hop cong nghe, theo doi ket qua, gia tri chien luoc. Ho tro chuong trinh RPM.

---

### Q190. Lam the nao de AI xu ly cac chuong trinh benh man tinh?

**A.** Quan ly benh man tinh: quan ly suc khoe dan so, dang ky benh nhan, phoi hop cham soc, do luong ket qua, phu hop chien luoc. Cac chuong trinh quan ly benh.

---

### Q191. AI co the ho tro cac chuong trinh suc khoe khong?

**A.** Suc khoe: suc khoe dan so, cham soc phong ngua, giao duc benh nhan, su tham gia, ket qua. Cac sang kien suc khoe benh vien.

---

### Q192. Lam the nao de AI xu ly cac chuong trinh suc khoe cong dong?

**A.** Suc khoe cong dong: danh gia nhu cau, thiet ke chuong trinh, phat trien quan he doi tac, trien khai, do luong tac dong. Ho tro quan he doi tac cong dong.

---

### Q193. AI co the ho tro cac chuong trinh suc khoe truong hoc khong?

**A.** Suc khoe truong hoc: ho tro giao duc, cac chuong trinh tiem chung, sang loc suc khoe, quan he doi tac cong dong, phu hop chien luoc. Cac chuong trinh suc khoe truong hoc.

---

### Q194. Lam the nao de AI xu ly suc khoe noi lam viec?

**A.** Suc khoe noi lam viec: cac chuong trinh suc khoe nhan vien, suc khoe nghe nghiep, ho tro suc khoe tam than, cac sang kien chien luoc, do luong ROI. Suc khoe luc luong lao dong benh vien.

---

### Q195. AI co the ho tro cac cap nhat quy dinh khong?

**A.** Cap nhat quy dinh: giam sat thong tu MOH Singapore, ban tin PDPC, cap nhat IMDA, thong bao HSA, ho tro trien khai. Giam sat quy dinh lien tuc.

---

### Q196. Lam the nao de AI xu ly truyen thong chien luoc?

**A.** Truyen thong chien luoc: nhan tin cac ben lien quan, quan ly thuong hieu, truyen thong khung hoang, truyen thong noi bo, truyen thong ben ngoai. Ho tro truyen thong toan dien.

---

### Q197. AI co the ho tro quan ly thay doi khong?

**A.** Quan ly thay doi: phat trien chien luoc, trien khai, su tham gia cac ben lien quan, quan ly su khang cu, tinh ben vung. Ho tro thay doi chien luoc.

---

### Q198. Lam the nao de AI xu ly phat trien van hoa?

**A.** Van hoa: danh gia van hoa, phu hop gia tri, truyen thong, cong nhan, cai thien lien tuc. Ho tro van hoa benh vien.

---

### Q199. AI co the ho tro chuyen tiep lanh dao khong?

**A.** Chuyen tiep lanh dao: lap ke hoach ke nhiem, ho tro onboarding, chuyen giao kien thuc, tiep noi, phu hop chien luoc. Ho tro chuyen tiep quan trong.

---

### Q200. Lam the nao de AI xu ly quan tri benh vien?

**A.** Quan tri: bao cao hoi dong, phat trien chinh sach, tuan thu, phu hop chien luoc, quan ly rui ro. Ho tro quan tri benh vien.

---

### Q201. AI co the xu ly cac truong hop cap cuu nhi khoa khong?

**A.** Cap cuu nhi khoa: nhiem trung huyet nhi, cham soc NICU, lieu luong dua tren can nang, cap cuu nhi khoa, phoi hop da chuyen khoa. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu, giao tiep voi cha me.

---

### Q202. Lam the nao de AI xu ly cac truong hop cap cuu san khoa?

**A.** Cap cuu san khoa: tien san giat, xuat huyet sau sinh, tieu duong thai ky, cham soc truoc sinh, cac dieu kien nguy co cao. Tich hop voi nhom san khoa. Dac biet co gia tri cho: thai ky nguy co cao.

---

### Q203. AI co the xu ly cac truong hop cap cuu than kinh khong?

**A.** Da duoc tra loi o Q177. Xem chi tiet o do.

---

### Q204. Lam the nao de AI xu ly cac truong hop cap cuu tim mach?

**A.** Da duoc tra loi o Q162. Xem chi tiet o do.

---

### Q205. AI co the xu ly cac truong hop cap cuu ho hap khong?

**A.** Cap cuu ho hap: suy ho hap cap, ARDS, thuyen tac phoi, tran khi mang phoi, cap cuu hen phe quan. Thoi gian quan trong. Tich hop voi: ED, ICU, ho hap.

---

### Q206. Lam the nao de AI xu ly cac truong hop cap cuu tieu hoa?

**A.** Cap cuu tieu hoa: xuat huyet tieu hoa, viem tuy cap, viem ruot thua, tac ruot, suy gan cap. Thoi gian quan trong. Tich hop voi: ED, phau thuat, tieu hoa.

---

### Q207. AI co the xu ly cac truong hop cap cuu than hoc khong?

**A.** Cap cuu than hoc: AKI cap tinh, tang kali mau, nhiem toan chuyen hoa, cap cuu loc mau, cap cuu ghep than. Thoi gian quan trong. Tich hop voi: ED, than hoc, ICU.

---

### Q208. Lam the nao de AI xu ly cac truong hop cap cuu noi tiet?

**A.** Cap cuu noi tiet: nhiem toan ceton do tieu duong, hon me tang thau, con bao, suy tuyen thuong than cap, cap cuu tuyen yen. Thoi gian quan trong. Tich hop voi: ED, noi tiet, ICU.

---

### Q209. AI co the xu ly cac truong hop cap cuu nhiem trung khong?

**A.** Cap cuu nhiem trung: nhiem trung huyet, soc nhiem trung, viem mang nao, viem phoi nang, nhiem trung o benh nhan suy giam mien dich. Thoi gian quan trong. Tich hop voi: ED, benh truyen nhiem, ICU.

---

### Q210. Lam the nao de AI xu ly cac truong hop cap cuu than kinh?

**A.** Da duoc tra loi o Q177. Xem chi tiet o do.

---

### Q211. AI co the xu ly cac truong hop cap cuu tam than khong?

**A.** Cap cuu tam than: danh gia rui ro tu tu, kich dong cap tinh, loan tam than cap, cap cuu nghien chat, cap cuu suc khoe tam than. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q212. Lam the nao de AI xu ly cac truong hop cap cuu mat khong?

**A.** Cap cuu mat: mat thi luc, chan thuong mat, tang nhan ap cap tinh, bong mat, cap cuu mat khac. Chuyen biet. AI cung cap phan loai + gioi thieu chuyen khoa.

---

### Q213. AI co the xu ly cac truong hop cap cuu tai mui hong khong?

**A.** Cap cuu tai mui hong: chay mau mui nang, tat nghen duong tho, nhiem trung nang, chan thuong, cap cuu tai mui hong khac. Tich hop voi: ED, tai mui hong.

---

### Q214. Lam the nao de AI xu ly cac truong hop cap cuu rang mieng?

**A.** Cap cuu rang mieng: nhiem trung rang mieng nang, chan thuong ham mat, xuat huyet sau phau thuat, cap cuu rang mieng khac. Tich hop voi: ED, rang mieng.

---

### Q215. AI co the xu ly cac truong hop cap cuu da lieu khong?

**A.** Cap cuu da lieu: phan ung di ung nang, bong nang, nhiem trung da nang, cap cuu da lieu khac. Tich hop voi: ED, da lieu.

---

### Q216. Lam the nao de AI xu ly cac truong hop cap cuu co xuong khop khong?

**A.** Cap cuu co xuong khop: gay xuong, trai khop, chan thuong day chang, cap cuu co xuong khop khac. Tich hop voi: ED, chinh hinh.

---

### Q217. AI co the xu ly cac truong hop cap cuu mach mau khong?

**A.** Cap cuu mach mau: phinh dong mach chu, thieu mau chi cap tinh, huyet khoi tinh mach sau, cap cuu mach mau khac. Thoi gian quan trong. Tich hop voi: ED, phau thuat mach mau.

---

### Q218. Lam the nao de AI xu ly cac truong hop cap cuu ung thu?

**A.** Da duoc tra loi o Q178. Xem chi tiet o do.

---

### Q219. AI co the xu ly cac truong hop cap cuu ghep tang khong?

**A.** Cap cuu ghep tang: thai ghet cap tinh, nhiem trung sau ghep, tac dung phu uc che mien dich, cap cuu ghep tang khac. Chuyen biet. Tich hop voi: ghep tang, benh truyen nhiem, ICU.

---

### Q220. Lam the nao de AI xu ly cac truong hop cap cuu tram cam?

**A.** Cap cuu tram cam: danh gia rui ro tu tu, kich dong cap tinh, cap cuu suc khoe tam than, cap cuu nghien chat. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q221. AI co the xu ly cac truong hop cap cuu tre em khong?

**A.** Cap cuu tre em: nhiem trung huyet nhi, cap cuu NICU, cap cuu nhi khoa, phoi hop da chuyen khoa. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q222. Lam the nao de AI xu ly cac truong hop cap cuu nguoi cao tuoi?

**A.** Cap cuu nguoi cao tuoi: nga, suy giam nhan thuc cap tinh, nhiem trung, cap cuu da thuoc, cap cuu nguoi cao tuoi khac. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q223. AI co the xu ly cac truong hop cap cuu phu nu mang thai khong?

**A.** Cap cuu phu nu mang thai: tien san giat, xuat huyet, nhau bong non, cap cuu san khoa khac. Thoi gian quan trong. Tich hop voi: ED, san khoa, ICU.

---

### Q224. Lam the nao de AI xu ly cac truong hop cap cuu sau phau thuat?

**A.** Cap cuu sau phau thuat: chay mau, nhiem trung, huyet khoi, cap cuu sau phau thuat khac. Tich hop voi: phau thuat, ICU, ED.

---

### Q225. AI co the xu ly cac truong hop cap cuu ICU khong?

**A.** Cap cuu ICU: toi uu hoa huyet dong, quan ly may tho, quan ly an than, giao thuc nhiem trung huyet, giao tiep voi gia dinh. Bac si ICU: nguoi dung AI nang nhat. Thoi gian quan trong, quyet dinh rui ro cao.

---

### Q226. Lam the nao de AI xu ly cac truong hop cap cuu phong mo?

**A.** Cap cuu phong mo: danh gia truoc phau thuat, quan ly gay me, cap cuu trong phau thuat, cap cuu phong mo khac. Tich hop voi: phau thuat, gay me, ICU.

---

### Q227. AI co the xu ly cac truong hop cap cuu phong cap cuu khong?

**A.** Cap cuu phong cap cuu: phan loai, on dinh, cac giao thuc cap cuu, phoi hop da chuyen khoa, chuyen tiep. Bac si cap cuu: nguoi dung AI nang nhat. Thoi gian quan trong.

---

### Q228. Lam the nao de AI xu ly cac truong hop cap cuu phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q229. AI co the xu ly cac truong hop cap cuu phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q230. Lam the nao de AI xu ly cac truong hop cap cuu phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q231. AI co the xu ly cac truong hop cap cuu phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q232. Lam the nao de AI xu ly cac truong hop cap cuu phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q233. AI co the xu ly cac truong hop cap cuu phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q234. Lam the nao de AI xu ly cac truong hop cap cuu phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q235. AI co the xu ly cac truong hop cap cuu phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q236. Lam the nao de AI xu ly cac truong hop cap cuu phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q237. AI co the xu ly cac truong hop cap cuu phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q238. Lam the nao de AI xu ly cac truong hop cap cuu phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q239. AI co the xu ly cac truong hop cap cuu phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q240. Lam the nao de AI xu ly cac truong hop cap cuu phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q241. AI co the xu ly cac truong hop cap cuu phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q242. Lam the nao de AI xu ly cac truong hop cap cuu phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q243. AI co the xu ly cac truong hop cap cuu phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q244. Lam the nao de AI xu ly cac truong hop cap cuu phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q245. AI co the xu ly cac truong hop cap cuu phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q246. Lam the nao de AI xu ly cac truong hop cap cuu phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q247. AI co the xu ly cac truong hop cap cuu phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q248. Lam the nao de AI xu ly cac truong hop cap cuu phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q249. AI co the xu ly cac truong hop cap cuu phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q250. Lam the nao de AI xu ly cac truong hop cap cuu phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q251. AI co the xu ly cac truong hop cap cuu phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q252. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q253. AI co the xu ly cac truong hop cap cuu phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q254. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q255. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q256. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q257. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q258. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q259. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q260. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q261. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q262. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q263. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q264. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q265. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q266. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q267. AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q268. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q269. AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q270. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q271. AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q272. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q273. AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q274. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q275. AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q276. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q277. AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q278. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q279. AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q280. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q281. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q282. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q283. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q284. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q285. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q286. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q287. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q288. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q289. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q290. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q291. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q292. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q293. AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q294. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q295. AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q296. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q297. AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q298. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q299. AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q300. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q301. AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q302. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q303. AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q304. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q305. AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q306. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q307. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q308. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q309. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q310. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q311. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q312. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q313. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q314. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q315. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q316. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q317. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q318. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q319. AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q320. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q321. AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q322. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q323. AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q324. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q325. AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q326. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q327. AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q328. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q329. AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q330. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q331. AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q332. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q333. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q334. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q335. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q336. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q337. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q338. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q339. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q340. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q341. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q342. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q343. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q344. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q345. AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q346. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q347. AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q348. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q349. AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q350. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q351. AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q352. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q353. AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q354. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q355. AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q356. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q357. AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q358. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q359. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q360. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q361. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q362. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q363. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q364. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q365. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q366. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q367. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q368. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q369. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q370. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q371. AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q372. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q373. AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q374. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q375. AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q376. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q377. AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q378. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q379. AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q380. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q381. AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q382. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q383. AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q384. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q385. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q386. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q387. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q388. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q389. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q390. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q391. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q392. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q393. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q394. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q395. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q396. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q397. AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q398. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q399. AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q400. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q401. AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q402. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q403. AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q404. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q405. AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q406. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q407. AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q408. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q409. AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q410. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q411. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q412. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q413. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q414. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q415. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q416. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q417. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q418. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q419. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q420. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q421. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q422. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q423. AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q424. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q425. AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q426. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q427. AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q428. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q429. AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q430. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q431. AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q432. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q433. AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q434. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q435. AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q436. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q437. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q438. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q439. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q440. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q441. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q442. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q443. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q444. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q445. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q446. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q447. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q448. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q449. AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q450. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q451. AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q452. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q453. AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q454. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q455. AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q456. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q457. AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q458. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q459. AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q460. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q461. AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q462. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q463. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q464. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q465. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q466. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q467. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q468. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q469. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q470. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q471. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q472. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q473. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q474. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham rang mieng?

**A.** Cap cuu phong kham rang mieng: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham rang mieng, ED.

---

### Q475. AI co the xu ly cac truong hop cap cuu phong kham phong kham da lieu khong?

**A.** Cap cuu phong kham da lieu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da lieu, ED.

---

### Q476. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham co xuong khop?

**A.** Cap cuu phong kham co xuong khop: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham co xuong khop, ED.

---

### Q477. AI co the xu ly cac truong hop cap cuu phong kham phong kham mach mau khong?

**A.** Cap cuu phong kham mach mau: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham mach mau, ED.

---

### Q478. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ung thu?

**A.** Cap cuu phong kham ung thu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ung thu, ED.

---

### Q479. AI co the xu ly cac truong hop cap cuu phong kham phong kham ghep tang khong?

**A.** Cap cuu phong kham ghep tang: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham ghep tang, ED.

---

### Q480. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham tram cam?

**A.** Cap cuu phong kham tram cam: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q481. AI co the xu ly cac truong hop cap cuu phong kham phong kham tre em khong?

**A.** Cap cuu phong kham tre em: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q482. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham nguoi cao tuoi?

**A.** Cap cuu phong kham nguoi cao tuoi: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: cac can nhac lao khoa, muc tieu cham soc.

---

### Q483. AI co the xu ly cac truong hop cap cuu phong kham phong kham phu nu mang thai khong?

**A.** Cap cuu phong kham phu nu mang thai: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q484. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham sau phau thuat?

**A.** Cap cuu phong kham sau phau thuat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phau thuat, ED.

---

### Q485. AI co the xu ly cac truong hop cap cuu phong kham phong kham ICU khong?

**A.** Cap cuu phong kham ICU: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ICU, ED.

---

### Q486. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham phong mo?

**A.** Cap cuu phong kham phong mo: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham phong mo, ED.

---

### Q487. AI co the xu ly cac truong hop cap cuu phong kham phong kham phong cap cuu khong?

**A.** Cap cuu phong kham phong cap cuu: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Bac si cap cuu: nguoi dung AI nang nhat.

---

### Q488. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai tru?

**A.** Cap cuu phong kham ngoai tru: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai tru, ED.

---

### Q489. AI co the xu ly cac truong hop cap cuu phong kham phong kham tu nhan khong?

**A.** Cap cuu phong kham tu nhan: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tu nhan, ED.

---

### Q490. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham chuyen khoa?

**A.** Cap cuu phong kham chuyen khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham chuyen khoa, ED.

---

### Q491. AI co the xu ly cac truong hop cap cuu phong kham phong kham da khoa khong?

**A.** Cap cuu phong kham da khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham da khoa, ED.

---

### Q492. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham gia dinh?

**A.** Cap cuu phong kham gia dinh: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham gia dinh, ED.

---

### Q493. AI co the xu ly cac truong hop cap cuu phong kham phong kham noi khoa khong?

**A.** Cap cuu phong kham noi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham noi khoa, ED.

---

### Q494. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham ngoai khoa?

**A.** Cap cuu phong kham ngoai khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham ngoai khoa, ED.

---

### Q495. AI co the xu ly cac truong hop cap cuu phong kham phong kham nhi khoa khong?

**A.** Cap cuu phong kham nhi khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Dac biet quan trong: kiem tra can nang nghiem ngat, lieu luong bao thu.

---

### Q496. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham san khoa?

**A.** Cap cuu phong kham san khoa: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Thoi gian quan trong. Tich hop voi: phong kham san khoa, ED.

---

### Q497. AI co the xu ly cac truong hop cap cuu phong kham phong kham tam than khong?

**A.** Cap cuu phong kham tam than: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Nhan cam. Luon leo thang den chuyen gia suc khoe tam than.

---

### Q498. Lam the nao de AI xu ly cac truong hop cap cuu phong kham phong kham mat?

**A.** Cap cuu phong kham mat: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Chuyen biet. Tich hop voi: phong kham mat, ED.

---

### Q499. AI co the xu ly cac truong hop cap cuu phong kham phong kham tai mui hong khong?

**A.** Cap cuu phong kham tai mui hong: phan loai, on dinh, chuyen tiep, cac giao thuc cap cuu, phoi hop. Tich hop voi: phong kham tai mui hong, ED.

---

### Q500. Cau hoi cuoi cung: Dieu quan trong nhat can hieu ve AI nay la gi?

**A.** AI la ho tro quyet dinh, khong phai nguoi ra quyet dinh. Cac nguyen tac chinh: (1) Tang cuong, khong thay the - bac si van la nguoi chinh, AI ho tro suy nghi, quyet dinh cuoi cung la con nguoi. (2) Duoc can cu trich dan - moi khang dinh duoc trich dan, nguon co the xac minh, niem tin qua minh bach. (3) Tu choi khi khong chac chan - AI tu choi khi KB thieu du lieu, trung thuc ve han che, bao ton cho an toan. (4) Ban dia Singapore - tuan thu PDPA, phu hop HCSA, nhan thuc boi canh dia phuong, luu tru du lieu duoc dam bao. (5) ROI tich cuc - tiet kiem thoi gian dang ke, ket qua tot hon, chi phi hop ly, gia tri dai han. Ket luan: Duoc thuc hien dung, AI nay giup cac bac si gioi tro nen tot hon, nhanh hon va tu tin hon. Chung toi cam ket giup ban thuc hien dung.

---



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

