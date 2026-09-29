# Verdrahtungsplan `lvds_tx`

Plan zum Routen von `layout/lvds_tx.gds` in KLayout. Die
Bilder sind waagerecht maßstäblich (1 Zeichen ≈ 1 µm), senkrecht gestaucht.
Koordinaten in µm, global in `lvds_tx` (57,5 × 61,1 µm). Der Driver liegt bei
(0, 0), Driver-lokal ist also global.

**Alles sitzt auf Regelabstand** (`layout.md`, *Placing by hand*): benachbarte PMOS teilen sich
n-Wanne und ThickGateOx (0,85 µm Überlappung), benachbarte NMOS ihr
ThickGateOx (0,175 µm), zwischen PMOS und NMOS liegen 0,5 µm. Gleich lange
Spiegelpaare teilen sich sogar den **Guard-Ring**: Kontaktbalken exakt auf
Kontaktbalken (1,54 µm PMOS, 0,92 µm NMOS Überlappung) – `M5|M4`, `M1|M3`,
`M6_0|M6_1`, `M9|M10`, die beiden `Mt`, `Mid|Mio`, `Mld|Mlo`, `Mpxn|Mpxp`,
`Mnxn|Mnxp`. Es gibt keine
Verdrahtungskanäle mehr: Metal1 bleibt in den Devices, alles ab Metal2 läuft
über die Devices.

## 0. Konventionen

| Lage | Richtung | wofür |
|---|---|---|
| Metal1 | – | nur in den Devices, und als Brücke zwischen zwei Guard-Ringen (0,24–0,54 µm auseinander) |
| Metal2 | waagerecht | Finger-Straps über jedem Device: Drain-Strap über der einen Hälfte, Source-Strap über der anderen; kurze Gate-Sprünge |
| Metal3 | senkrecht | Device ↔ Device, Stammleitungen, Achse |
| Metal4 | waagerecht | lange Querverbindungen, Busse, Kreuzkondensatoren |
| TopMetal1 | Kamm | Va / Vss, min. 1,64 µm breit und Abstand |

* **Guard-Ringe:** alle PMOS-Ringe sind Va, alle NMOS-Ringe Vss. Zwei
  benachbarte Ringe dürfen also frei mit Metal1 überbrückt werden – so
  erreicht die Versorgung auch Devices in der Mitte eines Blocks.
* **`Cxp`/`Cxn` (cap_cmomf) sind innen Metal1–Metal4.** Darüber nur
  TopMetal1. `c1` (Out) zeigt zu den Schaltern, `c2` (In) nach oben.
* **3,7-mA-Pfade** (`tail_p`, `tail_n`, `Out_p`, `Out_n`, Va/Vss am Driver):
  ≥ 4 µm Querschnitt, z. B. M3 + M4 übereinander. Faustwert ~1 mA/µm – das
  PDK-Regelwerk (`SG13CMOS5L_os_layout_rules.pdf`) nennt keine
  Stromdichtegrenzen, bitte in der Prozessspezifikation prüfen.
* Min. Maße: M1 0,16/0,18 µm, M2–M4 0,20/0,21 µm (0,24 µm Abstand neben
  Bahnen > 0,39 µm auf > 1 µm Länge – das M2.e aus `iref_x15`), Via
  0,19 µm, Abstand 0,22 µm.
* Rechte Hälfte = Spiegelbild der linken (Achse x = 28,8). Links routen,
  rechts spiegeln (KLayout: Auswahl → Transform → Mirror), nicht neu zeichnen.

## 1. Versorgungskamm (TopMetal1)

Va kommt von Westen, Vss von Osten; jeder Finger endet vor dem Strang der
anderen Seite, dadurch kreuzen sich die beiden nie. Die Finger liegen auf den
Grenzen zwischen den Blöcken, über den Devices:

```
  Va West (TM1, x 0-3)                               Vss Ost (TM1, x 54.5-57.5)
  ||=========================== Va  C1   y 63.8-65.5 ======>            ||   Oberkante
  ||[Cop] [ kpm: PMOS-Last oben ] [Mref] [ knm: PMOS-Last oben ] [Con]||
  ||[   ] [      Mt (NMOS) unten]        [      Mt (NMOS) unten] [   ]||
  ||   <======================== Vss C2    y 44-45   ================||
  ||[   ] [ Stage: NMOS-Reihe oben / PMOS-Reihe unten ]          [   ]||
  ||=========================== Va  C3   y 33-34   ======>             ||
  ||     [ Driver: Cc, M13/M2/M14, M5/M4  (PMOS)       ]               ||
  ||     [         M1/M3, M6, M11/M9/M10/M12 (NMOS)    ]               ||
  ||   <======================== Vss unten  y 0-2 ====================||
```

