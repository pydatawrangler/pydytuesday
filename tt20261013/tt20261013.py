import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # 🐸 Frogs and Toads: AmphibiaWeb

    **TidyTuesday · 2026-10-13**

    AmphibiaWeb is a Berkeley-based clearinghouse for amphibian biology, taxonomy
    and conservation. This week's TidyTuesday slice is every **Anura** (frog and
    toad) species account in that database, flattened to one tidy row per species.

    Each row mixes structured facts (id, clade, family, genus, ISO country codes)
    with whatever free-text narrative that account's curators have written so far:
    description, life history, larval notes, threats, references.

    - **Source file**: `frogs_and_toads_amphibiaweb.csv` — 8,018 rows, 26 columns, ~13 MB
    - **Curated by**: Ntobeko Sosibo
    - **Raw data**: <https://github.com/rfordatascience/tidytuesday/tree/main/data/2026/2026-10-13>

    > Jongsma, G. F. M., N. Barve, J. M. Allen, H. L. Owens, and D. C. Blackburn.
    > 2026. "Pleistocene Forest Stability Predicts Patterns of Frog Diversity in
    > Central Africa." *Ecology and Evolution* 16 (3): e73207.
    > <https://doi.org/10.1002/ece3.73207>
    """)
    return


@app.cell
def _():
    import marimo as mo
    import plotly.express as px
    import polars as pl
    import pycountry
    from plotly.subplots import make_subplots

    AMPHIBIAWEB_CSV_URL = (
        "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/"
        "data/2026/2026-10-13/frogs_and_toads_amphibiaweb.csv"
    )
    return AMPHIBIAWEB_CSV_URL, make_subplots, mo, pl, px, pycountry


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Loading the data

    Polars pulls the CSV straight from GitHub over HTTPS, so there is no local copy
    to keep in sync — `frogs_and_toads_amphibiaweb` below is fetched live from the
    `raw.githubusercontent.com` URL on every run.

    The columns arrive almost entirely as **text**, and that is deliberate: the
    source was written by R with its default `na = "NA"`, so missing values are the
    literal two-character string `"NA"` rather than empty fields. That detail drives
    most of the cleaning decisions in this notebook.
    """)
    return


