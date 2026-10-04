# SAPI-Bomberman

Port hry Bomberman (Hudson Soft 1983, verze pro Sharp MZ-700) na **Tesla SAPI-1**, sestavu „V“ Libora Lasoty
s barevnou grafikou **CGA-1V**. Zároveň je to test emulátoru SAPIemu pro vývoj softwaru: chyby emulátoru, na
které se při tom narazí, se opravují v SAPIemu (`E:\SAPI_GIT\SAPIemu`).

Neveřejné repo: hra je chráněná autorským právem Hudson Soft, znakový generátor MZ-700 (`orig/cgrom.bin`)
právem Sharp.

## Stav (2026-10-05)

Hra je hratelná v SAPIemu se sestavou `machines/sapi1v.sapi`: titulní obrazovka, hra, zvuk, joystick
i klávesnice, návrat do CP/M. Na skutečném HW zatím nevyzkoušeno.

## Hardware

- JPR-1V (Z80), RAM-1V s registrem MAP na 63h, CP/M;
- CGA-1V na C000h při MAP1 = MAP2 = H (`OUT 63h,C0h`), autorovo nastavení propojek;
- MPH-1V na 50h: 82C54 (časování), YM3812 (zvuk), joystick Atari na K4 (OVL);
- klávesnice Consul 262.3 na JPR-1V (bez úpravy 7474).

## Ovládání

| Akce | Joystick (K4) | Klávesnice Consul |
|---|---|---|
| pohyb | páka | šipky C1–C4 (jeden stisk = jedno políčko) |
| bomba, start hry | palba (FL) | mezerník |
| konec, návrat do CP/M | | ESC nebo BREAK |

V SAPIemu: joystick z gamepadu, nebo šipky a mezerník jako joystick (Ctrl+F8).

## Spuštění

1. `build.cmd` → `build\bomber.com` a `build\bomber.hex` (od 0100h).
2. V SAPIemu se sestavou SAPI-1 V: v CP/M Soubor → Nahrát program do paměti (`bomber.hex`), pak
   `SAVE 47 BOMBER.COM` (počet stránek vypíše `build.cmd`) a `BOMBER`.
3. Přes MCP: `load_binary` souboru `bomber.com` na 0100h a `set_registers` s `pc` = 0100h, když CP/M čeká na
   příkaz.

## Soubory

- `orig/bomber.asm`, `orig/bomber.mzf`: komentovaný disassembler originálu a originální páska z projektu
  BomberNet (`E:\SAPI_GIT\BomberNet`, commit c88818d; repo autorovi nepatří, slouží jen jako zdroj).
  `orig/bomber.asm` se pasmem přeloží bajt po bajtu stejně jako `orig/bomber.mzf` (ověřeno 2026-10-05).
- `orig/cgrom.bin`: znakový generátor MZ-700 (4 KB, 512 znaků 8×8, bit 0 vlevo). Kopie `CGROM.ROM` z emulátoru
  MZ8Emu (`E:\@Prebrat\prebrat_z_USB\Sharp\MZ8Emu\ROM`). S ním dává `make_zx_tables.py` z BomberNet bajt po
  bajtu stejné tabulky jako v BomberNet, je to tedy tentýž generátor.
- `sapi/bomber_sapi.asm`: `orig/bomber.asm` s ORG 0100h. Změny jsou označené `SAPI:`, komentáře s adresami
  jsou adresy originálu na MZ-700.
- `sapi/platform.asm`: náhrada monitoru a VRAM MZ-700 (CGA-1V, 82C54, YM3812, vstup).
- `sapi/tables.asm`: dlaždice pro CGA-1V, generuje `tools/make_tables.py` (needitovat).

## Jak je port udělaný

