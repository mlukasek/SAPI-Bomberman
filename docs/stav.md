# Stav a další kroky

Předávka mezi počítači a sezeními. Nejnovější nahoře.

## Kde jsme (2026-10-07)

- **Vydaná verze 1.0.1** (2026-10-16, oprava šipek): GitHub Release `v1.0.1` se zipem z `tools\release.cmd`.
  Předtím 1.0.0 (2026-10-07). Repo je veřejné.
- **Znakový generátor** MZ-700 (`orig/cgrom.bin`) je odstraněný z repa i z historie
  (`git filter-branch`, hashe commitů se změnily). Lokální kopie je ignorovaná v `orig/`, záloha je
  v `E:\SAPI_GIT\SAPI-Bomberman-private\cgrom.bin`.
- **Emulátor:** hra se zkouší v release SAPIemu 0.3.0 alpha (`E:\SAPI_GIT\SAPIemu-release`). Vývojový SAPIemu
  autor vyvíjí paralelně, nepoužívat ho.
- **Funguje v emulátoru:**
  - celá hra se zvukem;
  - joystick, klávesnice Consul 262.3 i EKL-1;
  - ESC a BREAK zpět do CP/M;
  - při 2 MHz se vejde do snímku i v nejhorším případě (5 bomb, 55 ms z 60,8).
- **Ověřeno na skutečném SAPI-1 V** (autor, 2026-10-07): hra funguje. Podrobnosti, které zatím nikdo cíleně
  neměřil, jsou v `docs/nejasnosti.md`.

## Další kroky

1. **Síťová hra**, až bude síťová karta pro SAPI: `docs/sitova-hra.md`.
2. **Zatočení z půlky políčka**, kam hráče nechá joystick: kolmá šipka nepomůže (pilíř), šipka ve stejné ose
   hráče dorovná. Tak to bylo vždy. Kdyby to vadilo, kolmá šipka by mohla nejdřív dorovnat políčko. Směr
   dorovnání ale není jasný, port nezná směr posledního pohybu joystickem.
3. Drobnosti, kdyby bylo potřeba ještě zrychlit:
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
- **2026-10-07, vydání 1.0.0:**
  - README pro uživatele, dokumentace do `docs/`, snímky obrazovky;
  - znakový generátor pryč z repa i historie (force push), přechod na release emulátoru;
  - repo veřejné, GitHub Release `v1.0.0` se zipem;
  - autor ověřil, že hra funguje na skutečném SAPI-1 V.
- **2026-10-16, šipky v půlce políčka** (předávka ze SAPI-BomberNet, `docs/predavka-klavesnice.md`):
  - jiná šipka během kroku přepsala rozdělané políčko a hráč zůstal v půlce a špatně zatáčel;
  - chyba prokázaná testem `tools/emu/taps.py --fast`: 7 půlek ze 112 kontrol;
  - oprava: nová šipka počká v `kdir_next` na celé políčko; po ní 0 půlek, Consul i EKL-1;
  - herní logika beze změny: 494 snímků scénářů a 60 obrazovek klávesnice shodných se starou verzí;
  - joystick na titulku ověřený: palba spustí hru, držená palba bombu nepoloží.
- **2026-10-16, vydání 1.0.1:**
  - oprava šipek;
  - spuštění v SAPIemu 0.3.0 volbou 3 (volba 1 se zasekne);
  - hra je u autora na RAM disku A: release emulátoru;
  - poznámky k vydání 1.0.0 na GitHubu opravené na boot 3.

## Chyby emulátoru

Poznatky k MCP jsou v `docs/vyvoj.md` (Pasti).

- **SAPIemu 0.3.0 alpha, `sapi1v.sapi`, boot volbou 1 visí** (zjištěno 2026-10-16, nahlášeno autorovi).
  - Výpis se zastaví na „LST: CENTRONIX“ a BIOS stojí na E6F0–E6F4 ve smyčce `IN A,(3Ch)` / `AND 40h` /
    `JP Z`: čeká na bit 6 řadiče disket RPD-1 („B,C: RPD1“). Ten v sestavě V není.
  - `io_read` portu 3Ch přes MCP přitom vrací E6h (bit 6 nastavený).
  - Volba 3 (A: stejný RAM disk, B:, C: IDE) bootuje normálně.
  - Vývojový SAPIemu 2026-10-05 volbu 1 nabootoval. Hru se to netýká.
  - Skripty `tools/emu` teď bootují volbou 3 a výsledek kontrolují. Dřív bootovaly volbou 1 bez kontroly, měření
    to ale neovlivnilo: hru nahrávají rovnou na 0100h a CP/M nepotřebují.
