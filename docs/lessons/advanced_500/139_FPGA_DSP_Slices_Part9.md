# FPGA DSP Slices เจาะลึกระดับ Senior: Part 9 - Complex Multiplication Optimization (複素乗算の最適化)

## ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
การคูณจำนวนเชิงซ้อน (Complex Multiplication) $(A+jB) \times (C+jD)$ โดยทั่วไปต้องใช้ตัวคูณ 4 ตัว แต่สามารถทำ Optimization แบบ Gauss's trick ให้เหลือเพียง 3 ตัวคูณ แต่ต้องแลกกับการใช้ตัวบวกเพิ่มขึ้น ในโครงสร้าง FPGA การพิจารณา Trade-off ระหว่าง DSP Slices และ LUT Adders เป็นเรื่องที่ Senior Engineer ต้องตัดสินใจขึ้นอยู่กับ Resource ที่เหลือในชิป

## ทริคหน้างาน OJT (OJT現場のコツ)
ในงานสื่อสารไร้สาย (5G/SDR) การคูณจำนวนเชิงซ้อนมีเยอะมาก หาก DSP Slices ใกล้หมด การปรับไปใช้วิธี 3-multiplier จะช่วยกู้ชีวิตโปรเจกต์ได้ แต่ต้องระวังเรื่อง Latency ที่ไม่เท่ากันในแต่ละเส้นทาง (Datapath) ต้องเพิ่ม Shift Register ไว้ทำ Delay Matching เสมอ

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用日本語用語)
- **複素乗算 (Fukuso Jouzan):** Complex multiplication
- **最適化 (Saitekika):** Optimization
- **遅延調整 (Chien Chousei):** Delay adjustment (Delay matching)
- **トレードオフ (Toreedo Ofu):** Trade-off
- **リソース使用率 (Risoosu Shiyouritsu):** Resource utilization

## ควิซท้ายบท (確認テスト)
**คำถาม:** วิธีการของ Gauss สำหรับ Complex Multiplication ช่วยลดการใช้ฮาร์ดแวร์ส่วนใด?
1. ลดจำนวน Adder (ตัวบวก)
2. ลดจำนวน Multiplier (ตัวคูณ)
3. ลดจำนวน Register
*เฉลย:* 2. ลดจำนวน Multiplier จาก 4 ตัวเหลือ 3 ตัว แต่ต้องใช้ Adder เพิ่มขึ้น
