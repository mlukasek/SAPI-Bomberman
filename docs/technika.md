# Jak je port udělaný

Technický popis portu Bombermana z MZ-700 na SAPI-1 V. Uživatelské informace jsou v `README.md`, překlad
a ověřování v `docs/vyvoj.md`.

## Hardware

- JPR-1V (Z80), RAM-1V s registrem MAP na 63h, CP/M;
- CGA-1V na C000h při MAP1 = MAP2 = H (`OUT 63h,C0h`), autorovo nastavení propojek;
- MPH-1V na 50h: 82C54 (časování), YM3812 (zvuk), joystick Atari na K4 (OVL);
- klávesnice Consul 262.3 (bez úpravy 7474) nebo EKL-1 na JPR-1V.

## Zdroj

- `sapi/bomber_sapi.asm`: `orig/bomber.asm` (disassembler originálu z BomberNet) s ORG 0100h.
  - Změny jsou označené `SAPI:` a popisují, co dělal MZ.
  - Komentáře s adresami (`; 1D46`) jsou adresy originálu na MZ-700.
  - Na konci jsou `include` ostatních souborů a adresy bufferů.
- `sapi/platform.asm`: náhrada monitoru a VRAM MZ-700: CGA-1V, 82C54, YM3812 a tóny, joystick a klávesnice.
- `sapi/tables.asm`: generuje `tools/make_tables.py` z `orig/bomber.asm` a znakového generátoru MZ-700
  (`orig/cgrom.bin`, v repu není):
  - dlaždice pro CGA-1V;
  - tabulky adres dlaždic po stránkách;
  - tabulka řádků `rtab`;
  - paleta.

## Co nahrazuje co

| MZ-700 | SAPI-1 V |
|---|---|
| VRAM D000h, atributy D800h, zapisuje jen `put_vram_char` | CGA-1V v režimu EGA: buňka 8×8 = 2 bajty × 8 řádků, 40×25 buněk = 320×200 |
| `game_table`, `title_table` (displejový kód MZ + atribut) | 145 předkreslených dlaždic po 16 bajtech (`tiles`) a tabulky jejich adres po stránkách: `game_tlo`/`game_thi`, `title_tlo`/`title_thi` (režim = `tile_page`, na MZ samomodifikující `mode_patch`) |
| barvy MZ: 8 barev popředí, hra má pozadí vždy černé | atribut CGA = barva popředí MZ, paleta Bt476: index = atribut × 2 + bod, COLMASK 1Fh |
| `GETKY` 001Bh | `key_fire` (palba nebo mezerník) a `key_dir` (páka nebo šipky) |
| `MSTA`, `MSTP`, `RATIO` (8253, tón 1108800 / RATIO Hz) | YM3812 kanál 0, F-number a blok se počítají z RATIO |
| `beep`: smyčka DJNZ × C, hra mezitím stojí | tón C jednotek po 0,95 ms hraje, zatímco hra běží (viz Zvuk) |
| `delay`: smyčka 5000h (150 ms) | 159 jednotek 82C54 (čítač 0, režim 3, 1055 Hz) |
| žádné časování snímku (rychlost dává zátěž CPU, 60,8 ms) | `frame_wait`: čítač 2 v režimu 2 nastavuje F2 každých 60,8 ms |
| ORG 1200h, zásobník pod programem | CP/M `.COM` od 0100h, vlastní zásobník za programem. Během hry je CGA namapovaná přes RAM C000–FFFF, BDOS se nevolá |
| `draw_buffer`, `shadow_vram`, `map_layer` v programu (snímek RAM) | za programem, zarovnané na 4 KB (viz Paměť) |

## Paměť a porty

| Adresa | Obsah |
|---|---|
| 0000–00FF | CP/M (stránka 0) |
| 0100–~1AFF | program (`bomber_sapi.asm`, `platform.asm`) |
| ~1B00–~296F | tabulky po stránkách 256 B (`game_tlo`, `game_thi`, `title_tlo`, `title_thi`, `rtab`), dlaždice, paleta |
| ~2970–~2A6F | zásobník (256 B pod `stack_top`) |
| 3000–33FF | `draw_buffer` (40×25 logických kódů, zarovnaný na 4 KB) |
| 3400–37FF | `shadow_vram` = `draw_buffer` \| 0400h (co je na obrazovce) |
| 3800–3BFF | `map_layer` = `draw_buffer` \| 0800h (mapa se zdmi; na titulku statický obraz) |
| 3C00–BFFF | **volné, asi 33 KB** (CP/M se během hry nevolá, CCP a BDOS jsou nad C000) |
| C000–FFFF | během hry CGA-1V (stránka A se zobrazuje, CPU píše do A), RAM pod ní je skrytá |

