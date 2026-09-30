# FPGA DSP Slices เจาะลึกระดับ Senior: Part 7 - Cascading & Pre-adders for Symmetric FIR (カスケード接続とプリ加算器)

## ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
การสร้าง FIR Filter แบบสมมาตร (Symmetric FIR) สามารถประหยัดตัวคูณได้ครึ่งหนึ่งโดยการบวกข้อมูลขาเข้าที่คูณด้วยสัมประสิทธิ์เดียวกันก่อน นำมาประยุกต์กับ DSP48E2 ซึ่งมี Pre-adder (D-register) ภายใน การใช้เส้นทาง Cascade (PCOUT to PCIN) แทนการต่อสาย (Routing) ทั่วไปผ่าน Fabric จะป้องกันปัญหาสายหน่วง (Routing delay) ใน Multi-tap FIR filters

## ทริคหน้างาน OJT (OJT現場のコツ)
เวลาดีไซน์ FIR Filter ขนาดใหญ่ ห้ามใช้ Adder tree แบบปกติที่เขียนใน RTL เด็ดขาด! ให้ใช้โครงสร้าง Systolic Array โดยส่งผ่านผลลัพธ์ย่อย (Partial products) ผ่านพอร์ต PCIN/PCOUT ของ DSP Slices หากไม่ได้ใช้โครงสร้างนี้ จะเกิดคอขวดที่ Routing Resources ทำให้ $F_{max}$ ตกอย่างน่าเกลียด

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用日本語用語)
- **カスケード接続 (Kasukeedo Setsuzoku):** Cascade connection
- **対称FIRフィルタ (Taishou FIR Firuta):** Symmetric FIR Filter
- **事前加算器 (Jizen Kasanki):** Pre-adder
- **配線遅延 (Haisen Chien):** Routing delay
- **リソースの枯渇 (Risoosu no Kokatsu):** การขาดแคลน Resource

## ควิซท้ายบท (確認テスト)
**คำถาม:** การใช้ Pre-adder ใน DSP Slice เหมาะสมกับโครงสร้างใดมากที่สุด?
1. IIR Filter
2. Symmetric FIR Filter
3. FFT Butterfly
*เฉลย:* 2. Symmetric FIR Filter เพราะมีการนำสัญญาณ x[n] และ x[n-k] มาบวกกันก่อนคูณด้วยสัมประสิทธิ์ $h[n]$
