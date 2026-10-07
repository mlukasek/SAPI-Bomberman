# Rozhodnutí

Rozhodnutí autora a jejich důvody. Nové rozhodnutí dopsat sem.

## Projekt

- **Vlastní repo** (2026-10-05):
  - Port je v repu SAPI-Bomberman (github mlukasek/SAPI-Bomberman), ne v SAPIemu.
  - Je to zároveň test emulátoru: chyby emulátoru, na které se narazí, se opravují v SAPIemu.
  - BomberNet autorovi nepatří, slouží jen jako zdroj.
- **Cílová sestava:** SAPI-1 „V“ s CGA-1V a MPH-1V (`machines/sapi1v.sapi` v SAPIemu), CP/M `.COM` od 0100h.
- **Assembler pasmo 0.5.3:** originál s ním vyjde bajt po bajtu stejně jako páska MZ.
  - z88dk je u autora v `E:\SAPI_GIT\Tools\z88dk` (pro případnou práci v C, jako BomberNet).
  - Rozšířit `tools/asm8080.py` ze SAPIemu o Z80 je vítané, ale není nutné.
- **Port zachovává herní kód.** Mění se jen HW vrstva, vykreslování, zvuk a vstup. Obsah `draw_buffer` musí
  být v každém okamžiku stejný jako na MZ, každá změna se ověřuje porovnáním obrazovek po snímcích.
- **Rychlost:** pevný snímek 60,8 ms (rychlost MZ-700 v klidu podle BomberNet), cíl i při CPU 2 MHz.

## Vstup

- **Joystick a klávesnice zvlášť:** palba a páka se čtou odděleně, takže jde chodit a pokládat bomby zároveň
  (na MZ jen jedna klávesa).
- **Šipka = jedno políčko** (autor, 2026-10-05). Klávesnice nepoznají držení klávesy. Dřívější „držená
  4 snímky“ nechávala hráče v půlce políčka.
- **Klávesnice potvrzuje ACK jako MikroMon** (2026-10-05). Funguje tak Consul 262.3 bez 7474 i EKL-1.
- **Stisk, který spustí hru, nepoloží bombu** (autor, 2026-10-05).

## Zvuk

- **YM3812 místo bzučáku:** výška z `RATIO` originálu. Hodiny 8253 jako u evropského MZ-700.
- **Pípání nezastavuje hru** (2026-10-05):
  - fronta tónů, takže se zachová sled tónů z MZ;
  - konec tónu podle čítače 2 v 82C54;
  - bez přerušení, hra běží se zakázanými přerušeními.

## Vydání 1.0.0 (2026-10-07)

- **Verze 1.0.0** (autor): hra je kompletní a hratelná, autor ji ověřil na skutečném SAPI-1 V.
- **Repo bude veřejné** (autor). Znakový generátor MZ-700 (© Sharp) z repa i z historie odstraněn
  (autor zvolil přepis historie).
  - V repu zůstávají odvozené dlaždice (`sapi/tables.asm`), stejně jako BomberNet zveřejňuje odvozené
    tabulky.
  - Páska `orig/bomber.mzf` a disassembler zůstávají, BomberNet je také zveřejňuje.
  - **Push přepsané historie** (autor, 2026-10-07): normální force push do stávajícího repa. Stačí, že ROM
    není vidět v aktuálním stavu. Ve staré historii by ji našel jen ten, kdo by se v ní šťoural, a ROM
    40 let starých počítačů jsou dostupné i jinde.
- **Bez licence** (autor, 2026-10-07): hru má licencovanou Hudson Soft, dávat na ni GPL-3 (jako u SAPIemu) je
  nevhodné. Soubor `LICENSE` proto v repu není.
- **Emulátor pro hru:** release SAPIemu (`E:\SAPI_GIT\SAPIemu-release`), ne vývojový SAPIemu (autor ho vyvíjí
  paralelně).
- **Dokumentace:** README pro uživatele, technické a vývojové informace v `docs/`. Dokumentace česky, kód
  a komentáře anglicky.