@app.cell
def _(AMPHIBIAWEB_CSV_URL, pl):
    frogs_and_toads_amphibiaweb = pl.read_csv(AMPHIBIAWEB_CSV_URL)

    frogs_and_toads_amphibiaweb
    return (frogs_and_toads_amphibiaweb,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## What the data contains

    **Grain.** One row per species account. Both `amphib_id` and the
    `genus` + `specificepithet` pair are unique across all 8,018 rows, so no species
    is duplicated.

    **Scope.** The file is already filtered to a single order — `ordr == "Anura"`
    for every row. Within that: 57 families, 504 genera, 51 subfamilies, and 57
    `clade` values (AmphibiaWeb's finer-grained, genus-level groupings). The largest
    families are Hylidae (tree frogs, 1,086 accounts), Strabomantidae (840),
    Microhylidae (768), Bufonidae (true toads, 666) and Ranidae (470).

    **Geography is the most complete thing here.** `isocc` holds comma-separated
    ISO 3166-1 alpha-2 codes for the native range — 99.6% of rows have them,
    covering 204 distinct countries and territories. `intro_isocc`, the introduced
    range, is filled in for only 66 rows.

    **The narrative fields are sparse and unevenly filled.** Only about 35% of
    accounts have a `common_name`, roughly a quarter have a `description` or
    `life_history`, and 19% have `trends_and_threats`. They are also rich text
    rather than plain text: entries routinely embed HTML such as
    `<i>Abavorana nazgul</i>` for italicised species names.

    **Conservation columns are the weak spot.** `interntnl_status` (the IUCN Red
    List category) is `"NA"` for *every single row*, so the "how does status vary by
    family?" question from the TidyTuesday prompt cannot be answered from this CSV
    as published. `national_status` and `regional_status` are each about 97%
    missing as well.

    **Provenance.** Accounts were submitted between 1999-02-16 and 2021-01-29 (only
    1,901 rows carry a `submit_date`) and last edited as recently as 2026-07-26,
    with `submittedby` and `editedby` naming 454 and 246 distinct contributors.
    """)
    return


@app.cell
def _(frogs_and_toads_amphibiaweb, mo):
    _amphibians = frogs_and_toads_amphibiaweb

    # Native-range codes: split the comma-separated lists, then drop the token "NA",
    # which is ambiguous (it can mean Namibia as well as missing).
    _country_codes = (
        _amphibians["isocc"]
        .filter(_amphibians["isocc"] != "NA")
        .str.split(",")
        .explode()
        .str.strip_chars()
    )
    _country_codes = _country_codes.filter(_country_codes != "NA")

    _with_common_name = (_amphibians["common_name"] != "NA").sum()

    dataset_highlights = mo.hstack(
        [
            mo.stat(f"{_amphibians.height:,}", label="Species accounts"),
            mo.stat(f"{_amphibians['family'].n_unique():,}", label="Families"),
            mo.stat(f"{_amphibians['genus'].n_unique():,}", label="Genera"),
            mo.stat(f"{_amphibians['clade'].n_unique() - 1:,}", label="Clades"),
            mo.stat(f"{_country_codes.n_unique():,}", label="ISO codes (native range)"),
            mo.stat(f"{_with_common_name / _amphibians.height:.0%}", label="Have a common name"),
        ],
        justify="start",
        wrap=True,
    )

    dataset_highlights
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Structure and schema

    26 columns × 8,018 rows. `amphib_id` is the only numeric column; the other 25
    are text, *including* the two date columns, which hold `YYYY-MM-DD` strings
    rather than parsed dates.

    | Group | Columns |
    |:--|:--|
    | Identity & taxonomy | `amphib_id`, `ordr`, `family`, `subfamily`, `genus`, `specificepithet`, `clade` |
    | Name | `common_name` |
    | Native range | `isocc` |
    | Introduced range | `intro_isocc` |
    | Conservation | `interntnl_status`, `national_status`, `regional_status`, `trends_and_threats` |
    | Free-text narrative | `description`, `distribution`, `life_history`, `larva`, `lannoo`, `relation_to_humans`, `comments` |
    | Provenance | `submit_date`, `submittedby`, `edit_date`, `editedby`, `refs` |

    **Missing values are the string `"NA"`, not nulls.** Polars reports zero nulls
    in all 26 columns, yet thousands of cells are effectively empty. Every
    "missing" number in `dataset_overview` below is really a count of cells equal to
    `"NA"`. A blank `example_value` means the whole column is `"NA"`.

    ⚠️ **The `NA` trap.** `NA` is also Namibia's ISO country code. In `isocc`, the
    token `NA` appears 73 times across the country lists, and 31 of those are cells
    whose entire value is `"NA"` — genuinely ambiguous between "missing" and
    "Namibia only". Do not blanket-clean this file with `null_values=["NA"]`; that
    would silently delete Namibian occurrences from both country columns.
    """)
    return


@app.cell
def _(frogs_and_toads_amphibiaweb, pl):
    _amphibians = frogs_and_toads_amphibiaweb

    # Count "NA" strings explicitly: the frame has no true nulls.
    _missing = _amphibians.select(
        [pl.col(name).cast(pl.String).eq("NA").sum() for name in _amphibians.columns]
    ).row(0)

    _examples = []
    for _name in _amphibians.columns:
        _column = _amphibians[_name]
        if _column.dtype == pl.String:
            _column = _column.filter(_column != "NA")
        _examples.append(f"{_column.first()}"[:70] if _column.len() else "")

    dataset_overview = pl.DataFrame(
        {
            "column": _amphibians.columns,
            "dtype": [str(dtype) for dtype in _amphibians.dtypes],
            "present": [_amphibians.height - missing for missing in _missing],
            "missing_pct": [
                round(100 * missing / _amphibians.height, 1) for missing in _missing
            ],
            "example_value": _examples,
        }
    )

    dataset_overview
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## What a single account looks like

    `dataset_overview` counts columns; this shows the *texture* of one record. The
    narrative fields are long — descriptions average around 555 characters, and
    `refs` strings run to thousands — so values below are trimmed to 300 characters.

    The row shown is the most complete account in the file: `amphib_id` 2858,
    *Eleutherodactylus coqui* (the Puerto Rican Coqui), with 22 of its 25 text fields
    populated. Most accounts look far sparser than this.
    """)
    return


@app.cell
def _(frogs_and_toads_amphibiaweb, pl):
    # The most complete account in the file: 22 of its 25 text fields are populated.
    _EXAMPLE_AMPHIB_ID = 2858

    _record = (
        frogs_and_toads_amphibiaweb.filter(pl.col("amphib_id") == _EXAMPLE_AMPHIB_ID)
        .row(0, named=True)
    )

    example_record = pl.DataFrame(
        {
            "field": list(_record.keys()),
            "value": [f"{value}"[:300] for value in _record.values()],
        }
    )

    example_record
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Species-rich families, and how their diversity sits across genera

    The figure below shows the 15 largest of the 57 Anura families, in two
    side-by-side panels that share the same family axis:

    **Left — species per family.** Bar length is the number of species accounts in
    that family. Each bar is split into the family's single largest genus (dark) and
    all of its other genera (light), so a dark-dominated bar means the family's
    diversity is concentrated in one genus.

    **Right — species per genus.** One box per family summarising the sizes of *all*
    its genera. The line is the median genus size, the box spans the middle 50% of
    genera, and dots are outlying genera. The x axis is logarithmic because genus
    size spans three orders of magnitude, from a single species to 631.

    The legend below the panels explains the dark/light split, and hovering over a
    bar reveals the family's totals and the name of its largest genus.

    ### Key observations

    - **Hylidae holds the most species — 1,086 accounts, 13.5% of the file — and is
      also the broadest family**: 85 genera, with nothing bigger than *Scinax* at 126
      species (12% of the family).
    - **Strabomantidae is the mirror image.** It ranks second with 840 species but
      packs them into only 20 genera, where *Pristimantis* alone accounts for 631 —
      75% of the family and 7.9% of the entire dataset. Its box sits far to the right
      of every other family's.
    - **Concentration is not the same thing as species-richness.** The most
      concentrated family here is not the biggest: Eleutherodactylidae has just 4
      genera, and *Eleutherodactylus* is 87% of its 241 species. Ranidae, by
      contrast, ranks 5th with a far more even spread across 25 genera (largest genus
      only 23% of the family).
    - **Hyperoliidae is the most lopsided of all**: 9 of its 17 genera hold a single
      species (median genus size of 1) while *Hyperolius* alone holds 155. That
      combination of many tiny genera plus one giant is exactly what the log scale is
      there to reveal.
    - **Small genera dominate the dataset overall.** The median genus holds 6
      species and 101 of the 504 genera (20%) are monotypic, which is why the right
      panel squeezes most boxes against the left edge with a long tail of outliers.
    - **The 15 families shown cover 81% of the data** (6,493 of 8,018 accounts), so
      described frog diversity is concentrated in a handful of families — but
      distributed very differently *within* them.

    Caveat: these are counts of the species accounts published in this CSV (order
    Anura, via TidyTuesday), not authoritative global species totals.
    """)
    return


