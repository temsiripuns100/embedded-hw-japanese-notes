# Lesson 154: BRAM Collision Handling and Read-during-Write Behavior

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
การทำงานร่วมกันระหว่างพอร์ตใน BRAM นำมาซึ่งความท้าทายเรื่อง Read-during-Write เมื่อมีการเขียนและอ่านที่ Address เดียวกันใน Clock cycle เดียวกัน (Collision) BRAM จะมีโหมดการทำงาน 3 แบบ: 
1. **WRITE_FIRST (Read-after-Write):** ข้อมูลใหม่จะถูกเขียนและถูกอ่านออกไปที่ Data Output พอร์ตทันที
2. **READ_FIRST (Read-before-Write):** ข้อมูลเก่าจะถูกอ่านออกมาก่อนที่ข้อมูลใหม่จะถูกเขียนทับลงไป
3. **NO_CHANGE:** Data Output ไม่เปลี่ยนแปลงค่าระหว่างการเขียน ลดการใช้พลังงาน
การเข้าใจพฤติกรรมนี้สำคัญมากในระบบที่ทำ Data forwarding หรือ Pipeline แบบซับซ้อน

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Data Forwarding:** หากต้องการจำลองพฤติกรรมของ Register File ใน Processor มักจะใช้ WRITE_FIRST 
- **Power Savings:** ในกรณีที่ไม่สนใจข้อมูลตอนที่กำลังเขียน ให้เลือกใช้โหมด NO_CHANGE เพื่อประหยัดพลังงาน (Dynamic power)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- 同時アクセス (Douji akusesu) - Simultaneous access
- 動作モード (Dousa moodo) - Operating mode
- 読み出し優先 (Yomidashi yuusen) - Read first
- 消費電力 (Shouhi denryoku) - Power consumption

## ควิซท้ายบท (Quiz)
**คำถาม:** หากวิศวกรต้องการออกแบบ BRAM ให้ลดการใช้พลังงานสูงสุดขณะทำการ Write โหมด Read-during-Write ใดควรถูกเลือก?
**คำตอบ:** (เฉลย: โหมด NO_CHANGE)
