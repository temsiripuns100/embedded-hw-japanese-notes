# Lesson 152: BRAM Timing, Pipelining, and Latency Optimization

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การใช้งาน BRAM ที่ความถี่สูง (High Fmax) จำเป็นต้องเข้าใจและใช้งาน Pipelining อย่างเหมาะสม BRAM มี Internal Output Register (DO_REG) ที่สามารถเปิดใช้งานได้ ซึ่งจะเพิ่ม Latency 1 cycle แต่ช่วยลด Clock-to-Out delay ได้อย่างมาก ทำให้ระบบโดยรวมสามารถทำงานที่ความถี่สูงขึ้นได้ การจัดการ Pipelining ที่ดีต้องพิจารณา Read Latency โดยรวมใน Data path เพื่อให้ Data alignment ยังคงถูกต้อง

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Pipeline Registers:** ถ้าทำ Timing closure ไม่ผ่านเนื่องจาก Critical path ยาวจาก BRAM output ให้เปิดใช้ BRAM internal register (DOA_REG / DOB_REG) ก่อนที่จะไปเพิ่ม register ภายนอก BRAM (Slice registers)
- **Retiming:** ระวังการตั้งค่า Retiming ใน Synthesizer บางครั้งมันไม่สามารถย้าย Register เข้าไปใน BRAM ได้เอง ต้องเขียน HDL ให้อยู่ในโครงสร้างที่ inferred BRAM register ได้อย่างถูกต้อง

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- レイテンシ (Reitenshi) - Latency
- パイプライン化 (Paipurain-ka) - Pipelining
- タイミング制約 (Taimingu seiyaku) - Timing constraint
- クリティカルパス (Kuritikaru pasu) - Critical path

## ควิซท้ายบท (Quiz)
**คำถาม:** การเปิดใช้งาน BRAM Internal Output Register ส่งผลต่อความถี่สูงสุด (Fmax) และ Latency อย่างไร?
**คำตอบ:** (เฉลย: ทำให้ Fmax สูงขึ้น แต่ Read Latency เพิ่มขึ้น 1 clock cycle)