**Im Predriver gebaut** (Abschnitt 4) liegen die drei Finger über seine
volle Breite (global x 9,4–48,2): C1 Va y 58,1–61,1, C2 Vss y 42,1–48,6,
C3 Va y 33,0–36,0 – breiter als oben skizziert, weil sie die
TopVia1-Posts auf den Source-Straps überdecken müssen. Der Kamm in
`lvds_tx` muss sie nur noch an die Stränge anschließen (C1/C3 nach Westen,
C2 nach Osten); über `Cop`/`Con` hinweg ist dafür Platz.

Von jedem Finger per Via-Stapel auf die Guard-Ringe darunter, dann Ring an
Ring per Metal1 weiter. Die großen Source-Ströme (`M2` S an Va, `M6` S an
Vss) bekommen eigene M3-Stiche zum Finger. `Cop`/`Con` (S/D/B = Vss) stehen
unter dem Vss-Finger C2, der quer über sie läuft.

## 2. Signale zwischen den Blöcken

```
         Pins Nord (M3)          alle fünf nebeneinander über der Achse, 30 µA auf Iref_*
                                         D_n   Iref_pd  Iref_drv
                                          |  D_p  |   Vref |
                                          |   |   |     |  |
                                          |   |   |     |  |
         C1 M4          +-----------------o---|---|-----|--|-----------+          D_n
                        |      +--------------o---|-----|--|-----------|------+   D_p
                        |      |      Iref_pd  -> |     |  |           |      |
                 +------o------o---------+        |     |  | +---------o------o------+
                 |    Mid    Mio         |     +--o--+  |  | |       Mio    Mid      |
+-----+          |    D_n    D_p         |     |Mref |  |  | |       D_n    D_p      |         +-----+
|     |          |  G=Iref         Out   o-----o     o--|--|-o  Out       G=Iref     |         |     |
| Cop |          | kpm                   |     |D=G  |  |  | |           knm (m90)   |         | Con |
|     |          |                       |     +-----+  |  | |                       |         |     |
|G=Out|          +--------------------o--+              |  | +--o--------------------+         |G=Out|
|  _p |  C2 Vss                       |                 |  |    |                              |  _n |
|     |                               |                 |  |    |                              |     |
|S/D/B|                         In_p  |                 |  |    | In_n                         |S/D/B|
|=Vss |                               |                 |  |    |                              |=Vss |
|     |          +--------------------o-------------------------o--------------------+         |     |
|     |          | Out_p        predriver_stage         |  |                Out_n    |         |     |
+--o--+          +---o-----------------------------------------------------------o---+         +--o--+
   |                 |                                  |  |                     |                |
   |     C3 M4       |                                  |  |                     |                |
   |                 +---------+                        |  |           +---------+                |
   |Out_p                      | In_p                   |  |      In_n |                    Out_n |
   |                           |                   Vref |  |           |                          |
   |                           |                        |  |           |                          |
   |           +---------------o------------------------o--o-----------o---------------+          |
   +-----------o                               Driver                                  o----------+
               |                                                                       |
               +---------o---------------------------------------------------o---------+
                         |                                                   |
                         |                                                   |
                       Out_p           Pins Sued (zu den Pads)             Out_n
```

`o` = Anschluss, `+` = Abzweig/Ecke. Wo sich zwei Linien nur kreuzen, liegen
sie auf verschiedenen Lagen und sind nicht verbunden.
`Cop`/`Con` gehören zur Driver-Zelle, stehen aber links und rechts neben dem
Predriver; `Out_p`/`Out_n` laufen außen am Driver hinauf zu ihren Gates.

