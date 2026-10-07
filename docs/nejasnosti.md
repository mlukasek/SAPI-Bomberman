# Nejasnosti k ověření na skutečném HW

Hra je zatím vyzkoušená jen v SAPIemu. Na skutečném SAPI-1 V ověřit:

- **Rychlost a zvuk na skutečné desce.** YM3812 má časování zápisů podle katalogu 3,3 µs po adrese a 23 µs po
  datech, `ym_write` čeká podle toho.
- **Délka snímku 60,8 ms** je převzatá z BomberNet (`docs/port-zx-spectrum.md` tam). Na skutečném MZ-700 ji
  nikdo z nás neměřil.
- **Klávesnice:**
  - ACK (`OUT 01h,03h`) při Consulu 262.3 bez 7474 na JPR-1V: v emulátoru nevadí, na HW ověřit, že nic neruší;
  - EKL-1 na JPR-1V: funguje s ACK?
  - kolik stisků Consulu se ztratí (STROBE 1 ms se čte jen v čekacích smyčkách).
- **Latch čítače 2 v 82C54** (`OUT 53h,80h`, dvě čtení 52h) pro délku tónů.
- **CGA-1V:** hra píše přímo do zobrazované stránky A (bez čekání na VBI). Na HW se podívat, jestli obraz
  netrhá.
- **Zakázaná přerušení a POP/PUSH přes SP** při kreslení: na JPR-1V nic, co by NMI vyvolalo?
