# บทที่ 59: การจำลองความร้อน (Thermal Simulation) และการแปลผลลัพธ์

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในฐานะ Senior การใช้ซอฟต์แวร์จำลองอย่าง Flotherm, Icepak หรือ HyperLynx Thermal อาศัยความเข้าใจเรื่อง Boundary Conditions อย่างถ่องแท้
ค่า "Effective Thermal Conductivity" ของ PCB ขึ้นอยู่กับเปอร์เซ็นต์ของทองแดงในแต่ละชั้น
สมการประมาณการ In-plane ($k_x, k_y$) และ Through-plane ($k_z$) จะต่างกันมหาศาล เนื่องจาก FR4 เป็นฉนวนความร้อน (k ~ 0.25 W/m·K) ในขณะที่ทองแดงนำความร้อนสูงมาก
ดังนั้นใน Simulation ต้องตั้งค่า Orthotropic material properties ให้ถูกต้อง ไม่เช่นนั้นผลลัพธ์จะเพี้ยน

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Garbage In, Garbage Out**: อย่าเชื่อผล Simulation ทันทีถ้าไม่ได้เซ็ต Power Dissipation (Pd) ของชิ้นส่วนให้สมจริง ในหลายกรณี ค่า Worst-case Pd ที่คำนวณได้อาจจะสูงเกินความจริงมากไป (Over-design) ให้ใช้ค่า Typical หรือ 80% ของ Max limit ในการประเมินเบื้องต้น
- **Mockup Testing**: หลังจากได้ผล Simulation ควรทำการวัดเทียบกับบอร์ดต้นแบบด้วย Thermocouple (ติดที่ขอบ IC หรือ T_case) เพื่อดูว่า Correlation Error มีกี่เปอร์เซ็นต์ (ถ้า Error เกิน 15% ต้องกลับไปจูน Model ใหม่)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **熱解析 (Netsukaiseki)**: Thermal Analysis / Simulation
- **境界条件 (Kyoukai Jouken)**: Boundary Conditions
- **実機検証 (Jikki Kenshou)**: Physical testing / Verification with actual device
- **誤差 (Gosa)**: Error / Deviation (ความคลาดเคลื่อน)

## ควิซท้ายบท (End of Chapter Quiz)
**Q: สิ่งใดคือสาเหตุหลักที่ทำให้ผล Thermal Simulation บนแผ่น PCB ผิดพลาดมากที่สุด?**
1. การเลือกสีของชิ้นส่วนในโปรแกรมผิด
2. การใช้ค่า Thermal Conductivity แบบ Isotropic (เท่ากันทุกทิศทาง) สำหรับ PCB
3. การตั้งค่าความละเอียดของ Mesh สูงเกินไป
4. การใช้คอมพิวเตอร์ที่ช้าเกินไป

*เฉลย: 2. เพราะโครงสร้าง PCB เป็นแบบ Orthotropic (มีชั้นทองแดงสลับกับ FR4) ทำให้การนำความร้อนแนวแกน X/Y ดีกว่าแนวแกน Z มาก*