| Netz | von → nach | Weg |
|---|---|---|
| `Iref_pd` | Pin Nord neben der Achse → `Mref` (x 26,6–30,8, y 45,3–49,3, zwischen den Komparatoren auf Höhe ihrer Tails); 30 µA vom `iref_x15` im Top-Level | M3 senkrecht, x 27,9 |
| `Iref_drv` | Pin Nord auf der Achse → `M9` (unterste Reihe, x 26,4–29,2, y 1,7–4,6); 30 µA vom `iref_x15` im Top-Level | M3 auf der Achse, über `Mref`, Stage, `Cc`, `M2` und den `M6`-Stoß hinweg bis `M9` |
| `Vref` | Pin Nord → `M12` Gate (obere Gate-Schiene, y ≈ 3,8, ab x 31,0) | M3 auf der Achse neben `Iref_drv`, unten über `M10` hinweg per M2 nach rechts |
| `D_n`, `D_p` | Pins Nord → 4 Paar-Gates (`Mid`/`Mio`, y ≈ 48,9–54,8) | M4-Bus über den Paaren (y ≈ 54,8 / 55,4), je zwei M3-Abgänge |
| `In_p` | Stage `Out_p` (`Mpp2`/`Mnp2`, x 9,4–20,6) → `M5`/`M1` Gates | M3 senkrecht bei x ≈ 17,5 über `Cc` und `M13` hinweg bis auf die obere Gate-Schiene von `M5` (y ≈ 19,1) |
| `In_n` | Spiegelbild, x ≈ 40 | |
| `Out_p`, `Out_n` | Driver → Pins Süd, x ≈ 10–13,5 / 44–47,5; hinauf zu `Cop`/`Con` neben dem Predriver | Stamm M3 + M4 ≥ 4 µm |

Auf der Achse liegen damit drei M3-Bahnen nebeneinander (`Iref_pd` bis
`Mref`, `Iref_drv`, `Vref`): mit 0,3 µm Breite und 0,3 µm Abstand sind
das 1,5 µm. Die beiden 1:15-Vorspiegel, die früher darüber saßen, sind jetzt
ein eigenes Makro (`macros/iref_x15`) im Top-Level.

## 3. `Driver` (57,5 × 33,9 µm, mit `Cop`/`Con` bis y 57,7)

```
0    5    10   15   20   25   30   35   40   45   50   55  x/µm
+------+                                          +------+
|Cop_1 |                                          |Con_1 |
|  G=  |                                          |  G=  |
|Out_p |                                          |Out_n |
+------+         (hier sitzt der Predriver)       +------+
|Cop_0 |                                          |Con_0 |
|  G=  |                                          |  G=  |
|Out_p |                                          |Out_n |
|S/D/B |                                          |S/D/B |
| =Vss |                                          | =Vss |
+------+                                          +------+
======================== Va (TM1) ========================
 +------------------------------------------------------+
 |          Cc (10 Finger)   G=cc_g   S/D/B=Va          |
 +------------------------------------------------------+
+------------+  +---+-----------------+---+ +-------------+
|Ctn1 G=tail_n  |M13|        M2       |M14| |Ctn2 G=tail_n|
+------------+  |D=G|      G=cmfb     |G=p| +-------------+
                | pd|  D=tail_p S=Va  |D=c|      +-------+
         Out_p  +---+-----------------+---+ Out_n|cf Rc g|
           ::  +-------------+-------------+ ::  +-------+
+--+       ::  |      M5     |   M4 (m90)  | ::       +--+
|  |       ::  |    G=In_p   |    G=In_n   | ::       |  |
|R |       ::  |S=tail_p oben|S=tail_p oben| ::       |R |
|p +-----+ ::  |D=Out_p unten|D=Out_n unten| :: +-----+n |
|  | Cxp | ::  +-------------+-------------+ :: | Cxn |  |
|  | c2^ | ::  |      M1     |   M3 (m90)  | :: |  ^c2|  |
|  |  c1>| ::  |    G=In_p   |    G=In_n   | :: |<c1  |  |
|  |     | ::  | D=Out_p oben| D=Out_n oben| :: |     |  |
|  |     | ::  |S=tail_n unt.|S=tail_n unt.| :: |     |  |
+--+-----+ ::  +-------------+-------------+ :: +-----+--+
[----------- M6_0 ----------][----------- M6_1 ----------]
   [-------- M11 --------]M9|M10[------- M12 --------]
======================= Vss (TM1) ========================
          Out_p                             Out_n
```

