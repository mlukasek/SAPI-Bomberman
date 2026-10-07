# Změny

## 1.0.0 (2026-10-07)

První vydání. Bomberman z MZ-700 na SAPI-1 V (JPR-1V, RAM-1V, CGA-1V, MPH-1V) jako `BOMBER.COM` pro CP/M.

- Hra je stejná jako na MZ-700: herní kód se nezměnil.
  - Vykreslování a zvuk jsou přepsané pro rychlost se stejným výsledkem.
  - Ověřeno v emulátoru porovnáním obrazovky v každém snímku s dřívější verzí.
- **Grafika:** CGA-1V 320×200, znaky a barvy MZ-700.
- **Zvuk:** YM3812 na MPH-1V, tóny hrají vedle hry.
- **Rychlost:** pevný snímek 60,8 ms i při procesoru 2 MHz, i při výbuchu pěti bomb najednou.
- **Ovládání:**
  - joystick Atari na MPH-1V (pohyb a bomba zároveň);
  - klávesnice Consul 262.3 (i bez úpravy 7474) a EKL-1: šipkou jedno políčko na stisk, mezerník bomba;
  - ESC nebo BREAK vrátí do CP/M;
  - stisk, kterým se spustí hra, bombu nepoloží.
- Ověřeno na skutečném SAPI-1 V (autor, 2026-10-07) a v SAPIemu 0.3.0 alpha.

Vývoj před vydáním (2026-10-05):
- první hratelný převod;
- šipky Consulu po celých políčkách;
- zrychlení vykreslování (snímek při 2 MHz 9–12 ms místo 57–60 ms) a pípání bez zastavení hry;
- EKL-1;
- opravené rameno výbuchu z rozpracované verze (pasmo, unární minus).

Podrobnosti: `docs/stav.md`.
