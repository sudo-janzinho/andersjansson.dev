# Kartfunksjonen på Fritidsaktiviteter i Asker

*Dokumentert: 2026-09-01*

Denne siden forklarer hvordan kartfunksjonen (Liste/Kart) ble bygget inn i `index.html` for Fritidsaktiviteter i Asker. Målet var å la brukeren veksle mellom en vanlig klubb-liste og et interaktivt kart med fargekodede markører, synkronisert med søk, filter og "Søk i nærheten".

---

## 1. Hva som ble lagt til

### 1.1 Leaflet (kartbibliotek) via CDN
I `<head>` ble Leaflet lastet inn fra CDN:

```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
```

Leaflet er et lett, åpen kildekode-kartbibliotek. Kartdata (fliser) hentes fra OpenStreetMap.

### 1.2 Segmentkontroll "Liste | Kart"
I headeren ble det lagt til to knapper som veksler visning:

```html
<div class="view-switch" role="tablist" aria-label="Visningsmodus">
  <button id="btn-list" class="active" role="tab" aria-selected="true">Liste</button>
  <button id="btn-map" role="tab" aria-selected="false">Kart</button>
</div>
```

### 1.3 Kartbeholder
Etter klubb-listen (`#grid`) ble det lagt til en kartbeholder:

```html
<div id="map-wrap" class="hidden">
  <div class="cat-legend" id="cat-legend"></div>
  <div id="map"></div>
  <p class="map-tip">Kartet synkroniserer med søk og filter. Zoom inn for å se hver enkelt klubb. Trykk på en markør for mer info, eller knappen "Søk i nærheten" for å vise klubber rundt deg.</p>
</div>
```

- `#cat-legend` – fargekodenøkkel (hvilken farge = hvilken aktivitet).
- `#map` – selve Leaflet-kartet.
- `.map-tip` – kort brukerhjelp.

### 1.4 Kart-JavaScript
Kartlogikken ble lagt i det eksisterende inline-`<script>`-blokken, slik at den får tilgang til de allerede eksisterende variablene (`cards`, `apply()`, `homePos`, `maxKm` osv.).

---

## 2. Hvordan kartet bygges

### 2.1 Fargekoding per aktivitet
Hver aktivitet (fotball, badminton, svømming osv.) får en fast farge. Farger defineres i et oppslag:

```js
const CAT_COLORS = { fotball: '#e74c3c', badminton: '#9b59b6', svømming: '#3498db', /* ... */ };
```

Aktiviteter som ikke finnes i oppslaget får en farge fra en fallback-palett.

### 2.2 Markører fra klubbkortene
Hvert klubbkort i `#grid` har data-attributter:

```html
<div class="card" data-lat="59.83" data-lon="10.44" data-name="..." data-activity="fotball" data-address="...">
```

`buildMarkers()` leser disse og lager en Leaflet-markør per klubb som har koordinater:

```js
function buildMarkers() {
  markerLayer.clearLayers();
  cards.forEach(c => {
    const lat = parseFloat(c.dataset.lat), lon = parseFloat(c.dataset.lon);
    if (!lat || !lon) return;               // klubber uten koordinater hoppes over
    if (c.classList.contains('hidden')) return;  // filtrerte klubber skjules
    const m = L.marker([lat, lon], { icon: coloredIcon(activity) });
    m.bindPopup(`<b>${name}</b><br>${activity}<br>${address}<br><a href="${page}">Mer info →</a>`);
    m.addTo(markerLayer);
  });
  if (markerLayer.getLayers().length) map.fitBounds(markerLayer.getBounds());
}
```

### 2.3 Synkronisering med søk/filter
Den eksisterende `apply()`-funksjonen (som viser/skjuler kort basert på søk, filter og avstand) ble wrappet slik at den også oppdaterer kartet:

```js
const origApply = apply;
apply = function () {
  origApply();
  if (mapInitialized) buildMarkers();
};
```