Übereinander bzw. nebeneinander verschmolzen sind: `Cc` ↔ `M13`/`M2`/`M14`
↔ `M5`/`M4` (PMOS), `M1`/`M3` ↔ `M6_0`/`M6_1` ↔ `M11`/`M9`/`M10`/`M12`
(NMOS). `Rp`/`Cxp` und `Cxn`/`Rn` sitzen außen auf `M6`, `Cop`/`Con`
(je 2 × 10 × 5 µm, hochkant) stehen oben in den Ecken neben dem Predriver. `M6` sind zwei Blöcke à 31
Finger mit 1,6 µm, Stoß genau auf der Achse; `M9` und `M10` (je ein Finger
0,8 µm) sitzen in der untersten Reihe direkt unter diesem Stoß. Zwischen `M5`/`M4`
und `M1`/`M3` liegen 0,5 µm. `Rc` (rppd 1 × 6 µm, 1,6 kΩ, quer) liegt oben auf
`Rn` in der freien Ecke rechts von `M4`/`M14`, x 48,6–57,5, y 18,4–21,4: R1
links (x ≈ 49,8), R2 rechts (x ≈ 56,4), beide y ≈ 19,9. `cf` = `cmfb`, `g` =
`cc_g`. `Ctn1` (x 0–13,8, y 18,4–27,0) und `Ctn2` (x 42,6–57,5, y 21,4–27,0) sind
PMOS-Kondensatoren von `tail_n` nach Va in den beiden Ecken unter `Cc`, mit `Cc`
verschmolzen. `Cop`/`Con` sind je zwei Hälften (10 × 5 µm) auf einem gemeinsamen Ring,
beide Gates an `Out_p` bzw. `Out_n`.

### H-Brücke: so werden die Finger gestrapt

```
                 tail_p  (von M2-Drain, M3-Stiche bei x≈22-27 und 30.5-35.5,
                   |      Achse x≈28.8 frei lassen)
   M5  +===========+===== Source-Strap M2 =====+====+=====+   M4 (Spiegel)
       | | | | | | | | | | | | | | | | |       | | | | ...
       +===== Drain-Strap M2 (Out_p) =====+    +== Out_n ==
       | G-Schiene unten (y≈13.7)         |
  ---- In_p: M3-Stiche x≈15-17 von der unteren G-Schiene von M5 ---
       | G-Schiene oben (y≈11.2)          |      auf die obere von M1
   M1  +===== Drain-Strap M2 (Out_p) =====+    (Out_p: 3-4 M3-Stiche,
       | | | | | | | | | | | | | | |            x 21.5-27, verbinden die
       +===== Source-Strap M2 (tail_n) ===+     beiden Drain-Straps; x≈19 bleibt pd)
                   |
                 tail_n  (M3 hinunter auf die Drain-Straps von M6_0/M6_1)
```

### Netze im Driver

