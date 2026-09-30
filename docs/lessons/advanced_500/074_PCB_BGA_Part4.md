# Lesson 074: BGA Signal Integrity & Crosstalk

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
สำหรับ High-Speed BGA (เช่น DDR4/5, PCIe Gen4/5) Signal Integrity (SI) เป็นเรื่องสำคัญที่สุด
- **Crosstalk**: สัญญาณที่วิ่งขนานกันออกจาก BGA จะเกิด Electromagnetic Coupling กัน ทำให้เกิด NEXT (Near-End Crosstalk) และ FEXT (Far-End Crosstalk) ต้องควบคุมระยะห่าง (Spacing) ให้เหมาะสม (เช่น กฎ 3W)
- **Return Path**: สัญญาณทุกเส้นต้องมี Return Path ที่ต่อเนื่อง หากมีการเปลี่ยนชั้น (Layer transition) ผ่าน Via ต้องวาง Ground Transfer Via (Stitching Via) ไว้ใกล้ๆ เสมอ เพื่อไม่ให้ Return Current ต้องอ้อมไกล ซึ่งจะเพิ่ม Loop Area และ EMI

## ทริคหน้างาน OJT (OJT Field Tricks)
- เวลาทำ Length Matching สำหรับ High-speed bus (เช่น DDR) ต้องนับความยาวรวมถึงความยาวของขา BGA ภายในตัวแพ็กเกจ (Package Length) ที่ผู้ผลิตระบุใน IBIS model ด้วย ไม่ใช่แค่บน PCB อย่างเดียว
- ระวัง "Swiss Cheese Effect" ที่เกิดจากการเจาะ Via ถี่ๆ ใต้ BGA ซึ่งจะเจาะทำลาย Reference Plane ทำให้ Return Path ขาดตอน (Plane split)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **クロストーク (Kurosutōku)** - Crosstalk
- **リターンパス (Ritān pasu)** - Return Path
- **等長配線 (Tōchō haisen)** - Length Matching
- **インピーダンス整合 (Inpīdansu seigō)** - Impedance Matching
- **層間移動 (Sōkan idō)** - Layer Transition

## ควิซท้ายบท (Quiz)
**คำถาม:** "Swiss Cheese Effect" บริเวณใต้ BGA ส่งผลเสียต่อสัญญาณ High-speed อย่างไร?
<details>
<summary>ดูเฉลย</summary>
**คำตอบ:** การมีรู Via จำนวนมากทำให้ Reference Plane ถูกตัดขาด (Anti-pads ซ้อนทับกัน) ทำให้ Return Path ไม่ต่อเนื่อง เพิ่ม Impedance ชั่วขณะ และทำให้เกิดปัญหา Signal Integrity และ EMI
</details>