- Přesné adresy jsou v `build\bomber.sym`.
- Buffery nejsou v `.COM`. `draw_buffer` je `(stack_top + 0FFFh) & 0F000h` a musí zůstat pod C000h.
- Přerušení jsou během hry zakázaná (`plat_init`, `DI`). Na tom stojí čtení dlaždic přes `POP` a `fill_1000`
  přes `PUSH`.

Porty, které hra používá:
- 01h, 02h: klávesnice (P0, P1 na JPR-1V);
- 50h–57h: MPH-1V (82C54 50h–53h, STATUS 53h, IEN a joystick 54h, IACK 55h, YM3812 56h–57h);
- 63h: MAP (RAM-1V).

Ostatní karty sestavy V: DSM-1V 10h a 14h, IDE-1 58h a 5Ch, ZRD-1V 60h (podle `docs/porty.md` v SAPIemu).

## Klávesnice

- Čte se ve všech čekacích smyčkách (`poll_key`), jinde ne.
- Postup je jako v MikroMonu:
  1. STROBE (P0-IN0 = 0);
  2. kód z P1 (invertovaný);
  3. ACK (`OUT 01h,03h`), dokud STROBE nezhasne (nejvýš 256 čtení);
  4. `OUT 01h,02h`.
- Consul 262.3 posílá STROBE jen jako pulz 1 ms, ACK nepotřebuje a nemá autorepeat. EKL-1 drží STROBE, dokud
  nepřijde ACK. Bez ACK by po prvním znaku visela.
- Šipky: Consul C1–C4, EKL-1 kódy WordStar 05 (nahoru), 18 (dolů), 04 (vpravo), 13 (vlevo).
- **Šipka** udělá krok a pak pokračuje, dokud hráč nestojí na celém políčku.
  - Na celém políčku je souřadnice v ose pohybu lichá, takže jeden stisk = jedno políčko.
  - Stojí-li hráč v půlce políčka (po joysticku), stisk ho dorovná.
  - Stisk téže šipky během pohybu přidá jedno políčko, takže autorepeat dává plynulý pohyb.
  - Dřív se i šipka brala jako držená 4 snímky. Když přišel další stisk dřív, než doběhly (rychlé ťukání,
    autorepeat), mohl hráč zůstat v půlce políčka a nemohl zatočit.
- **Mezerník** se bere jako držený 4 snímky (`KEY_HOLD`). Po startu hry z titulku (`title_start`, `fire_lock`)
  dává `key_fire` 0, dokud se palba i mezerník neuvolní.
- **Pohyb a bomba zároveň:** originál volá `GETKY` zvlášť pro pohyb a pro bombu a dostane jednu klávesu. Port
  čte palbu a páku zvlášť.

## Zvuk

- **Tón generuje YM3812:** kanál 0, modulátor s feedbackem a nosná, takže zní bzučivě jako obdélník MZ.
  - `MSTA` spočítá F-number a blok z `RATIO` originálu (dělení v `tone_fnum`), `MSTP` dá key off.
- **Pípnutí hru nezdržuje:**
  - `beep` = `tone_start` tón jen spustí a vrátí se.
  - Délku hlídá `tone_poll` podle čítače 2 v 82C54 (latch, tiky 17,9 µs). Volá se v `frame_wait`,
    `wait_units` a na začátku a konci `flush_screen`.
  - Pípnutí během tónu čeká ve frontě `tone_queue` (8 míst) a hraje po něm. Sled tónů je tedy stejný jako na
    MZ, kde hra během pípání stála.
  - Konec tónu se pozná při nejbližší kontrole, tóny bývají o 1–2 ms delší.
  - Přesněji by to šlo s přerušením (82C54 nebo časovač YM3812). Hru by to ale nezrychlilo a přerušení by se
    musela ověřit na HW.
- **Výška tónu:** hodiny 8253 1,1088 MHz odpovídají evropskému MZ-700 (PAL). Japonský model má 0,895 MHz, tóny
  by byly o 24 % hlubší.

## Vykreslování

