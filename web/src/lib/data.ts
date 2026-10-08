export type Listing = {
  id: string;
  latitude: number;
  longitude: number;
  price: number;
  room_type: string;
  bedrooms: number | null;
  neighborhood: string;
};
export type Dataset = {
  schema_version: number;
  snapshot_date: string;
  synthetic: boolean;
  source: string;
  listings: Listing[];
};
export function parseDataset(value: unknown): Dataset {
  if (!value || typeof value !== "object") throw new Error("Invalid dataset");
  const data = value as Dataset;
  if (
    data.schema_version !== 1 ||
    typeof data.snapshot_date !== "string" ||
    typeof data.synthetic !== "boolean" ||
    !Array.isArray(data.listings)
  )
    throw new Error("Unsupported dataset schema");
  for (const row of data.listings) {
    if (
      typeof row.id !== "string" ||
      !/^\d+$/.test(row.id) ||
      !Number.isFinite(row.price) ||
      row.price <= 0 ||
      !Number.isFinite(row.latitude) ||
      !Number.isFinite(row.longitude) ||
      row.latitude < -90 ||
      row.latitude > 90 ||
      row.longitude < -180 ||
      row.longitude > 180 ||
      typeof row.room_type !== "string" ||
      typeof row.neighborhood !== "string" ||
      (row.bedrooms !== null &&
        (!Number.isInteger(row.bedrooms) || row.bedrooms < 0))
    )
      throw new Error("Invalid listing record");
  }
  return data;
}
export function median(rows: Listing[]): number | null {
  const prices = rows.map((r) => r.price).sort((a, b) => a - b);
  const mid = Math.floor(prices.length / 2);
  return prices.length
    ? prices.length % 2
      ? prices[mid]
      : (prices[mid - 1] + prices[mid]) / 2
    : null;
}

export type Geography = {
  listing_sha256: string;
  schema_version: number;
  snapshot_date: string;
  assignments: {
    id: string;
    zcta: string | null;
    status: "assigned" | "ambiguous" | "unassigned";
    near_boundary: boolean;
  }[];
};
export function parseGeography(
  value: unknown,
  dataset: Dataset,
  listingSha: string,
): Geography {
  if (!value || typeof value !== "object") throw new Error("Invalid geography");
  const data = value as Geography;
  if (
    data.schema_version !== 1 ||
    data.listing_sha256 !== listingSha ||
    data.snapshot_date !== dataset.snapshot_date ||
    !Array.isArray(data.assignments) ||
    data.assignments.length !== dataset.listings.length
  )
    throw new Error("Geography snapshot mismatch");
  const ids = new Set(dataset.listings.map((row) => row.id));
  for (const row of data.assignments) {
    if (
      typeof row.id !== "string" ||
      typeof row.near_boundary !== "boolean" ||
      !ids.delete(row.id) ||
      !["assigned", "ambiguous", "unassigned"].includes(row.status) ||
      (row.status === "assigned"
        ? typeof row.zcta !== "string" || !/^[0-9]{5}$/.test(row.zcta)
        : row.zcta !== null)
    )
      throw new Error("Invalid geography assignment");
  }
  return data;
}
