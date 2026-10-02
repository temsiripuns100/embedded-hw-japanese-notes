# Lesson 063: PCB Decoupling Part 3 - PDN Impedance Profile & Anti-resonance (PDNインピーダンスプロファイルと反共振)

## 1. ทฤษฎีวิศวกรรมเชิงลึก (高度なエンジニアリング理論)

เมื่อเรานำ Capacitor หลายๆ ค่า (Multi-decade Capacitors) มาต่อขนานกันเพื่อครอบคลุมความถี่ (Broadband Decoupling) กราฟ Impedance Profile มักจะไม่แบนเรียบเสมอไป แต่จะเกิดยอดแหลมที่เรียกว่า **Anti-resonance Peaks** 

สมการของความถี่ที่เกิด Anti-resonance ($f_{anti}$) ระหว่าง Capacitor 2 กลุ่มคือ:
$$ f_{anti} = \frac{1}{2\pi\sqrt{ESL_1 \cdot C_2}} $$
โดยที่ $ESL_1$ คือ ESL (รวม Mounting ESL) ของ Capacitor ตัวใหญ่ และ $C_2$ คือ Capacitance ของ Capacitor ตัวเล็ก

ความสูงของยอด Peak (Peak Impedance, $Z_{peak}$) ขึ้นอยู่กับค่าความต้านทาน (ESR) ในวงจร:
$$ Z_{peak} \approx \sqrt{\frac{ESL_1}{C_2}} $$
หาก $Z_{peak} > Z_{target}$ จะทำให้เกิด Noise Voltage ที่ความถี่นั้นเกินสเปก

## 2. ทริคหน้างาน OJT แบบ Step-by-step (現場の実践テクニック)
การทำ Damping เพื่อกด Anti-resonance peak เป็นทักษะขั้นสูง (Senior Level OJT)

**Step-by-step:**
1. **วิเคราะห์กราฟ Impedance vs Frequency**: ดึงข้อมูล Z-parameters หรือใช้ PDN Tool จำลอง Profile
2. **หาจุด Peak**: สังเกตความถี่ที่กราฟทะลุ $Z_{target}$
3. **ลด $ESL_1$**: ปรับปรุง Layout ของ Bulk/Mid-frequency Capacitor วางให้ใกล้ IC ขึ้น เพิ่ม Vias
4. **Controlled ESR**: บางครั้งการจงใจใช้ Capacitor ที่มี ESR สูงขึ้นนิดหน่อย (เช่น Tantalum แทนที่จะเป็น Ceramic ทั้งหมด) หรือใส่ตัวต้านทานอนุกรมขนาดจิ๋ว จะช่วยลด $Q$-factor ของ LC Circuit และดึง $Z_{peak}$ ให้ต่ำลงได้ (Targeted Damping)

## 3. คำศัพท์ญี่ปุ่นเชิงเทคนิคสำหรับการตรวจแบบ (検図用語)

- **反共振 (Hankoushin)**: Anti-resonance
- **インピーダンスプロファイル (Inpiidansu purofairu)**: Impedance Profile
- **ダンピング (Danpingu)**: Damping
- **Q値 (Q-chi)**: Quality Factor
- **広帯域デカップリング (Koutaiiki dekappuringu)**: Broadband Decoupling

## 4. ควิซวิเคราะห์ปัญหาระดับยาก (高度な問題分析クイズ)

**คำถาม (問題):**
ในการวิเคราะห์ PDN ด้วยซอฟต์แวร์ PI (Power Integrity) พบว่ามี Anti-resonance peak ที่ 150 MHz ซึ่งทะลุ $Z_{target}$ วิศวกรจูเนียร์เสนอว่าให้ "เพิ่ม MLCC $1nF$ ไปอีก 20 ตัวเพื่อกด Impedance ลง" วิธีนี้ถูกต้องหรือไม่? อธิบายเชิงลึก

**เฉลยและคำอธิบาย (解答と解説):**
การแก้ปัญหาด้วยวิธีนี้ **มักจะไม่ได้ผลและอาจทำให้แย่ลง**
การเพิ่ม Capacitor เล็กๆ ($1nF$) เข้าไป จะเป็นการลด Impedance ที่ความถี่สูงมาก (High-frequency range) แต่มันจะไปทำปฏิกิริยากับ ESL ของ Capacitor เดิม ทำให้ **Anti-resonance peak ขยับความถี่ (Shift frequency)** หรือสร้าง Peak ใหม่ที่ความถี่อื่น ซึ่งอาจไปตรงกับ Clock Frequency ของระบบ ทำให้ระบบพังได้
**วิธีแก้ระดับ Senior:** 
ต้องลด Mounting Inductance ($ESL_{mount}$) ของ Capacitor กลุ่มเดิมก่อน ถ้าทำเต็มที่แล้ว Peak ยังสูง ต้องใช้เทคนิค **Damping** โดยการใช้ Capacitor ที่มี **Controlled ESR** (เช่น เลือก MLCC ที่มี ESR ประมาณ $100 m\Omega$) เพื่อกินพลังงาน (Dissipate energy) ที่จุด Resonance และทำให้ยอด Peak เรียบ (Flat Impedance Profile)
