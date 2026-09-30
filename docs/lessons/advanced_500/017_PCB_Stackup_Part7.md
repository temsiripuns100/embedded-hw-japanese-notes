# บทที่ 17: HDI (High Density Interconnect) and Microvia Technology (เทคโนโลยี HDI และความท้าทาย)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Advanced Engineering Theory)
HDI Stackup เป็นสิ่งที่หลีกเลี่ยงไม่ได้ในอุปกรณ์สมัยใหม่ที่มี Pitch ของ BGA ต่ำกว่า 0.65mm รูปแบบของ HDI แบ่งเป็น N+C+N (เช่น 1+n+1, 2+n+2) ไปจนถึง Any-Layer HDI (ELIC - Every Layer Interconnect)
จุดสำคัญคือ **Microvia Reliability**:
- การใช้ **Stacked Vias** ประหยัดพื้นที่ แต่เพิ่มความเสี่ยงเรื่อง Thermo-mechanical stress ระหว่างกระบวนการบัดกรี ส่งผลให้เกิด Microvia Separation (รอยร้าวที่ฐาน Via)
- **Staggered Vias** แข็งแรงกว่าในเชิงกล แต่ใช้พื้นที่เยอะกว่า
การเลือก Prepreg ในชั้น HDI มักใช้แบบ LDP (Laser Drillable Prepreg) หรือ RCC (Resin Coated Copper) เพื่อให้เลเซอร์เจาะได้แม่นยำ

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick #1**: ในกรณีที่เลี่ยง Stacked Microvia เกิน 2 ชั้นไม่ได้ (เช่น 3-n-3) ต้องกำชับให้โรงงาน (Fabricator) ทำการทดสอบ IST (Interconnect Stress Test) อย่างเข้มงวด
- **OJT Trick #2**: ควรเติม (Fill) Microvia ด้วยทองแดง (Copper Filled) เสมอหากต้องทำ Via-in-Pad หรือซ้อน Via เพื่อป้องกัน Solder Void

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **ビルドアップ基板 (Birudo-appu Kiban)**: Build-up PCB / HDI PCB
- **スタガードビア (Sutagādo Bia)**: Staggered Via
- **スタックビア (Sutakku Bia)**: Stacked Via
- **レーザー穴あけ (Rēzā Ana-ake)**: Laser Drilling
- **めっき充填 (Mekki Jūten)**: Plating Fill / Copper Fill (การเติมผ่านรูด้วยการชุบทองแดง)

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: ระหว่าง Stacked Via และ Staggered Via แบบใดมีความเสี่ยงสูงที่สุดที่จะเกิดรอยร้าว (Crack) เมื่อผ่านอุณหภูมิสูง (เช่น Reflow รอบที่สอง)?
1. Staggered Via
2. Stacked Via
3. มีความเสี่ยงเท่ากัน
4. ไม่มีความเสี่ยงใน Microvia

*เฉลย: 2. Stacked Via (เนื่องจากการซ้อนกันในแนวตั้ง ทำให้แรงเค้นจากความร้อน (Thermal Stress) สะสมบริเวณรอยต่อ (Target Pad) มากกว่า)*
