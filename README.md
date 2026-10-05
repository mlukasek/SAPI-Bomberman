# SAPI-Bomberman

Port hry Bomberman (Hudson Soft 1983, verze pro Sharp MZ-700) na **Tesla SAPI-1**, sestavu „V“ Libora Lasoty
s barevnou grafikou **CGA-1V**. Zároveň je to test emulátoru SAPIemu pro vývoj softwaru: chyby emulátoru, na
které se při tom narazí, se opravují v SAPIemu (repo `SAPIemu` vedle tohoto).

Neveřejné repo: hra je chráněná autorským právem Hudson Soft, znakový generátor MZ-700 (`orig/cgrom.bin`)
právem Sharp.

## Stav (2026-10-05)

- Hra je hratelná v SAPIemu se sestavou `machines/sapi1v.sapi`: titulní obrazovka, hra, zvuk, joystick,
  klávesnice Consul 262.3 i EKL-1, návrat do CP/M.
- Stíhá i při 2 MHz, i při výbuchu pěti bomb najednou (viz Rychlost).
- Na skutečném HW zatím nevyzkoušeno.
- V emulátoru autora je hra na disku C: (IDE, `SAPIemu\work\ide\sapi_hdd.img`) jako `C:BOMBER.COM`.
- **Další velký krok: síťová hra**, až bude síťová karta pro SAPI (viz Síťová hra).

## Začít na jiném počítači

