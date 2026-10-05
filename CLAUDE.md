# SAPI-Bomberman – kontext projektu

Port Bombermana (Hudson Soft, Sharp MZ-700) na Tesla SAPI-1, sestavu V (JPR-1V, RAM-1V, CGA-1V, MPH-1V), jako
CP/M `.COM`. Autor: Martin Lukášek (mlukasek). Komunikace s autorem **česky**.

## Kde co je

- **Začni tady:** `README.md`. Je v něm stav, postup na novém počítači, paměť a porty, jak je port udělaný,
  vykreslování, rychlost, ověřování, pasti a plán síťové hry.
- **Zdroj:** `sapi/bomber_sapi.asm` (disassembler originálu, změny označené `SAPI:`), `sapi/platform.asm` (HW
  vrstva), `sapi/tables.asm` (generuje `tools/make_tables.py`, needitovat). Originál v `orig/`.
- **Emulátor:** repo `..\SAPIemu` (sestava `machines/sapi1v.sapi`, MCP, dokumentace desek v `docs/desky/`).
  Poznámky k portu jsou i tam v `docs/software/bomberman.md`. Chyby emulátoru se opravují tam.
- **BomberNet** (`..\BomberNet`): zdroj disassembleru a síťová verze pro MZ/ZX. Repo autorovi nepatří.

## Pravidla

- **Jazyk:** kód a komentáře v asm a skriptech **anglicky**, dokumentace **česky**.
- **Styl asm:** pasmo 0.5.3. Komentáře originálu s adresami MZ (`; 1D46`) zachovat. Každou změnu označit
  `SAPI:` a popsat, co dělal MZ.
- **Herní logika se nesmí změnit.** Hra čte `draw_buffer` (kolize, oheň), takže jeho obsah musí být
  v každém okamžiku stejný jako na MZ.
  - Každou změnu ověřit porovnáním obrazovek se starou verzí v každém snímku (`tools/emu`, README → Vývoj
    a ověřování).
  - Nový zápis do `draw_buffer` nebo `map_layer` musí být označený pro `flush_screen` (`draw_addr_w`,
    `map_addr_w`, `mark2`, `mark_range`).
- **Měřit v emulátoru**, nehádat: `bench.py` (práce snímku), `prof.py` (rozpad po rutinách). Cíl: snímek
  60,8 ms i při CPU 2 MHz.
- **Pasti:**
  - unární minus v pasmo neguje celý zbytek výrazu (`-1*40+1` = −41, `-1+2` = −3), další pasti pasmo jsou
    v `..\SAPIemu\CLAUDE.md`;
  - `read_memory` vrací nejvýš 4096 bajtů;
  - `cycles` v MCP počítá takty 4 MHz;
  - podrobně v README (Pasti).
- **Git:** lokální commity průběžně, push jen na výslovné vyžádání (jako v SAPIemu). Na konec commitu patří
  řádek Co-Authored-By.
- **Reálný HW:** autor ho má. Otázky k ověření sbírat v README do „Nejasností k ověření na HW“.
- **Disk C: emulátoru** (`..\SAPIemu\work\ide\sapi_hdd.img`) je mimo repo. Hru na něj nahrávat podle README
  (Spuštění) a emulátor pak vypnout přes `power off`, ne zabít.
