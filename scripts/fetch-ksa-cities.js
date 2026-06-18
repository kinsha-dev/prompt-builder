#!/usr/bin/env node
/**
 * Fetches GeoJSON for all cities, towns, and villages in Saudi Arabia
 * using the OpenStreetMap Overpass API.
 *
 * Outputs: ksa-cities.geojson in the project root
 * Requires: Node.js 18+ (uses built-in fetch)
 *
 * Usage:
 *   node scripts/fetch-ksa-cities.js
 *   node scripts/fetch-ksa-cities.js --place city
 *   node scripts/fetch-ksa-cities.js --out ./output/cities.geojson
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(__dirname, '..');

const OVERPASS_URL = 'https://overpass-api.de/api/interpreter';

// Parse CLI flags
const args = process.argv.slice(2);
const flagIndex = (flag) => args.indexOf(flag);
const flagValue = (flag) => {
  const i = flagIndex(flag);
  return i !== -1 ? args[i + 1] : null;
};

// --place city|town|village|all  (default: all)
const placeArg = flagValue('--place') ?? 'all';
// --out <path>  (default: <root>/ksa-cities.geojson)
const outArg = flagValue('--out') ?? path.join(PROJECT_ROOT, 'ksa-cities.geojson');

const PLACE_FILTER =
  placeArg === 'all'
    ? '~"^(city|town|village|municipality|borough)$"'
    : `"${placeArg}"`;

// Overpass QL query — targets the ISO 3166-1 area for Saudi Arabia
const buildQuery = () => `
[out:json][timeout:120];
area["ISO3166-1"="SA"]->.sa;
(
  node["place"${PLACE_FILTER}](area.sa);
  way["place"${PLACE_FILTER}](area.sa);
  relation["place"${PLACE_FILTER}](area.sa);
);
out center tags;
`.trim();

/** POST query to Overpass and return parsed JSON. */
async function queryOverpass(query, attempt = 1) {
  const MAX_ATTEMPTS = 4;
  const BACKOFF_MS = [0, 2000, 4000, 8000];

  if (attempt > 1) {
    const wait = BACKOFF_MS[attempt - 1] ?? 16000;
    console.log(`Retry ${attempt}/${MAX_ATTEMPTS} — waiting ${wait / 1000}s...`);
    await new Promise((r) => setTimeout(r, wait));
  }

  const res = await fetch(OVERPASS_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `data=${encodeURIComponent(query)}`,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    if (attempt < MAX_ATTEMPTS) {
      console.warn(`HTTP ${res.status}: ${text.slice(0, 120)}`);
      return queryOverpass(query, attempt + 1);
    }
    throw new Error(`Overpass API error ${res.status}: ${text.slice(0, 200)}`);
  }

  return res.json();
}

/** Convert a single OSM element to a GeoJSON Feature (Point). */
function toFeature(el) {
  let lon, lat;
  if (el.type === 'node') {
    lon = el.lon;
    lat = el.lat;
  } else if (el.center) {
    lon = el.center.lon;
    lat = el.center.lat;
  } else {
    return null; // way/relation without center — skip
  }

  const tags = el.tags ?? {};

  return {
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates: [lon, lat],
    },
    properties: {
      osm_id: el.id,
      osm_type: el.type,
      name: tags.name ?? '',
      name_ar: tags['name:ar'] ?? '',
      name_en: tags['name:en'] ?? '',
      place: tags.place ?? '',
      population: tags.population != null ? Number(tags.population) || tags.population : null,
      admin_level: tags.admin_level ?? null,
      wikipedia: tags.wikipedia ?? null,
      wikidata: tags.wikidata ?? null,
    },
  };
}

/** Main entry point. */
async function main() {
  const query = buildQuery();
  const outputPath = path.resolve(outArg);

  console.log(`Querying Overpass API for KSA cities (place: ${placeArg})...`);
  console.log(`Output → ${outputPath}\n`);

  const data = await queryOverpass(query);

  if (!Array.isArray(data.elements)) {
    throw new Error('Unexpected response shape — missing elements array');
  }

  console.log(`Received ${data.elements.length} OSM elements.`);

  const features = data.elements.map(toFeature).filter(Boolean);

  const geojson = {
    type: 'FeatureCollection',
    metadata: {
      source: 'OpenStreetMap via Overpass API',
      query_date: new Date().toISOString(),
      place_filter: placeArg,
      country: 'Saudi Arabia',
      iso3166_1: 'SA',
      feature_count: features.length,
    },
    features,
  };

  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(outputPath, JSON.stringify(geojson, null, 2), 'utf8');

  console.log(`\nSaved ${features.length} features to ${outputPath}`);

  // Summary by place type
  const counts = features.reduce((acc, f) => {
    const p = f.properties.place || 'unknown';
    acc[p] = (acc[p] ?? 0) + 1;
    return acc;
  }, {});
  console.log('\nBreakdown by place type:');
  Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .forEach(([type, count]) => console.log(`  ${type}: ${count}`));
}

main().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});
