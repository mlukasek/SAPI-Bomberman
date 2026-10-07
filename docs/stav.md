# Stav a další kroky

Předávka mezi počítači a sezeními. Nejnovější nahoře.

## Kde jsme (2026-10-07)

- **Verze 1.0.0** připravená k vydání: `tools\release.cmd` → `build\SAPI-Bomberman-1.0.0.zip`.
- **Repo jde na veřejnost.** Znakový generátor MZ-700 (`orig/cgrom.bin`) je odstraněný z repa i z historie
  (`git filter-branch`, hashe commitů se změnily). Lokální kopie je ignorovaná v `orig/`, záloha je
  v `E:\SAPI_GIT\SAPI-Bomberman-private\cgrom.bin`.
- **Emulátor:** hra se zkouší v release SAPIemu 0.3.0 alpha (`E:\SAPI_GIT\SAPIemu-release`). Vývojový SAPIemu
  autor vyvíjí paralelně, nepoužívat ho.
- **Funguje v emulátoru:**
  - celá hra se zvukem;
  - joystick, klávesnice Consul 262.3 i EKL-1;
  - ESC a BREAK zpět do CP/M;
  - při 2 MHz se vejde do snímku i v nejhorším případě (5 bomb, 55 ms z 60,8).
- **Na skutečném HW nevyzkoušeno.** Seznam otázek: `docs/nejasnosti.md`.

## Další kroky

1. **Vydání 1.0.0:**
   - zveřejnit repo;
   - pushnout přepsanou historii (force) nebo založit nové repo, viz `docs/rozhodnuti.md`;
   - tag `v1.0.0` a GitHub Release se zipem.
2. **Vyzkoušet na skutečném SAPI-1** (`docs/nejasnosti.md`).
3. **Síťová hra**, až bude síťová karta pro SAPI: `docs/sitova-hra.md`.
4. Drobnosti, kdyby bylo potřeba ještě zrychlit:
   - `draw_hud` jen při změně skóre a času (asi 1,8 ms za snímek);
   - předpočítané F-number místo dělení v `tone_fnum` (asi 0,5 ms na pípnutí);
   - vypršení času trvá jeden snímek 70 ms (zmizí všechny cihly, překresluje se celá obrazovka).

## Historie

- **2026-10-05, začátek:**
  - rozbor originálu z BomberNet, plán portu;
  - repo založené, překlad originálu pasmem bajt po bajtu ověřený.
- **2026-10-05, první hratelná verze:**
  - CGA-1V, YM3812, 82C54, joystick, Consul, ESC/BREAK;
  - jediná chyba při ladění byla v portu: `MSTA` měnil IX, který hra drží během pípání.
- **2026-10-05, Consul:** šipky po celých políčkách. Dřív mohl hráč při rychlém ťukání zůstat v půlce
  políčka.
- **2026-10-05, zrychlení:**
  - porovnávají se jen kreslená místa, zdi jsou v mapě, titulek se kreslí jednou;
  - rychlejší kreslení buněk a výbuchů, pípání bez zastavení hry;
  - při 2 MHz z 57–60 ms na 9–12 ms v klidu, výbuch pěti bomb ze 100–180 ms na nejvýš 55 ms.
- **2026-10-05, klávesnice:**
  - ACK jako MikroMon, takže funguje EKL-1, i její šipky WordStar;
  - stisk, který spustí hru, už bombu nepoloží.
- **2026-10-05, ověřování:**
  - měřicí skripty `tools/emu` (MCP z Pythonu).
  - První porovnání obrazovek bylo neplatné: `read_memory` vrací nejvýš 4096 bajtů a vracelo chybový text.
  - Opravené porovnání každého snímku našlo chybu pravého sloupce horního ramene výbuchu (pasmo: unární minus).
    Opraveno, pak všechny obrazovky shodné.
- **2026-10-07, příprava vydání 1.0.0:**
  - README pro uživatele, dokumentace do `docs/`, snímky obrazovky;
  - znakový generátor pryč z repa i historie, přechod na release emulátoru.

## Chyby emulátoru

Zatím žádná. Poznatky k MCP jsou v `docs/vyvoj.md` (Pasti).
