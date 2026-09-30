# FPGA PLL Deep Dive - Part 5: Advanced PLL Debugging and Troubleshooting

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
เมื่อ PLL ไม่ยอม Lock (Unlock Condition) สาเหตุมักไม่ได้มาจาก Logic ภายใน แต่มาจาก Physical Environment
**Phase Noise/Jitter Analysis** เบื้องต้นต้องใช้ Spectrum Analyzer หรือ Oscilloscope ระดับ High-End (Real-Time Oscilloscope > 10GHz) วิเคราะห์ Time Interval Error (TIE)
- **Spurious Emissions**: ถ้าพบ Peak ความถี่แปลกๆ รอบๆ Clock Carrier มักเกิดจาก Power Supply Switching Frequency รบกวน หรือ Coupling จากสายสัญญาณข้างเคียง (Crosstalk)
- **Fractional-N PLL**: ใน FPGA รุ่นใหม่มี Fractional-N ช่วยให้หารความถี่แบบทศนิยมได้ แต่แลกมาด้วย Fractional Spurs (Jitter เพิ่ม) วงจร Sigma-Delta Modulator (SDM) ภายในใช้เทคนิค Noise Shaping ดัน Noise ไปยังย่านความถี่สูง ซึ่ง Loop Filter ต้องตัดทิ้งให้หมด

## 2. ทริคหน้างาน OJT (現場のOJTテクニック)
- **SignalTap / ILA Debugging**: อย่าพยายาม Sample สัญญาณ Clock ด้วย Logic Analyzer ภายใน (SignalTap/ILA) เพราะมันใช้ Clock อื่นในการ Sample (Over-sampling) ค่าที่ได้จะไม่แม่นยำ ควรต่อขา Clock ออกมาที่ขา FPGA (Clock Output Pin) แล้ววัดด้วย Scope นอกเสมอ
- **Loss of Lock (LOL) Interrupt**: อย่ารีเซ็ต State Machine ทันทีที่ PLL Lock ตกแค่ 1 Clock Cycle (Glitch) ควรใส่ Counter หน่วงเวลา (Debounce) สัก 10-100 Cycles ก่อนตัดสินใจว่า PLL ร่วงจริงๆ
- **Lock Signal Polarity**: ตรวจสอบ Datasheet ให้ดี บางเบอร์ Active Low บางเบอร์ Active High ถ่ายทอดประสบการณ์: "เสียเวลาแก้ RTL ไป 3 วัน สุดท้ายพบว่าต่อ Lock Signal กลับหัว (論理反転) !!"

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用語)
- **不具合解析 (ふぐあいかいせき, Fuguai Kaiseki)**: Troubleshooting / Failure Analysis
- **論理反転 (ろんりはんてん, Ronri Hanten)**: Logic Inversion (กลับขั้ว)
- **チャタリング防止 (ちゃたりんぐぼうし, Chataringu Boushi)**: Debouncing (ป้องกันสัญญาณสวิง)
- **ノイズ除去 (のいずじょきょ, Noizu Jokyo)**: Noise Removal / Filtering
- **実機検証 (じっきけんしょう, Jikki Kenshou)**: On-board Verification / Hardware Testing

## 4. ควิซท้ายบท (理解度チェック)
**Q5:** วิธีที่ถูกต้องที่สุดในการวัดคุณภาพสัญญาณ Clock จาก PLL ภายใน FPGA คืออะไร?
A) ใช้ SignalTap II (Logic Analyzer ภายใน) จับสัญญาณ Clock
B) ดูสถานะจากสัญญาณ LOCK
C) นำสัญญาณ Clock ออกทางขา IO เฉพาะ (Dedicated Clock Out) และวัดด้วย Oscilloscope
D) รัน Simulation ระดับ Gate-Level

*เฉลย:* C) นำสัญญาณออกไปวัดด้วยเครื่องมือภายนอก (オシロスコープで測定) เพื่อดู Analog Characteristic (Jitter, Duty Cycle, Rise/Fall time) ที่ Logic Analyzer ภายในมองไม่เห็น
