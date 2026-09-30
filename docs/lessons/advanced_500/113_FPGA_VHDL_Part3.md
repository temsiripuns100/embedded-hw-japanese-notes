# Lesson 113: Clock Domain Crossing (CDC) Techniques

## ทฤษฎีวิศวกรรมเชิงลึก (Deep Engineering Theory)
Clock Domain Crossing (CDC) เป็นสาเหตุอันดับหนึ่งของความล้มเหลวแบบสุ่มในระบบจริง การส่งสัญญาณระหว่าง Clock Domains ที่ไม่สัมพันธ์กัน (Asynchronous) จะทำให้เกิด Metastability
วิธีแก้สำหรับ Single-bit คือการใช้ 2-stage หรือ 3-stage Synchronizer
สำหรับ Multi-bit ต้องใช้วิธี Gray Code Handshake หรือ Asynchronous FIFO ห้ามส่งสัญญาณหลายบิตผ่าน Synchronizer ธรรมดาเด็ดขาดเพราะจะเกิด Data Coherency Issue (Data Skew)

## ทริคหน้างาน OJT (On-the-Job Training Tricks)
- **MTBF Calculation:** ทำความเข้าใจ Mean Time Between Failures สำหรับระบบความปลอดภัยสูง
- **CDC Tool Check:** ห้ามปล่อยผ่าน Warnings จาก CDC Analysis Tools (เช่น SpyGlass) เด็ดขาด
- **False Path:** อย่าลืมใส่คำสั่ง `set_false_path` หรือ `set_clock_groups` ในไฟล์ SDC สำหรับสัญญาณที่มี Synchronizer แล้ว เพื่อให้เครื่องมือไม่เสียเวลาวิเคราะห์ Timing

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図 - Kenzu)
- **非同期 (Hidouki):** Asynchronous (อซิงโครนัส)
- **メタスタビリティ (Metasutabiriti):** Metastability (ความไม่เสถียร)
- **クロック乗り換え (Kurokku Norikae):** Clock Domain Crossing (CDC)
- **誤動作 (Godosah):** Malfunction (การทำงานผิดปกติ)

## ควิซท้ายบท (Quiz)
1. เหตุใดจึงไม่สามารถใช้ 2-stage Synchronizer กับข้อมูลขนาด 8-bit โดยตรงได้?
2. จงอธิบายความหมายของ クロック乗り換え ในบริบทของการออกแบบชิป
