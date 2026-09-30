# Lesson 108: FPGA Power Optimization Techniques (電力最適化技術)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
FPGA มักจะกินไฟมากกว่า ASIC ดังนั้นการลด Power Consumption จึงเป็นสิ่งที่ Senior ต้องใส่ใจ
- **Dynamic Power vs Static Power:** Dynamic เกิดจากการสลับสถานะของ Transistor ($P = \alpha C V^2 f$) ส่วน Static (Leakage) เกิดจากกระแสรั่วไหล
- **Clock Gating:** เทคนิคหลักในการลด Dynamic Power โดยการตัด Clock ในส่วนของวงจรที่ไม่ได้ใช้งาน
- **Logic Overlap & Glitch Reduction:** การออกแบบ Data path ให้สมดุลกัน เพื่อลด Glitch (การสลับสถานะที่ไม่จำเป็น) ซึ่งทำให้กินไฟเพิ่ม

## 2. ทริคหน้างาน OJT (OJT Field Tricks)
- **Xilinx/Altera Power Estimator:** ก่อนเริ่มโปรเจกต์ อย่าลืมกรอก Excel Power Estimator เพื่อให้ทีม Hardware เตรียมวงจร Power Supply และ Heat Sink ได้ถูกต้อง
- **Avoid Async Resets if possible:** การใช้ Reset แบบอซิงโครนัสในบางสถาปัตยกรรมอาจเพิ่มทรัพยากร routing และใช้พลังงานมากกว่า การใช้ Synchronous Reset บางครั้งถูก Optimize ให้เข้าไปรวมกับ Control pin ของ DSP/BRAM ได้ดีกว่า

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **消費電力 (Shōhi denryoku):** Power consumption
- **静的電力 (Seiteki denryoku):** Static power / Leakage power
- **動的電力 (Dōteki denryoku):** Dynamic power
- **発熱 (Hatsunetsu):** Heat generation
- **クロックゲーティング (Kurokku gētingu):** Clock gating

## 4. ควิซท้ายบท (Quiz)
**Q1:** ถ้าต้องการลด Dynamic Power ในวงจรที่มีการทำงานเป็นพักๆ วิธีใดดีที่สุด?
**Answer:** การใช้ Clock Gating ควบคุมผ่าน Clock Enable (CE) เพื่อหยุดการสลับสถานะของ Flip-Flop ในจังหวะที่ไม่ได้คำนวณ