| Netz | verbindet | Weg | Breite |
|---|---|---|---|
| `tail_p` | `M2` D → `M5`/`M4` S | Drain-Strap über der unteren Hälfte von `M2`, Source-Straps über den oberen Hälften von `M5`/`M4`; M3-Stiche bei x ≈ 22–27 und 30,5–35,5 | ≥ 4 µm |
| `Out_p` | `M5` D, `M1` D, `Rp` R1, `Cxp` c1, `Cop_0`/`Cop_1` G → Pin Süd | Drain-Straps unten in `M5` / oben in `M1`, M3-Stiche dazwischen bei x ≈ 21,5–27; Stamm M3 bei x ≈ 10–13,5 im Spalt zwischen `Cxp` und den Schaltern, über `M6_0` und `M11` bis zur Südkante, mit M4 gedoppelt, wo keine M4-Bahn quert; die Drain-Straps (M2) nach links bis zum Stamm verlängert; `Cxp` c1 (rechter Rand, x 9,0, y ≈ 11,1) liegt direkt am Stamm; bei y ≈ 17,2 M4 nach links auf `Rp` R1 (x ≈ 1,5) und von dort M3 bei x ≈ 3 hinauf, über `Ctn1` und das linke Ende von `Cc` hinweg (beide belegen nur Metal1), bis auf die Gate-Schienen von `Cop_0` (y ≈ 35,2) und `Cop_1` (y ≈ 46,4) | ≥ 4 µm |
| `Out_n` | Spiegelbild, Stamm bei x ≈ 44–47,5, hinauf bei x ≈ 54,5 zu `Con` | der Weg hinauf kreuzt in M3 `Rc` zwischen seinen beiden Anschlüssen (dort kein Via), `Ctn2` und das rechte Ende von `Cc` | ≥ 4 µm |
| `tail_n` | `M1`/`M3` S → `M6_0`/`M6_1` D, `Ctn1` G, `Ctn2` G | Source-Straps unten in `M1`/`M3`, M3 hinunter auf die Drain-Straps über der oberen Hälfte von `M6_0`/`M6_1` (liegen direkt darunter). Zu den Kondensatoren je eine M3-Bahn am Außenrand der Schalter: links bei x ≈ 14,1 (zwischen `Out_p`-Stamm und `M5`/`M1`) hinauf bis y ≈ 18,9 und per M2 auf die untere Gate-Schiene von `Ctn1`; rechts gespiegelt bei x ≈ 43,4 auf die von `Ctn2` (y ≈ 21,9). **Niederohmig** – die Kondensatoren wirken auf die 50-ps-Flanken | ≥ 4 µm, Äste ≥ 1 µm |
| `In_p` | Stage → `M5` G, `M1` G, `Cxn` c2 | siehe Abschnitt 2 und Skizze; nach `Cxn` c2 (Oberkante, x ≈ 51,5, y 14,0) als M4 bei y ≈ 14,3 nach rechts | 0,3 µm |
| `In_n` | Spiegelbild; nach `Cxp` c2 (x ≈ 6, y 14,0) als M4 bei y ≈ 15,0 | | 0,3 µm |
| `Iref` | Achse → `M9` D+G, `M6_0`/`M6_1` G, `M10` G | M3 auf der Achse über den `M6`-Stoß bis in die unterste Reihe; `M9` (links der Achse) und `M10` (rechts) liegen Rand an Rand, ihre Gates per M2 verbunden; die untere Gate-Schiene von `M6_0`/`M6_1` liegt direkt über ihnen, per M2/M3-Stich an der Achse | 0,3 µm |
| `Vref` | Achse → `M12` G | M3 auf der Achse bis y ≈ 3,8, M2 über `M10` hinweg nach rechts auf die obere Gate-Schiene von `M12` (ab x 31,0) | 0,3 µm |
| `otail` | `M10` D → `M11` S, `M12` S | Source-Straps über den unteren Hälften von `M11`/`M12`; `M10` liegt direkt an `M12`, zu `M11` per M2 unter `M9` durch | 1 µm |
| `cm` | `Rp` R2, `Rn` R2 → `M11` G | von `Rp` R2 (x ≈ 1,5, y ≈ 9,3) M3 hinunter; M4 waagerecht bei y ≈ 7,5 über `M6` hinweg bis unter `Rn` (x ≈ 56) – **unter `Cxp`/`Cxn` durch, nicht darüber** (MOM, M1–M4 belegt); links M3 weiter hinunter bis y ≈ 3,8, M2 nach rechts auf die obere Gate-Schiene von `M11` (ab x 2,6) | 0,3 µm |
| `pd` | `M11` D → `M13` D+G → `M14` G | Drain-Strap über der oberen Hälfte von `M11`, M3 senkrecht bei x ≈ 19 über `M6_0`, `M1` und `M5` hinweg bis auf `M13` (x 15,6–19,5, die Bahn endet direkt über ihm); von `M13` M4 bei y ≈ 23 über `M2` hinweg auf `M14` G | 0,3 µm |
| `cmfb` | `M12` D → `M14` D → `M2` G, `Rc` R1 | Spiegelbild von `pd`: M3 bei x ≈ 38,5 von `M12` bis auf `M14` D; von `M14` D M2 waagerecht bei y ≈ 24 nach rechts über `Ctn2` hinweg (nur Metal1) und bei x ≈ 49,8 hinunter auf `Rc` R1 (y ≈ 19,9); y ≈ 24 statt tiefer, damit der `tail_n`-Anschluss von `Ctn2` (x ≈ 43,4, y ≈ 21,9) frei bleibt. `Cc` hängt nicht mehr an `cmfb`: keine Stiche mehr von `M2` G auf `Cc` | 0,3 µm |
| `cc_g` | `Rc` R2 → `Cc` G | von `Rc` R2 (x ≈ 56,4, y ≈ 19,9) M2 senkrecht hinauf, über `Ctn2` hinweg, auf die untere Gate-Schiene von `Cc` (y ≈ 27,3), die über alle 10 Finger läuft; rechts neben dem `Out_n`-Aufstieg (M3, x ≈ 54,5) | 0,3 µm |
| Va | alle PMOS-Ringe, `M2` S, `M13`/`M14` S, `Cc` S/D, `Ctn1`/`Ctn2` S/D | Finger C3 über `Cc`; Ring an Ring per M1 nach unten bis `M5`/`M4`; `M2`-Source-Strap mit 3–4 M3-Stichen über `Cc` hinweg an C3 | ≥ 4 µm für `M2` S |
| Vss | alle NMOS-Ringe, `M6` S, `M9`/`M10` S, `Cop`/`Con`, Ringe von `Rp`/`Rn` | Ring an Ring per M1; `M6`-Source-Straps (untere Hälfte) per M3 über `M11`/`M12` hinweg auf den unteren Finger; `Cop`/`Con` vom Finger C2 darüber | ≥ 4 µm für `M6` S |

