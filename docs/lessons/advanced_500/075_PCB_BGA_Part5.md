# Lesson 075: BGA Manufacturing Defects & DFM (X-Ray Inspection)

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Design for Manufacturing (DFM) สำคัญมากสำหรับ BGA เพราะข้อบกพร่อง (Defects) จะมองไม่เห็นด้วยตาเปล่า ต้องใช้ X-Ray
- **Head-in-Pillow (HiP)**: อาการที่ตะกั่วจาก BGA Ball แตะกับ Solder Paste บน Pad แต่ไม่หลอมรวมกันเป็นเนื้อเดียว มักเกิดจากบอร์ดหรือตัว IC โก่งตัว (Warpage) ระหว่างกระบวนการ Reflow
- **Bridging**: การช็อตกันระหว่าง Ball ที่อยู่ติดกัน เกิดจากการใส่ Solder paste มากเกินไป (Stencil หนาไป) หรืออุณหภูมิ Reflow ไม่เหมาะสม
- **Voids**: ฟองอากาศในรอยบัดกรี มาตรฐาน IPC-A-610 ยอมรับ Voids ได้ไม่เกิน 25% (หรือ 30% ตามคลาส) ของพื้นที่หน้าตัดรอยเชื่อม

## ทริคหน้างาน OJT (OJT Field Tricks)
- การแก้ปัญหา HiP ฝั่ง Design ทำได้ยาก (มักเป็นเรื่องของ Process และ Material) แต่อาจช่วยได้โดยปรับขนาด Pad ให้เหมาะสม และหลีกเลี่ยงการวาง Component หนักๆ หรือทำคัตเอาท์ (Cutout) ใกล้ๆ BGA ซึ่งทำให้บอร์ดโก่งง่าย
- หากพบปัญหา Voids บ่อยๆ ลองปรึกษาโรงงานให้ปรับ Thermal Profile หรือเปลี่ยนประเภทของ Flux ใน Solder Paste

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **X線検査 (Ekkususen kensa)** - X-Ray Inspection
- **反り (Sori)** - Warpage / Board bending
- **ブリッジ (Burijji)** - Solder Bridging (Short)
- **未はんだ (Mi-handa)** - Unsoldered / Open joint
- **ボイド率 (Boido ritsu)** - Void ratio

## ควิซท้ายบท (Quiz)
**คำถาม:** ปรากฏการณ์ Head-in-Pillow (HiP) ในการบัดกรี BGA มีสาเหตุหลักมาจากอะไร?
<details>
<summary>ดูเฉลย</summary>
**คำตอบ:** เกิดจากการโก่งตัว (Warpage) ของตัวถัง BGA หรือแผ่น PCB เมื่อโดนความร้อนในเตา Reflow ทำให้ Ball ยกตัวขึ้นและไม่หลอมรวมกับ Solder Paste บน PCB
</details>
