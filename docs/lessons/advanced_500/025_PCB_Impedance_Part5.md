# Lesson 25: Impedance Measurement and Tolerance (TDR測定と製造公差)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
แม้จะออกแบบอย่างสมบูรณ์แบบ แต่ในกระบวนการผลิต PCB (製造プロセス) จะมีค่าความคลาดเคลื่อน (Manufacturing Tolerance - 製造公差) เช่น ความกว้างเส้นทองแดงหลังการกัด (Etching), ความหนาของ Prepreg หลังจากการอัด (Pressing) 
มาตรฐานทั่วไปของ Impedance Tolerance คือ **±10%** (เช่น 50Ω ±5Ω) สำหรับงานความถี่สูงมากอาจระบุ **±5%** แต่จะมีราคาแพง
โรงงานจะใช้ **TDR (Time Domain Reflectometer - TDR測定器)** ยิงสัญญาณ Step pulse เข้าไปในสายส่ง และวัดสัญญาณสะท้อนกลับ เพื่อพลอตกราฟแสดงอิมพีแดนซ์ตามระยะทาง หากกราฟมีการกระตุกขึ้นหรือลง (Bump/Dip) แสดงว่าเกิด Discontinuity ณ จุดนั้น

## ทริคหน้างาน OJT (OJT Field Tricks)
- **Impedance Coupon:** โรงงานจะไม่วัด TDR บนบอร์ดจริง แต่จะสร้าง Test Coupon ไว้ที่ขอบพาเนล (Panel edge) ซึ่งมีโครงสร้าง Stack-up และ Trace width เหมือนกับบอร์ดจริงเป๊ะๆ เพื่อใช้วัดและออก Report (Impedance Report)
- **Design for Manufacturing (DFM):** ถ้าคำนวณเส้น 50Ω ได้ 4.2 mil ในขณะที่โรงงานมี Tolerance การกัดกรด ±0.5 mil การที่เส้นเล็กลง 0.5 mil จะกระทบ Z0 เยอะกว่าเส้นใหญ่ ควรออกแบบให้เส้นกว้างอย่างน้อย 5-6 mil ถ้าเป็นไปได้
- **Copper Plating:** จำไว้ว่าเส้นนอกสุด (Top/Bottom) จะมีการชุบทองแดงเพิ่ม (Plating) ทำให้ความหนาและความกว้างควบคุมยากกว่าชั้นใน (Inner layers)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **製造公差 (Seizou Kousa):** Manufacturing Tolerance (ค่าความคลาดเคลื่อน)
- **テストクーポン (Tesuto Kuupon):** Test Coupon (ชิ้นงานทดสอบข้างพาเนล)
- **TDR測定 (Tii Dii Aaru Sokutei):** TDR Measurement (การวัดด้วย TDR)
- **エッチング (Etchingu):** Etching (การกัดกรด)
- **仕上がり寸法 (Shiagari Sunpou):** Finished dimension / Final size

## ควิซท้ายบท (End of Chapter Quiz)
**Q:** เพราะเหตุใดโรงงานผลิต PCB จึงมักทดสอบ TDR ที่ Test Coupon แทนที่จะวัดบนบอร์ดของลูกค้าโดยตรง?
1. เครื่อง TDR ไม่สามารถวัดบอร์ดที่มี Component Pad ได้
2. เพื่อหลีกเลี่ยงความเสียหายที่อาจเกิดบนบอร์ดลูกค้า และสะดวกต่อการสร้าง Probe Pattern ที่มาตรฐาน
3. เพราะ Test Coupon ผลิตด้วยวัสดุเกรดต่ำกว่าบอร์ดจริง

*เฉลย: 2*
