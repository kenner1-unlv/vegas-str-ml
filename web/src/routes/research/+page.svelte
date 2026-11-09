<script lang="ts">
  import summary from "#lib/research-summary.json";

  type Market = {
    id: string;
    area: string;
    snapshot_date: string;
    source_rows: number;
    priced_rows: number;
    missing_price_rows: number;
    source_url: string;
    fresh_final: boolean;
    final_n?: number;
    within_city_mae_usd?: Record<string, number>;
    classification_macro_f1?: Record<string, number>;
    adaptation_mae_usd?: Record<string, number>;
  };

  const markets = summary.markets as Market[];
  const finalMarkets = markets.filter((market) => market.fresh_final);
  const finalMetrics = summary.final_metrics as Record<
    string,
    { mae_usd: number; rmse_usd: number }
  >;
  const locoMetrics = summary.loco_mae_usd as Record<
    string,
    Record<string, number>
  >;
  const methods = [
    { id: "global_median", label: "Global median", kind: "Baseline" },
    { id: "room_median", label: "Room-type median", kind: "Baseline" },
    { id: "ridge", label: "Ridge", kind: "Linear" },
    {
      id: "hist_gradient_boosting",
      label: "Histogram boosting",
      kind: "Selected on development",
    },
  ];
  const maxMae = Math.max(
    ...methods.map((method) => finalMetrics[method.id].mae_usd),
  );
  let selectedId = $state("new-york-city");
  const selected = $derived(markets.find((market) => market.id === selectedId));
  const usd = (value: number) =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  const count = (value: number) => new Intl.NumberFormat("en-US").format(value);
  const github = "https://github.com/kenner1-unlv/vegas-str-ml/blob/main/";
</script>

<svelte:head>
  <title>Four-market ML research | Las Vegas STR Explorer</title>
  <meta
    name="description"
    content="A reproducible four-market study of advertised Airbnb asking prices: baselines, geographic holdouts, cross-city transfer, model failures and limitations."
  />
</svelte:head>

<header class="site-header">
  <a class="identity" href="/">LV <span>STR Research</span></a>
  <nav aria-label="Primary navigation">
    <a href="/">Map explorer</a>
    <a href="/research/" aria-current="page">Research case study</a>
    <a href="https://github.com/kenner1-unlv/vegas-str-ml"
      >Code &amp; evidence ↗</a
    >
  </nav>
</header>