## 4. `predriver` (38,8 × 28,0 µm, liegt bei x 9,4–48,2, y 33,0–61,1)

`scripts/archive/route_predriver.py` hat diese Verdrahtung per Skript gezeichnet (DRC
und LVS waren sauber), ist aber **archiviert**: sie nutzt Metal1 bis TopMetal1,
und der Chipalooza-Slot führt seine Versorgungs-Straps senkrecht in Metal4
über das ganze Projekt. Welche Lagen der Makro nutzen darf, wird zuerst
geklärt. Koordinaten hier im `predriver`-Rahmen (global: x + 9,36, y + 33,02).

```
   D_n D_p Iref          Pins Nord (M3), x 17,13 / 17,83 / 18,53
    |   |   |
  ==|===|===|======== TM1 Va    y 25,1-28,0 =====================  Posts von Mld/Mlo
    |   |   |   [kpm Mld|Mlo]                 [knm Mlo|Mld]
  --+---|---|------------------------------------ M4 D_n  y 21,8
  ------+---|------------------------------------ M4 D_p  y 22,4
            |   [kpm Mid|Mio]                 [knm Mio|Mid]     Abgriffe auf die
            |                                                   oberen Gate-Schienen
            +--> [Mref]  (Iref auf Mrefs obere Gate-Schiene)
                [kpm Mt|Mt]==[Mref]==[knm Mt|Mt]   Iref: ein M2-Balken durch die
                                                   unteren Gate-Schienen aller fuenf
  ================== TM1 Vss   y 9,1-15,6 ======================  Posts von Mt S, Stage-NMOS S
                [Stage NMOS]
  -------------------------- M4 Spur B  y 7,2 / Spur A y 6,4 ---
                [Stage PMOS]
  ================== TM1 Va    y 0,0-3,0 =======================  Posts von Stage-PMOS S
        In_p (x 8,14)                     In_n (x 30,66)         Pins Sued (M3)
```

* `D_p`/`D_n`: M4-Bus bei y 21,8 (`D_n`) und 22,4 (`D_p`), 0,8 / 1,4 µm
  über den oberen Gate-Schienen der Eingangspaare, je zwei M3-Abgriffe
  darauf: `D_n` auf `kpm Mid` (x ≈ 5,0) und `knm Mio` (≈ 27,8), `D_p` auf
  `kpm Mio` (≈ 11,0) und `knm Mid` (≈ 33,8). Die Pins kommen in M3 von oben
  herunter, über die Lasten hinweg.
* `Iref`: `Mref` (2 × 2 µm) sitzt auf der Achse **zwischen** den beiden
  Komparatoren (`kpm` x 3,5–16,4, `knm` x 22,4–35,3), unten auf Höhe ihrer
  Tails, x 17,2–21,5, y 12,3–16,3. Die vier Tail-Hälften sind nur unten
  kontaktiert, ihre Gate-Schienen und die untere von `Mref` liegen auf
  einer Höhe: **ein** M2-Balken durch alle fünf. `Mref`s Drain darauf
  (Diode). Der Pin (M3, x 18,53 – so nah an der Achse, wie
  `Iref_drv`/`Vref` es erlauben) kommt zwischen den Komparatoren herunter
  auf `Mref`s obere Gate-Schiene. `Mref`s Source geht in M2 auf seinen
  eigenen Ring; der hängt über die M1-Brücken der Stage an Vss.
* Komparator-Ausgang → Stage-Eingang: M3 bei x 15,96 (`kpm`) bzw. 22,84
  (`knm`) senkrecht hinunter auf den Gate-Balken von Spalte 3 bzw. 6.
* **Achse frei:** in M3 liegt zwischen x 18,68 und 20,10 nichts – dort laufen
  später `Iref_drv` und `Vref` (global 28,4 / 29,1) zum Driver durch.
* TopMetal1: drei Schienen über die volle Breite, `Va` oben und unten
  (erst der Versorgungskamm in `lvds_tx` verbindet die beiden), `Vss` in der
  Mitte. Im LVS werden die beiden `Va` per Name verbunden.

## 5. `predriver_comp` (`kpm`; `knm` ist das Spiegelbild)

