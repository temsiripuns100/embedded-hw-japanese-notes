# บทที่ 16: High-Speed Signal Integrity & Controlled Impedance in Complex Stackups (การควบคุม Impedance และ SI ในระดับสูง)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
ในระดับ Senior Engineer, การควบคุม Impedance ไม่ใช่แค่การคำนวณผ่านโปรแกรม (เช่น Polar SI9000) แต่ต้องเข้าใจถึง **Differential Insertion Loss**, **Return Loss** และพฤติกรรมของ **Glass Weave Effect** (Fiber Weave Effect) ที่ส่งผลต่อ Skew ในสัญญาณความเร็วสูง (เช่น PCIe Gen 4/5, PAM4 56G/112G)
การออกแบบ Stackup ต้องคำนึงถึง:
- **Resin Starvation**: ปัญหาปริมาณเรซินไม่พอเติมเต็มช่องว่างระหว่างทองแดงในชั้นที่มีความหนาแน่นสูง
- **Surface Roughness**: ความขรุขระของผิวทองแดง (Copper Foil Profiling) เช่น RTF, VLP, HVLP ที่มีผลโดยตรงต่อ Skin Effect Loss ในระดับ GHz

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick #1**: อย่าเชื่อสเปกวัสดุจาก Datasheet 100% ในช่วงความถี่สูง Dk/Df จะเปลี่ยนไป ให้ขอข้อมูลแบบ Broadband (เช่น ข้อมูล S-parameters จากผู้ผลิตวัสดุ) เสมอ
- **OJT Trick #2**: หากทำ Stackup แบบ Asymmetrical (ไม่สมมาตร) จะทำให้เกิดบอร์ดโก่ง (Warpage) หลังผ่านกระบวนการ Reflow ให้พยายามบาลานซ์ Copper Density ในเลเยอร์ที่สมมาตรกันให้มากที่สุด

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **インピーダンス整合 (Impiidansu Seigou)**: Impedance Matching (การแมทช์อิมพีแดนซ์)
- **表皮効果 (Hyōhi Kōka)**: Skin Effect (ปรากฏการณ์สกินเอฟเฟกต์)
- **反り (Sori)**: Warpage / Bow and Twist (การโก่งงอของบอร์ด)
- **銅箔粗さ (Dōhaku Arasa)**: Copper Foil Roughness (ความขรุขระของฟอยล์ทองแดง)
- **ガラス編組 (Garasu Henso)**: Glass Weave (โครงสร้างการทอใยแก้ว)

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: ปัญหาใดที่มักเกิดขึ้นเมื่อใช้ทองแดงแบบ HTE (High Temperature Elongation) ทั่วไปแทน HVLP ในงานออกแบบ 28 Gbps ขึ้นไป?
1. บอร์ดโก่งงอง่ายกว่าปกติ
2. Signal Attenuation (Insertion Loss) สูงขึ้นอย่างมากเนื่องจาก Skin Effect
3. ค่า Dk ของวัสดุพิมพ์จะเปลี่ยนแปลงอย่างรวดเร็ว
4. ทำให้เกิด Microvia crack ได้ง่าย

*เฉลย: 2. Signal Attenuation สูงขึ้นอย่างมากเนื่องจาก Skin Effect (ความขรุขระทำให้ระยะทางเดินของกระแสที่ผิวไกลขึ้น เพิ่ม Loss อย่างมีนัยสำคัญ)*
