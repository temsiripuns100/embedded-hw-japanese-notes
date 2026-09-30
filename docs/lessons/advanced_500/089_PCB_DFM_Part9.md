# Lesson 89: PCB DFM Part 9 - RF PCB Design and DFM Considerations

## ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
การออกแบบวงจร RF (Radio Frequency) ต้องการความแม่นยำสูงในระดับคลื่นแม่เหล็กไฟฟ้า (Electromagnetic) การใช้ DFM สำหรับ RF PCB ต้องคำนึงถึงวัสดุฐาน (Substrate Material) เช่น PTFE (Teflon) หรือ Rogers ซึ่งมีคุณสมบัติ Dk/Df ต่ำและเสถียร ข้อควรระวังในกระบวนการผลิตคือวัสดุกลุ่มนี้มักจะนิ่มและมีปัญหา Dimensional Stability (หด/ขยายตัว) ตอนผลิต ทำให้การเจาะรู (Drilling) และการทำ Registration ลำบาก นอกจากนี้ การทำ Copper Thieving (การเติมทองแดงหลอกเพื่อ Balance ความหนาแน่น) ต้องระวังไม่ให้กระทบกับ RF Trace (ควรวางห่างอย่างน้อย 3-5 เท่าของความกว้าง Trace)

## ทริคหน้างาน OJT (OJT Practical Tricks)
- การใช้ Hybrid Stackup (เช่น นำ FR-4 มาผสมกับ Rogers) เป็นเทคนิคที่ดีในการลดต้นทุน แต่ต้องระวังปัญหาบอร์ดโก่ง (Warpage) เนื่องจาก CTE ของวัสดุสองชนิดไม่เท่ากัน ควรจัด Stackup ให้สมมาตรมากที่สุด
- หลีกเลี่ยงการทำ Silkscreen (ตัวหนังสือ) ทับบน RF Trace หรือ RF Antenna เด็ดขาด เพราะหมึกมีค่า Dk ที่อาจไปเปลี่ยน Impedance ของเส้น
- การทำ Via Fence / Shielding Vias ควรคำนวณระยะห่างระหว่าง Via ให้เหมาะสม (ปกติ < λ/20 ของความถี่สูงสุด) และระวังอย่าเจาะชิดกันเกินไปจนแผ่น PCB แตก

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **高周波基板 (Koushuuha Kiban):** High Frequency Board / RF PCB
- **誘電率 (Yuudenritsu):** Dielectric Constant (Dk)
- **誘電正接 (Yuuden Seisetsu):** Dissipation Factor (Df)
- **寸法安定性 (Sunpou Anteisei):** Dimensional Stability (ความเสถียรของขนาด)
- **ハイブリッド構成 (Haiburiddo Kousei):** Hybrid Stackup (การจัดเรียงชั้นแบบผสมวัสดุ)

## ควิซท้ายบท (Quiz)
**คำถาม:** การพิมพ์ Silkscreen ทับลงบน RF Trace ส่งผลเสียอย่างไร และควรหลีกเลี่ยงหรือไม่?
**เฉลย:** ส่งผลเสียคือ หมึก Silkscreen มีค่า Dielectric Constant (Dk) ที่สามารถทำให้ค่า Impedance หรือความถี่ Resonant ของวงจร RF/Antenna ผิดเพี้ยนไป ดังนั้นในการตรวจแบบ (検図) ต้องหลีกเลี่ยงการวางตัวหนังสือทับเส้น RF อย่างเด็ดขาด