<main>
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero-copy">
      <p class="eyebrow">
        APPLIED ML · FOUR US MARKETS · SEPTEMBER 2026 SNAPSHOTS
      </p>
      <h1 id="hero-title">Can a price model travel to a new city?</h1>
      <p class="lead">
        We tested advertised nightly prices across Clark County, New York City,
        Los Angeles and Nashville. The work starts with source audits and simple
        baselines, then asks where a model improves—and where it fails.
      </p>
      <div class="hero-links">
        <a class="primary-link" href="#results">Explore the results ↓</a>
        <a href={`${github}docs/model-card.md`}>Read the model card ↗</a>
      </div>
    </div>
    <aside class="release-note" aria-label="Release decision">
      <span class="note-kicker">RELEASE DECISION</span>
      <strong>Research model only</strong>
      <p>
        Public predictions remain withheld. A hotel-room subgroup regressed
        against the room-type baseline, and temporal validation is still absent.
      </p>
    </aside>
  </section>

  <section class="stats" aria-label="Study at a glance">
    <div>
      <span>Source listings</span><strong>{count(summary.source_rows)}</strong>
    </div>
    <div>
      <span>With parsed asking prices</span><strong
        >{count(summary.priced_rows)}</strong
      >
    </div>
    <div>
      <span>New-market final test</span><strong>{count(summary.final_n)}</strong
      >
    </div>
    <div>
      <span>Geographic development validation</span><strong
        >{count(summary.development_n)}</strong
      >
    </div>
  </section>

  <section class="section" aria-labelledby="scope-title">
    <div class="section-heading">
      <p class="eyebrow">01 / THE DATA</p>
      <h2 id="scope-title">Four source areas, one documented contract</h2>
      <p>
        Every source is pinned by snapshot date and hash. Missing asking prices
        are reported by market; they are never treated as zero or as confirmed
        bookings. Clark County covers more than the city of Las Vegas.
      </p>
    </div>
    <div class="market-grid">
      {#each markets as market (market.id)}
        <article class="market-card">
          <span class="card-date">{market.snapshot_date}</span>
          <h3>{market.area}</h3>
          <dl>
            <div>
              <dt>Source rows</dt>
              <dd>{count(market.source_rows)}</dd>
            </div>
            <div>
              <dt>With asking price</dt>
              <dd>{count(market.priced_rows)}</dd>
            </div>
            <div>
              <dt>Missing asking price</dt>
              <dd>{count(market.missing_price_rows)}</dd>
            </div>
          </dl>
          <a href={market.source_url}>Source archive ↗</a>
        </article>
      {/each}
    </div>
    <p class="note">
      Source: <a href={summary.source_page}>Inside Airbnb</a>, public detailed
      listings under <a href={summary.license_url}>CC BY 4.0</a>. We normalized
      selected fields and kept full source tables local. Asking prices are not
      realized revenue; unavailable calendar nights are not confirmed bookings.
    </p>
  </section>

  <section class="section method-section" aria-labelledby="method-title">
    <div class="section-heading">
      <p class="eyebrow">02 / THE METHOD</p>
      <h2 id="method-title">Baseline first. Geography held apart.</h2>
      <p>
        Training-only preprocessing uses bedrooms, beds, advertised capacity,
        room type and property group. Listing IDs are grouped, spatial blocks
        are held out, and a 1 km observed-point buffer separates fitting rows
        from validation rows.
      </p>
    </div>
    <div class="steps">
      <article>
        <b>01</b>
        <h3>Verify sources</h3>
        <p>Pin URLs, dates, checksums, missingness and exclusions.</p>
      </article>
      <article>
        <b>02</b>
        <h3>Freeze splits</h3>
        <p>Use 3 km geographic blocks before fitting any new model.</p>
      </article>
      <article>
        <b>03</b>
        <h3>Compare baselines</h3>
        <p>
          Test median, Ridge and fixed boosting methods on the same partitions.
        </p>
      </article>
      <article>
        <b>04</b>
        <h3>Inspect failures</h3>
        <p>
          Report subgroup support and keep weak predictions off the public map.
        </p>
      </article>
    </div>
    <p class="note">
      The earlier Clark County model and its inspected holdout are historical
      evidence. Fresh final blocks were reserved only in NYC, LA and Nashville.
      Approximate listing coordinates cannot prove two IDs are different houses.
    </p>
  </section>

  <section
    class="section results-section"
    id="results"
    aria-labelledby="results-title"
  >
    <div class="section-heading">
      <p class="eyebrow">03 / FROZEN FINAL TEST</p>
      <h2 id="results-title">Overall error improved. Some groups did not.</h2>
      <p>
        The fixed boosting candidate was chosen on separate development folds.
        These are errors against advertised asking prices on {count(
          summary.final_n,
        )}
        new-market held-out listings. Lower MAE is better.
      </p>
    </div>
    <div class="results-layout">
      <div class="chart-card">
        <h3>Pooled final mean absolute error</h3>
        <div
          class="bars"
          role="img"
          aria-label="Pooled final MAE: global median 197 dollars 84 cents, room median 176 dollars 46 cents, Ridge 149 dollars 83 cents, histogram boosting 144 dollars 11 cents"
        >
          {#each methods as method (method.id)}
            <div class="bar-row">
              <div class="bar-meta">
                <span>{method.label}</span><small>{method.kind}</small>
              </div>
              <div class="bar-track">
                <span
                  class:chosen={method.id === summary.selected_candidate}
                  style={`width: ${(finalMetrics[method.id].mae_usd / maxMae) * 100}%`}
                ></span>
              </div>
              <strong>{usd(finalMetrics[method.id].mae_usd)}</strong>
            </div>
          {/each}
        </div>
        <p class="note">
          Selected model pooled RMSE: {usd(
            finalMetrics[summary.selected_candidate].rmse_usd,
          )}. A 500-resample block-bootstrap interval for its MAE is
          {usd(summary.pooled_mae_interval_usd[0])}–{usd(
            summary.pooled_mae_interval_usd[1],
          )}. This is not an interval for an individual listing.
        </p>
      </div>
      <div class="failure-card">
        <span class="note-kicker">THE RELEASE GATE</span>
        <h3>Hotel rooms need more work.</h3>
        <p>
          On {summary.hotel_failure.n} hotel-room listings, boosting error was
          <strong>{usd(summary.hotel_failure.candidate_mae_usd)}</strong> versus
          <strong>{usd(summary.hotel_failure.room_median_mae_usd)}</strong> for
          the room-median baseline. The $250–499 asking-price band also
          regressed:
          {usd(summary.mid_price_failure.candidate_mae_usd)} versus
          {usd(summary.mid_price_failure.room_median_mae_usd)}
          (n={count(summary.mid_price_failure.n)}).
        </p>
        <p class="failure-decision">Prediction release: withheld.</p>
      </div>
    </div>
  </section>

  <section class="section city-section" aria-labelledby="city-title">
    <div class="section-heading">
      <p class="eyebrow">04 / MARKET DETAIL</p>
      <h2 id="city-title">Inspect the local comparison</h2>
      <p>
        Choose a newly held-out market. The classification result below uses
        development folds only.
      </p>
    </div>
    <div class="city-tabs" aria-label="Select market">
      {#each finalMarkets as market (market.id)}
        <button
          type="button"
          class:active={selectedId === market.id}
          aria-pressed={selectedId === market.id}
          onclick={() => (selectedId = market.id)}>{market.area}</button
        >
      {/each}
    </div>
    {#if selected?.within_city_mae_usd && selected.classification_macro_f1 && selected.adaptation_mae_usd}
      <div class="city-panel">
        <div>
          <span class="note-kicker"
            >WITHIN-CITY FROZEN FINAL · {count(selected.final_n ?? 0)} LISTINGS</span
          >
          <h3>{selected.area}</h3>
          <p>
            Boosting MAE <strong
              >{usd(
                selected.within_city_mae_usd.hist_gradient_boosting,
              )}</strong
            >
            · room-median MAE {usd(selected.within_city_mae_usd.room_median)}.
          </p>
        </div>
        <div>
          <span class="note-kicker">LIMITED LOCAL DATA</span>
          <h3>Adaptation test</h3>
          <p>
            Boosting MAE with 0 local training groups: {usd(
              selected.adaptation_mae_usd["0"],
            )}. With 500: {usd(selected.adaptation_mae_usd["500"])}.
          </p>
        </div>
        <div>
          <span class="note-kicker">SECONDARY QUESTION · DEVELOPMENT ONLY</span>
          <h3>Price segment</h3>
          <p>
            Macro F1: logistic {selected.classification_macro_f1.logistic.toFixed(
              3,
            )}
            · random forest {selected.classification_macro_f1.random_forest.toFixed(
              3,
            )}. The threshold is each fold's training-market median asking
            price.
          </p>
        </div>
      </div>
    {/if}
  </section>

  <section class="section transfer-section" aria-labelledby="transfer-title">
    <div class="section-heading">
      <p class="eyebrow">05 / TRANSFER TEST</p>
      <h2 id="transfer-title">A city left out can change the story.</h2>
      <p>
        Fixed candidates were trained without the target city's listings. These
        leave-one-city-out errors are transfer diagnostics, not fresh
        selected-model final estimates.
      </p>
    </div>
    <div class="table-wrap">
      <table>
        <thead
          ><tr
            ><th scope="col">Target source area</th><th scope="col"
              >Room median MAE</th
            ><th scope="col">Boosting MAE</th><th scope="col">Interpretation</th
            ></tr
          ></thead
        >
        <tbody>
          {#each markets as market (market.id)}
            <tr>
              <th scope="row">{market.area}</th>
              <td>{usd(locoMetrics[market.id].room_median)}</td>
              <td>{usd(locoMetrics[market.id].hist_gradient_boosting)}</td>
              <td
                >{market.id === "clark-county-nv"
                  ? "Historical snapshot; baseline wins"
                  : "Fixed-candidate diagnostic"}</td
              >
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    <p class="note">
      Ridge's Nashville leave-one-city-out RMSE reached
      {usd(summary.nashville_loco_ridge_rmse_usd)}, exposing severe tail
      instability. We report that failure rather than using this exposed outcome
      to retune the model.
    </p>
  </section>

  <section class="section evidence-section" aria-labelledby="evidence-title">
    <div class="section-heading">
      <p class="eyebrow">06 / REVIEW THE WORK</p>
      <h2 id="evidence-title">Trace the claim back to the run.</h2>
      <p>
        Source files and row-level research stay local. The repository contains
        specifications, code, tests and reviewed aggregate evidence, with hashes
        that connect each result to its inputs and split.
      </p>
    </div>
    <div class="evidence-links">
      <a href={`${github}specs/003-multi-city-research/spec.md`}
        >Research specification <span>↗</span></a
      >
      <a href={`${github}specs/003-multi-city-research/source-audit.json`}
        >Source audit <span>↗</span></a
      >
      <a href={`${github}specs/003-multi-city-research/split-support.json`}
        >Split support <span>↗</span></a
      >
      <a href={`${github}specs/003-multi-city-research/final-evaluation.json`}
        >Final aggregate results <span>↗</span></a
      >
      <a href={`${github}specs/003-multi-city-research/secondary-results.json`}
        >Classification results <span>↗</span></a
      >
      <a href={`${github}docs/model-card.md`}
        >Model card and limitations <span>↗</span></a
      >
    </div>
  </section>
</main>

<footer>
  <p>
    Analysis based on Inside Airbnb detailed listings for Clark County, New York
    City, Los Angeles and Nashville, September 2026. Source data: <a
      href={summary.source_page}>Inside Airbnb</a
    >
    · <a href={summary.license_url}>CC BY 4.0</a>. Normalization, splits and
    analysis are project modifications. Inside Airbnb does not endorse these
    findings.
  </p>
  <p>
    Advertised prices are not realized revenue. Review activity is not
    occupancy. No address, parcel, investment or legal-eligibility claim is
    made.
  </p>
  <a href="/">← Return to Las Vegas map explorer</a>
</footer>

<style>
  :global(*) {
    box-sizing: border-box;
  }
  :global(body) {
    margin: 0;
    background: #f4f5f0;
    color: #172e37;
    font-family: Inter, system-ui, sans-serif;
  }
  :global(a) {
    color: #087268;
  }
  :global(a:focus-visible),
  :global(button:focus-visible) {
    outline: 3px solid #d66c36;
    outline-offset: 3px;
  }
  .site-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    padding: 22px max(24px, calc((100vw - 1200px) / 2));
    background: #122d36;
    color: #fff;
  }
  .identity {
    color: #fff;
    text-decoration: none;
    font-weight: 800;
    font-size: 22px;
    letter-spacing: 0.03em;
    white-space: nowrap;
  }
  .identity span {
    font-size: 16px;
    font-weight: 600;
    margin-left: 9px;
    letter-spacing: 0;
  }
  nav {
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
    font-size: 14px;
  }
  nav a {
    color: #d8e9e4;
    text-decoration: none;
  }
  nav a:hover,
  nav a[aria-current="page"] {
    color: #fff;
    text-decoration: underline;
    text-underline-offset: 6px;
  }
  main {
    max-width: 1248px;
    margin: auto;
    padding: 0 24px 80px;
  }
  .hero {
    display: grid;
    grid-template-columns: minmax(0, 1.8fr) minmax(265px, 0.8fr);
    gap: 42px;
    align-items: end;
    padding: 86px 0 64px;
  }
  .eyebrow,
  .note-kicker {
    color: #0d7569;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
  }
  h1,
  h2,
  h3,
  p {
    margin-top: 0;
  }
  h1 {
    font-size: clamp(42px, 5.4vw, 76px);
    line-height: 1.04;
    max-width: 760px;
    margin-bottom: 24px;
    letter-spacing: -0.04em;
  }
  h2 {
    font-size: clamp(30px, 3vw, 44px);
    line-height: 1.14;
    letter-spacing: -0.03em;
    margin-bottom: 16px;
  }
  h3 {
    font-size: 20px;
    line-height: 1.25;
    margin-bottom: 12px;
  }
  p {
    line-height: 1.68;
  }
  .lead {
    font-size: 19px;
    color: #3c565c;
    max-width: 670px;
  }
  .hero-links {
    display: flex;
    gap: 22px;
    align-items: center;
    flex-wrap: wrap;
    margin-top: 32px;
    font-weight: 700;
  }
  .primary-link {
    display: inline-block;
    background: #0b7269;
    color: #fff;
    padding: 13px 19px;
    border-radius: 8px;
    text-decoration: none;
  }
  .primary-link:hover {
    background: #075d55;
  }
  .release-note {
    background: #173c44;
    color: #fff;
    padding: 28px;
    border-radius: 14px;
    box-shadow: 0 12px 30px #16343b1a;
  }
  .release-note .note-kicker {
    color: #9ad4c3;
  }
  .release-note strong {
    display: block;
    font-size: 27px;
    margin: 12px 0;
  }
  .release-note p {
    margin: 0;
    color: #d8e8e4;
    font-size: 14px;
  }
  .stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
  }
  .stats div {
    background: #e3eee9;
    border-top: 3px solid #0b7269;
    border-radius: 0 0 10px 10px;
    padding: 22px;
  }
  .stats span,
  .stats strong {
    display: block;
  }
  .stats span {
    color: #49656a;
    font-size: 13px;
    min-height: 36px;
  }
  .stats strong {
    font-size: clamp(22px, 2.6vw, 32px);
    letter-spacing: -0.03em;
  }
  .section {
    padding-top: 94px;
    scroll-margin-top: 20px;
  }
  .section-heading {
    max-width: 780px;
    margin-bottom: 32px;
  }
  .section-heading > p:last-child {
    color: #496067;
    font-size: 17px;
  }
  .market-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
  }
  .market-card {
    background: #fff;
    border: 1px solid #d7e2dc;
    border-radius: 12px;
    padding: 24px;
    min-width: 0;
  }
  .market-card h3 {
    min-height: 54px;
  }
  .card-date {
    color: #5b7476;
    font-size: 12px;
  }
  dl {
    margin: 18px 0 12px;
  }
  dl div {
    display: flex;
    justify-content: space-between;
    gap: 6px;
    border-bottom: 1px solid #edf1ed;
    padding: 9px 0;
    font-size: 12px;
  }
  dt {
    color: #577074;
  }
  dd {
    margin: 0;
    font-weight: 700;
    text-align: right;
  }
  .market-card a {
    font-size: 13px;
    font-weight: 700;
  }
  .note {
    color: #566b70;
    font-size: 13px;
    margin-top: 20px;
  }
  .method-section {
    border-top: 1px solid #dce4dd;
    margin-top: 90px;
  }
  .steps {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
  }
  .steps article {
    padding: 4px 10px 4px 0;
    border-right: 1px solid #cbd9d2;
  }
  .steps article:last-child {
    border: 0;
  }
  .steps b {
    color: #0b7269;
    font-size: 30px;
  }
  .steps h3 {
    margin-top: 18px;
  }
  .steps p {
    color: #506970;
    font-size: 14px;
  }
  .results-layout {
    display: grid;
    grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.8fr);
    gap: 20px;
  }
  .chart-card,
  .failure-card,
  .city-panel {
    border-radius: 12px;
    padding: 28px;
  }
  .chart-card {
    background: #fff;
    border: 1px solid #d7e2dc;
  }
  .chart-card h3 {
    margin-bottom: 28px;
  }
  .bars {
    display: grid;
    gap: 20px;
  }
  .bar-row {
    display: grid;
    grid-template-columns: 155px minmax(100px, 1fr) 80px;
    gap: 14px;
    align-items: center;
  }
  .bar-meta span,
  .bar-meta small {
    display: block;
  }
  .bar-meta span {
    font-weight: 700;
    font-size: 13px;
  }
  .bar-meta small {
    color: #688086;
    margin-top: 2px;
    font-size: 10px;
  }
  .bar-track {
    background: #eaf0ed;
    height: 28px;
    border-radius: 5px;
    overflow: hidden;
  }
  .bar-track span {
    display: block;
    height: 100%;
    background: #96b6ad;
    border-radius: 5px;
  }
  .bar-track span.chosen {
    background: #0b7269;
  }
  .bar-row strong {
    text-align: right;
    font-size: 13px;
  }
  .failure-card {
    background: #fff1e8;
    border: 1px solid #eac7b1;
  }
  .failure-card h3 {
    font-size: 28px;
    margin-top: 10px;
  }
  .failure-card p {
    font-size: 14px;
  }
  .failure-card strong {
    white-space: nowrap;
  }
  .failure-decision {
    color: #873d21;
    font-weight: 800;
    margin-bottom: 0;
  }
  .city-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 14px;
  }
  .city-tabs button {
    border: 1px solid #b9d0c8;
    border-radius: 8px;
    padding: 10px 16px;
    background: #fff;
    color: #163c43;
    cursor: pointer;
    font: inherit;
    font-weight: 700;
  }
  .city-tabs button.active {
    color: #fff;
    background: #0b7269;
    border-color: #0b7269;
  }
  .city-panel {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 25px;
    background: #e8f1ed;
  }
  .city-panel > div + div {
    border-left: 1px solid #c3d6ce;
    padding-left: 25px;
  }
  .city-panel h3 {
    margin-top: 10px;
  }
  .city-panel p {
    margin-bottom: 0;
    color: #3e5a60;
    font-size: 14px;
  }
  .table-wrap {
    overflow-x: auto;
    background: #fff;
    border-radius: 12px;
    border: 1px solid #d7e2dc;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    min-width: 610px;
    text-align: left;
  }
  th,
  td {
    padding: 16px 20px;
    border-bottom: 1px solid #e7eee8;
    font-size: 14px;
  }
  th {
    font-weight: 700;
  }
  thead th {
    color: #526a70;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  tbody tr:last-child th,
  tbody tr:last-child td {
    border-bottom: 0;
  }
  .evidence-links {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }
  .evidence-links a {
    background: #fff;
    border: 1px solid #d7e2dc;
    border-radius: 9px;
    padding: 18px;
    text-decoration: none;
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    gap: 20px;
  }
  .evidence-links a:hover {
    border-color: #0b7269;
    background: #f8fcf9;
  }
  footer {
    padding: 42px max(24px, calc((100vw - 1200px) / 2));
    background: #122d36;
    color: #c9ddd8;
    font-size: 13px;
  }
  footer p {
    max-width: 1000px;
  }
  footer a {
    color: #a9e4d3;
  }
  @media (max-width: 980px) {
    .market-grid,
    .steps {
      grid-template-columns: repeat(2, 1fr);
    }
    .stats {
      grid-template-columns: repeat(2, 1fr);
    }
    .results-layout {
      grid-template-columns: 1fr;
    }
    .evidence-links {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  @media (max-width: 680px) {
    .site-header {
      align-items: flex-start;
      flex-direction: column;
      padding: 18px 20px;
    }
    nav {
      gap: 16px;
    }
    main {
      padding: 0 18px 60px;
    }
    .hero {
      display: block;
      padding: 52px 0 36px;
    }
    .release-note {
      margin-top: 35px;
    }
    .stats,
    .market-grid,
    .steps,
    .city-panel,
    .evidence-links {
      grid-template-columns: 1fr;
    }
    .stats span {
      min-height: 0;
    }
    .section {
      padding-top: 68px;
    }
    .method-section {
      margin-top: 60px;
    }
    .steps article {
      border-right: 0;
      border-bottom: 1px solid #cbd9d2;
    }
    .city-panel > div + div {
      border-left: 0;
      border-top: 1px solid #c3d6ce;
      padding-left: 0;
      padding-top: 20px;
    }
    .bar-row {
      grid-template-columns: 1fr 70px;
      gap: 7px;
    }
    .bar-meta {
      grid-column: 1 / -1;
    }
    .bar-track {
      height: 22px;
    }
    .chart-card,
    .failure-card {
      padding: 22px;
    }
    footer {
      padding: 34px 18px;
    }
  }
</style>
