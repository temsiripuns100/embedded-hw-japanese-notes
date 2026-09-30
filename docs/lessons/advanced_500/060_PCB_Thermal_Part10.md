# บทที่ 60: การรีวิวการออกแบบความร้อน (Thermal Design Review - 検図) และ Troubleshooting

## ทฤษฎีวิศวกรรมเชิงลึก (In-depth Engineering Theory)
ในขั้นตอน Design Review, Senior Engineer ต้องทำหน้าที่ Design Rule Checking (DRC) แบบใช้สมอง (Manual Check) สำหรับ Thermal issues โดยเฉพาะ
การประเมิน Thermal Derating Curve ของส่วนประกอบที่สำคัญ (เช่น MOSFET, Diode, LDO) ต้องคำนึงถึง Ambient Temperature สูงสุดที่เป็นไปได้ (Ta_max)
และพิจารณา Tj (Junction Temperature) ว่าต้องมี Margin ต่ำกว่า Tj_max ของผู้ผลิตอย่างน้อย 15-20°C เพื่อรับประกัน Reliability ตามมาตรฐานอุตสาหกรรม (เช่น Automotive AEC-Q)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **Checklist สำหรับ 検図 (Kenzu)**:
  1. ดูการแยกระหว่างส่วนที่มีกำลังสูง (Power section) กับส่วนที่อ่อนไหวต่อความร้อน (Sensitive analog/RF section) เช่น การทำ Thermal slit (เซาะร่อง PCB เพื่อตัดการนำความร้อน)
  2. ตรวจสอบ Mounting hole ว่าสามารถเป็นเส้นทางระบายความร้อนสู่แชสซี (Chassis) ได้หรือไม่
- **Thermal IR Camera**: เมื่อผลิตบอร์ดรุ่นทดลองออกมา การใช้กล้องถ่ายภาพความร้อน (Thermographic camera) ควรกระทำเมื่อทาสีดำทับ (Black paint/tape) บนพื้นผิวที่เป็นโลหะเงา หรือปรับค่า Emissivity (ε) ให้ถูกต้อง ไม่เช่นนั้นค่าอุณหภูมิที่อ่านได้จะสะท้อนสิ่งแวดล้อมแทน

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **検図 (Kenzu)**: Design Review / Drawing check
- **熱対策 (Netsutaisaku)**: Thermal countermeasures (มาตรการจัดการความร้อน)
- **ディレーティング (Direetingu)**: Derating
- **信頼性 (Shinraisei)**: Reliability

## ควิซท้ายบท (End of Chapter Quiz)
**Q: การใช้กล้องถ่ายภาพความร้อน (IR Camera) วัดชิ้นส่วนที่มีพื้นผิวโลหะสะท้อนแสงบน PCB มักจะเกิดปัญหาอะไร หากไม่มีการปรับตั้งค่าใดๆ?**
1. กล้องจะพังทันที
2. อุณหภูมิที่วัดได้จะต่ำกว่าความเป็นจริงมาก หรือสะท้อนอุณหภูมิร่างกายผู้ส่อง
3. อุณหภูมิที่วัดได้จะสูงทะลุสเกล
4. ภาพจะกลายเป็นสีขาวดำทั้งหมด

*เฉลย: 2. โลหะเงาจะมีการแผ่รังสี (Emissivity) ต่ำ ทำให้มันสะท้อนรังสีอินฟราเรดจากสิ่งแวดล้อม (เช่น ตัวคน) แทนที่จะวัดความร้อนที่ตัวมันเอง*
