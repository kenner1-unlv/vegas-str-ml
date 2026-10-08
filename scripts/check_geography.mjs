import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { parseDataset, parseGeography } from "../web/src/lib/data.ts";

const index = JSON.parse(await readFile(new URL("../web/static/data/index.json", import.meta.url)));
assert.match(index.path, /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/);
if (index.geography) {
  const base = new URL("../web/static/data/" + index.path + "/", import.meta.url);
  const bytes = await readFile(new URL("listings.json", base));
  const listings = parseDataset(JSON.parse(bytes));
  const sha = createHash("sha256").update(bytes).digest("hex");
  const raw = JSON.parse(await readFile(new URL("geography.json", base)));
  const geography = parseGeography(raw, listings, sha);
  const boundaries = JSON.parse(await readFile(new URL("zcta-boundaries.geojson", base)));
  const codes = new Set(boundaries.features.map(feature => feature.properties.zcta));
  assert.equal(codes.size, boundaries.features.length);
  for (const row of geography.assignments) {
    assert.deepEqual(Object.keys(row).sort(), ["id", "near_boundary", "status", "zcta"]);
    if (row.zcta) assert.ok(codes.has(row.zcta));
  }
  const counts = Object.fromEntries(["assigned", "ambiguous", "unassigned"].map(
    status => [status, geography.assignments.filter(row => row.status === status).length],
  ));
  for (const [key, count] of Object.entries(counts)) assert.equal(raw.counts[key] ?? 0, count);
  assert.equal(raw.near_boundary_count, geography.assignments.filter(row => row.near_boundary).length);
  assert.throws(() => parseGeography(raw, listings, "wrong checksum"));
  const duplicate = structuredClone(raw);
  duplicate.assignments[1] = duplicate.assignments[0];
  assert.throws(() => parseGeography(duplicate, listings, sha));
  const wrongSnapshot = { ...raw, snapshot_date: "2000-01-01" };
  assert.throws(() => parseGeography(wrongSnapshot, listings, sha));
  const badFlag = structuredClone(raw);
  badFlag.assignments[0].near_boundary = "false";
  assert.throws(() => parseGeography(badFlag, listings, sha));
  console.log("Geography contract: " + geography.assignments.length + " string-ID assignments, hashes, codes, counts and rejection cases passed.");
} else {
  console.log("Snapshot has no optional geography sidecar.");
}
