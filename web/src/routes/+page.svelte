<script lang="ts">
  import { onMount } from "svelte";
  import Map from "#lib/Map.svelte";
  import {
    median,
    parseDataset,
    parseGeography,
    type Geography,
    type Dataset,
    type Listing,
  } from "#lib/data.ts";
  let dataset = $state<Dataset>();
  let path = $state("");
  let loading = $state(true);
  let error = $state("");
  let room = $state("");
  let bedrooms = $state("");
  let neighborhood = $state("");
  let zcta = $state("");
  let geography = $state<Geography>();
  let excludeBoundary = $state("");
  const boundaryIds = $derived(
    new Set(
      geography?.assignments
        .filter((row) => row.near_boundary)
        .map((row) => row.id),
    ),
  );
  const zctaById = $derived(
    new globalThis.Map(
      geography?.assignments.map((row) => [row.id, row.zcta ?? row.status]),
    ),
  );
  const zctas = $derived(
    [
      ...new Set(geography?.assignments.map((row) => row.zcta ?? row.status)),
    ].sort(),
  );
  let minPrice = $state<number | undefined>();
  let maxPrice = $state<number | undefined>();
  let selected = $state<Listing>();
  let limit = $state(30);
  const areaLabel = (value: string) =>
    value === "unassigned"
      ? "Unassigned"
      : value === "ambiguous"
        ? "Ambiguous"
        : value;
  const money = (n: number | null) =>
    n === null
      ? "—"
      : new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
          maximumFractionDigits: 0,
        }).format(n);
  const filtered = $derived(
    (dataset?.listings ?? []).filter(
      (r) =>
        (!room || r.room_type === room) &&
        (!neighborhood || r.neighborhood === neighborhood) &&
        (!zcta || zctaById.get(r.id) === zcta) &&
        (!excludeBoundary || !boundaryIds.has(r.id)) &&
        (!bedrooms ||
          (bedrooms === "unknown"
            ? r.bedrooms === null
            : r.bedrooms === Number(bedrooms))) &&
        (minPrice === undefined || r.price >= minPrice) &&
        (maxPrice === undefined || r.price <= maxPrice),
    ),
  );
  const rooms = $derived(
    [...new Set(dataset?.listings.map((r) => r.room_type))].sort(),
  );
  const areas = $derived(
    [...new Set(dataset?.listings.map((r) => r.neighborhood))].sort(),
  );
  const beds = $derived(
    [
      ...new Set(
        dataset?.listings.flatMap((r) =>
          r.bedrooms === null ? [] : [r.bedrooms],
        ),
      ),
    ].sort((a, b) => a - b),
  );
  const summaries = $derived(
    (geography ? zctas : areas)
      .map((name) => ({
        name,
        rows: filtered.filter((r) =>
          geography ? zctaById.get(r.id) === name : r.neighborhood === name,
        ),
      }))
      .filter((g) => g.rows.length),
  );
  $effect(() => {
    if (selected && !filtered.some((r) => r.id === selected?.id))
      selected = undefined;
  });
  async function load() {
    loading = true;
    error = "";
    try {
      const indexResponse = await fetch("/data/index.json");
      if (!indexResponse.ok) throw new Error("Data index unavailable");
      const index = await indexResponse.json();
      if (index.schema_version !== 1 || !/^\d{4}-\d{2}-\d{2}$/.test(index.path))
        throw new Error("Invalid data index");
      const response = await fetch("/data/" + index.path + "/listings.json");
      if (!response.ok) throw new Error("Listing data unavailable");
      const listingText = await response.text();
      dataset = parseDataset(JSON.parse(listingText));
      geography = undefined;
      if (index.geography === true) {
        const geoResponse = await fetch(
          "/data/" + index.path + "/geography.json",
        );
        if (!geoResponse.ok) throw new Error("Geography unavailable");
        const digest = await crypto.subtle.digest(
          "SHA-256",
          new TextEncoder().encode(listingText),
        );
        const listingSha = [...new Uint8Array(digest)]
          .map((byte) => byte.toString(16).padStart(2, "0"))
          .join("");
        geography = parseGeography(
          await geoResponse.json(),
          dataset,
          listingSha,
        );
      }
      path = index.path;
    } catch {
      error =
        "Listing data could not be loaded. Check your connection and retry.";
    } finally {
      loading = false;
    }
  }
  onMount(() => {
    void load();
  });
  function reset() {
    room = "";
    bedrooms = "";
    neighborhood = "";
    zcta = "";
    excludeBoundary = "";
    minPrice = undefined;
    maxPrice = undefined;
    limit = 30;
  }
  function select(row: Listing) {
    selected = row;
  }
