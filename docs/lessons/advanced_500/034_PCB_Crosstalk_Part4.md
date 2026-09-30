# Lesson 034: PCB Crosstalk - Part 4: Differential Pair & Mode Conversion (差動配線とモード変換)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Differential Pair มีความต้านทานต่อ Crosstalk จากภายนอกได้ดี (Common-Mode Rejection) แต่มีปัญหาในตัวเองคือ **Mode Conversion (モード変換)** 
หากสาย P และ N ไม่สมมาตรกัน (เช่น ยาวไม่เท่ากัน หรือ ระยะห่างไม่สม่ำเสมอ) สัญญาณ Differential-mode จะถูกแปลงเป็น Common-mode ซึ่งทำให้เกิดการแผ่กระจายคลื่นแม่เหล็กไฟฟ้า (EMI) และลด Signal Integrity 
นอกจากนี้ Differential pair คู่ข้างๆ กันก็สามารถสร้าง Differential Crosstalk ต่อกันได้หากระยะห่างระหว่างคู่ (Inter-pair spacing) ไม่เพียงพอ

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Intra-pair Skew Matching:** การทำ Length matching ในคู่ Diff-pair ต้องชดเชยให้ใกล้กับจุดที่เกิดความไม่สมมาตร (เช่น โค้ง, via) ให้มากที่สุด ไม่ใช่ไปชดเชยที่ปลายสาย เพราะถ้ามี Skew ค้างอยู่ตรงกลางสาย มันจะเกิด Common-mode ตลอดเส้นทางนั้น
- **5W Rule for Diff Pairs:** ระยะห่างระหว่างคู่ Differential (Inter-pair spacing) ควรมากกว่าระยะห่างในคู่ตัวเอง (Intra-pair spacing) อย่างน้อย 3 ถึง 5 เท่า (5W rule) เพื่อป้องกัน Inter-pair crosstalk

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **差動配線 (Sadou Haisen):** Differential Pair routing
- **等長配線 (Touchou Haisen):** Length matching
- **スキュー (Sukyuu):** Skew (ความต่างของเวลา/ความยาว)
- **モード変換 (Moodo Henkan):** Mode Conversion (Diff to Common mode)
- **ペア間隔 (Pea Kankaku):** Inter-pair spacing

## ควิซท้ายบท (Quiz)
**Q1:** Mode Conversion เกิดจากสาเหตุหลักอะไร?
**A:** ความไม่สมมาตรในคู่ Differential (เช่น Intra-pair skew หรือความไม่สมมาตรของ Return path)
**Q2:** การทำ Length matching ที่ถูกต้องควรทำที่บริเวณใดของเส้นทางสาย?
**A:** ชดเชยความยาวให้ใกล้กับจุดที่เกิดความไม่สมมาตรให้มากที่สุด
