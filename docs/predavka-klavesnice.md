# Předávka: šipky z klávesnice nechávají hráče v půlce políčka (2026-10-16)

Zápis ze session SAPI-BomberNet (síťová verze v C, `..\SAPI-BomberNet`) pro opravu v této assemblerové verzi.
Martin hlásí v obou verzích stejné příznaky:
- hráč ovládaný šipkami občas skončí **v půlce políčka**;
- pak se špatně zatáčí;
- „někdy jen velmi lehoučkým stiskem“, nedá se to spolehlivě vyvolat.

## Co se našlo v C verzi a je opravené (`SAPI-BomberNet/sapi/plat_sapi.c`)

Klávesnice SAPI hlásí jen stisk, ne puštění (Consul 262.3 bez 7474 jen pulz STROBE 1 ms), takže „držení“ šipky
musí program vyrobit sám. V C verzi drží stisk šipky 4 snímky a hráč jde o znak každý druhý snímek, 4 snímky tedy
dají celé políčko (2 znaky). Půlkroky měly **tři příčiny**:

1. **Jiný směr během kroku přepsal rozdělané políčko.** Ťuknutí vpravo a hned nahoru: první políčko je v půlce,
   nový směr ho zahodí a hráč zůstane v půlce na původní ose. To je i „špatné zatáčení“.
   **Oprava:** nový směr si počká (`kp_a`, „next“), až se rozdělané políčko dojde, a teprve pak začne.
2. **Strop podržení uřízl část přidaného políčka.** Další stisk téže šipky přidal 4 snímky, ale strop 8 snímků
   je ořízl na méně. **Oprava:** přidat jen celé políčko, nebo nic.
3. **Stisk zestárl ve snímku, ve kterém ho hra nepřečetla.** Zachycený uprostřed snímku (jinde než v čekání na
   snímek) vydržel jen 3 čtení a dal 1 nebo 2 kroky podle fáze časovače. **Oprava:** stárne jen přečtený stisk.

**Měření:** test ťuká šipkami v náhodných směrech a v náhodných okamžicích snímku (0–300 ms po sobě) a po pauze
kontroluje, že hráč stojí na celém políčku. Na celém políčku je souřadnice lichá, v C i v této verzi. Výsledek:
- předchozí verze: 120 ťuknutí → **21× v půlce políčka**;
- opravená: **0×**.

Skript `..\SAPI-BomberNet\tools\emu\taps.py` jde snadno upravit pro tuto verzi: symboly z `build\bomber.sym`,
`player_x`/`player_y` místo `_players`, start hry jako `tools/emu/emu.py` `start_game`.

## Jak to vypadá v této verzi (`sapi/platform.asm`, `poll_key` a `key_dir`)

Tady se šipka nedrží po snímcích, je to stavový automat: `kdir_code`, `kdir_fresh`, `kdir_cont` (nejvýš 2 kroky)
a `kdir_more`. Hráč na celém políčku poznává podle liché souřadnice v ose pohybu. Příčiny 2 a 3 tu proto nejsou
stejně, **příčina 1 ale ano**:

- `poll_key`, větev `.pk_new`: stisk **jiné** šipky, než je `kdir_code`, okamžitě přepíše `kdir_code` a nastaví
  `kdir_fresh = 1`, `kdir_cont = 2`, `kdir_more = 0`. Je-li hráč zrovna po prvním kroku (sudá souřadnice v původní
  ose), udělá první krok novým směrem a zbytek nové osy doběhne. **Na původní ose ale zůstane v půlce** a další
  zatáčení se zasekává (pohyb kolmo vyžaduje volné 2×2 před hráčem, v půlce políčka narazí na pilíř).
- Návrh opravy ve stejném duchu jako v C: když přijde jiná šipka a `kdir_code` je aktivní a hráč je v ose
  pohybu v půlce (sudá souřadnice), **ulož ji jako další** (nová proměnná, např. `kdir_next`). V `key_dir` u
  `.kd_stop` (dojdeno na celé políčko) ji převezmi jako nový stisk (`kdir_code`, `kdir_fresh = 1`, `kdir_cont = 2`).
  Na celém políčku může nový směr začít hned.