```
   TM1 Va ------------------------------------------------------------
   Ring (Va) ============================================================
             S-Streifen in M1 hinauf in den Ring (kein Gate oben)
   Mldo      ein Block, ein Ring, 8 Finger:  S A S B S B S A S   (A = Mld, B = Mlo)
   (Mld|Mlo) [ S-Strap (Va) oben, 2 Posts = V2+V3+TV1 ----------------- ]
             [        D-Strap Mlo (Out) ueber B, nach rechts verlaengert ]
             [ Gate-Schiene M1 durch alle Finger; A-Streifen in M1 darauf ]
                  | net1 (M3, ab der Gate-Schiene)   | Out (M3)
   Mid|Mio   [ G oben (Din / Gin) ...................................... ]
             [ D-Strap Mid (net1)       ] [ D-Strap Mio (Out) -------+   ]
             [  D  S  D  S  D  S  D     |   D  S  D  S  D  S  D      |   ]
                   :     :     :                :     :     :        |     net2 in M1:
             [ ====:=====:=====:==== ]~M2~[ ====:=====:=====:=== ]   |     senkrecht + ein
                   :     :     :                :     :     :        |     Balken je Haelfte
             [ Vss net2 ... (Mt_0)      |   (Mt_1)                   |   ]
   Mt_0|Mt_1 [ S-Strap (Vss), 4 Posts, Via auf die Aussenbalken des Rings ]
             [ G unten (Iref) .......................................... ]
                                                     Out (M3) hinunter zur Stage
```

* **Tail unter dem Paar:** `Mt` ist zwei Hälften zu je 6 Fingern (L = 0,45
  µm wie das Paar), `Mt_0` unter `Mid`, `Mt_1` gespiegelt unter `Mio`,
  Finger auf Finger. `Mt` nur unten kontaktiert, Ring oben offen, das Paar
  nur oben kontaktiert, Ring unten offen; bei genau `JOIN` (1,56 µm
  Überlappung der Zellrahmen) werden die beiden Ringe einer. Zwischen den
  Reihen liegt kein Metal.
* `net2`: jeder Drain von `Mt` läuft in **Metal1** senkrecht in die Source
  des Paars darüber; ein Metal1-Balken im 0,68-µm-Spalt zwischen den Reihen
  verbindet die drei Spalten einer Hälfte; nur über den Ringbalken zwischen
  den Hälften (Vss) ein kurzes Stück Metal2. Kein Metal3 mehr.
* Last `Mld|Mlo`: **ein** Block mit acht Fingern in einem Ring
  (`devices.py: MERGED`), gemeinsames Gate `net1` und gemeinsame Source
  `Va`. Die Gate-Schiene läuft in Metal1 durch alle Finger, kein Ring
  dazwischen. Drains `ABBA`: `Mld` außen, `Mlo` innen (gemeinsamer
  Schwerpunkt).
* `net1`: `Mld`s Drain-Streifen laufen in Metal1 hinunter in die
  Gate-Schiene (Diode, ohne M2); ein M3-Link von der Gate-Schiene hinunter
  auf den Drain-Strap von `Mid`.
* `Out`: M2-Strap über `Mlo`s Drains, M3-Link auf `Mio` D; von dort M3
  senkrecht aus der Zelle nach unten zur Stage.
* `Iref`: die unteren Gate-Schienen von `Mt_0` und `Mt_1` per M2 verbunden
  (in `predriver` dann ein Balken bis `Mref` und zum anderen Komparator).
* `Vss`: ein M2-Strap über den Sources beider Hälften, vier Posts
  (2 × Via2/Via3, 1 TopVia1) abseits der `Out`-Leitung; der Strap läuft
  links und rechts über die Außenbalken des gemeinsamen Rings hinaus und
  landet dort auf einem Via – so sind Sources und Ring schon in der Zelle
  ein Vss.
* `Va`: zwei Posts vom Source-Strap der Last hinauf auf TopMetal1. Die Last
  ist nur unten kontaktiert (`topc 0`), ihre Source-Streifen laufen in
  Metal1 direkt hinauf in den Ring – der braucht keinen eigenen Via-Stapel.

## 6. `predriver_stage` (38,8 × 11,5 µm)

