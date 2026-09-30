# บทที่ 83: PCB DFM Part 3 - การออกแบบ Via และรูเจาะ (Vias & Holes)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในการเจาะรู PCB (Drilling) ต้องแยกแยะระหว่าง PTH (Plated Through Hole) และ NPTH (Non-Plated Through Hole) 
ค่า Annular Ring ต้องคำนวณเผื่อ Drill Wander (ความคลาดเคลื่อนของหัวเจาะ) โดยทั่วไปต้องเหลืออย่างน้อย 1-2 mil เพื่อป้องกัน Hole Breakout
การใช้ Blind/Buried Vias ในโครงสร้าง HDI ต้องระวังเรื่อง Aspect Ratio (อัตราส่วนความหนาบอร์ดต่อเส้นผ่านศูนย์กลางรู) ซึ่งไม่ควรเกิน 1:1 หรือ 0.8:1 เพื่อให้กระบวนการชุบทองแดงลงไปในรู (Plating) ทำได้สมบูรณ์

## ทริคหน้างาน OJT (OJT Tricks)
- การวาง Via บน Pad (Via-in-Pad) สำหรับ BGA ต้องสั่งทำกระบวนการ "Via Plugging & Capping (POFV)" เสมอ มิฉะนั้น Solder paste จะไหลลงไปในรูระหว่างขั้นตอน Reflow ทำให้ข้อต่อบัดกรีไม่สมบูรณ์และเกิด Void
- รู Mounting Hole แบบ NPTH ควรมี Keep-out zone ที่ไม่มีทองแดงเลย เพื่อป้องกันสกรูหรือแหวนรองบาดโซลเดอร์มาสก์แล้วไปชอร์ตกับวงจรข้างล่าง

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **スルーホール (Suruu Hooru):** Through Hole / PTH (รูเจาะทะลุชุบทองแดง)
- **ノンスルーホール (Non Suruu Hooru):** NPTH (รูเจาะทะลุไม่ชุบทองแดง)
- **ビアインパッド (Bia In Paddo):** Via-in-Pad (รูเจาะบนแพด)
- **穴ズレ (Ana Zure):** Drill Wander / Misregistration (การเจาะเยื้อง/คลาดเคลื่อน)
- **アニュラーリング (Anyuraa Ringu):** Annular Ring (วงแหวนทองแดงรอบรูเจาะ)

## ควิซท้ายบท (Quiz)
Q1: ทำไมการทำ Via-in-Pad จึงต้องสั่งกระบวนการ Plugging & Capping (POFV)?
A) เพื่อลดต้นทุน
B) เพื่อป้องกันตะกั่วบัดกรีไหลลงรูเจาะจนเกิดข้อบกพร่องที่รอยเชื่อม (Correct)
C) เพื่อให้เจาะรูได้เร็วขึ้น
D) เพื่อเพิ่มความสามารถในการกระจายความร้อน
