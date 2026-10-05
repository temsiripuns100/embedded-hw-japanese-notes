# Lesson 106: Advanced Clock Domain Crossing (CDC) (クロックドメイン交差)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในการออกแบบระบบ FPGA ที่มีความซับซ้อนสูง มักจะมีหลาย Clock Domain การส่งข้อมูลข้าม Domain (CDC) โดยไม่ใช้เทคนิคที่ถูกต้องจะนำไปสู่ปัญหา Metastability
- **MTBF (Mean Time Between Failures):** การคำนวณ MTBF เพื่อประเมินความน่าจะเป็นที่ Flip-Flop จะหลุดจากสภาวะ Metastable ก่อนถึง Clock edge ถัดไป
- **Synchronizer Design:** การใช้ 2-stage หรือ 3-stage synchronizer สำหรับ Single-bit signal
- **Multi-bit CDC:** การใช้ Async FIFO (พร้อม Gray code pointer) หรือ Handshake protocols สำหรับ Data bus เพื่อป้องกัน Data incoherency

## 2. ทริคหน้างาน OJT (OJT Field Tricks)
- **False Path & Clock Groups:** ในการเขียน Constraint (SDC) อย่าลืมตั้ง `set_clock_groups -asynchronous` หรือ `set_false_path` ระหว่าง Clock ที่ไม่เกี่ยวข้องกัน เพื่อลดภาระของ Timing Analyzer และลดเวลาในการ Compile
- **CDC Analysis Tools:** หน้างานจริง Senior มักจะไม่พึ่งแค่ Simulation แต่จะใช้ Linting / CDC Tools เฉพาะทาง (เช่น SpyGlass CDC) เพื่อจับบั๊กที่อาจเกิดในระดับ Silicon

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **非同期 (Hidōki):** Asynchronous (อซิงโครนัส)
- **メタスタビリティ (Metasutabiriti):** Metastability
- **タイミング違反 (Taimingu ihan):** Timing violation
- **同期化回路 (Dōkika kairo):** Synchronizer circuit
- **誤動作 (Godosah):** Malfunction

## 4. ควิซท้ายบท (Quiz)
**Q1:** ทำไมถึงห้ามใช้ 2-stage synchronizer กับสัญญาณที่เป็น Bus ข้อมูล (Multi-bit)?
**Answer:** เพราะแต่ละบิตอาจใช้เวลาออกจาก Metastability ไม่เท่ากัน ทำให้เกิดการอ่านค่าผิดพลาด (Data incoherency) ควรใช้ Async FIFO หรือ Handshake แทน
