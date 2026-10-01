# Advanced PCB Stackup - Part 5: Design for Manufacturability (DFM) & Cost vs Yield (Senior Level)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในมุมมองของ Senior Engineer การออกแบบ Stackup ที่ดีเลิศแต่ผลิตไม่ได้ หรือ Yield ต่ำ คือความล้มเหลว
- **Symmetrical Stackup:** โครงสร้างของ PCB ควรจะสมมาตร (Symmetrical) รอบจุดศูนย์กลางแกน Z เสมอ ทั้งชนิดของวัสดุ (Core/Prepreg), ความหนา, และปริมาณทองแดง (Copper weight) หาก Stackup ไม่สมมาตร เมื่อผ่านเตาอบ (Reflow) ที่อุณหภูมิสูง จะเกิดแรงเค้น (Thermal stress) ทำให้บอร์ดโก่ง (Bow and Twist) ซึ่งมีผลทำให้ SMT เครื่องจักรวางอุปกรณ์ผิดพลาด
- **Sequential Build-Up (SBU):** เทคโนโลยี HDI (High Density Interconnect) ที่ใช้ Microvia จะต้องผ่านการอัด (Lamination) หลายรอบ (เช่น 2-N-2 หมายถึงอัด Core กลาง 1 รอบ แล้วเพิ่ม Layer นอกอัดอีก 2 รอบ) ยิ่งอัดหลายรอบ ราคาจะก้าวกระโดดแบบทวีคูณ และเกิดความเสี่ยงเรื่อง Misregistration

## 2. ทริคหน้างาน OJT (Field Tricks)
- **OJT Trick 1:** หลีกเลี่ยงการใช้ Prepreg ชนิดที่มี Resin ต่ำหรือบางเกินไป อัดระหว่างชั้นที่มีลายทองแดงหนาๆ หรือมีพื้นที่ว่างมาก (Resin starvation) เพราะ Resin จะไหลไปเติมเต็มช่องว่างไม่พอ เกิดเป็นฟองอากาศ (Delamination) แนะนำให้ปรึกษา Field Application Engineer (FAE) ของโรงงานผู้ผลิตแผ่นเพื่อคำนวณ Resin volume
- **OJT Trick 2:** ถ้าไม่จำเป็นจริงๆ อย่าใช้ Stack-via (เจาะ Microvia ทับกันตรงๆ บนแกนเดียวกัน) โรงงานเกลียดมากเพราะทำยากและหลุดร่อนง่าย ให้พยายามใช้ Staggered-via (เจาะเหลื่อมกัน) จะผลิตง่ายกว่าและ Yield สูงกว่า

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **対称性 (Taishōsei):** Symmetry (ความสมมาตร)
- **反り / ねじれ (Sori / Nejire):** Bow and Twist (การโก่งและบิดตัวของบอร์ด)
- **製造性考慮設計 (Seizōsei kōryo sekkei):** Design for Manufacturability (DFM)
- **歩留まり (Budomari):** Yield (อัตราของเสีย/ดี ในการผลิต)
- **層間剥離 (Sōkan hakuri):** Delamination
- **スタックビア / スタガードビア (Sutakku bia / Sutagādo bia):** Stacked via / Staggered via

**ตัวอย่างประโยคตรวจแบบ:**
"層構成がZ軸に対して非対称になっています。リフロー時に基板の反り（Bow and Twist）が発生する恐れがあるので、対称な構成に見直してください。" 
(โครงสร้างชั้นไม่สมมาตรเทียบกับแกน Z อาจทำให้เกิดบอร์ดโก่งตัวระหว่างการทำ Reflow ได้ กรุณาทบทวนให้เป็นโครงสร้างสมมาตรครับ)

## 4. ควิซท้ายบท (Quiz)
**Q1:** โครงสร้าง HDI แบบ 1-N-1 เทียบกับ 2-N-2 ข้อใดมีความเสี่ยงในการเกิด Misregistration (การเหลื่อมกันของชั้น) มากกว่ากัน และเพราะเหตุใด?
A) 1-N-1 เสี่ยงกว่า เพราะแผ่นบางกว่า
B) 2-N-2 เสี่ยงกว่า เพราะต้องผ่านกระบวนการ Lamination (การอัด) มากครั้งกว่า
C) ทั้งสองแบบมีความเสี่ยงเท่ากัน หากใช้เครื่องจักรเดียวกัน
*(เฉลย: B) 2-N-2 ต้องทำ Lamination cycles มากกว่า ทุกครั้งที่มีการอัดความร้อน วัสดุจะมีการยืดหดตัว ทำให้ความคลาดเคลื่อนสะสม (Cumulative tolerance) เพิ่มขึ้น)*
