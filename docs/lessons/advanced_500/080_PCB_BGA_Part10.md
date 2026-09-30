# Lesson 080: BGA DFM/DFA & Inspection (X-Ray, AOI)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
ในมุมมองของการออกแบบเพื่อการผลิตและการประกอบ (DFM/DFA) BGA เป็นแพ็กเกจที่ไม่สามารถใช้สายตาหรือ Automated Optical Inspection (AOI) ตรวจสอบรอยเชื่อมประสาน (Solder joint) ด้านล่างได้ ต้องพึ่งพา Automated X-Ray Inspection (AXI)
- **Pad Design (SMD vs NSMD)**:
  - Non-Solder Mask Defined (NSMD): เปิด Solder mask กว้างกว่า Pad ทองแดง ให้ความยืดหยุ่นของจุดเชื่อมดีกว่า (Reliability สูงกว่า) เป็นที่นิยมใน BGA ส่วนใหญ่
  - Solder Mask Defined (SMD): Solder mask เกยบน Pad ทองแดง ใช้ในแพ็กเกจที่ต้องการการยึดเกาะของ Pad กับ PCB ให้แน่นขึ้น (ลด Pad cratering)
- **Voiding**: การตรวจสอบ X-Ray จะดูเปอร์เซ็นต์ของโพรงอากาศ (Void) ใน Solder ball มาตรฐาน IPC มักยอมรับ Voids ได้ไม่เกิน 25-30% ของพื้นที่หน้าตัดลูกตะกั่ว

## 2. ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **OJT Trick**: อย่าลืมใส่ Fiducial marks (Local fiducials) อย่างน้อย 2 จุดบริเวณมุมทแยงของ BGA เพื่อให้เครื่อง Pick and Place (Mounter) วางชิปได้อย่างแม่นยำ
- **Keep-out Zone**: เว้นระยะห่างรอบๆ BGA ไว้พอสมควร (อย่างน้อย 2-3mm หรือตาม Tool clearance) เพื่อเผื่อพื้นที่ให้หัวฉีด Rework nozzle เข้าไปเป่าลมร้อนได้ในกรณีที่ต้องถอดชิปซ่อม (BGA Rework)

## 3. คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **実装 (Jissou)**: Mounting / Assembly (การประกอบชิ้นส่วนลงบอร์ด)
- **ボイド (Boido)**: Void (โพรงอากาศในรอยเชื่อมตะกั่ว)
- **はんだマスク (Handa masuku)**: Solder mask / Solder resist
- **認識マーク (Ninshiki maaku)**: Fiducial mark
- **リワーク (Riwaaku)**: Rework (การซ่อมแซม ถอดประกอบชิป)

## 4. ควิซท้ายบท (Quiz)
**คำถาม**: ทำไมส่วนใหญ่จึงแนะนำให้ใช้ Pad แบบ NSMD สำหรับ BGA ทั่วไป?
A. เพราะทำให้ผลิต Solder mask ได้ง่ายกว่า
B. ป้องกันปัญหา Solder Wicking ได้ 100%
C. ตะกั่วสามารถเกาะด้านข้างของแผ่นทองแดงได้ ทำให้รอยเชื่อมทนทานต่อแรงเค้นเชิงกลมากขึ้น
D. ลดปัญหาโพรงอากาศ (Voiding) ได้ดีกว่า SMD
**เฉลย**: C. NSMD (Non-Solder Mask Defined) อนุญาตให้ตะกั่วไหลลงมาเกาะที่ขอบด้านข้างของทองแดง (Sidewall) ทำให้ได้ข้อต่อตะกั่วที่แข็งแรงกว่าและยืดหยุ่นกว่าเมื่อเทียบกับ SMD
