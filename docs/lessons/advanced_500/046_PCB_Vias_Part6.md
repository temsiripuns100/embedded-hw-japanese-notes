# Lesson 046: PCB Vias Part 6 - High-Speed Signal Integrity & Vias

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
เมื่อสัญญาณความถี่สูงผ่าน Via จะเกิดการเปลี่ยนแปลงของ Impedance (Impedance Discontinuity) เนื่องจาก Via มีโครงสร้างแบบ 3 มิติที่มีทั้ง Parasitic Capacitance ระหว่าง Pad กับ Anti-pad บน Layer อื่นๆ และ Parasitic Inductance จากความยาวของกระบอก Via เอง การออกแบบระดับ High-speed (เช่น PCIe Gen4/5, 112G PAM4) ต้องคำนวณขนาดของ Anti-pad และ Pad ให้เหมาะสมเพื่อชดเชย Capacitance ให้ Impedance ใกล้เคียงกับ 50 หรือ 100 Ohms มากที่สุด

## ทริคหน้างาน OJT (On-the-Job Training)
ถ้าเจอปัญหา TDR (Time Domain Reflectometry) กราฟตก (Capacitive dip) ตรงตำแหน่ง Via ให้ลองขยายขนาด Anti-pad ใน Plane layer ที่ไม่ได้เชื่อมต่อ เพื่อลด Parasitic C ลง

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **インピーダンス整合 (Impedance Seigou):** การแมตช์อิมพีแดนซ์ (Impedance Matching)
- **寄生容量 (Kisei Youryou):** Parasitic Capacitance
- **アンチパッド (Anchi-paddo):** Anti-pad

## ควิซท้ายบท
Q: หาก TDR แสดงกราฟ impedance ตกที่ตำแหน่ง via ควรแก้ปัญหาเบื้องต้นอย่างไร?
A: ขยายขนาด Anti-pad เพื่อลด Parasitic Capacitance
