# Advanced PCB Impedance Part 8: Coplanar Waveguide (CPW) Design (コプレーナ導波路設計)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
Coplanar Waveguide (CPW) เป็นโครงสร้างที่มี Ground plane อยู่ข้างเส้นสัญญาณในชั้นเดียวกัน (Layer เดียวกัน) นิยมใช้อย่างมากในงาน RF (Radio Frequency) และเสาอากาศ (Antenna feedline) 
เสน่ห์ของ CPW คือสามารถลดความสูญเสีย (Loss) บน Dielectric ได้ เพราะ EM Field ส่วนใหญ่จะเดินทางในอากาศเหนือรอยต่อระหว่าง Trace และ Ground นอกจากนี้ CPW (หรือ Coplanar with Ground - CPWG) ยังช่วยควบคุม Z0 ได้ง่ายขึ้นบนบอร์ดที่มีความหนา Dielectric คงที่ แต่ต้องระมัดระวังความกว้างของช่องว่าง (Gap/Clearance) ให้แม่นยำ 

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- สำหรับ CPWG ต้องวาง Ground Vias อย่างแน่นหนาตามขอบของเส้นสัญญาณ (Stitching vias) เพื่อทำหน้าที่เหมือนเป็น "กรงฟาราเดย์" ป้องกันปัญหา Ground Loop Resonance และรักษาพฤติกรรม Ground ให้แข็งแกร่ง (Solid reference) ระยะห่างระหว่าง Via ควรน้อยกว่า λ/10 (1 ใน 10 ของความยาวคลื่นสูงสุด) 
- ระวังปัญหาน้ำยาประสาน (Solder Mask) ในบริเวณ Gap ของ CPW หนาไม่เท่ากัน ซึ่งจะทำให้ค่า Dk เฉลี่ยเพี้ยน ส่งผลให้ Impedance Shift

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **コプレーナ (Kopurēna):** Coplanar
- **クリアランス (Kuriaransu):** Clearance / Gap
- **グラウンドビア (Guraundo bia):** Ground via
- **ソルダーレジスト (Sorudā rejisuto):** Solder mask (หรือ レジスト - Resist)
- **高周波 (Kōshūha):** High frequency

## ควิซท้ายบท (Quiz)
**Q:** กฎเหล็กที่สำคัญที่สุดในการออกแบบ Coplanar Waveguide คืออะไร?
1. การเชื่อมต่อ Ground ตลอดแนวด้วย Ground Via ให้มีระยะห่างน้อยกว่า λ/10
2. การใช้ Dielectric ที่มีความหนามากกว่า 60 mils เสมอ
3. การเคลือบ Solder Mask ให้หนาที่สุดเท่าที่จะทำได้
**Ans:** 1. การเชื่อมต่อ Ground ตลอดแนวด้วย Ground Via ให้มีระยะห่างน้อยกว่า λ/10
