# FPGA DSP Slices เจาะลึกระดับ Senior: Part 6 - Advanced Pipelining & Retiming (高度なパイプライン化とリタイミング)

## ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)
ในการออกแบบระบบความถี่สูง (High-frequency design) การใช้ DSP Slices ไม่ได้หยุดแค่การคูณและบวก แต่ต้องพิจารณา Internal Registers ของ DSP Slice อย่างละเอียด เช่น A, B, M, และ P registers การเปิดใช้ Pipeline registers เหล่านี้จะช่วยลด Logic delay และทำให้ $F_{max}$ พุ่งทะลุขีดจำกัด การทำ Retiming ผ่าน Synthesis tool (เช่น `synth_design -retiming`) ต้องอาศัยการตั้งค่าที่ถูกต้องเพื่อให้ tool สามารถดึง register เข้ามาใน DSP block ได้

## ทริคหน้างาน OJT (OJT現場のコツ)
เวลา Synthesis แล้วไม่ผ่าน Timing (Timing violation) อย่าเพิ่งไปแก้ Logic ให้ยุ่งยาก ให้เช็คดูก่อนว่าคุณได้ลง Register ที่ทางเข้า (Inputs) และทางออก (Outputs) ของวงจรคำนวณแล้วหรือยัง ถ้ายัง ลองเติมเข้าไปแล้วปล่อยให้ Tool ทำ Register Balancing การเขียนโค้ดที่ "Synthesis-friendly" คือการประกาศ Register ไว้ลอยๆ หลังการคูณ เพื่อให้ Tool ดูดมันเข้าไปใน DSP Slice (DSP48E1/E2)

## คำศัพท์ภาษาญี่ปุ่นที่ใช้ในการตรวจแบบ (検図用日本語用語)
- **パイプライン段数 (Pipeline Dansuu):** จำนวนสเตจของ Pipeline (Number of pipeline stages)
- **クリティカルパス (Kuritikaru Pasu):** Critical Path
- **レジスタの配置 (Rejisuta no Haichi):** การวางตำแหน่ง Register (Register placement)
- **タイミング制約 (Taimingu Seiyaku):** Timing constraints
- **リタイミング (Retaimingu):** Retiming

## ควิซท้ายบท (確認テスト)
**คำถาม:** การเปิดใช้งาน M-register ภายใน DSP Slice ส่งผลต่อสิ่งใดมากที่สุด?
1. ลดจำนวน LUT ที่ใช้
2. เพิ่มความเร็วสัญญาณนาฬิกาสูงสุด ($F_{max}$) โดยแบ่ง Delay ของตัวคูณ
3. ลดการกินไฟแบบ Static Power
*เฉลย:* 2. การใช้ M-register เป็นการคั่นกลางระหว่างตัวคูณและตัวบวก ทำให้ Critical path สั้นลง ส่งผลให้ทำงานที่ความถี่สูงขึ้นได้