> **Stand 2026-09-29:** Die Stufe ist umgebaut (`layout.md`, *The stage:
> rows and tap strips*): Devices ohne Guard-Ring, PMOS und NMOS jeder Spalte
> auf einer Mittellinie, Va als ntap-Streifen unten, Vss als ptap-Streifen
> oben, 41,9 × 9,7 µm (die Streifen je 3,4 µm über die äußeren PMOS hinaus). Netze und Spuren unten gelten weiter, Koordinaten und
> alles zu Ringen, Ring-Vias und M1-Brücken zwischen Ringen nicht mehr.

```
   TM1 Vss -------------------------------------------------------------------
   NMOS-Ringe ==M1-Bruecken== hinauf zum Ring der Mt (mit Via und Post)
  [Mnp2 ] [Mnp1 ] [Mnp0 ] [Mnxn|Mnxp] [Mnn0 ] [Mnn1 ] [Mnn2 ]   S oben (Posts), D unten
    |G |D   |G |D  |D G|   |D G  G D|  |G D|   |D G|   |D G|
  --o-----o--|--------o----o         o-------------------------  Spur A y 6,4: net2 (Sp. 1-5), net3 (6-7)
  ---------o-o--------o---------o-----o-----o-----o-------o-----  Spur B y 7,2: net1 (2-3), net4 (4-8)
  [Mpp2 ] [Mpp1 ] [Mpp0 ] [Mpxn|Mpxp] [Mpn0 ] [Mpn1 ] [Mpn2 ]   D oben, S unten (Posts)
   PMOS-Ringe: untere Kanten per M1 zu einer Linie gebrueckt, jeder Post mit Ring-Via
   TM1 Va --------------------------------------------------------------------
   Out_p x 8,14                                       Out_n x 30,66
```

* Pro Spalte ein M2-Gate-Balken von der oberen Gate-Schiene des PMOS zur
  unteren des NMOS und eine M3-Drain-Leitung vom PMOS- zum NMOS-Drain-Strap.
* Die waagerechten Netze auf zwei M4-Spuren. `net2` und `net4` kreuzen
  beide die Achse, deshalb ist die rechte Hälfte das Spiegelbild der
  linken **mit vertauschten Spuren**: links `net2` auf A, `net1` auf B,
  rechts `net4` auf B, `net3` auf A.
* Spalte 4 (`Mpxn|Mnxn`, Gate `net4`) und Spalte 5 (Gate `net2`): der
  Gate-Anschluss geht per M2-Stich nach außen (x 17,19 / 21,61), weg von der
  Drain-Leitung und von der Achse, immer auf Höhe der Spur B – auf Höhe A
  käme er der PMOS-Gate-Schiene zu nahe.
* `Out_p`: zwei M3-Leitungen zwischen den Drain-Straps von `Mpp2` und
  `Mnp2`, eine davon bei x 8,14 weiter nach unten aus der Zelle (global
  17,5, die `In_p`-Leitung des Drivers). `Out_n` gespiegelt bei x 30,66.
* Versorgung: Posts auf den Source-Straps (PMOS unten auf TM1 Va, NMOS oben
  auf TM1 Vss). `Mnp0`/`Mnn0` (Eingang kommt direkt darüber) und die
  `Mpx`/`Mnx`-Paare (Source an der Achse) gehen stattdessen auf ihren Ring.
  Jeder NMOS-Ring hat eine M1-Brücke hinauf zum Ring der `Mt`, die
  NMOS-Posts laufen in M3 bis auf diese Brücken – so ist `Vss` schon in der
  Zelle ein Netz.

## 7. Reihenfolge

1. `predriver_comp` (von Hand angefangen; die Skriptversion liegt in
   `scripts/archive/route_predriver.py`).
2. `predriver_stage` (Skriptversion ebenso im Archiv).
3. `Driver`: zuerst Finger-Straps (M2), dann H-Brücke (`tail_p`, `Out`,
   `tail_n`), dann CMFB (`pd`, `cmfb`, `cc_g`, `cm`, `otail`), zuletzt Bias (`Iref`,
   `Vref`) und Ringe.
4. `predriver` (ebenso).
5. `lvds_tx`: Versorgungskamm (Stränge West/Ost an die TM1-Schienen des
   Predrivers), dann die Netze aus Abschnitt 2, Pins.

Geroutet wird direkt in `layout/lvds_tx.gds`. `make layout-pcells` tauscht dort
nur die `dev_*`-Zellen aus. Verdrahtung gehört deshalb in die Zelle des
Subcircuits (`predriver_comp`, `Driver`, …), nie in eine `dev_*`-Zelle.
Nach jeder Zelle `bash scripts/check_lvs.sh <zelle>`.
