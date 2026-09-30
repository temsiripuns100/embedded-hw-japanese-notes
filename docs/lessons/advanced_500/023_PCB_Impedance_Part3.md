# Lesson 23: Differential Pair Routing & Return Path (差動配線とリターンパス)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
สัญญาณ High-speed ส่วนใหญ่ใช้การส่งแบบ **Differential Pair (差動ペア)** (เช่น 90Ω สำหรับ USB, 100Ω สำหรับ Ethernet/PCIe)
Differential Impedance ($Z_{diff}$) ไม่ได้ขึ้นอยู่กับความกว้างของเส้นเพียงอย่างเดียว แต่ต้องคำนึงถึง **ระยะห่าง (Spacing/Coupling)** ระหว่างคู่สายด้วย
กฎเหล็กที่สำคัญที่สุดของ High-speed คือ **Return Path (リターンパス)**: กระแสไหลไปทางไหน ต้องมีทางกลับที่สั้นที่สุดเสมอ ในความถี่สูง Return Path จะไหลอยู่บน Reference Plane (GND) ที่อยู่ติดกับเส้นสัญญาณเป๊ะๆ (Directly beneath the trace)
หาก Reference Plane ขาด (Split Plane) หรือมีรอยแยก (Gap) จะทำให้ Return Path ต้องอ้อม Impedance จะกระโดด (Impedance discontinuity) เกิด EMI และ Crosstalk ทันที

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Length Matching:** ความยาวของเส้น P และ N ใน Diff Pair ต้องเท่ากัน (Delay skew < 5ps หรือระยะห่าง < 15 mil)
- **Phase Matching:** เวลาแกะลายผ่านโค้ง ให้ทำ Length Match ให้ใกล้จุดที่เลี้ยวมากที่สุด (Uncoupled length ต้องน้อยที่สุด)
- **Ground Void:** ห้ามเดินเส้นสัญญาณข้ามรอยแตกของ GND Plane เด็ดขาด (スプリット跨ぎ禁止 - Split matagi kinshi) ถ้าเลี่ยงไม่ได้ ต้องใส่ Stitching Capacitor เชื่อม Plane ทั้งสอง

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **差動インピーダンス (Sadou Inpiidansu):** Differential Impedance
- **等長配線 (Touchou Haisen):** Length Matching / Tuning
- **リターンパス (Ritaan Pasu):** Return Path
- **ベタ抜け (Beta Nuke) / スプリット (Supuritto):** Split plane / Void in copper
- **跨ぎ配線 (Matagi Haisen):** Routing across a split plane (พฤติกรรมต้องห้าม)

## ควิซท้ายบท (End of Chapter Quiz)
**Q:** หากจำเป็นต้องเดินเส้นสัญญาณความถี่สูงข้ามรอยแยกของ Power Plane สิ่งที่ควรทำคืออะไร?
1. ปรับเส้นสัญญาณให้ใหญ่ขึ้น
2. เพิ่ม Stitching Capacitor คล่อมรอยแยกใกล้กับเส้นสัญญาณ
3. ลบ Plane ทิ้งไปเลย

*เฉลย: 2*
