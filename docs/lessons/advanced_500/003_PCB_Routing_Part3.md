# 003 PCB Routing Part 3: BGA Escape Routing (BGA引き出し配線)

## ทฤษฎีวิศวกรรมเชิงลึก (In-Depth Engineering Theory)
BGA (Ball Grid Array) ที่มี Pitch ต่ำ (เช่น < 0.8mm) เป็นความท้าทายหลักในการออกแบบ PCB แบบ High-Density Interconnect (HDI)
- **Dogbone vs. Via-in-Pad**: 
  - *Dogbone*: ใช้กับ Pitch ใหญ่ (> 0.8mm) โดยเดิน Trace สั้นๆ ออกจาก Pad แล้วลง Via
  - *Via-in-Pad (VIP)*: ต้องใช้ใน Fine Pitch BGA ข้อดีคือลด Parasitic Inductance แต่ต้องใช้กระบวนการ Tented, Capped หรือ Plated over (POFV) เพื่อป้องกันตะกั่วไหลลง Via (Solder Wicking)
- **Layer Stackup Strategy**: การวางแผนจำนวนเลเยอร์ที่จำเป็นต้องใช้ กฎพื้นฐานคือ จำนวน Routing Layers = จำนวน BGA Rows / 2 (โดยประมาณ ขึ้นอยู่กับ Design Rules)

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **วางแผน Fanout ล่วงหน้า**: เริ่มจากการกำหนด Fanout pattern (เช่น Quadrant routing แบ่งเป็น 4 ทิศทาง) เพื่อไม่ให้เส้นทางบล็อกกันเอง
- **Pin Swapping**: ทำงานร่วมกับ Firmware/FPGA Engineer เพื่อทำ Pin swapping ในกลุ่มสัญญาณที่สลับได้ (เช่น GPIO, Data bus บางประเภท) ช่วยลดการตัดกันของสาย (Crossover) และลดจำนวนเลเยอร์ได้มาก
- **Ground/Power Vias**: แชร์ Via สำหรับ GND/PWR ให้มากที่สุด (หากยอมรับ Parasitics ได้) เพื่อเปิดพื้นที่ให้สัญญาณ

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **引き出し配線 (Hikidashi Haisen)**: Escape routing / Fanout
- **パッド・オン・ビア (Paddo-on-Bia)**: Via-in-Pad
- **ドッグボーン (Doggubōn)**: Dogbone routing
- **多層基板 (Tasō Kiban)**: Multilayer PCB
- **ピンアサイン変更 (Pin Asain Henkō)**: Pin assignment change / Pin swapping

## ควิซท้ายบท (Quiz)
**คำถาม:** ปัญหาหลักที่ต้องระวังหากใช้เทคนิค Via-in-Pad โดยไม่ผ่านการอุด (Capping/Plugging) คืออะไร?
1. Crosstalk สูงขึ้น
2. น้ำยาบัดกรี (Solder paste) ไหลลงรู Via ทำให้เกิดจุดบัดกรีที่ไม่สมบูรณ์ (Solder Wicking / Void)
3. สัญญาณขาดหายในความถี่ต่ำ
**เฉลย:** ข้อ 2