@app.cell
def _(frogs_and_toads_amphibiaweb, make_subplots, pl, px):
    TOP_N_FAMILIES = 15

    # Species and genus counts per family, richest first.
    _family_totals = (
        frogs_and_toads_amphibiaweb.group_by("family")
        .agg(pl.len().alias("species"), pl.col("genus").n_unique().alias("genera"))
        .sort("species", descending=True)
    )
    top_families = _family_totals.head(TOP_N_FAMILIES)

    # Species per genus, restricted to the families we are plotting.
    _genera = frogs_and_toads_amphibiaweb.group_by("family", "genus").agg(
        pl.len().alias("species_in_genus")
    )
    _genera_top = _genera.filter(pl.col("family").is_in(top_families["family"].to_list()))

    # Split each family into its single largest genus and everything else.
    _largest_genus = (
        _genera_top.sort("species_in_genus", descending=True)
        .group_by("family")
        .first()
        .select(
            "family",
            pl.col("genus").alias("largest_genus"),
            pl.col("species_in_genus").alias("largest_genus_species"),
        )
    )
    _composition = (
        top_families.join(_largest_genus, on="family", how="left")
        .with_columns(
            (pl.col("species") - pl.col("largest_genus_species")).alias("other_species")
        )
        .with_columns(
            (100 * pl.col("largest_genus_species") / pl.col("species"))
            .round(1)
            .alias("largest_genus_pct")
        )
    )
    _bars = _composition.unpivot(
        index=["family", "genera", "species", "largest_genus", "largest_genus_pct"],
        on=["largest_genus_species", "other_species"],
        variable_name="component",
        value_name="count",
    ).with_columns(
        pl.when(pl.col("component") == "largest_genus_species")
        .then(pl.lit("Largest genus"))
        .otherwise(pl.lit("All other genera"))
        .alias("component")
    )

    # Categorical axes in Plotly run bottom-to-top, so sort ascending to put the
    # richest family at the top.
    _family_order = top_families.sort("species")["family"].to_list()

    _fig_species_per_family = px.bar(
        _bars,
        x="count",
        y="family",
        color="component",
        orientation="h",
        barmode="stack",
        custom_data=["species", "genera", "largest_genus", "largest_genus_pct"],
        category_orders={
            "family": _family_order,
            "component": ["Largest genus", "All other genera"],
        },
        color_discrete_map={"Largest genus": "#1b4965", "All other genera": "#8ab6d6"},
    )
    _fig_species_per_family.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Family total: %{customdata[0]} species in %{customdata[1]} genera<br>"
            "%{fullData.name}: %{x} species<br>"
            "Largest genus: %{customdata[2]} (%{customdata[3]}% of family)"
            "<extra></extra>"
        )
    )

    _fig_genus_sizes = px.box(
        _genera_top,
        x="species_in_genus",
        y="family",
        category_orders={"family": _family_order},
        color_discrete_sequence=["#c1666b"],
    )
    _fig_genus_sizes.update_traces(
        hovertemplate="<b>%{y}</b><br>%{x} species in a genus<extra></extra>"
    )

    families_overview = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        column_widths=[0.55, 0.45],
        horizontal_spacing=0.04,
        subplot_titles=("Species per family", "Species per genus within each family"),
    )
    for _trace in _fig_species_per_family.data:
        families_overview.add_trace(_trace, row=1, col=1)
    for _trace in _fig_genus_sizes.data:
        families_overview.add_trace(_trace, row=1, col=2)

    # The category order must be re-applied by hand: px stores it on its own
    # layout, which is discarded when the traces are copied into the subplot figure.
    families_overview.update_yaxes(categoryorder="array", categoryarray=_family_order)
    families_overview.update_xaxes(title_text="Number of species accounts", row=1, col=1)
    families_overview.update_xaxes(
        title_text="Species in genus (log scale)", type="log", row=1, col=2
    )
    families_overview.update_layout(
        title=dict(
            text="Frog and toad diversity by family",
            subtitle=dict(
                text=(
                    "The 15 richest of 57 Anura families, and how each spreads its "
                    "species across genera · AmphibiaWeb via TidyTuesday 2026-10-13"
                )
            ),
        ),
        legend=dict(
            title=dict(text="Within each family"),
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5,
        ),
        height=700,
        margin=dict(t=120, b=130, l=140, r=40),
        plot_bgcolor="white",
    )

    families_overview
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Native range: where the species actually are

    The map colours every country by how many of the 8,018 species accounts list it
    in `isocc`, the native-range field. Land shown in grey has no records in this
    dataset.

    `isocc` stores comma-separated ISO alpha-2 codes, so the map is built by
    splitting that column, exploding it into one row per species-country pair
    (13,843 pairs), counting species per code, and translating the two-letter codes
    into the ISO-3 codes Plotly's choropleth expects.

    The colour scale is **Turbo** — chosen for its high contrast — and it is
    **logarithmic**: the country counts run from 1 species to 1,173 while the median
    country has only 14, so on a linear ramp almost every country would collapse
    into the same dark shade. The colorbar ticks are labelled with real counts
    placed at their log positions. Note that Turbo's brightness peaks in the
    middle of its range rather than rising steadily, so read the colorbar rather
    than assuming that a brighter country is a richer one.

    ### Key observations

    - **Brazil is in a class of its own with 1,173 species** — 14.6% of every account
      in the file, and 51% more than second-placed Colombia (777).
    - **The top of the table mixes tropical hotspots with large landmasses:**
      Colombia 777, Ecuador 696, Peru 676, then China 593, Madagascar 443, Papua New
      Guinea 435, India 430, Indonesia 400, Venezuela 351. Five of the top ten are
      Neotropical, the pattern the TidyTuesday prompt points at.
    - **Most countries sit in the pale end of the scale.** The median country has 14
      species, 49 of the 203 mapped countries have 5 or fewer, and 12 have exactly
      one.
    - **Ranges are narrow on average:** 13,843 country records across 8,018 species
      works out to just 1.73 countries per species, reflecting how many of these
      accounts describe island and montane endemics.

    Two data-handling notes: whole-cell `"NA"` values (31 of them) are dropped
    because they are ambiguous — they could mean "no data" *or* Namibia on its own —
    while `NA` appearing *inside* a longer country list (42 cases) can only be
    Namibia, so it is kept. And one deprecated code, `AN` (Netherlands Antilles,
    2 records), has no current ISO-3 equivalent, so it is left off the map.
    """)
    return


@app.cell
def _(frogs_and_toads_amphibiaweb, pl, px, pycountry):
    # One row per (species, country) pair from the comma-separated `isocc` codes.
    _species_countries = (
        frogs_and_toads_amphibiaweb.select("amphib_id", "isocc")
        # A whole-cell "NA" is ambiguous ("no data" or Namibia alone), so drop those.
        # An "NA" inside a longer list can only be Namibia, so those are kept.
        .filter(pl.col("isocc") != "NA")
        .with_columns(pl.col("isocc").str.split(",").alias("country_code"))
        .explode("country_code")
        .with_columns(pl.col("country_code").str.strip_chars())
        # One source cell has a stray empty entry: "...MZ,NA,,SO...".
        .filter(pl.col("country_code") != "")
        .unique()
    )

    # Plotly's choropleth needs ISO-3 codes and readable names, so translate the
    # alpha-2 codes held in the data with pycountry.
    _country_counts = (
        _species_countries.group_by("country_code")
        .agg(pl.len().alias("species"))
        .sort("species", descending=True)
    )
    _iso3 = {}
    _country_names = {}
    for _code in _country_counts["country_code"]:
        _country = pycountry.countries.get(alpha_2=_code)
        if _country is not None:
            _iso3[_code] = _country.alpha_3
            _country_names[_code] = _country.name

    native_species_by_country = (
        _country_counts.with_columns(
            pl.col("country_code").replace_strict(_iso3, default=None).alias("iso3"),
            pl.col("country_code")
            .replace_strict(_country_names, default=None)
            .alias("country"),
        )
        # "AN" (Netherlands Antilles) is deprecated and has no ISO-3 equivalent.
        .filter(pl.col("iso3").is_not_null())
        .with_columns(pl.col("species").log10().alias("log_species"))
    )

    # The distribution is far too skewed for a linear ramp (1 to 1,173 species with a
    # median country on 14), so colour by log10 and label the colorbar with the real
    # counts, positioned at their log values.
    _COLORBAR_COUNTS = (1, 3, 10, 30, 100, 300, 1000)

    country_map = px.choropleth(
        native_species_by_country,
        locations="iso3",
        color="log_species",
        hover_name="country",
        custom_data=["species"],
        color_continuous_scale="Turbo",
    )
    country_map.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]} native species<extra></extra>"
    )
    country_map.update_coloraxes(
        colorbar=dict(
            title=dict(text="Native species<br>(log scale)"),
            tickvals=pl.Series("count", _COLORBAR_COUNTS).log(10).to_list(),
            ticktext=[f"{count:,}" for count in _COLORBAR_COUNTS],
            thickness=14,
        )
    )
    country_map.update_geos(
        projection_type="natural earth",
        showframe=False,
        showcoastlines=False,
        showcountries=True,
        countrycolor="#b8b8b8",
        landcolor="#ededed",
        bgcolor="#ffffff",
    )
    country_map.update_layout(
        title=dict(
            text="Native frog and toad species by country",
            subtitle=dict(
                text=(
                    "Species whose native range includes each country, from the isocc "
                    "field · AmphibiaWeb via TidyTuesday 2026-10-13"
                )
            ),
        ),
        height=620,
        margin=dict(t=100, b=10, l=10, r=10),
    )

    country_map
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Can the notes explain where the species cluster?

    This is the fourth question in the TidyTuesday prompt, and this dataset can only
    answer it in part. There is no time dimension to the "historical" range notes —
    the only dates are when an account was submitted or edited (1999–2021) — so the
    evidence available is the prose itself: the `distribution` (range) and
    `life_history` (habitat) fields. **2,255 of the 8,018 accounts (28%) contain at
    least one of them.**

    The heatmap below reads that prose. For the 15 most species-rich countries, each
    cell is the share of that country's *noted* species whose range/habitat text
    mentions a given theme, matched by keyword regexes (forest, montane, streams,
    ponds/wetlands, arboreal, leaf litter/fossorial, grassland/arid, human-modified).
    Rows are grouped by biogeographic realm, darkest means highest, and the colour
    scale runs 0–90%.

    The final column, after the gap, measures something different: the share of
    *all* of that country's species that have any note at all. Keep an eye on it —
    it turns out to matter more than anything else on the chart.

    ### Key observations

    - **The vocabulary does vary by region, in ecologically sensible ways.**
      Montane/elevation language dominates the Southeast Asian and Andean profiles
      (Viet Nam 73%, Mexico 69%, Ecuador 66%, Peru 62%) and nearly vanishes from
      Australia (16%). Stream talk peaks in China (74%) and Malaysia (63%);
      ponds/wetlands in Australia (59%), Bolivia (57%) and Malaysia (56%); arboreal
      and tree-cavity language in Venezuela (49%); grassland/arid in Australia (31%)
      and Mexico (28%); and forest language in Madagascar (88%).
    - **But forest vocabulary is high almost everywhere** (54–88% of noted species),
      so the notes agree about the obvious thing and diverge on the details. The
      regional signal lives in the secondary themes, not in "is there forest here".
    - **Coverage undercuts the comparison, and the last column shows it.** Only 18%
      of Papua New Guinea's and Viet Nam's species carry notes, against 86% of
      Australia's and 62% of Madagascar's. The most distinctive profiles — Australia's
      arid/pond signature, Madagascar's forest signature — belong to the
      best-documented rows, so regional ecology and editorial attention are badly
      tangled together.
    - **Note coverage is not a random sample of species.** Of the 1,901 accounts with
      a `submit_date`, 97–100% carry prose; of the 6,117 without one, only 7% do.
      Having notes is essentially a marker of a *fully curated* account, so these
      profiles describe the curated 28% of the file, not the order Anura.

    **Verdict:** the notes are *consistent with* regional habitat clustering —
    tropical regions reading as forest/montane/stream specialists, Australia as
    pond-and-grassland country — but with 28% coverage, an 18–86% spread in coverage
    between countries, and no temporal dimension, they illustrate that clustering
    rather than explain it. Read them as a qualitative overlay, not a covariate.
    """)
    return