Repozitáře vedle sebe ve společné složce (u autora `E:\SAPI_GIT\`):

| Složka | Co | K čemu |
|---|---|---|
| `SAPI-Bomberman` | toto repo (github mlukasek/SAPI-Bomberman, neveřejné) | |
| `SAPIemu` | emulátor (github mlukasek/SAPIemu) | běh a ladění, `sapiemu-cli` s MCP |
| `Tools\pasmo-0.5.3\pasmo.exe` | assembler pasmo 0.5.3 | překlad; jinde nastavit proměnnou `PASMO` |
| `BomberNet` | zdroj disassembleru, síťová verze pro MZ a ZX (repo autorovi nepatří) | jen jako podklad |

1. **Python 3** (jen standardní knihovna, žádné balíčky) pro `tools/make_tables.py` a `tools/emu/*.py`.
2. **Emulátor** sestavit podle `SAPIemu\docs\build.md` (`tools\build.cmd release`), výstup
   `SAPIemu\out\build\windows-release\sapiemu.exe` a `sapiemu-cli.exe`.
3. **Překlad hry:** `build.cmd` → `build\bomber.com`, `build\bomber.hex` (od 0100h) a `build\bomber.sym`.
   Na konci vypíše počet stránek pro `SAVE` (teď 42). Složka `build\` je v `.gitignore`.
4. **Vyzkoušet:** viz Spuštění. Disk C: v emulátoru (`work\ide\sapi_hdd.img`) se repem nepřenáší, hru je
   na novém PC potřeba na něj nahrát znovu.

## Hardware

- JPR-1V (Z80), RAM-1V s registrem MAP na 63h, CP/M;
- CGA-1V na C000h při MAP1 = MAP2 = H (`OUT 63h,C0h`), autorovo nastavení propojek;
- MPH-1V na 50h: 82C54 (časování), YM3812 (zvuk), joystick Atari na K4 (OVL);
- klávesnice Consul 262.3 (bez úpravy 7474) nebo EKL-1 na JPR-1V.

## Ovládání

| Akce | Joystick (K4) | Klávesnice Consul 262.3 | Klávesnice EKL-1 |
|---|---|---|---|
| pohyb | páka | šipky C1–C4 | šipky (kódy WordStar 05, 18, 04, 13) |
| bomba, start hry | palba (FL) | mezerník | mezerník |
| konec, návrat do CP/M | | ESC nebo BREAK | ESC |

- Šipkou jeden stisk = jedno políčko.
- Palba nebo mezerník, kterými se hra spustí, bombu nepoloží: po startu se palba bere až po uvolnění.
- V SAPIemu: joystick z gamepadu, nebo šipky a mezerník jako joystick (Ctrl+F8). Klávesnice se přepíná
  v menu Stroj → Klávesnice. Nejpohodlnější je joystick: klávesnice nepoznají, že je klávesa držená.

## Spuštění

- **Z disku C: (IDE):** v SAPIemu se sestavou SAPI-1 V zvolit při bootu **3** (B, C: HDD), pak `C:BOMBER`.
- **Nahrát na disk:** v CP/M Soubor → Nahrát program do paměti (`build\bomber.hex`), pak
  `SAVE 42 C:BOMBER.COM`.
  - Přes MCP: `load_hex` souboru `bomber.hex` a `type_text` „`SAVE 42 C:BOMBER.COM\r`“.
  - Potom emulátor vypnout přes `power off` (nebo normálně zavřít): obraz disku se zapisuje přes buffer
    souboru, po zabití procesu by zápis mohl chybět.
- **Jen do paměti (ladění):** přes MCP `load_binary` souboru `bomber.com` na 0100h a `set_registers` s `pc` =
  0100h, když CP/M čeká na příkaz (tak to dělají skripty v `tools/emu`).

## Soubory

- `orig/bomber.asm`, `orig/bomber.mzf`: komentovaný disassembler originálu a originální páska z projektu
  BomberNet (commit c88818d). `orig/bomber.asm` se pasmem přeloží bajt po bajtu stejně jako `orig/bomber.mzf`
  (ověřeno 2026-10-05).
- `orig/cgrom.bin`: znakový generátor MZ-700 (4 KB, 512 znaků 8×8, bit 0 vlevo). Kopie `CGROM.ROM` z emulátoru
  MZ8Emu (u autora `E:\@Prebrat\prebrat_z_USB\Sharp\MZ8Emu\ROM`). S ním dává `make_zx_tables.py` z BomberNet
  bajt po bajtu stejné tabulky jako v BomberNet, je to tedy tentýž generátor.
- `sapi/bomber_sapi.asm`: `orig/bomber.asm` s ORG 0100h. Změny jsou označené `SAPI:`, komentáře s adresami
  jsou adresy originálu na MZ-700. Na konci jsou `include` ostatních souborů a adresy bufferů.
- `sapi/platform.asm`: náhrada monitoru a VRAM MZ-700: CGA-1V, 82C54, YM3812 a tóny, joystick a klávesnice.
- `sapi/tables.asm`: dlaždice pro CGA-1V, tabulky adres dlaždic a tabulka řádků `rtab`, generuje
  `tools/make_tables.py` (needitovat, `build.cmd` ho generuje při každém překladu).
- `tools/emu/`: měření a ověřování v SAPIemu přes MCP (viz Vývoj a ověřování).
- `CLAUDE.md`: kontext a pravidla pro práci s Claude Code.

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

Přesné adresy jsou v `build\bomber.sym`. Buffery nejsou v `.COM`. `draw_buffer` je `(stack_top + 0FFFh) & 0F000h`
a musí zůstat pod C000h.

Porty, které hra používá:
- 01h, 02h: klávesnice (P0, P1 na JPR-1V);
- 50h–57h: MPH-1V (82C54 50h–53h, STATUS 53h, IEN a joystick 54h, IACK 55h, YM3812 56h–57h);
- 63h: MAP (RAM-1V).

Ostatní karty sestavy V: DSM-1V 10h a 14h, IDE-1 58h a 5Ch, ZRD-1V 60h (`SAPIemu\docs\porty.md`).

Přerušení jsou během hry zakázaná (`plat_init`, `DI`). Na tom stojí čtení dlaždic přes `POP`
a `fill_1000` přes `PUSH`.

## Jak je port udělaný

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

### Klávesnice

- Čte se ve všech čekacích smyčkách (`poll_key`), jinde ne.
- Postup je jako v MikroMonu:
  1. STROBE (P0-IN0 = 0);
  2. kód z P1 (invertovaný);
  3. ACK (`OUT 01h,03h`), dokud STROBE nezhasne (nejvýš 256 čtení);
  4. `OUT 01h,02h`.
- Consul 262.3 posílá STROBE jen jako pulz 1 ms, ACK nepotřebuje a nemá autorepeat. EKL-1 drží STROBE, dokud
  nepřijde ACK. Dřív ho port neposílal, takže EKL-1 po prvním znaku visela.
- Šipky: Consul C1–C4, EKL-1 kódy WordStar 05 (nahoru), 18 (dolů), 04 (vpravo), 13 (vlevo).
- **Šipka** udělá krok a pak pokračuje, dokud hráč nestojí na celém políčku.
  - Na celém políčku je souřadnice v ose pohybu lichá, takže jeden stisk = jedno políčko.
  - Stojí-li hráč v půlce políčka (po joysticku), stisk ho dorovná.
  - Stisk téže šipky během pohybu přidá jedno políčko, takže autorepeat PC v emulátoru dává plynulý pohyb.
  - Dřív se i šipka brala jako držená 4 snímky. Když přišel další stisk dřív, než doběhly (rychlé ťukání,
    autorepeat), mohl hráč zůstat v půlce políčka a nemohl zatočit (autor, 2026-10-05).
- **Mezerník** se bere jako držený 4 snímky (`KEY_HOLD`). Po startu hry z titulku (`title_start`, `fire_lock`)
  dává `key_fire` 0, dokud se palba i mezerník neuvolní. Dřív stisk, který spustil hru, hned položil bombu.
- **Pohyb a bomba zároveň:** originál volá `GETKY` zvlášť pro pohyb a pro bombu a dostane jednu klávesu. Port
  čte palbu a páku zvlášť, takže s joystickem jde chodit a pokládat bomby zároveň.

### Zvuk

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

### Vykreslování

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

### Rychlost (změřeno v SAPIemu, 2026-10-05)

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

- „Dřív“ = commit d387f93. Přímý převod (první verze portu) měl 48 ms při 4 MHz a 96 ms při 2 MHz.
- Pípání dřív zastavilo hru (výbuch 11 ms za každou bombu a snímek), teď běží vedle hry.
- Klávesnice se čte jen v čekacích smyčkách. Dřív zbývaly při 2 MHz ze snímku asi 3 ms čekání, teď kolem
  50 ms, takže se krátký STROBE Consulu ztratí méně často.
- Co ze snímku zbývá: hlavně kopie dlaždic na CGA (16 bajtů na změněnou buňku, CGA-1V nemá nic, co by
  kopírovalo samo), logika výbuchů a HUD (asi 1,8 ms: `draw_hud` vypisuje skóre a čas každý snímek, šlo by jen
  při změně).

## Vývoj a ověřování

Skripty v `tools/emu/` řídí emulátor přes MCP. Ke spuštění: `sapiemu-cli --machine machines/sapi1v.sapi --mcp
--mcp-port 8591` ze složky SAPIemu (na pozadí; jiný port nebo GUI: proměnná `SAPIEMU_MCP`, GUI má
`http://127.0.0.1:8580/mcp`). Skript si sám nabootuje CP/M (volba 1) a uloží stav `cpm` do paměti emulátoru.

| Skript | Co dělá |
|---|---|
| `bench.py` | práce každého snímku ve scénáři (`--scen walk`, `chain`, `death`; `--time 30` = vypršení času; `--turbo` = 4 MHz), s `--dump DIR --every N` uloží obsah CGA |
| `compare.py DIR1 DIR2` | porovná výpisy CGA dvou běhů |
| `prof.py FRAME...` | čas jednotlivých volání `main_loop` ve zvolených snímcích |
| `audio.py record OUT.wav`, `audio.py tones A.wav B.wav` | nahraje zvuk scénáře a vypíše tóny (délka @ kmitočet) |
| `sapimcp.py TOOL '{json}'` | jedno volání MCP z příkazové řádky |
| `emu.py` | společné: symboly z `build\bomber.sym`, scénáře, checkpoint |

**Ověření, že změna nemění hru:**
1. Starou verzi přeložit vedle: `git worktree add ..\bomber-old <commit>` a v ní `build.cmd`.
2. `python bench.py --every 1 --dump A --root ..\..\..\bomber-old` a `python bench.py --every 1 --dump B`.
3. `python compare.py A B`.

Skripty dělají náhodu pevnou (`LD A,R` v `random` → `XOR A`, jinak závisí na počtu instrukcí) a joystick
mačkají podle scénáře snímek po snímku. Dvě verze se stejnou herní logikou proto musí mít v každém snímku
stejnou obrazovku. 2026-10-05 ověřeno takto: scénáře `walk` (160 snímků), `chain` (60) a vypršení času (120)
v každém snímku, `death` každých 5. Všechny obrazovky jsou bajt po bajtu stejné jako u d387f93 a sled tónů je
stejný.

**Pasti (2026-10-05):**
- **pasmo čte `-1*40+1` jako −(1·40+1).** Unární minus platí pro celý výraz. Takhle vznikla chyba pravého
  sloupce horního ramene výbuchu, kterou našlo až porovnání každého snímku. Záporné konstanty psát jako
  hotová čísla nebo `0-40+1`.
- **MCP `read_memory` vrací nejvýš 4096 bajtů.** Při větší délce vrátí chybový text, ne data. `emu.read` čte po
  4 KB a délku kontroluje. První porovnání obrazovek kvůli tomu porovnávalo jen chybové hlášky.
- **`cycles` v MCP počítá takty 4 MHz** i při CPU 2 MHz (ms = cycles / 4000).
- **`run_until` na adresu:** když se breakpoint trefí při běhu v reálném čase mezi voláními, stroj stojí na té
  adrese a `run_until` pokračuje dál. Skripty proto emulátor drží v pauze (`pause`).
- **pasmo neumí `DEFL` v `REPT`.** Tabulky s výrazy generuje `make_tables.py`.

## Síťová hra (plán)

Až bude síťová karta pro SAPI. Podklady:
- **BomberNet** (`..\BomberNet`) má síťovou verzi pro MZ-700/800 a ZX Spectrum (přepis do C, z88dk):
  - `docs/net-protocol.md`, `docs/net-timing.md`;
  - síťové zařízení jako deset volání (`c/core/netdev.h`), lockstep (`c/core/netplay.c`);
  - relay přes WebSocket (`relay/`), testy dvou emulátorů proti sobě (`tools/lockstep_*.py`).
- **Hra je deterministická po snímcích:** stav se mění jen v `main_loop` a vstup se čte jednou za snímek
  (`key_dir`, `key_fire`). To se hodí pro lockstep (vyměňuje se jen vstup).
  - Náhodu je ale potřeba udělat společnou: `random` míchá registr R, který závisí na počtu provedených
    instrukcí. Stačí sdílené semínko a `random` bez R (skripty to tak dělají už teď).
- **Rezerva:** při 2 MHz zbývá ze snímku v klidu asi 50 ms, v nejhorším případě (5 bomb) asi 6 ms. Při 4 MHz
  vždy přes 30 ms. Volná paměť asi 33 KB (3C00h–BFFFh).
- **Grafika:** obrazovka umí jen jednoho hráče (originál je single player). Další hráče kreslit jako další
  2x2 objekty přes `draw_addr_w`, dlaždice a barvy přidat v `make_tables.py`.
- Porty a paměť: viz Paměť a porty. Kartu bude potřeba přidat do SAPIemu (a do `docs/porty.md` tam).

## Nejasnosti k ověření na HW

- Rychlost a zvuk na skutečné desce (YM3812 časování zápisů je podle katalogu: 3,3 µs po adrese, 23 µs po
  datech).
- Délka snímku 60,8 ms je převzatá z BomberNet (`docs/port-zx-spectrum.md`). Na skutečném MZ-700 ji neměřil
  nikdo z nás.
- Klávesnice: ACK (`OUT 01h,03h`) při Consulu 262.3 bez 7474 na JPR-1V. V emulátoru ACK nevadí, na HW
  ověřit, že Consul nic neruší a EKL-1 na JPR-1V jede.
- Latch čítače 2 v 82C54 (`OUT 53h,80h`, dvě čtení 52h) pro délku tónů.
