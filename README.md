#hackpad 
## show rather then tell 
### used xiao  rp2040 , 16 keys ,roatary incoder ,  and some stuff from my  side
<img width="1600" height="1600" alt="hackpad16_back" src="https://github.com/user-attachments/assets/34f5a0dc-c1e5-457e-9f68-da388b1ca364" /><img width="1754" height="1241" alt="hackpad16_schematic_preview" src="https://github.com/user-attachments/assets/30f209fe-e5d3-442a-a576-86df51ac5ee3" /><img width="1772" height="962" alt="hackpad16_pcb_preview" src="https://github.com/user-attachments/assets/23a88b0f-6ca2-4040-93f9-4c9f7bc979d1" />
<img width="378" height="378" alt="hackpad16_front" src="https://github.com/user-attachments/assets/08f3ddca-d669-48c4-a3d0-2340478d29da" />
<img width="378" height="378" alt="hackpad16_back" src="https://github.com/user-attachments/assets/ea7ced58-6b6c-46be-a7af-6f5e4cbe50f7" />

[hackpadSCH.pdf](https://github.com/user-attachments/files/33123543/hackpadSCH.pdf)
<img width="303" height="164" alt="Screenshot 2026-10-06 224635" src="https://github.com/user-attachments/assets/b18df49a-abdf-4cd5-b485-684902a4ba46" />
<img width="175" height="148" alt="Screenshot 2026-10-06 003650" src="https://github.com/user-attachments/assets/3e1ae1c2-5d79-4514-8870-38db9d76aa41" />
<img width="326" height="332" alt="Screenshot 2026-10-05 235646" src="https://github.com/user-attachments/assets/77430444-de18-49f5-8af0-a224e316d00a" />


| Component | What it do | GPIO | Receipts |
| :--- | :--- | :---: | :--- |
| Display Mux | SDA / SCL | `GPIO8` / `GPIO9` | pull-ups are your friends! |
| Neon Lighting | WS2812B Data | `GPIO4` | requires 5V logic shifts |
| The Dial | Encoder A / B / SW | `GPIO5` / `GPIO6` / `GPIO7` | uses quadrature ISR |
| Top Keys | SW1 / SW2 | `GPIO1` / `GPIO2` | crisped debounced |
| Mid Keys | SW3 / SW4 / SW7 | `GPIO42` / `GPIO41` / `GPIO40` | crisped debounced v2 |

| Bot Keys | SW6 / SW8 / SW9 | `GPIO39` / `GPIO38` / `GPIO21` | swap these keys if they do dumb things |
rt tracking your Spotify streams?
