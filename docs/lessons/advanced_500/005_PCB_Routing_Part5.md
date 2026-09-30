# 005 PCB Routing Part 5: 3W Rule & Crosstalk Prevention (3Wルールとクロストーク対策)

## ทฤษฎีวิศวกรรมเชิงลึก (In-Depth Engineering Theory)
Crosstalk เกิดจากการรบกวนทางแม่เหล็กไฟฟ้า (Electromagnetic Coupling) ระหว่างสายสัญญาณที่อยู่ใกล้กัน แบ่งเป็น Capacitive (Electric field) และ Inductive (Magnetic field) coupling
- **NEXT (Near-End Crosstalk) & FEXT (Far-End Crosstalk)**: NEXT สังเกตเห็นได้ที่ฝั่งต้นทางของ Victim line, FEXT เห็นที่ปลายทาง (FEXT มักเป็น 0 ใน Stripline แบบ Homogeneous)
- **3W Rule**: กฎที่ว่าระยะห่างระหว่างศูนย์กลางของ Trace ทั้งสองต้องห่างกันอย่างน้อย 3 เท่าของความกว้าง Trace (Width) เพื่อลด Crosstalk ลงเหลือประมาณ 30% (หรือ -70dB)
- **20H Rule**: การหด Power plane เข้ามาด้านในจากขอบ GND plane เท่ากับ 20 เท่าของระยะห่างระหว่างชั้น (H) เพื่อลด Fringing field ที่แผ่ออกขอบบอร์ด

## ทริคหน้างาน OJT (On-the-Job Tricks)
- **ใช้ Stripline**: การวางสายสัญญาณที่ไวต่อการรบกวนไว้ในชั้นใน (Inner layers) ระหว่าง GND Planes (Stripline) ช่วยป้องกัน Crosstalk ได้ดีกว่า Microstrip อย่างมาก
- **Orthogonal Routing**: หากต้องเดินสายสัญญาณความถี่สูงในเลเยอร์ที่ติดกัน (เช่น L3 และ L4) ให้เดินสายในแนวตั้งฉากกัน (Orthogonal) เพื่อลด Coupling Area
- **Guard Traces**: ในทางปฏิบัติ ไม่ค่อยแนะนำให้ใช้ Guard Trace เปล่าๆ ยกเว้นแต่จะมีการเย็บ Via (Stitching Vias) ลง GND อย่างถี่พอ มิฉะนั้น Guard Trace อาจกลายเป็นสายอากาศ (Antenna) เสียเอง

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **クロストーク (Kurosutōku)**: Crosstalk
- **層間クロストーク (Sōkan Kurosutōku)**: Inter-layer crosstalk
- **直交配線 (Chokkō Haisen)**: Orthogonal routing
- **ガードパターンのビア打ち (Gādo Patān no Bia Uchi)**: Via stitching on guard traces
- **沿面距離 / 離隔 (Enmen Kyori / Rikaku)**: Clearance / Separation distance

## ควิซท้ายบท (Quiz)
**คำถาม:** หากเลเยอร์สัญญาณสองชั้นอยู่ติดกัน (Adjacent signal layers) ควรวางแนวการเดินสายอย่างไรเพื่อลด Crosstalk ให้เหลือน้อยที่สุด?
1. เดินขนานกัน (Parallel) ให้เป็นระเบียบ
2. เดินทำมุม 45 องศาต่อกัน
3. เดินทำมุมตั้งฉากกัน (Orthogonal / 90 องศา)
**เฉลย:** ข้อ 3
