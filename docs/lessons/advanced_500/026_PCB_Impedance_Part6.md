# Lesson 026: PCB Impedance Part 6 - Microstrip vs. Stripline in GHz Range

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
เมื่อความถี่สัญญาณเข้าสู่ระดับ GHz พฤติกรรมของ Microstrip และ Stripline จะมีความแตกต่างกันอย่างชัดเจน Microstrip จะเกิด Dispersion ได้ง่ายกว่าเนื่องจากสนามแม่เหล็กไฟฟ้า (EM field) เดินทางผ่านสองตัวกลาง (FR4 และอากาศ) ที่มี Dielectric constant ($\epsilon_r$) ต่างกัน ทำให้ความเร็วคลื่นเปลี่ยนไปตามความถี่ (Phase velocity) ในขณะที่ Stripline ซึ่งถูกหุ้มด้วย Dielectric ชนิดเดียวกันทั้งหมด (Homogeneous) จะมี Dispersion ต่ำกว่ามาก แต่ Stripline ก็จะเผชิญกับ Dielectric loss (Loss tangent) ที่สูงกว่า และมีความยากในการผลิตมากกว่า

## 2. ทริคหน้างาน OJT (On-the-Job Training Tips)
- **Senior Tip:** ถ้าต้องลากสายสัญญาณระดับ 10 Gbps ขึ้นไป (เช่น PCIe Gen4/5) ควรพยายามใช้ Stripline (inner layer) ให้มากที่สุดเพื่อลด EMI และ Forward Crosstalk (FEXT) 
- ข้อควรระวัง: Stripline ต้องใช้ Via ในการเข้าถึง ซึ่ง Via stub จะทำให้เกิด Impedance discontinuity ดังนั้นต้องทำ Backdrill เสมอถ้าชั้นที่ลงไปไม่ลึกพอ!

## 3. คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **ストリップライン (Sutorippurain):** Stripline (สายสัญญาณที่อยู่ชั้นใน)
- **マイクロストリップ (Maikurosutorippu):** Microstrip (สายสัญญาณชั้นนอก)
- **誘電正接 (Yūden seisetsu):** Loss Tangent (ค่าความสูญเสียใน Dielectric)
- **表皮効果 (Hyōki kōka):** Skin Effect (สัญญาณวิ่งแค่ผิวทองแดงที่ความถี่สูง)
- **ばらつき (Baratsuki):** Variation/Tolerance (ความคลาดเคลื่อน)

## 4. ควิซท้ายบท (End-of-chapter Quiz)
**Q:** สาเหตุหลักที่ทำให้ Microstrip มี Forward Crosstalk สูงกว่า Stripline คืออะไร?
**A:** การที่ EM Field ของ Microstrip กระจายอยู่ใน 2 ตัวกลาง (อากาศและ Dielectric) ทำให้ Even mode และ Odd mode มีความเร็ว (Propagation delay) ไม่เท่ากัน เกิดเป็น FEXT ในขณะที่ Stripline อยู่ในตัวกลางเดียวกัน ความเร็วทั้งสองโหมดจึงเท่ากัน ทำให้ FEXT หักล้างกันไปเกือบหมด
