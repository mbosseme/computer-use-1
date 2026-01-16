## Chunk 2 (pages 1-1)

## Key points
- Discussion of adding **filters and sorting** in a Tableau-based dashboard; these are described as easy additions but not done live (“*2-3 minutes*” / “*4 or 5 minute ad*”).
- The demo view spans **Premier and non-Premier** segments and includes “*something like 1600 different facilities*.”
- Competitive detail can be shown down to “*a skew level*” (SKU level context).
- **Rows represent individual hospitals** (“*Every row here is an individual hospital with a like a definitive care ID*”); corporate/IDN hierarchy exists but is intentionally not displayed to preserve blinding.
- Team preference discussion: initial scope emphasizes **tailored dashboards** vs sending a large raw data stream; stakeholders want confidence in what informs outputs and want to see **attribute list / data dictionary**.
- Segmentation/targeting use cases discussed include: leakage analysis, launch targeting, portfolio gap/whitespace analysis, competitor traction in subsegments, and pricing analysis by segment/region/class of trade (with privacy constraints).
- Premier data differentiators claimed: granularity and lower latency; “*almost 1/4 to 1/3 now is coming in daily*.”
- Pricing constraints: pricing is **not provided at facility level**; can be rolled up to “*a class of trade manufacturer*” and can do geographic pricing “*probably… down to a three digit zip*” but not adjacent to facility ID due to supplier agreement concerns.
- Demonstrated a **scatter plot**: each dot = hospital; x-axis = spend in category; y-axis = Braun market share; highlighted 20–80% share segment as an opportunity area.
- Discussion of **CAPS/compounding/nutrition/anesthesia/cardioplegia** market visibility; Premier team suggests providing a SKU list to validate representation and share a data cut.
- Suggestion to show a **pre-built app** (less expensive, less customizable) for immediate use; Audrey demoed portfolio view with Premier taxonomy and competitor growth by subcategory.

## Decisions / confirmations
- Confirmed: Dashboard currently keeps facilities at **individual hospital level** to maintain blinding; hierarchy not shown in-model though metadata exists.
- Confirmed: Team interest in seeing **data dictionary/attribute list**; presenter agrees to walk through it and notes they have supporting materials about accuracy.
- Confirmed: For pricing, there is detail to product level averages over time by segment, but **not facility-level pricing** (“*we don't provide price at a facility level*”).
- Confirmed: Premier can map client taxonomy to competitor products if client provides SKU list + taxonomy levels; competitive products inherit taxonomy via cross-references and an algorithm.
- Confirmed: Next steps will be decided **offline**; group will debrief internally before choosing between dashboard build vs data feed vs both.

## Open questions
- Whether the organization wants to start with **interactive dashboards only** or also receive a **raw data feed** (and at what stage) — *unknown final choice*.
- Which specific category/taxonomy path best fits “injectables / premix / infusion” in Premier categorization — *uncertain in discussion*.
- Whether the dataset fully covers the **CAPS portfolio** and competitors (e.g., “*Fragran Sterl Service*” and “*QUVA*”) across relevant submarkets (compounding, nutrition, anesthesia, cardioplegia) — pending sample/cut.

## Action items (with owners if present)
- **Premier team (Bossemeyer/Matt)**: Share a **data dictionary / attribute list** and supporting materials explaining what informs outputs and accuracy.
- **Client team (Claire/Jake/others)**: Provide a **list of SKUs** (name + part number; optionally volume) for CAPS/target products to validate coverage and receive a sample data cut.
- **Client team (Tracy + group)**: Debrief internally for “*a few days*” and revert with preferred direction/next steps (custom dashboards vs portfolio-gap/pricing workstream vs data feed vs both).
- **Premier team (Audrey, per Sachin suggestion)**: Provide/continue a brief demo of the **standard app view** to show category contents and portfolio breakdowns.

## Notable metrics/claims (exact phrases where possible)
- Build tweaks time estimates: “*2-3 minutes*” to add a filter; “*4 or 5 minute ad*” to add sorting calculation.
- Dataset size: “*something like 1600 different facilities*.”
- Data latency: “*almost 1/4 to 1/3 now is coming in daily*.”
- Scatter plot opportunity sizing: “*There's $50 million of annual spend just within this group here*” (referring to hospitals in the 20–80% share segment).
- Commitment thresholds referenced: “*a lot of commitments are either 80 or 90% for fluids*” / committed customers at “*a 90% or higher level*.”
- Category definition in scatter plot: “*fluids, bag based drug delivery and TPN macronutrients*.”
- Blinding rationale: showing hierarchy would make it “*pretty… obvious who it is*,” so hierarchy isn’t included directly in the model view.
