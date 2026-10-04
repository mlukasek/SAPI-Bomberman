# SAPI-Bomberman

Port hry Bomberman (Hudson Soft 1983, verze pro Sharp MZ-700) na **Tesla SAPI-1**, sestavu „V“ Libora Lasoty
s barevnou grafikou **CGA-1V**. Zároveň je to test emulátoru SAPIemu pro vývoj softwaru: chyby emulátoru, na
které se při tom narazí, se opravují v SAPIemu (`E:\SAPI_GIT\SAPIemu`).

Neveřejné repo: hra je chráněná autorským právem Hudson Soft.

## Zdroj

- `orig/bomber.asm`, `orig/bomber.mzf`: komentovaný disassembler originálu a originální páska z projektu
  BomberNet (`E:\SAPI_GIT\BomberNet`, commit c88818d; repo autorovi nepatří, slouží jen jako zdroj).
- `orig/bomber.asm` se pasmem přeloží bajt po bajtu stejně jako `orig/bomber.mzf` (ověřeno 2026-10-05).

## Nástroje

- Assembler **pasmo 0.5.3**: `E:\SAPI_GIT\Tools\pasmo-0.5.3\pasmo.exe`.
- Emulátor SAPIemu s MCP serverem: `sapiemu-cli --machine machines/sapi1v.sapi --mcp --mcp-port 8591`.

## Plán portu

Závislosti originálu na MZ-700 a jejich náhrady:

| MZ-700 | Kde | SAPI-1 V |
|---|---|---|
| VRAM D000h / D800h, zapisuje jen `put_vram_char` | 40×25 buněk | CGA-1V na C000h (`OUT 63h,C0h`), EGA režim, buňka 8×8 = 2 bajty × 8 řádků; 320×200 = přesně CGA |
| `game_table`, `title_table` (displejový kód MZ + atribut) | logické kódy buněk | glyfy 8×8 z CGROM MZ-700 (z BomberNet), barvy MZ (8×8 kombinací) na 16 atributů a paletu Bt476 |
| `GETKY` 001Bh (klávesa nebo 0) | 13B2, 1C21, 1F85 | joystick MPH-1V (port 54h) + klávesnice P0/P1 JPR-1V (Consul 262.3, pulzní strobe) |
| `MSTA` 0044h, `MSTP` 0047h, `RATIO` 11A1h | tón | YM3812 na MPH-1V (50h–57h) |
| smyčky zpoždění pro 3,5 MHz | snímek 60,8 ms | VBI CGA-1V (60 Hz) nebo čítač 82C54 na MPH-1V |
| ORG 1200h, zásobník pod 1200h | | CP/M `.COM` od 0100h. Během hry je mapování MAP zapnuté, takže BDOS se nevolá. Návrat do CP/M `OUT 63h,00h` a `JP 0` |

## Potřebné podklady

- **Znakový generátor MZ-700** (CGROM, 4 KB, 8×8 bodů na znak). BomberNet ho čte z
  `~/src/mz-catalog/tools/mzfont/cgrom.bin`. Na tomto PC není, uložit do `orig/cgrom.bin`. Glyfy ZX v BomberNet
  jsou zúžené na 6 bodů, pro CGA (8 bodů) se nehodí.

## Postup

1. `sapi/bomber_sapi.asm` = `orig/bomber.asm` s ORG 0100h, data snímku RAM → `defs`, platformní vrstva
   v `sapi/platform.asm`.
2. Glyfy a barvy: skript `tools/make_tables.py` z tabulek BomberNet.
3. Překlad `build.cmd` → `build/bomber.hex` (Intel HEX pro SAPIemu `load_hex` / Soubor → Nahrát program).
4. Ladění přes MCP (screenshot CGA-1V, joystick, save_state).
