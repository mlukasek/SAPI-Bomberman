# Vývoj

Překlad, emulátor, ověřování změn, vydání a pasti. Jak port funguje, je v `docs/technika.md`.

## Začít na jiném počítači

Složky vedle sebe (u autora `E:\SAPI_GIT\`):

| Složka | Co | K čemu |
|---|---|---|
| `SAPI-Bomberman` | toto repo (github mlukasek/SAPI-Bomberman) | |
| `SAPIemu-release` | rozbalený release emulátoru SAPIemu (teď 0.3.0 alpha, github mlukasek/SAPIemu, Releases) | běh a ladění, `sapiemu-cli` s MCP |
| `Tools\pasmo-0.5.3\pasmo.exe` | assembler pasmo 0.5.3 | překlad; jinde nastavit proměnnou `PASMO` |
| `BomberNet` | zdroj disassembleru, síťová verze pro MZ a ZX (github MZPico/BomberNet, autorovi nepatří) | jen jako podklad |
| `SAPI-Bomberman-private` | `cgrom.bin` (znakový generátor MZ-700), mimo git | jen pro nové vygenerování dlaždic |

- **Vývojový SAPIemu** (`E:\SAPI_GIT\SAPIemu`, zdrojáky emulátoru) se pro práci na hře **nepoužívá**: autor ho
  vyvíjí paralelně. Hra se zkouší v release (`SAPIemu-release`). Chyby emulátoru zapsat a nahlásit autorovi.
- **Python 3**, jen standardní knihovna (žádné balíčky), pro `tools/make_tables.py` a `tools/emu/*.py`.
- **Znakový generátor MZ-700** je potřeba jen pro změnu dlaždic. Bez něj `build.cmd` použije uložené
  `sapi/tables.asm`. Dump: `CGROM.ROM` z emulátoru MZ8Emu (u autora `E:\@Prebrat\prebrat_z_USB\Sharp\MZ8Emu\ROM`
  a záloha v `SAPI-Bomberman-private\cgrom.bin`), 4 KB, SHA-1 `4ea887241a0b60948a86c5acab664dcfdf51101c`.
  Zkopírovat do `orig\cgrom.bin` (je v `.gitignore`). S ním dává `make_zx_tables.py` z BomberNet bajt po bajtu
  stejné tabulky jako v BomberNet, je to tedy tentýž generátor.

## Překlad

`build.cmd`:
1. `tools\make_tables.py` → `sapi\tables.asm` (jen když je `orig\cgrom.bin`);
2. pasmo → `build\bomber.com`, `build\bomber.hex` (Intel HEX od 0100h) a `build\bomber.sym`;
3. na konci vypíše velikost a počet stránek pro `SAVE` (verze 1.0.0: 10 608 bajtů, `SAVE 42`).

Složka `build\` je v `.gitignore`.

`orig/bomber.asm` se pasmem přeloží bajt po bajtu stejně jako `orig/bomber.mzf` (ověřeno 2026-10-05). Je to
disassembler z BomberNet (commit c88818d).

## Emulátor

- **GUI:** `SAPIemu-release\sapiemu.exe`, sestava `machines\sapi1v.sapi`. MCP je na
  `http://127.0.0.1:8580/mcp`.
- **Bez okna, pro skripty:** ze složky `SAPIemu-release` spustit na pozadí
  `sapiemu-cli --machine machines/sapi1v.sapi --mcp --mcp-port 8591`.
  - Skripty v `tools/emu` čekají MCP na portu 8591, jiný port nebo GUI: proměnná `SAPIEMU_MCP`.
  - Ukončit přes MCP `power off` (pak proces zastavit). Obraz IDE disku se zapisuje přes buffer souboru,
    po zabití procesu by zápis mohl chybět.
- **Boot sestavy V:** `1` = CP/M z RAM disku A:, `3` = i s IDE diskem B:, C: (`work\ide\sapi_hdd.img`).
- **Hru na disk C: emulátoru:**
  - ručně: v CP/M (boot `3`) Soubor → Nahrát program do paměti → `build\bomber.hex`, pak
    `SAVE 42 C:BOMBER.COM`;
  - přes MCP: `load_hex` souboru `bomber.hex`, `type_text` „`SAVE 42 C:BOMBER.COM\r`“, pak `power off`.
  - Disk C: se repem nepřenáší, na novém PC je potřeba hru nahrát znovu. U autora je hra jako `C:BOMBER.COM`
    na disku C: vývojového SAPIemu (`SAPIemu\work\ide\sapi_hdd.img`).
- **Jen do paměti (ladění):** MCP `load_binary` souboru `bomber.com` na 0100h a `set_registers` s `pc` =
  0100h, když CP/M čeká na příkaz (tak to dělají skripty v `tools/emu`).
- **Užitečné MCP nástroje:**
  - `joystick`, `press_key`, `type_text`, `set_keyboard`, `cpu_turbo`;
  - `screenshot` s `display=CGA-1V`, `audio_record`;
  - `save_state`/`load_state` (`name` = jen v paměti procesu);
  - `run_until` s adresou ze `build\bomber.sym`.

## Skripty `tools/emu`

Řídí emulátor přes MCP. Skript si sám nabootuje CP/M (volba 1) a uloží stav `cpm` do paměti emulátoru.

| Skript | Co dělá |
|---|---|
| `bench.py` | práce každého snímku ve scénáři (`--scen walk`, `chain`, `death`; `--time 30` = vypršení času; `--turbo` = 4 MHz), s `--dump DIR --every N` uloží obsah CGA |
| `compare.py DIR1 DIR2` | porovná výpisy CGA dvou běhů |
| `prof.py FRAME...` | čas jednotlivých volání `main_loop` ve zvolených snímcích |
| `audio.py record OUT.wav`, `audio.py tones A.wav B.wav` | nahraje zvuk scénáře a vypíše tóny (délka @ kmitočet) |
| `shots.py [DIR]` | snímky obrazovky pro README (`docs/img`) |
| `sapimcp.py TOOL '{json}'` | jedno volání MCP z příkazové řádky |
| `emu.py` | společné: symboly z `build\bomber.sym`, scénáře, checkpoint |

Scénáře mačkají joystick snímek po snímku: `walk` je chůze, bomby a výbuchy, `chain` je pět bomb v chodbě
(nejhorší případ), `death` je bomba pod hráčem. Počítají s mapou stage 1 při pevné náhodě. Po změně
generování mapy nebo pohybu je potřeba je upravit (`--trace` vypíše polohu hráče a bomby).

## Ověření, že změna nemění hru

Herní logika se nesmí změnit (hra čte `draw_buffer`). Každou změnu porovnat se starou verzí v každém snímku:

1. Starou verzi přeložit vedle: `git worktree add ..\bomber-old <commit>` a v ní `build.cmd`.
2. Ve `tools\emu`: `python bench.py --every 1 --dump A --root ..\..\..\bomber-old` a
   `python bench.py --every 1 --dump B`.
3. `python compare.py A B`, pak totéž pro `--scen chain`, `--scen death` a `--time 30`.
4. Zvuk: `python audio.py record` pro obě verze, pak `python audio.py tones`.
5. Úklid: `git worktree remove ..\bomber-old`.

Proč to funguje:
- Skripty dělají náhodu pevnou: `LD A,R` v `random` → `XOR A`, jinak náhoda závisí na počtu provedených instrukcí.
- Joystick mačkají podle scénáře snímek po snímku.
- Dvě verze se stejnou herní logikou proto musí mít v každém snímku stejnou obrazovku.

2026-10-05 ověřeno takto proti 63779ea: `walk` (160 snímků), `chain` (60) a vypršení času (120) v každém
snímku, `death` každých 5. Všechny obrazovky jsou bajt po bajtu stejné a sled tónů je stejný.

Pozor na zámek palby po startu: palba v prvním snímku po startu se ignoruje (`fire_lock`). Scénáře proto
první palbu mají až od 2. snímku.

## Vydání (release)

1. V `CHANGELOG.md` zapsat verzi a změny, verzi i v `tools\release.cmd` (`VERSION`).
2. `tools\release.cmd`: přeloží hru a udělá `build\SAPI-Bomberman-<verze>.zip` (`BOMBER.COM`, `bomber.hex`,
   `README.md`, `CHANGELOG.md`).
3. Ověřit v emulátoru: nahrát `bomber.hex`, `SAVE`, spustit, zahrát. Na porovnání s předchozí verzí stačí
   `bench.py` a `compare.py`.
4. Commit, tag `v<verze>`, push (jen na pokyn autora).
5. GitHub Release z tagu se zipem:
   - ručně na GitHubu (Releases → Draft a new release);
   - nebo GitHub CLI (u autora `C:\Program Files\GitHub CLI\gh.exe`, přihlášení `gh auth login`):
     `gh release create v<verze> build\SAPI-Bomberman-<verze>.zip -t "SAPI Bomberman <verze>" -F poznamky.md`.
   - Poznámky k vydání: co je nového z `CHANGELOG.md`, obsah zipu, jak spustit, na čem je vyzkoušeno, krátce
     anglicky.

## Pasti

**Assembler pasmo 0.5.3** (ověřeno 2026-10-05):
- **Unární minus na začátku výrazu neguje celý zbytek výrazu.**
  - Příklady: `-1*40+1` = −41 (ne −39), `-1+2` = −3, `-10/2+1` = −6.
  - Správně: `(-1)*40+1`, `0-1*40+1` nebo hotové číslo.
  - Za operátorem (`5+-1`, `2*-3`) je to chyba překladu, závorky pomohou: `2*(-3)`.
  - Takhle vznikla chyba pravého sloupce horního ramene výbuchu, kterou našlo až porovnání každého snímku.
    Tabulky posunů psát hotovými čísly a po překladu zkontrolovat v binárce.
- **Operand začínající závorkou** je adresa v paměti: `ld a,(X+3) & 0FFh` se nepřeloží. Pomůže
  `ld a,0+(X+3) & 0FFh` nebo `ld a,low (X+3)`.
- **Operátory:** `low`, `high`, `&`, `>>` fungují.
- **Chybí ALIGN:** zarovnání na stránku je `defs (256 - ($ & 0FFh)) & 0FFh`.
- **REPT:** `DEFL` jako počitadlo se uvnitř `REPT` nepodařilo použít, tabulky s výrazy proto generuje
  `make_tables.py`.
- **Návěští `.jmeno`** jsou globální (jsou i v `.sym`): druhé `.x` v programu je chyba „previously defined“.
- **„Relative jump out of range“:** použít `jp`.
- **Dopředné odkazy v `equ`** (i na návěští definovaná později) fungují.

**MCP SAPIemu:**
- `read_memory` vrací nejvýš 4096 bajtů. Při větší délce vrátí chybový text, ne data. `emu.read` čte po 4 KB
  a délku kontroluje. První porovnání obrazovek kvůli tomu porovnávalo jen chybové hlášky.
- `cycles` počítá takty 4 MHz i při CPU 2 MHz (ms = cycles / 4000).
- `run_until` na adresu: když se breakpoint trefí při běhu v reálném čase mezi voláními, stroj stojí na té adrese
  a `run_until` pokračuje dál. Skripty proto emulátor drží v pauze (`pause`).
- `load_state` s `name` čte stav z paměti procesu, po novém spuštění emulátoru tam není (`emu.checkpoint` si ho
  vyrobí).
- PNG z `screenshot` nejsou komprimované, `shots.py` je ukládá znovu přes zlib.

**Hra:**
- Hra čte `draw_buffer` (kolize, oheň pod postavou). Obsah musí zůstat jako na MZ. Každý nový zápis do
  `draw_buffer` nebo `map_layer` označit pro `flush_screen` (`docs/technika.md` → Vykreslování).
- `random` míchá registr R, mapy proto závisí na přesném počtu instrukcí (na skutečném HW i na časování kláves).
- Klávesnice se čte jen v čekacích smyčkách (`poll_key`). Dlouhá práce bez čekání = ztracené stisky Consulu.
- Alternativní registry (`exx`, `ex af,af'`) používá hra jen uvnitř `draw_bombs` a `generate_map`, nic v nich
  nedrží přes snímek. `flush_screen` je proto smí měnit.