</script>

<svelte:head
  ><title>Las Vegas STR Explorer</title><meta
    name="description"
    content="Explore advertised short-term rental prices across the Las Vegas Valley. Transparent source data, no investment rankings."
  /></svelte:head
>
<header>
  <a class="brand" href="/">LV <span>Las Vegas STR Explorer</span></a><span
    class="stage">DATA EXPLORER · INITIAL MILESTONE</span
  >
</header>
<main>
  <div class="intro">
    <div>
      <p class="eyebrow">CLARK COUNTY, NEVADA</p>
      <h1>A clearer view of the Valley.</h1>
      <p>
        Explore advertised nightly prices. Compare the sample. Understand the
        limits.
      </p>
    </div>
    <div class="source">
      <strong
        >{dataset?.synthetic
          ? "SYNTHETIC DEVELOPMENT FIXTURE"
          : "Inside Airbnb"}</strong
      ><span>Snapshot {dataset?.snapshot_date ?? "loading…"}</span><a
        href="https://insideairbnb.com/get-the-data/">Source & attribution ↗</a
      >
    </div>
  </div>
  <p class="caution">
    Asking prices are not realized income or investment value. Coordinates are
    anonymized and approximate (reported displacement up to about 150 m); dots
    do not identify a particular house. Listings do not establish legal
    eligibility. Source neighborhoods are not verified legal jurisdictions.
  </p>
  {#if loading}<section class="state" role="status">
      Loading listing data…
    </section>
  {:else if error}<section class="state" role="alert">
      <p>{error}</p>
      <button onclick={load}>Retry data loading</button>
    </section>
  {:else if dataset}
    <section class="filters" aria-label="Listing filters">
      <label
        >Room type<select bind:value={room}
          ><option value="">All room types</option
          >{#each rooms as value (value)}<option>{value}</option>{/each}</select
        ></label
      >
      <label
        >Bedrooms<select bind:value={bedrooms}
          ><option value="">Any bedrooms</option
          >{#each beds as value (value)}<option value={String(value)}
              >{value}</option
            >{/each}<option value="unknown">Unknown</option></select
        ></label
      >
      <label
        >Source neighborhood<select bind:value={neighborhood}
          ><option value="">All neighborhoods</option
          >{#each areas as value (value)}<option>{value}</option>{/each}</select
        ></label
      >
      {#if geography}<label
          >ZIP area (Census ZCTA)<select bind:value={zcta}
            ><option value="">All ZIP areas</option
            >{#each zctas as value (value)}<option {value}
                >{areaLabel(value)}</option
              >{/each}</select
          ></label
        >{/if}
      {#if geography}<label
          >Boundary sensitivity<select bind:value={excludeBoundary}
            ><option value="">Include all locations</option><option
              value="exclude"
              >Exclude locations within ~150 m of ZCTA edge</option
            ></select
          ></label
        >{/if}
      <label
        >Minimum asking $ / night<input
          type="number"
          min="0"
          bind:value={minPrice}
          placeholder="Any"
        /></label
      >
      <label
        >Maximum asking $ / night<input
          type="number"
          min="0"
          bind:value={maxPrice}
          placeholder="Any"
        /></label
      >
      <button class="reset" onclick={reset}>Reset filters</button>
    </section>
    <section
      class="metrics"
      aria-label="Filtered sample summary"
      aria-live="polite"
    >
      <div>
        <span>Matching listings</span><strong
          >{filtered.length.toLocaleString()}</strong
        ><small
          >of {dataset.listings.length.toLocaleString()} usable records</small
        >
      </div>
      <div>
        <span>Median advertised price</span><strong
          >{money(median(filtered))}<small> / night</small></strong
        ><small>USD · before any unobserved fees</small>
      </div>
      <div>
        <span>{geography ? "ZIP areas (ZCTA)" : "Source neighborhoods"}</span
        ><strong
          >{geography
            ? summaries.filter(
                (g) => g.name !== "unassigned" && g.name !== "ambiguous",
              ).length
            : summaries.length}</strong
        ><small>in the current filtered sample</small>
      </div>
    </section>
    {#if !filtered.length}<p class="empty" role="status">
        No listings match these filters. Adjust the price range or reset
        filters.
      </p>{/if}
    <div class="workspace">
      <Map
        listings={filtered}
        boundaryUrl={"/data/" + path + "/boundaries.geojson"}
        zctaUrl={geography
          ? "/data/" + path + "/zcta-boundaries.geojson"
          : undefined}
        selectedZcta={zcta}
        onselect={select}
      />
      <aside aria-label="Listing detail">
        <p class="eyebrow">LISTING DETAIL</p>
        {#if selected}<h2>Listing {selected.id}</h2>
          <p class="price">
            {money(selected.price)} <span>/ night advertised</span>
          </p>
          <dl>
            <dt>Room type</dt>
            <dd>{selected.room_type}</dd>
            <dt>Bedrooms</dt>
            <dd>{selected.bedrooms ?? "Unknown"}</dd>
            <dt>Source neighborhood</dt>
            <dd>{selected.neighborhood}</dd>
            {#if geography}<dt>ZIP area (Census ZCTA)</dt>
              <dd>
                {areaLabel(zctaById.get(selected.id) ?? "unassigned")} · approximate
                assignment
              </dd>{/if}
            {#if geography && boundaryIds.has(selected.id)}<dt>
                Boundary sensitivity
              </dt>
              <dd>
                Within approximately 150 m of a ZCTA edge; area assignment may
                change with location anonymization.
              </dd>{/if}
            <dt>Jurisdiction / eligibility</dt>
            <dd>Not verified</dd>
          </dl>
          <p class="muted">
            Approximate location. No parcel match, occupancy estimate, or income
            prediction.
          </p>
          <a
            href={"https://www.airbnb.com/rooms/" + selected.id}
            target="_blank"
            rel="noreferrer">View source listing ↗</a
          ><button class="clear" onclick={() => (selected = undefined)}
            >Clear selection</button
          >
        {:else}<h2>Start with a location.</h2>
          <p>
            Select a marker, zoom into a cluster, or choose a listing below.
          </p>
          <div class="detail-empty">
            Asking price.<br />Source context.<br />No hidden assumptions.
          </div>{/if}
      </aside>
    </div>
    <div class="tables">
      <section>
        <h2>
          {geography
            ? "Compare ZIP areas (ZCTA)"
            : "Compare source neighborhoods"}
        </h2>
        <p class="muted">
          Filtered sample medians describe listings, not all homes in an area.
          {#if geography}ZCTAs approximate ZIP areas, not named neighborhoods.
            Coordinates are anonymized; assignments near boundaries may be
            wrong. Filter room type and bedrooms for closer comparisons. Medians
            are withheld below 20 listings; this is a display threshold, not
            statistical confidence.{/if}
        </p>
        <div class="table-wrap">
          <table>
            <thead
              ><tr
                ><th>{geography ? "ZIP area (ZCTA)" : "Neighborhood"}</th><th
                  >Sample n</th
                ><th>Median asking / night</th></tr
              ></thead
            ><tbody
              >{#each summaries as group (group.name)}<tr
                  ><td>{areaLabel(group.name)}</td><td
                    >{group.rows.length.toLocaleString()}</td
                  ><td
                    >{geography && group.rows.length < 20
                      ? "Insufficient sample (<20)"
                      : money(median(group.rows))}</td
                  ></tr
                >{/each}</tbody
            >
          </table>
        </div>
      </section>
      <section>
        <h2>Browse matching listings</h2>
        <p class="muted">
          Showing {Math.min(limit, filtered.length)} of {filtered.length.toLocaleString()}.
          All matching records appear on the map.
        </p>
        <div class="listing-list">
          {#each filtered.slice(0, limit) as row (row.id)}<button
              class:selected={selected?.id === row.id}
              onclick={() => select(row)}
              aria-pressed={selected?.id === row.id}
              ><span
                ><strong>Listing {row.id}</strong><small
                  >{row.neighborhood} · {row.room_type} · {row.bedrooms ?? "?"} bedrooms</small
                ></span
              ><b>{money(row.price)}</b></button
            >{/each}
        </div>
        {#if limit < filtered.length}<button onclick={() => (limit += 30)}
            >Show 30 more</button
          >{/if}
      </section>
    </div>
  {/if}
  <footer>
    Listings and source boundaries © Inside Airbnb · <a
      href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a
    >. Basemap © OpenStreetMap contributors / OpenFreeMap.
    {#if path}<a href="/data/{path}/quality.json">Data quality report</a>{/if}.
    {#if geography}ZIP area boundaries: <a
        href="https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html"
        >U.S. Census Bureau, 2020 ZCTAs</a
      >. <a href="/data/{path}/geography.json">Assignment provenance</a>.{/if}
    Housing costs and ML evaluation are future milestones.
    <a href="https://github.com/kenner1-unlv/vegas-str-ml"
      >Source code &amp; development history</a
    >
  </footer>
</main>

<style>
  :global(*) {
    box-sizing: border-box;
  }
  :global(body) {
    margin: 0;
    font-family: Inter, system-ui, sans-serif;
    color: #172e37;
    background: #f5f6f2;
  }
  :global(button),
  :global(input),
  :global(select) {
    font: inherit;
  }
  :global(button) {
    cursor: pointer;
  }
  :global(a) {
    color: #0b7269;
  }
  :global(button:focus-visible),
  :global(a:focus-visible),
  :global(input:focus-visible),
  :global(select:focus-visible) {
    outline: 3px solid #d66c36;
    outline-offset: 3px;
  }
  header {
    background: #122d36;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 22px 4vw;
  }
  .brand {
    color: #fff;
    text-decoration: none;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 1px;
  }
  .brand span {
    font-size: 16px;
    font-weight: 500;
    letter-spacing: 0;
    margin-left: 18px;
  }
  .stage {
    font-size: 11px;
    letter-spacing: 2px;
    color: #b9d2d0;
  }
  main {
    max-width: 1520px;
    margin: auto;
    padding: 36px 4vw;
  }
  .intro {
    display: flex;
    justify-content: space-between;
    gap: 24px;
    align-items: center;
  }
  .eyebrow {
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 700;
    color: #0b7269;
  }
  h1 {
    font-size: clamp(30px, 3.4vw, 50px);
    letter-spacing: -2px;
    margin: 10px 0;
  }
  h2 {
    font-size: 21px;
    letter-spacing: -0.5px;
  }
  p {
    line-height: 1.6;
  }
  .intro p:last-child {
    color: #617174;
  }
  .source {
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 13px;
    min-width: 175px;
    border-left: 2px solid #cedbd5;
    padding-left: 20px;
  }
  .caution {
    font-size: 13px;
    padding: 14px 18px;
    background: #edf0e9;
    border-left: 3px solid #b68b4a;
    border-radius: 4px;
    margin: 24px 0;
  }
  .filters {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    align-items: end;
  }
  label {
    font-size: 12px;
    font-weight: 600;
    display: flex;
    flex-direction: column;
    gap: 7px;
  }
  select,
  input {
    width: 100%;
    padding: 10px;
    border: 1px solid #cbd4ce;
    border-radius: 7px;
    background: #fff;
    color: #172e37;
    min-height: 43px;
  }
  button {
    border: 1px solid #bdccc6;
    border-radius: 7px;
    padding: 10px 14px;
    background: white;
    color: #172e37;
  }
  .reset {
    height: 43px;
  }
  .metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin: 24px 0;
  }
  .metrics > div {
    border-top: 1px solid #c9d6cc;
    padding: 17px 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .metrics span {
    font-size: 12px;
    color: #556b6f;
  }
  .metrics strong {
    font-size: 31px;
    letter-spacing: -1px;
  }
  .metrics small {
    font-size: 12px;
    color: #617174;
    font-weight: 400;
    letter-spacing: 0;
  }
  .workspace {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 300px;
    gap: 20px;
  }
  aside {
    background: white;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #e1e5df;
    overflow-wrap: anywhere;
  }
  .price {
    font-size: 30px;
    font-weight: 700;
  }
  .price span {
    font-size: 12px;
    font-weight: 400;
  }
  dl {
    display: grid;
    gap: 8px;
  }
  dt {
    font-size: 11px;
    color: #617174;
    margin-top: 8px;
  }
  dd {
    margin: 0;
    font-size: 14px;
  }
  .muted {
    color: #617174;
    font-size: 13px;
  }
  .detail-empty {
    color: #80928c;
    line-height: 2;
    font-size: 22px;
    margin-top: 70px;
  }
  .clear {
    display: block;
    margin-top: 20px;
  }
  .tables {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 28px;
    margin-top: 36px;
  }
  .table-wrap {
    overflow: auto;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 13px;
  }
  th {
    font-size: 11px;
    color: #556b6f;
  }
  td,
  th {
    padding: 12px 8px;
    border-bottom: 1px solid #dce3db;
  }
  .listing-list {
    max-height: 360px;
    overflow: auto;
    display: grid;
    gap: 6px;
    margin-bottom: 12px;
  }
  .listing-list button {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    text-align: left;
  }
  .listing-list small {
    display: block;
    font-size: 11px;
    color: #617174;
    margin-top: 4px;
  }
  .listing-list .selected {
    border: 2px solid #0b7269;
    background: #e6f2ed;
  }
  footer {
    font-size: 12px;
    line-height: 1.8;
    color: #617174;
    margin-top: 40px;
    padding-top: 18px;
    border-top: 1px solid #d5ded5;
  }
  .state,
  .empty {
    padding: 30px;
    background: #fff;
    border-radius: 12px;
  }
  @media (max-width: 1050px) {
    .filters {
      grid-template-columns: repeat(3, 1fr);
    }
    .workspace {
      grid-template-columns: minmax(0, 1fr) 260px;
    }
  }
  @media (max-width: 700px) {
    header {
      padding: 18px;
    }
    .stage {
      display: none;
    }
    .brand span {
      font-size: 13px;
      margin-left: 10px;
    }
    main {
      padding: 22px 18px;
    }
    .intro {
      display: block;
    }
    .source {
      margin-top: 20px;
    }
    .filters {
      grid-template-columns: 1fr 1fr;
    }
    .metrics {
      gap: 12px;
    }
    .metrics strong {
      font-size: 23px;
    }
    .workspace,
    .tables {
      grid-template-columns: 1fr;
    }
    .detail-empty {
      margin-top: 20px;
    }
    aside {
      padding: 20px;
    }
    .caution {
      font-size: 12px;
    }
  }
</style>
