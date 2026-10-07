# Síťová hra (plán)

Až bude síťová karta pro SAPI. Zatím jen podklady a úvahy.

## Podklady

**BomberNet** (`..\BomberNet`, github MZPico/BomberNet, autorovi nepatří) má síťovou verzi pro MZ-700/800 a ZX
Spectrum (přepis do C, z88dk):
- `docs/net-protocol.md`, `docs/net-timing.md`;
- síťové zařízení jako deset volání (`c/core/netdev.h`), lockstep (`c/core/netplay.c`);
- relay přes WebSocket (`relay/`), testy dvou emulátorů proti sobě (`tools/lockstep_*.py`).

## Co z portu vyplývá

- **Hra je deterministická po snímcích.** Stav se mění jen v `main_loop` a vstup se čte jednou za snímek
  (`key_dir`, `key_fire`). To se hodí pro lockstep: vyměňuje se jen vstup.
- **Náhoda musí být společná.** `random` míchá registr R, který závisí na počtu provedených instrukcí. Stačí
  sdílené semínko a `random` bez R (skripty v `tools/emu` to tak dělají už teď).
- **Rezerva času:** při 2 MHz zbývá ze snímku v klidu asi 50 ms, v nejhorším případě (5 bomb) asi 6 ms. Při
  4 MHz vždy přes 30 ms.
- **Paměť:** volných asi 33 KB (3C00h–BFFFh), viz `docs/technika.md`.
- **Grafika:** originál je pro jednoho hráče.
  - Další hráče kreslit jako další 2x2 objekty přes `draw_addr_w`. Pravidlo označování zápisů pro
    `flush_screen` platí i pro ně.
  - Dlaždice a barvy přidat v `tools/make_tables.py`. Na nové dlaždice je potřeba znakový generátor nebo
    vlastní kresba.
- **Porty:** hra používá 01h, 02h, 50h–57h a 63h. Kartu bude potřeba přidat do SAPIemu.
- **Klávesnice** se čte jen v čekacích smyčkách. Síťová komunikace by asi měla běžet tam, kde se teď čeká na
  snímek (`frame_wait`).
