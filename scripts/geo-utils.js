/**
 * Geo utilities — great-circle distance calculations for GeoJSON features.
 * All distances are in kilometres using the WGS-84 mean Earth radius (6371 km).
 */

const EARTH_RADIUS_KM = 6371;

/**
 * Haversine great-circle distance between two lat/lon coordinate pairs.
 * @param {number} lat1 - Latitude of point A (degrees)
 * @param {number} lon1 - Longitude of point A (degrees)
 * @param {number} lat2 - Latitude of point B (degrees)
 * @param {number} lon2 - Longitude of point B (degrees)
 * @returns {number} Distance in kilometres
 */
export function haversineKm(lat1, lon1, lat2, lon2) {
  const toRad = (d) => (d * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * EARTH_RADIUS_KM * Math.asin(Math.sqrt(a));
}

/**
 * Great-circle distance between two GeoJSON Point features.
 * @param {object} featureA - GeoJSON Feature with Point geometry
 * @param {object} featureB - GeoJSON Feature with Point geometry
 * @returns {number} Distance in kilometres
 */
export function distanceBetween(featureA, featureB) {
  const [lon1, lat1] = featureA.geometry.coordinates;
  const [lon2, lat2] = featureB.geometry.coordinates;
  return haversineKm(lat1, lon1, lat2, lon2);
}

/**
 * Returns all cities sorted by distance from a target feature (nearest first).
 * @param {object} target - GeoJSON Point feature
 * @param {object[]} candidates - Array of GeoJSON Point features
 * @returns {{ feature: object, distanceKm: number }[]}
 */
export function sortByDistance(target, candidates) {
  return candidates
    .map((f) => ({ feature: f, distanceKm: distanceBetween(target, f) }))
    .sort((a, b) => a.distanceKm - b.distanceKm);
}

/**
 * Build a minimal GeoJSON Point feature.
 * @param {string} name
 * @param {number} lat
 * @param {number} lon
 * @param {object} [extraProps]
 */
export function makeFeature(name, lat, lon, extraProps = {}) {
  return {
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [lon, lat] },
    properties: { name, ...extraProps },
  };
}
