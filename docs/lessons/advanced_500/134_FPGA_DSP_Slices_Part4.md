# Lesson 134: FPGA DSP Slices - Part 4 (Cascade Paths & Wide Adders)

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
FPGA รุ่นใหม่มี Cascade Paths เฉพาะ (Dedicated Cascade Routing) ระหว่าง DSP Slices ที่อยู่ติดกัน เช่น PCIN/PCOUT และ ACIN/ACOUT ซึ่งมี Delay ต่ำมาก ระดับ Senior Engineer จะใช้เส้นทางเหล่านี้ในการทำ Wide Adders (บวกเลขขนาดใหญ่กว่า 48-bit) หรือทำ Systolic Array FIR Filters โดยไม่ต้องออกไปยัง Fabric Routing ทั่วไปเลย

## ทริคหน้างาน OJT (OJT Tricks)
- **Systolic FIR vs Direct FIR:** เลือกใช้ Systolic Architecture เมื่อออกแบบ FIR Filter ความเร็วสูง เพราะการส่งข้อมูลผ่าน Cascade path จะช่วยรักษา Fmax ไว้ได้ แม้ Tap จะมีจำนวนมาก
- **Placement Constraints:** เมื่อใช้ Cascade path ต้องแน่ใจว่า Tool วาง DSP slices ติดกันจริงๆ ในคอลัมน์เดียวกัน (DSP Column) การใส่ Pblock อาจจำเป็นในบางดีไซน์ที่แน่น

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **隣接配置 (Rinsetsu Haichi):** Adjacent Placement (การจัดวางติดกัน)
- **専用配線 (Sen'you Haisen):** Dedicated Routing (เส้นทางเชื่อมต่อเฉพาะ)
- **加算器の拡張 (Kasanki no Kakuchou):** Adder Extension (การขยายขนาดตัวบวก)
- **制約条件 (Seiyaku Jouken):** Constraint Conditions (เงื่อนไขข้อจำกัด)

## ควิซท้ายบท (Quiz)
**Q:** ข้อดีที่สุดของการใช้ Dedicated Cascade Path (PCIN/PCOUT) ระหว่าง DSP Slices คืออะไร?
**A:** เป็นเส้นทางตรงระหว่าง DSP ภายใน Column เดียวกัน ทำให้ Delay ต่ำมากและไม่กินทรัพยากร Routing ภายนอก ส่งผลให้ Timing ปิดได้ง่ายขึ้น
