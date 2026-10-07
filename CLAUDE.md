# SAPI-Bomberman – kontext projektu

Port Bombermana (Hudson Soft, Sharp MZ-700) na Tesla SAPI-1, sestavu V (JPR-1V, RAM-1V, CGA-1V, MPH-1V), jako
CP/M `.COM`. Autor: Martin Lukášek (mlukasek). Komunikace s autorem **česky**. Repo je veřejné (od verze 1.0.0).

## Kde co je

- **Začni tady:** `docs/stav.md` (stav, další kroky, historie).
- `README.md` je pro uživatele.
- **Dokumentace pro vývoj:**
  - `docs/technika.md`: jak je port udělaný, paměť, porty, rychlost;
  - `docs/vyvoj.md`: nový počítač, překlad, emulátor, skripty, ověřování, vydání, pasti;
  - `docs/rozhodnuti.md`, `docs/sitova-hra.md`, `docs/nejasnosti.md`.
- **Zdroj:**
  - `sapi/bomber_sapi.asm`: disassembler originálu, změny označené `SAPI:`;
  - `sapi/platform.asm`: HW vrstva;
  - `sapi/tables.asm`: generuje `tools/make_tables.py`, needitovat;
  - originál v `orig/`.
- **Emulátor:** release SAPIemu v `..\SAPIemu-release` (0.3.0 alpha, sestava `machines/sapi1v.sapi`, MCP).
  **Vývojový `..\SAPIemu` nepoužívat ani neměnit**, autor ho vyvíjí paralelně. Chyby emulátoru zapsat
  a nahlásit autorovi.
- **BomberNet** (`..\BomberNet`): zdroj disassembleru a síťová verze pro MZ/ZX. Repo autorovi nepatří.

## Pravidla

- **Jazyk:** kód a komentáře v asm a skriptech **anglicky**, dokumentace **česky**.
- **Styl asm:** pasmo 0.5.3. Komentáře originálu s adresami MZ (`; 1D46`) zachovat. Každou změnu označit
  `SAPI:` a popsat, co dělal MZ.
- **Herní logika se nesmí změnit.** Hra čte `draw_buffer` (kolize, oheň), takže jeho obsah musí být
  v každém okamžiku stejný jako na MZ.
  - Každou změnu ověřit porovnáním obrazovek se starou verzí v každém snímku (`docs/vyvoj.md`).
  - Nový zápis do `draw_buffer` nebo `map_layer` musí být označený pro `flush_screen` (`draw_addr_w`,
    `map_addr_w`, `mark2`, `mark_range`).
- **Měřit v emulátoru**, nehádat: `tools/emu/bench.py` (práce snímku), `prof.py` (rozpad po rutinách). Cíl:
  snímek 60,8 ms i při CPU 2 MHz.
- **Pasti** (podrobně v `docs/vyvoj.md`):
  - unární minus v pasmo neguje celý zbytek výrazu (`-1*40+1` = −41, `-1+2` = −3);
  - `read_memory` vrací nejvýš 4096 bajtů;
  - `cycles` v MCP počítá takty 4 MHz.
- **Autorská práva:** repo je veřejné, znakový generátor MZ-700 (`orig/cgrom.bin`, © Sharp) do něj nepatří
  (je v `.gitignore`). Ani jiné ROM a cizí dumpy necommitovat.
- **Git:** lokální commity průběžně, push jen na výslovné vyžádání. Na konec commitu patří řádek
  Co-Authored-By.
- **Zápis poznatků:** důležité věci zapisovat do `docs/` (na projektu se pracuje z více počítačů), stav
  a historii do `docs/stav.md`, rozhodnutí do `docs/rozhodnuti.md`.
- **Reálný HW:** autor ho má. Otázky k ověření sbírat v `docs/nejasnosti.md`.
- **Disk C: emulátoru** (`work\ide\sapi_hdd.img` vedle exe emulátoru) je mimo repo. Hru na něj nahrávat
  podle `docs/vyvoj.md` a emulátor pak vypnout přes `power off`, ne zabít.
