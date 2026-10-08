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