- Dál ověřit:
  - `kdir_more` přidá jen jedno další políčko. Rychlé ťukání stejnou šipkou tedy nezpůsobí půlku, jen se další
    stisky ztratí. Případně počítadlo místo příznaku.
  - `kdir_cont` = 2 pokusy: když je druhý krok blokovaný (bomba?), hráč zůstane v půlce. Zdi a pilíře jsou na
    celých políčkách, takže by to nemělo nastat. Ověřit s položenou bombou a nepřítelem.
  - **Joystick chodí po znacích**, po puštění páky může hráč stát v půlce. Šipka ho pak má dorovnat (stisk
    s `kdir_fresh` udělá krok a `.kd_axis` doběhne na lichou souřadnici). Ověřit, že to platí i pro zatočení
    z půlky.
- **Ztracené stisky** (ne půlky): `poll_key` se volá jen v čekacích smyčkách. Pulz Consulu 1 ms během práce snímku
  se ztratí (popsáno v `docs/technika.md`). Při 2 MHz zbývá v klidu asi 50 ms čekání ze 60, při výbuchu méně.

**Doporučený postup:** nejdřív test jako `taps.py` a zopakovat chybu (počet půlek), pak oprava, pak stejný test
(0 půlek) a porovnání obrazovek se starou verzí (pravidlo `docs/vyvoj.md`: herní logika se nesmí změnit). Změna je
jen v `platform.asm`, `draw_buffer` se nemění.

## Joystick v menu

V C verzi (BomberNet má menu s režimem, sítí, hráči a kódem místnosti) se menu ovládalo jen klávesnicí. Teď
páka a palba platí i jako šipky a mezera. V této verzi menu není: titulek čeká jen na `key_fire`, který už čte
palbu joysticku (`IN 54h`, D4). Mělo by to tedy fungovat a stačí ověřit:
- titulek → palba joysticku spustí hru;
- ESC/BREAK (konec do CP/M) joystickem nejde, a nemusí.

**Pozor v GUI SAPIemu:** Ctrl+F8 přepne šipky a mezerník PC na joystick MPH-1V. Do klávesnice SAPI pak
nejdou, takže šipkami SAPI jde jen joystick. Při zkoušení klávesnice Ctrl+F8 vypnout.

## Výsledek v této verzi (2026-10-16)

- **Test:** `tools/emu/taps.py` (převzatý `taps.py`, symboly z `build\bomber.sym`, nepřátelé vypnutí, čas
  udržovaný).
- **Příčina 1 potvrzená:**
  - pomalé ťukání (s pauzou) 0 půlek;
  - rychlé ťukání (`--fast`, seed 1–3 po 120 ťuknutích) před opravou 4 + 3 + 0 = 7 půlek ze 112 kontrol;
  - s EKL-1 (seed 2) 3 půlky.
- **Oprava v `sapi/platform.asm`:**
  - `poll_key` (`.pk_other`): jiná šipka během pohybu, kdy je hráč v ose pohybu v půlce (`kdir_half`: sudá
    souřadnice), se uloží do `kdir_next`;
  - `key_dir` (`.kd_stop`): na celém políčku ji převezme a hned udělá její první krok;
  - na celém políčku začne nový směr hned, jako dřív.
- **Po opravě:** stejné série 0 půlek (Consul i EKL-1). Herní logika beze změny: scénáře `walk`, `chain`,
  `death` a vypršení času v každém snímku (494 obrazovek) a pomalé ťukání (60 obrazovek) jsou shodné se starou
  verzí.
- **Další body zápisu:**
  - `kdir_more`: rychlé ťukání stejnou šipkou dá nejvýš jedno políčko navíc, půlky nedělá (je i v `--fast`).
  - `kdir_cont` a blokovaný druhý krok: bomby ani nepřátelé pohyb neblokují (`count_block` jen zdi, pilíře
    a cihly). Ověřeno přechodem přes vlastní bombu po celých políčkách.
  - Joystick v půlce políčka: šipka ve stejné ose hráče dorovná. Kolmá šipka nepomůže (pilíř), stejně jako
    ve staré verzi. Je to v `docs/stav.md` jako možný další krok.
- **Joystick na titulku:** páka nic nedělá, palba spustí hru, držená palba bombu nepoloží, ve hře páka hýbe
  hráčem. ESC joystickem nejde (nemusí).
