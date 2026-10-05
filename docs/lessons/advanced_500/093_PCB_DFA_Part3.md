# 093 - PCB DFA Part 3: Stencil Design and Fiducial Marks

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ปริมาณของ Solder Paste ที่พิมพ์ลงบน Pad เป็นตัวกำหนดคุณภาพของรอยเชื่อม (Solder Joint) การออกแบบ Stencil ไม่ใช่แค่การเจาะรูให้เท่ากับขนาด Pad เสมอไป (1:1 Ratio) วิศวกรต้องคำนึงถึง Area Ratio และ Aspect Ratio เพื่อให้ Solder Paste ลอกออกจากรู Stencil ได้สมบูรณ์ โดยปกติ Area Ratio (พื้นที่เปิด/พื้นที่ผนังด้านใน) ต้อง > 0.66
ส่วน Fiducial Marks คือจุดอ้างอิงสำหรับการทำ Image Processing ของเครื่องจักร (Printer, Mounter, AOI) ต้องมีลักษณะที่กล้องมองเห็นได้ชัดเจน ตัดกับพื้นหลัง และต้องเปิด Solder Mask ให้กว้างพอ

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Home Plate Design:** สำหรับอุปกรณ์ที่เป็นชิปตัวใหญ่หรือมีปัญหา Solder Ball บ่อยๆ เรามักจะแก้แบบ Stencil Aperture เป็นรูปคล้ายโฮมเพลทในเบสบอล (เว้าตรงกลาง) เพื่อลดปริมาณตะกั่วและลดแก๊สที่ดันออกมาตอน Reflow
- **Fiducial Placement:** ควรมี Global Fiducials อย่างน้อย 3 จุดที่มุมบอร์ด (แบบอสมมาตร) เพื่อให้เครื่องจักรจับได้ทันทีถ้าวางบอร์ดกลับด้าน (Orientation Error) และต้องมี Local Fiducials สำหรับ IC ที่มีระยะพิตช์ละเอียด (Fine-pitch BGA/QFP)

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図用語 - Kenzu Yōgo)
- **認識マーク (Ninshiki Māku):** Fiducial mark / จุดอ้างอิงสำหรับการจดจำของกล้อง
- **メタルマスク (Metaru Masuku):** Metal Stencil / แผ่นสเตนซิล
- **開口率 (Kaikō-ritsu):** Aperture ratio / อัตราส่วนการเปิดช่องสเตนซิลเทียบกับ Pad
- **はんだボール (Handa bōru):** Solder ball / ลูกตะกั่วกระเด็น
- **かすれ (Kasure):** Smearing, incomplete printing / การพิมพ์ตะกั่วไม่เต็มหรือขาดหาย

## ควิซท้ายบท (Quiz)
1. ทำไมถึงต้องวาง Fiducial Mark เป็นรูปตัว L (3 จุด) แทนที่จะวาง 4 จุดให้สมมาตรกัน?
2. ถ้ารูเจาะบน Stencil เล็กและหนาเกินไป จะเกิดผลเสียอย่างไรต่อการพิมพ์ Solder Paste?
