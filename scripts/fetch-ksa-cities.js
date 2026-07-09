#!/usr/bin/env node
/**
 * Fetches GeoJSON for all cities in Saudi Arabia.
 *
 * Primary source  : OpenStreetMap Overpass API (overpass-api.de)
 * Fallback source : lutangar/cities.json on GitHub raw (raw.githubusercontent.com)
 *
 * Outputs: ksa-cities.geojson in the project root
 * Requires: Node.js 18+ (uses built-in fetch)
 *
 * Usage:
 *   node scripts/fetch-ksa-cities.js
 *   node scripts/fetch-ksa-cities.js --place city
 *   node scripts/fetch-ksa-cities.js --out ./output/cities.geojson
 *   node scripts/fetch-ksa-cities.js --source github     # force GitHub fallback
 *   node scripts/fetch-ksa-cities.js --source overpass   # force Overpass only
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, '..');

// ── Sources ─────────────────────────────────────────────────────────────────

const OVERPASS_URL = 'https://overpass-api.de/api/interpreter';

// lutangar/cities.json — world city list with lat/lng/country fields
const GITHUB_CITIES_URL =
  'https://raw.githubusercontent.com/lutangar/cities.json/master/cities.json';

// ── CLI flags ────────────────────────────────────────────────────────────────

const args      = process.argv.slice(2);
const flagValue = (flag) => { const i = args.indexOf(flag); return i !== -1 ? args[i + 1] : null; };

const placeArg  = flagValue('--place')  ?? 'all';   // city|town|village|all
const outArg    = flagValue('--out')    ?? path.join(PROJECT_ROOT, 'ksa-cities.geojson');
const sourceArg = flagValue('--source') ?? 'auto';   // auto|overpass|github

// ── Overpass ─────────────────────────────────────────────────────────────────

// Regex without anchors — anchored patterns (^...$) trigger 406 on some Overpass instances
const PLACE_FILTER =
  placeArg === 'all'
    ? '~"city|town|village|municipality"'
    : `"${placeArg}"`;

// admin_level=2 pins the area to the country boundary (avoids 406 from ambiguous area lookup)
const OVERPASS_QUERY = `
[out:json][timeout:180][maxsize:536870912];
area["ISO3166-1"="SA"]["admin_level"="2"]->.sa;
(
  node["place"${PLACE_FILTER}](area.sa);
  way["place"${PLACE_FILTER}](area.sa);
);
out center tags;
`.trim();

async function fetchWithRetry(url, opts, maxAttempts = 4) {
  const BACKOFF = [0, 2000, 4000, 8000];
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    if (attempt > 1) {
      const wait = BACKOFF[attempt - 1] ?? 16000;
      console.log(`  Retry ${attempt}/${maxAttempts} — waiting ${wait / 1000}s…`);
      await new Promise((r) => setTimeout(r, wait));
    }
    const res = await fetch(url, opts);
    if (res.ok) return res;
    const body = await res.text().catch(() => '');
    // Strip HTML tags for readable error output
    const plain = body.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 300);
    if (attempt === maxAttempts) throw new Error(`HTTP ${res.status}: ${plain}`);
    console.warn(`  HTTP ${res.status}: ${plain.slice(0, 120)}`);
  }
}

async function fetchFromOverpass() {
  console.log('Source: Overpass API (OpenStreetMap)');
  const res = await fetchWithRetry(OVERPASS_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `data=${encodeURIComponent(OVERPASS_QUERY)}`,
  });
  const data = await res.json();
  if (!Array.isArray(data.elements)) throw new Error('Unexpected Overpass response shape');

  return data.elements
    .map((el) => {
      let lon, lat;
      if (el.type === 'node')      { lon = el.lon;        lat = el.lat;        }
      else if (el.center)          { lon = el.center.lon; lat = el.center.lat; }
      else return null;
      const t = el.tags ?? {};
      return {
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [lon, lat] },
        properties: {
          osm_id:      el.id,
          osm_type:    el.type,
          name:        t.name        ?? '',
          name_ar:     t['name:ar'] ?? '',
          name_en:     t['name:en'] ?? '',
          place:       t.place       ?? '',
          population:  t.population != null ? Number(t.population) || t.population : null,
          admin_level: t.admin_level ?? null,
          wikidata:    t.wikidata    ?? null,
          source:      'openstreetmap',
        },
      };
    })
    .filter(Boolean);
}

// ── GitHub fallback ──────────────────────────────────────────────────────────

async function fetchFromGitHub() {
  console.log('Source: lutangar/cities.json via raw.githubusercontent.com');
  const res = await fetchWithRetry(GITHUB_CITIES_URL, {});
  const all  = await res.json();
  const sa   = all.filter((c) => c.country === 'SA');
  console.log(`  Found ${sa.length} SA cities in dataset`);

  return sa.map((c) => ({
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [parseFloat(c.lng), parseFloat(c.lat)] },
    properties: {
      name:    c.name,
      name_ar: '',
      name_en: c.name,
      place:   'city',
      population:  null,
      admin_level: c.admin1 || null,
      wikidata:    null,
      source:      'lutangar/cities.json',
    },
  }));
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const outputPath = path.resolve(outArg);
  console.log(`\nFetching KSA cities (place: ${placeArg}) → ${outputPath}\n`);

  let features;

  if (sourceArg === 'github') {
    features = await fetchFromGitHub();
  } else {
    try {
      features = await fetchFromOverpass();
    } catch (err) {
      if (sourceArg === 'overpass') throw err;
      console.warn(`\nOverpass unavailable (${err.message.slice(0, 80)})`);
      console.warn('Falling back to GitHub dataset…\n');
      features = await fetchFromGitHub();
    }
  }

  const geojson = {
    type: 'FeatureCollection',
    metadata: {
      source:        features[0]?.properties?.source ?? 'unknown',
      query_date:    new Date().toISOString(),
      place_filter:  placeArg,
      country:       'Saudi Arabia',
      iso3166_1:     'SA',
      feature_count: features.length,
    },
    features,
  };

  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(geojson, null, 2), 'utf8');

  console.log(`\nSaved ${features.length} features to ${outputPath}`);

  // Breakdown by place type
  const counts = features.reduce((acc, f) => {
    const p = f.properties.place || 'unknown';
    acc[p] = (acc[p] ?? 0) + 1;
    return acc;
  }, {});
  if (Object.keys(counts).length > 1) {
    console.log('\nBreakdown by place type:');
    Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .forEach(([type, count]) => console.log(`  ${type}: ${count}`));
  }
}

main().catch((err) => { console.error('Error:', err.message); process.exit(1); });
