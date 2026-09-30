# FPGA & VHDL Part 10: Hardware Debugging & Logic Analyzer

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
แม้จะทำ Simulation มาอย่างดี แต่เมื่อลงบอร์ดจริง (Hardware) อาจเจอปัญหาที่ Simulation มองไม่เห็น
- การดีบักในระบบจริงทำได้โดยใช้ **In-System Logic Analyzer** (เช่น ILA ของ Xilinx, SignalTap ของ Intel)
- เครื่องมือนี้จะฝังลอจิกสำหรับดักจับสัญญาณ (Probe) เข้าไปในดีไซน์หลัก และใช้ BRAM (Block RAM) ในตัว FPGA เพื่อเก็บข้อมูล (Trace Data) แล้วส่งกลับมาแสดงผลที่ PC ผ่าน JTAG

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Trade-offs:** การใส่ ILA จะกินทรัพยากร BRAM เยอะมาก และอาจทำให้เกิด **Routing Congestion** ส่งผลให้ Timing พังได้ (ดีไซน์เดิมผ่าน แต่พอใส่ ILA แล้ว Setup Violation)
- ควรเลือก Probe เฉพาะสัญญาณที่จำเป็น และพยายาม Probe สัญญาณที่ออกมาจาก Register (Registered Signal) มากกว่าสัญญาณที่เป็น Combinational Logic เปล่าๆ เพื่อลดผลกระทบต่อ Timing
- **ห้ามลืม:** ก่อนทำ Release Build หรือส่งมอบ (Mass Production) ต้องเอา ILA Core ออกเสมอ!

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **実機検証 (Jikki kenshou)** - Real hardware verification (การตรวจสอบการทำงานบนฮาร์ดแวร์จริง)
- **波形 (Hakei)** - Waveform (รูปคลื่นสัญญาณ)
- **トリガー条件 (Torigā jouken)** - Trigger condition (เงื่อนไขการทริกเกอร์ให้เริ่มบันทึก)
- **リソース枯渇 (Risōsu kokatsu)** - Resource depletion / routing congestion (ทรัพยากรหมด / การเดินสายหนาแน่นเกินไป)

## ควิซท้ายบท (Quiz)
**Q:** ข้อเสียหรือความเสี่ยงที่ใหญ่ที่สุดในการใส่ Logic Analyzer (เช่น ILA/SignalTap) เข้าไปในดีไซน์ FPGA คืออะไร?
**A:** มันจะใช้ทรัพยากรภายใน เช่น BRAM และ Logic จำนวนมาก ซึ่งอาจนำไปสู่ปัญหา Routing Congestion และทำให้ Timing ของระบบเดิมล้มเหลว (Timing Violation) ได้
