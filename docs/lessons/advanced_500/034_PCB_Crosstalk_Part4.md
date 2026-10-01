# 034: PCB Crosstalk เจาะลึก Part 4 - Differential Pair & Common-Mode Noise

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Differential Signalling ออกแบบมาเพื่อหักล้าง Common-Mode Noise แต่ตัวมันเองก็มีประเด็นเรื่อง Intra-pair Crosstalk และ Inter-pair Crosstalk:
- **Intra-pair Crosstalk:** การที่เส้น P (Positive) และ N (Negative) มีการ Coupling กันเอง นี่คือข้อดี! เพราะทำให้ Differential Impedance ($Z_{diff}$) ลดลง ($Z_{diff} = 2 \times Z_{odd}$) การรักษาระยะห่าง P/N ให้คงที่จึงสำคัญมากต่อ Impedance Matching
- **Inter-pair Crosstalk:** เมื่อ Differential Pair 1 รบกวน Differential Pair 2 หาก Coupling ไม่สมมาตร (เส้น P ของ Pair 1 รบกวนเส้น P ของ Pair 2 มากกว่าเส้น N) จะทำให้เกิด **Common-Mode Noise (Skew)** บน Pair 2 ส่งผลให้ Receiver ไม่สามารถหักล้าง Noise ออกไปได้หมด (CMRR ไม่เพียงพอ) 
- **Mode Conversion ($S_{cd21}$):** ความไม่สมมาตร (Length Mismatch, Gaps in Reference Plane, Asymmetric routing) ทำให้สัญญาณ Differential เปลี่ยนรูปเป็น Common-Mode ซึ่งแผ่รังสี EMI ได้ง่าย

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Phase Matching ไม่ใช่แค่ความยาวรวม:** อย่าทำ Length Matching (Zig-zag) มั่วๆ ไว้ตรงปลายทาง หากเกิด Skew ตั้งแต่ต้นทาง ให้ทำ Compensation ที่จุดเกิด Skew ทันที (Right at the mismatch source) ไม่เช่นนั้นช่วงที่สัญญาณเหลื่อมกัน (Out of phase) จะกลายเป็น Common-Mode แผ่ EMI ไปตลอดทาง
- **ระวัง Spacing ระหว่าง Pair:** ใช้กฎ "5W" หรือมากกว่า ระหว่างสอง Differential Pairs แทนที่จะใช้แค่ 3W เพื่อลด Inter-pair Crosstalk ให้ได้ระดับ <-40dB

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **差動配線 (Sadō haisen):** Differential wiring / routing
- **同相ノイズ (Dōsō noizu):** Common-mode noise
- **等長配線 (Tōchō haisen):** Length matching (การปรับให้สายยาวเท่ากัน)
- **スキュー (Sukyū):** Skew (ความเหลื่อมล้ำของเวลา)
- **インピーダンス整合 (Inpīdansu seigō):** Impedance matching

## 4. ควิซท้ายบท (Quiz)
**คำถาม:** หาก Differential Pair มีความยาวเส้น P และ N ไม่เท่ากันตั้งแต่ต้นทาง แต่ไปทำ Snake routing หักล้างให้ความยาวรวมเท่ากันที่ปลายทาง จะเกิดผลเสียอย่างไร?
**คำตอบ:** สัญญาณจะเกิด Phase Skew ตลอดทางตั้งแต่ต้นจนถึงจุดที่ชดเชย ทำให้เกิด Common-mode noise ระหว่างทาง ซึ่งสามารถแผ่ EMI (Electromagnetic Interference) รบกวนวงจรอื่น และทำให้เกิด Crosstalk ที่ไม่สมดุลต่อสายใกล้เคียง
