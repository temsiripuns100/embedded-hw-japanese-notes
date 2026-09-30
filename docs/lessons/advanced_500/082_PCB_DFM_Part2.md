# บทที่ 82: PCB DFM Part 2 - การออกแบบลายวงจรและอิมพีแดนซ์ (Traces & Impedance Control)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
การออกแบบ Track width และ Clearance ต้องอ้างอิงความสามารถของผู้ผลิต (Manufacturer's capability) เช่น 3/3 mil หรือ 4/4 mil สำหรับบอร์ด HDI 
การควบคุมอิมพีแดนซ์ (Impedance Control) เช่น 50 Ohm Single-ended หรือ 90/100 Ohm Differential pair จำเป็นต้องกำหนด Stackup ให้ชัดเจน (Prepreg/Core thickness) เพื่อให้ผู้ผลิตสามารถชดเชย (Compensate) ลายเส้นตอนกัดกรด (Etching) ได้ เนื่องจากกระบวนการ Etching มักเกิดปัญหา Trapezoidal trace (ฐานกว้างกว่ายอด)

## ทริคหน้างาน OJT (OJT Tricks)
- อย่าลืมเผื่อ Copper Thieving หรือ Pouring Copper ในพื้นที่ว่าง เพื่อให้ความหนาแน่นของทองแดง (Copper density) สม่ำเสมอทั้งเลเยอร์ ป้องกันปัญหาบอร์ดโก่งตัว (Warpage) ระหว่างอบหรือ Reflow
- เมื่อกำหนด Impedance ใน Fabrication Note ให้ระบุว่า "Target Impedance with +/- 10% tolerance" และให้ทางโรงงานปรับค่า Track width เล็กน้อยเพื่อให้ได้ตามสเปค

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **配線幅 (Haisen Haba):** Track width (ความกว้างลายวงจร)
- **線間隔 (Sen Kankaku):** Clearance / Spacing (ระยะห่างลายวงจร)
- **インピーダンス整合 (Inpiidansu Seigou):** Impedance matching (การแมตช์อิมพีแดนซ์)
- **エッチング (Etchingu):** Etching (การกัดกรด)
- **反り (Sori):** Warpage (การโก่งตัวของบอร์ด)

## ควิซท้ายบท (Quiz)
Q1: การทำ Copper Pour ทิ้งไว้ในพื้นที่ว่างของเลเยอร์มีประโยชน์เรื่องใดมากที่สุดในแง่ของ DFM?
A) ลดต้นทุนการกัดกรดทองแดง
B) ป้องกันปัญหาบอร์ดโก่งตัวจากการกระจายความร้อนที่ไม่สม่ำเสมอ (Correct)
C) ทำให้บอร์ดดูสวยงาม
D) เพิ่มความเร็วของสัญญาณ