Originál každý snímek smaže `draw_buffer` (40×25 logických kódů) a nakreslí do něj všechno znovu: zdi,
překrytí mapy (`composite_map`), HUD, bomby, nepřátele, hráče. `flush_screen` pak porovná všech 1000 buněk se
stínem (`shadow_vram`) a pošle na obrazovku změněné. Hra z `draw_buffer` i čte (kolize, oheň pod nepřítelem
nebo hráčem), proto musí jeho obsah zůstat v každém okamžiku stejný jako na MZ. Port to dělá takto:

- **Zdi jsou i v `map_layer`** (`clear_map`).
  - `flush_screen` po porovnání vrací do `draw_buffer` pozadí z mapy, takže ve snímku odpadají
    `draw_walls` a `composite_map`.
  - Hra je volá jen v `stage_start`: `generate_map` čte zdi z `draw_buffer`.
- **Porovnávají se jen kreslená místa.**
  - Rozsah sloupců v řádku (`rtab`) si označí: kreslení hráče, nepřátel, bomb, bonusu a východu
    (`draw_addr_w`), zápisy do mapy (`map_addr_w`) a výbuch (`mark_cross`, celý kříž najednou).
  - `flush_screen` porovná sloupce kreslené v tomto nebo minulém snímku (minulý = co zmizelo) a řádek 24
    (HUD). Pozadí vrátí jen tam.
  - Celou obrazovku porovná dva snímky po `clear_buffers` a `clear_map`.
  - **Pravidlo pro nový kód:** každý zápis do `draw_buffer` nebo `map_layer` mimo řádek 24 musí být
    označený (`draw_addr_w`, `map_addr_w`, `mark2`, `mark_range`). Jinak se na obrazovce neobjeví nebo
    z ní nezmizí.
- **Titulek:** statická část (logo, texty, skóre) se nakreslí jednou (`title_static`) do `map_layer` jako
  pozadí, na titulku se mapa nepoužívá. Každý snímek se kreslí jen bomba a nepřátelé z legendy.
- **Buňka na CGA:**
  - adresa dlaždice z tabulek po stránkách, kopie přes `POP`;
  - vykreslení je přímo ve smyčce porovnání (`fs_seg`, používá i alternativní registry; hra v nich přes
    snímek nic nedrží);
  - `draw_addr` a `map_addr` berou adresu řádku z `rtab`;
  - výbuch počítá adresy ramen jako posun od bomby (`blast_pattern` v bajtech bufferu, `blast_addr`).

## Rychlost (změřeno v SAPIemu, 2026-10-05)

Práce snímku = od `flush_screen` po další `frame_wait` (`tools/emu/bench.py`). Snímek má 60,8 ms.

| | 2 MHz dřív | 2 MHz teď | 4 MHz dřív | 4 MHz teď |
|---|---|---|---|---|
| titulek | 48–56 ms | 8–13 ms | 24–28 ms | 4–7 ms |
| hra v klidu | 57–60 ms | 9–12 ms | 29 ms | 5 ms |
| chůze | 73 ms | 11–14 ms | | |
| výbuch jedné bomby | 80–101 ms | 17–26 ms | | do 14 ms |
| pět bomb najednou (scénář `chain`) | 100–180 ms | 37–55 ms | | do 27 ms |
| vypršení času (zmizí všechny cihly, jeden snímek) | 112 ms | 70 ms | | |
| začátek stage (celá obrazovka) | 450 ms | 280 ms | 225 ms | 140 ms |

- „Dřív“ = commit 63779ea (první hratelná verze s Consul šipkami). Přímý převod (první verze portu) měl 48 ms při 4 MHz
  a 96 ms při 2 MHz.
- Pípání dřív zastavilo hru (výbuch 11 ms za každou bombu a snímek), teď běží vedle hry.
- Klávesnice se čte jen v čekacích smyčkách. Dřív zbývaly při 2 MHz ze snímku asi 3 ms čekání, teď kolem
  50 ms, takže se krátký STROBE Consulu ztratí méně často.
- Co ze snímku zbývá:
  - hlavně kopie dlaždic na CGA (16 bajtů na změněnou buňku; CGA-1V nemá nic, co by kopírovalo samo);
  - logika výbuchů;
  - HUD, asi 1,8 ms: `draw_hud` vypisuje skóre a čas každý snímek, šlo by jen při změně;
  - na zvuk asi 0,5 ms na pípnutí (dělení v `tone_fnum`, šlo by předpočítat).
