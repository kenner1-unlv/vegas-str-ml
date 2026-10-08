<script lang="ts">
  import { onMount } from "svelte";
  import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
  import type { Map as MapType, GeoJSONSource } from "maplibre-gl";
  import type { FeatureCollection, Point } from "geojson";
  import type { Listing } from "./data.ts";
  import "maplibre-gl/dist/maplibre-gl.css";
  let {
    listings,
    boundaryUrl,
    onselect,
  }: {
    listings: Listing[];
    boundaryUrl: string;
    onselect: (row: Listing) => void;
  } = $props();
  let container: HTMLDivElement;
  let map = $state<MapType>();
  let ready = $state(false);
  let error = $state("");
  function points(): FeatureCollection<Point> {
    return {
      type: "FeatureCollection",
      features: listings.map((row) => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [row.longitude, row.latitude] },
        properties: { id: row.id },
      })),
    };
  }
  $effect(() => {
    const data = points();
    if (ready && map)
      (map.getSource("listings") as GeoJSONSource).setData(data);
  });
  onMount(() => {
    let disposed = false;
    import("maplibre-gl")
      .then((ml) => {
        if (disposed) return;
        try {
          ml.setWorkerUrl(workerUrl);
          const instance = new ml.Map({
            container,
            style:
              import.meta.env.VITE_MAP_STYLE ||
              "https://tiles.openfreemap.org/styles/liberty",
            center: [-115.14, 36.12],
            zoom: 10,
            attributionControl: false,
          });
          map = instance;
          instance.addControl(new ml.NavigationControl(), "top-right");
          instance.addControl(
            new ml.AttributionControl({
              compact: false,
              customAttribution:
                'Listings & boundaries: <a href="https://insideairbnb.com/get-the-data/">Inside Airbnb</a> · CC BY 4.0',
            }),
          );
          instance.on("error", () => {
            error =
              "Some map resources could not load. Listing controls below remain available.";
          });
          instance.on("load", () => {
            instance.addSource("boundaries", {
              type: "geojson",
              data: boundaryUrl,
            });
            instance.addLayer({
              id: "boundaries",
              source: "boundaries",
              type: "line",
              paint: {
                "line-color": "#656f83",
                "line-width": 1,
                "line-opacity": 0.5,
              },
            });
            instance.addSource("listings", {
              type: "geojson",
              data: points(),
              cluster: true,
              clusterMaxZoom: 14,
              clusterRadius: 45,
            });
            instance.addLayer({
              id: "clusters",
              type: "circle",
              source: "listings",
              filter: ["has", "point_count"],
              paint: {
                "circle-color": "#0b7269",
                "circle-radius": [
                  "step",
                  ["get", "point_count"],
                  18,
                  100,
                  24,
                  500,
                  31,
                ],
                "circle-stroke-color": "#fff",
                "circle-stroke-width": 2,
              },
            });
            instance.addLayer({
              id: "counts",
              type: "symbol",
              source: "listings",
              filter: ["has", "point_count"],
              layout: {
                "text-field": "{point_count_abbreviated}",
                "text-size": 12,
                "text-font": ["Noto Sans Regular"],
              },
              paint: { "text-color": "#fff" },
            });
            instance.addLayer({
              id: "points",
              type: "circle",
              source: "listings",
              filter: ["!", ["has", "point_count"]],
              paint: {
                "circle-color": "#e06442",
                "circle-radius": 6,
                "circle-stroke-width": 1.5,
                "circle-stroke-color": "#fff",
              },
            });
            instance.on("click", "points", (e) => {
              const id = String(e.features?.[0]?.properties?.id);
              const row = listings.find((r) => r.id === id);
              if (row) onselect(row);
            });
            instance.on("click", "clusters", async (e) => {
              const f = e.features?.[0];
              if (!f || f.geometry.type !== "Point") return;
              const zoom = await (
                instance.getSource("listings") as GeoJSONSource
              ).getClusterExpansionZoom(f.properties?.cluster_id);
              instance.easeTo({
                center: f.geometry.coordinates as [number, number],
                zoom,
              });
            });
            for (const layer of ["clusters", "points"]) {
              instance.on("mouseenter", layer, () => {
                instance.getCanvas().style.cursor = "pointer";
              });
              instance.on("mouseleave", layer, () => {
                instance.getCanvas().style.cursor = "";
              });
            }
            ready = true;
          });
        } catch {
          error =
            "Interactive map is unavailable on this device. Use the listing controls below.";
        }
      })
      .catch(() => {
        error = "Map library could not load. Use the listing controls below.";
      });
    return () => {
      disposed = true;
      map?.remove();
    };
  });
</script>

<div class="map-shell">
  <div
    class="map"
    bind:this={container}
    aria-label="Las Vegas Valley listing map"
  ></div>
  {#if !ready && !error}<div class="notice" role="status">
      Loading map…
    </div>{/if}
  {#if error}<div class="notice" role="status">{error}</div>{/if}
  <div class="legend">● Clusters / listings · Lines: source neighborhoods</div>
</div>

<style>
  .map-shell {
    position: relative;
    min-height: 520px;
    height: 100%;
    background: #e8ece6;
    border-radius: 18px;
    overflow: hidden;
  }
  .map {
    position: absolute;
    inset: 0;
  }
  .notice {
    position: absolute;
    top: 16px;
    left: 16px;
    right: 60px;
    padding: 12px;
    background: white;
    border-radius: 8px;
  }
  .legend {
    position: absolute;
    bottom: 38px;
    left: 12px;
    padding: 6px 10px;
    font-size: 12px;
    background: #ffffffed;
    border-radius: 6px;
    pointer-events: none;
  }
  @media (max-width: 700px) {
    .map-shell {
      min-height: 380px;
    }
  }
</style>
