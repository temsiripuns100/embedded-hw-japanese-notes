# Advanced PCB Stackup Part 3: Prepreg vs Core Properties (プリプレグとコア材の特性)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ความแตกต่างระหว่าง Core (C-stage) และ Prepreg (B-stage) มีผลอย่างมากต่อการควบคุม Impedance และกระบวนการผลิต (Pressing) Core คือแผ่นทองแดงประกบไฟเบอร์กลาสที่อบแข็งตัวมาแล้วจากโรงงานผู้ผลิตวัสดุ ในขณะที่ Prepreg คือไฟเบอร์กลาสชุบเรซินที่ยังไม่แข็งตัวเต็มที่ (Partially cured) ซึ่งจะละลายและอุดช่องว่างของวงจร (Resin flow) ระหว่างการทำ Lamination 
Senior Engineer ต้องคำนวณ "Pressed Thickness" ของ Prepreg ให้แม่นยำ เพราะความหนาจะลดลงตามปริมาณทองแดง (Resin fill) ในชั้นข้างเคียง หากคำนวณพลาด ค่า Impedance จะเพี้ยนไปจากที่ออกแบบไว้

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- เมื่อออกแบบ Impedance, อย่าใช้ค่า "Nominal Thickness" ของ Prepreg จาก Datasheet ตรงๆ ให้ขอ "Pressed Thickness" จาก PCB Vendor ที่ผ่านการคำนวณ Resin Starvation แล้ว
- หากใช้ Copper หนา (เช่น 2oz หรือมากกว่า) ต้องใช้ Prepreg ที่มีค่า Resin Content (RC%) สูงพอที่จะเติมเต็มช่องว่าง (Fill) ระหว่างเส้นทองแดงได้ เพื่อป้องกันปัญหา Void (ฟองอากาศ) ที่ทำให้เกิด Delamination หรือ CAF (Conductive Anodic Filament)

## คำศัพท์ภาษาญี่ปุ่นในการตรวจแบบ (検図 - Kenzu)
- **プリプレグ (Puripuregu):** Prepreg
- **コア材 (Koa-zai):** Core material
- **板厚 (Ita-atsu):** Board thickness - ความหนาของบอร์ด
- **ボイド (Boido):** Void - ฟองอากาศหรือช่องว่าง
- **樹脂流れ (Jushi nagare):** Resin flow - การไหลของเรซิน

## ควิซท้ายบท (Quiz)
**Q:** เพราะเหตุใดจึงไม่ควรใช้ค่าความหนา Nominal ของ Prepreg ในการจำลอง (Simulate) Impedance โดยตรง?
1. เพราะ Prepreg จะยุบตัวลง (Pressed thickness) เพื่ออุดช่องว่างของทองแดงในชั้นที่ประกบ
2. เพราะความหนาแปรผันตามอุณหภูมิห้อง
3. เพราะ Prepreg มีค่า Dk ไม่คงที่
**Ans:** 1. เพราะ Prepreg จะยุบตัวลงเพื่ออุดช่องว่างของทองแดง
