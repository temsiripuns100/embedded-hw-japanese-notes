# Lesson 048: PCB Vias Part 8 - Differential Pair Vias and Return Path

## ทฤษฎีวิศวกรรมเชิงลึก (Senior Engineer Level)
เมื่อ Differential Pair มีการเปลี่ยน Layer ผ่าน Vias กระแส Return path จะถูกขัดจังหวะหาก Reference Plane มีการเปลี่ยนชนิด (เช่น จาก GND ไป GND หรือ GND ไป VCC) หากเปลี่ยน Layer อ้างอิงจาก GND สู่ GND ต้องวาง Return Via (หรือ Stitching Via) ไว้ใกล้เคียงที่สุด (ระยะไม่เกิน 100 mils) เพื่อให้ Return current ไหลกลับได้สะดวก ไม่เกิด Common-mode noise และ EMI

## ทริคหน้างาน OJT
เวลาตรวจแบบ (Kenzu) คู่ Diff Pair ที่ทะลุ Layer ต้องดูเสมอว่า Return Via อยู่กี่หลุมและสมมาตรไหม ถ้าไม่สมมาตร สัญญาณ P กับ N จะเกิด Skew ได้

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図)
- **リターンパス (Ritaan Pasu):** Return Path
- **差動ペア (Sadou Pea):** Differential Pair
- **層間移動 (Soukan Idou):** Layer transition / เปลี่ยน Layer

## ควิซท้ายบท
Q: หาก Differential Pair เปลี่ยน Layer โดยที่ Reference plane เปลี่ยนจาก GND เป็น VCC ควรทำอย่างไร?
A: วาง Stitching Capacitor ใกล้กับ Via เพื่อเชื่อม Return path ทาง AC ระหว่าง GND กับ VCC