| MZ-700 | SAPI-1 V |
|---|---|
| VRAM D000h, atributy D800h, zapisuje jen `put_vram_char` | CGA-1V v režimu EGA: buňka 8×8 = 2 bajty × 8 řádků, 40×25 buněk = 320×200 |
| `game_table`, `title_table` (displejový kód MZ + atribut) | 145 předkreslených dlaždic po 16 bajtech (`tiles`) a tabulky čísel dlaždic `game_idx`, `title_idx` |
| barvy MZ: 8 barev popředí, hra má pozadí vždy černé | atribut CGA = barva popředí MZ, paleta Bt476: index = atribut × 2 + bod, COLMASK 1Fh |
| `GETKY` 001Bh | `key_fire` (palba nebo mezerník) a `key_dir` (páka nebo šipky) |
| `MSTA`, `MSTP`, `RATIO` (8253, tón 1108800 / RATIO Hz) | YM3812 kanál 0, F-number a blok se počítají z RATIO |
| `beep`: smyčka DJNZ × C | C jednotek po 0,95 ms (82C54 čítač 0, režim 3, 1055 Hz) |
| `delay`: smyčka 5000h (150 ms) | 159 jednotek 82C54 |
| žádné časování snímku (rychlost dává zátěž CPU, 60,8 ms) | `frame_wait`: čítač 2 v režimu 2 nastavuje F2 každých 60,8 ms |
| ORG 1200h, zásobník pod programem | CP/M `.COM` od 0100h, vlastní zásobník za programem. Během hry je CGA namapovaná přes RAM C000–FFFF, BDOS se nevolá |

- **Klávesnice Consul 262.3** posílá STROBE jen jako pulz 1 ms a nemá autorepeat. Program ji čte ve všech
  čekacích smyčkách (`poll_key`).
  - **Šipka** udělá krok a pak pokračuje, dokud hráč nestojí na celém políčku. Na celém políčku je souřadnice
    v ose pohybu lichá. Jeden stisk = jedno políčko. Stojí-li hráč v půlce políčka (po joysticku), stisk ho
    dorovná. Stisk téže šipky během pohybu přidá jedno políčko, takže autorepeat PC v emulátoru dává plynulý pohyb.
  - **Mezerník** se bere jako držený 4 snímky.
  - Dřív se i šipka brala jako držená 4 snímky. Když přišel další stisk dřív, než doběhly (rychlé ťukání,
    autorepeat), mohl hráč zůstat v půlce políčka a nemohl zatočit (autor, 2026-10-05).
- **Pohyb a bomba zároveň:** originál volá `GETKY` zvlášť pro pohyb a pro bombu a dostane jednu klávesu. Port
  čte palbu a páku zvlášť, takže s joystickem jde chodit a pokládat bomby zároveň.
- **Zrychlení:** `composite_map` (překrytí mapy přes buffer) a `flush_screen` (porovnání s obrazem) jsou
  přepsané se stejným výsledkem. Na MZ-700 zabíraly většinu snímku.
- **Výška tónu:** hodiny 8253 1,1088 MHz odpovídají evropskému MZ-700 (PAL). Japonský model má 0,895 MHz, tóny
  by byly o 24 % hlubší.

### Rychlost (změřeno v SAPIemu, 2026-10-05)

| CPU | Práce snímku v klidu | Snímek |
|---|---|---|
| 4 MHz (TURBO) | 29 ms | 60,8 ms, rezerva 32 ms |
| 2 MHz | 57 ms | 60,8 ms v klidu, při výbuchu 78–100 ms (pípání výbuchu zabere 11 ms ze snímku) |

Původně (přímý převod) to bylo 48 ms při 4 MHz a 96 ms při 2 MHz.

## Nástroje

- Assembler **pasmo 0.5.3**: `E:\SAPI_GIT\Tools\pasmo-0.5.3\pasmo.exe` (jinde nastavit proměnnou `PASMO`).
- Python 3 pro `tools/make_tables.py`.
- Emulátor SAPIemu s MCP serverem: `sapiemu-cli --machine machines/sapi1v.sapi --mcp --mcp-port 8591`.

## Nejasnosti k ověření na HW

- Rychlost a zvuk na skutečné desce (YM3812 časování zápisů je podle katalogu: 3,3 µs po adrese, 23 µs po
  datech).
- Délka snímku 60,8 ms je převzatá z BomberNet (`docs/port-zx-spectrum.md`). Na skutečném MZ-700 ji neměřil
  nikdo z nás.