På den måten oppdateres markørene automatisk når brukeren søker, filtrerer eller bruker "Søk i nærheten".

---

## 3. Veksling mellom Liste og Kart

`setView('list' | 'map')` styrer hvilken visning som er aktiv:

```js
function setView(v) {
  const isMap = v === 'map';
  if (isMap) {
    grid.classList.add('hidden');          // skjul klubb-listen
    mapWrap.classList.remove('hidden');    // vis kartbeholderen
    mapWrap.style.height = '560px';        // eksplisitt høyde (viktig!)
    mapWrap.style.overflow = 'visible';
    mapWrap.style.margin = '0';
    mapWrap.style.padding = '0';
    void mapWrap.offsetHeight;             // tving reflow
    initMap();                             // opprett kartet (kun første gang)
    if (map) map.invalidateSize();
    buildMarkers();
  } else {
    grid.classList.remove('hidden');
    mapWrap.classList.add('hidden');
    mapWrap.style.height = '';
    mapWrap.style.overflow = '';
    mapWrap.style.margin = '';
    mapWrap.style.padding = '';
  }
  // oppdater aktiv knapp
  btnList.classList.toggle('active', !isMap);
  btnMap.classList.toggle('active', isMap);
  setMapViewport();
}
```

---

## 4. Den viktigste lærdommen (feilsøking)

Kartet fungerte ikke i starten – det var helt blankt under søkefeltene når man trykket "Kart". Etter grundig feilsøking (Playwright headless-tester) ble årsaken funnet:

### ❌ Problemet: `#map-wrap` lå INNI `#grid`
Da kartbeholderen ble satt inn i HTML-en, havnet den **inni** `<div class="grid" id="grid">` i stedet for etter den. Når man trykket "Kart", ble `#grid` satt til `display:none` – og siden `#map-wrap` var et barnebarn av `#grid`, forsvant kartet også. Kartet fikk høyde 0 og ble usynlig.

**Symptom:** `#map` hadde `clientHeight = 0`, markørene fantes i DOM (141 stk) men var usynlige, og flisene lastet ikke.

### ✅ Løsningen: Flytt `#map-wrap` UT av `#grid`
En manglende `</div>` gjorde at `#grid` aldri ble stengt før `#map-wrap`. Ved å legge til en ekstra `</div>` rett før `<div id="map-wrap">` ble `#map-wrap` et søsken av `#grid` (direkte under `<body>`), ikke et barnebarn.

**Verifisert:** `grid.contains(mapWrap) === false` og `mapWrap.parentElement === BODY`.

### 🔑 Nøkkelinnsikt
- **`#map-wrap` må ligge UTENFOR `#grid`** – ellers skjules kartet når listen skjules.
- **Eksplisitt høyde på `#map-wrap`** (`height: 560px`) er nødvendig for at Leaflet skal kunne måle kartets høyde. Uten den blir `#map` høyde 0.
- **`void mapWrap.offsetHeight`** tvinger en reflow slik at Leaflet får korrekt høyde ved initiering.

---

## 5. Teknisk oppsummering

| Del | Teknologi |
|-----|-----------|
| Kartbibliotek | Leaflet 1.9.4 (CDN) |
| Kartdata | OpenStreetMap-tiles |
| Markører | Fargekodet per aktivitet, popup med info + lenke |
| Synkronisering | Wrapper rundt eksisterende `apply()` |
| Veksling | `setView()` med `hidden`-klasse + inline høyde |
| Klubber på kartet | 141 av 197 (de med koordinater) |

### Filendringer
- `aktiviteter_asker/index.html` – kart-CSS, segmentkontroll, kartbeholder, kart-JS.

### Backup
- `aktiviteter_asker_backup_kart_20260901_120822/index.html` – fungerende versjon før deploy.

---

*Dokumentasjonen er skrevet for å kunne gjenskape eller videreføre kartfunksjonen, f.eks. til askeridrett.no.*
