# hackpad:
UltimateEdition Macro pad powered by an SEEED XIAO rp2040 only huh
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