@app.cell
def _(frogs_and_toads_amphibiaweb, pl, px, pycountry):
    # Habitat and range vocabulary used by the prose notes, as keyword regexes.
    HABITAT_THEMES = {
        "Forest / rainforest": r"forest",
        "Montane / high elev.": r"montane|highland|cloud forest|elevation",
        "Streams / rivers": r"stream|river|creek",
        "Ponds / wetlands": r"pond|pool|wetland|swamp|marsh|bog",
        "Arboreal / trees": r"arboreal|tree|canopy|cavity",
        "Leaf litter / fossorial": r"leaf litter|fossorial|burrow|underground|subterranean",
        "Grassland / arid": r"grassland|savanna|savannah|arid|desert|xeric|meadow",
        "Human-modified land": r"agricultur|disturb|plantation|pasture|urban|cultivat",
    }

    TOP_N_COUNTRIES = 15
    COVERAGE_COLUMN = "Notes coverage"

    # Biogeographic realm for the countries shown, so similar regions sit together.
    COUNTRY_REALMS = {
        "BR": "Neotropics", "CO": "Neotropics", "EC": "Neotropics",
        "PE": "Neotropics", "VE": "Neotropics", "MX": "Neotropics", "BO": "Neotropics",
        "MG": "Malagasy",
        "IN": "Indomalayan", "ID": "Indomalayan", "MY": "Indomalayan", "VN": "Indomalayan",
        "CN": "East Asia",
        "PG": "Australasian", "AU": "Australasian",
    }
    _REALM_ORDER = ["Neotropics", "Malagasy", "Indomalayan", "East Asia", "Australasian"]

    # An account "has notes" when either prose field is filled in (they are "NA"
    # strings rather than nulls).
    _no_notes = pl.col("distribution").eq("NA") & pl.col("life_history").eq("NA")
    _prose = (
        pl.when(pl.col("distribution").eq("NA"))
        .then(pl.lit(""))
        .otherwise(pl.col("distribution"))
        + " "
        + pl.when(pl.col("life_history").eq("NA"))
        .then(pl.lit(""))
        .otherwise(pl.col("life_history"))
    )

    habitat_notes = (
        frogs_and_toads_amphibiaweb.select(
            "amphib_id", "isocc", "distribution", "life_history"
        )
        .with_columns(_no_notes.alias("no_notes"), _prose.alias("prose"))
        .with_columns(
            [
                pl.col("prose").str.to_lowercase().str.contains(pattern).alias(theme)
                for theme, pattern in HABITAT_THEMES.items()
            ]
        )
    )
    noted_species = habitat_notes.filter(~pl.col("no_notes"))

    # Order themes by how often they appear overall, so the heatmap has a gradient.
    _theme_prevalence = {theme: 100 * noted_species[theme].mean() for theme in HABITAT_THEMES}
    _theme_order = sorted(HABITAT_THEMES, key=_theme_prevalence.get, reverse=True)

    # One row per (species, country), then restricted to the richest countries.
    _species_countries = (
        frogs_and_toads_amphibiaweb.select("amphib_id", "isocc")
        .filter(pl.col("isocc") != "NA")
        .with_columns(pl.col("isocc").str.split(",").alias("country_code"))
        .explode("country_code")
        .with_columns(pl.col("country_code").str.strip_chars())
        .filter(pl.col("country_code") != "")
        .unique()
    )
    _top_countries = (
        _species_countries.group_by("country_code")
        .agg(pl.len().alias("species"))
        .sort("species", descending=True)
        .head(TOP_N_COUNTRIES)["country_code"]
        .to_list()
    )

    _country_notes = _species_countries.join(habitat_notes, on="amphib_id")
    _country_rows = []
    for _code in _top_countries:
        _country_species = _country_notes.filter(pl.col("country_code") == _code)
        _country_noted = _country_species.filter(~pl.col("no_notes"))
        _row = {
            "realm": COUNTRY_REALMS.get(_code, "Other"),
            "country": pycountry.countries.get(alpha_2=_code).name.split(",")[0],
            "species": _country_species.height,
            "noted": _country_noted.height,
        }
        _row.update(
            {
                theme: round(100 * _country_noted[theme].mean(), 1)
                for theme in HABITAT_THEMES
            }
        )
        _country_rows.append(_row)

    habitat_by_region = (
        pl.DataFrame(_country_rows)
        .with_columns(
            pl.col("realm")
            .replace_strict(
                {realm: index for index, realm in enumerate(_REALM_ORDER)},
                default=len(_REALM_ORDER),
            )
            .alias("_realm_order")
        )
        .sort(["_realm_order", "species"], descending=[False, True])
        .drop("_realm_order")
        .with_columns(
            (100 * pl.col("noted") / pl.col("species")).round(0).alias(COVERAGE_COLUMN)
        )
    )

    # Build the matrix, its labels, and a cell-by-cell hover. The NaN column is a
    # visual gap separating the theme shares from the coverage column, which uses a
    # different denominator (all species rather than species with notes).
    _matrix = []
    _cell_text = []
    _cell_hover = []
    _row_labels = []
    for _row in habitat_by_region.iter_rows(named=True):
        _matrix.append(
            [_row[theme] for theme in _theme_order] + [float("nan"), _row[COVERAGE_COLUMN]]
        )
        _cell_text.append(
            [f"{_row[theme]:.0f}" for theme in _theme_order]
            + ["", f"{_row[COVERAGE_COLUMN]:.0f}"]
        )
        _cell_hover.append(
            [
                f"{_row[theme]:.0f}% of {_row['country']}'s noted species mention {theme}"
                for theme in _theme_order
            ]
            + [""]
            + [
                f"{_row[COVERAGE_COLUMN]:.0f}% of {_row['country']}'s {_row['species']} "
                "species have any note"
            ]
        )
        _row_labels.append(
            f"{_row['realm']} · {_row['country']} ({_row['noted']}/{_row['species']})"
        )

    habitat_heatmap = px.imshow(
        _matrix,
        x=_theme_order + ["", COVERAGE_COLUMN],
        y=_row_labels,
        color_continuous_scale=[[0.0, "#ffffff"], [0.5, "#bcd9ea"], [1.0, "#1f5f8b"]],
        zmin=0,
        zmax=90,
        aspect="auto",
    )
    habitat_heatmap.update_traces(
        text=_cell_text,
        texttemplate="%{text}",
        textfont=dict(size=10, color="#0b2540"),
        customdata=_cell_hover,
        hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
    )
    habitat_heatmap.update_coloraxes(colorbar=dict(title=dict(text="%")))
    habitat_heatmap.update_layout(
        title=dict(
            text="Do the habitat notes explain where the species cluster?",
            subtitle=dict(
                text=(
                    "Share of each country's noted species whose range/habitat prose "
                    "mentions each theme · 15 richest countries, grouped by realm"
                )
            ),
        ),
        xaxis=dict(
            title="Habitat & range vocabulary in the notes",
            tickangle=-25,
            automargin=True,
        ),
        yaxis=dict(title="Where the species occur", automargin=True),
        height=760,
        margin=dict(t=120, b=170, l=20, r=20),
        plot_bgcolor="white",
    )

    habitat_heatmap
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Data dictionary

    Definitions below are transcribed from the
    [TidyTuesday readme](https://github.com/rfordatascience/tidytuesday/blob/main/data/2026/2026-10-13/readme.md).
    The `class` column is the type declared there: `character` means text in
    Polars, and `date` arrives as a `YYYY-MM-DD` string. Use the search box to look
    up a field by name.

    `data_dictionary` is an ordinary Polars DataFrame, so it can also be filtered in
    code — for example `data_dictionary.filter(pl.col("class") == "date")`.
    """)
    return


@app.cell
def _(mo, pl):
    # Field definitions transcribed from the TidyTuesday readme.
    _data_dictionary_rows = [
        ("amphib_id", "integer", "Unique identifier assigned to the species record in AmphibiaWeb."),
        ("clade", "character", "The taxonomic clade to which the individual belongs, representing a monophyletic group of frogs or toads sharing a common ancestor."),
        ("comments", "character", "General notes, taxonomic discussions, or miscellaneous observations regarding the species record."),
        ("common_name", "character", "Primary vernacular or English common name (often NA if none exists)."),
        ("description", "character", "Free-text narrative detailing physical features, morphology, or coloration."),
        ("distribution", "character", "Geographic range description, country codes, or regional distribution notes."),
        ("edit_date", "date", "Date when the species account was last edited or updated."),
        ("editedby", "character", "Editor(s) who reviewed or revised the account entry."),
        ("family", "character", "Taxonomic family (e.g., Hylidae, Bufonidae)."),
        ("genus", "character", "Taxonomic genus name."),
        ("interntnl_status", "character", "International conservation status designation (e.g., IUCN Red List category)."),
        ("intro_isocc", "character", "ISO country codes indicating regions where the species has been introduced."),
        ("isocc", "character", "ISO country codes representing the native range and occurrence of the species."),
        ("lannoo", "character", "Account summary or commentary derived from Lannoo's Amphibian Declines reference texts."),
        ("larva", "character", "Morphological description, traits, or ecology of the larval or tadpole stage."),
        ("life_history", "character", "Habitat, ecology, breeding behavior, clutch size, or larval traits."),
        ("national_status", "character", "Conservation or legal status of the species within specific national jurisdictions."),
        ("ordr", "character", "Higher taxonomic order (Anura, Caudata, Gymnophiona)."),
        ("refs", "character", "Citations and bibliographic references supporting the species account."),
        ("regional_status", "character", "Local or regional conservation assessment status."),
        ("relation_to_humans", "character", "Anthropogenic interaction, pet trade notes, or cultural significance."),
        ("specificepithet", "character", "Specific epithet / species name."),
        ("subfamily", "character", "Taxonomic subfamily designation beneath family."),
        ("submit_date", "date", "Date when the species account was originally submitted to AmphibiaWeb."),
        ("submittedby", "character", "Author/contributor who compiled or updated the species account."),
        ("trends_and_threats", "character", "Known threats (e.g., chytrid fungus, habitat loss) and population trend notes."),
    ]

    data_dictionary = pl.DataFrame(
        _data_dictionary_rows,
        schema=["variable", "class", "description"],
        orient="row",
    )

    mo.ui.table(
        data_dictionary,
        selection=None,
        show_column_summaries=False,
    )
    return


if __name__ == "__main__":
    app.run()
