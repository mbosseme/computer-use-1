## Chunk 2 (pages 1-1)

## Key points
- Discussion of adding Tableau features to the demo (filters and sorting), acknowledged as easy but not done live due to time (estimated “2-3 minutes” / “4 or 5 minute ad”).
- Dataset/view covers both “Premier and non Premier” segments with “something like 1600 different facilities.”
- Competitive visibility: can color/segment by manufacturer and drill “all the way down to a skew level” (SKU level).
- Facility rows shown are individual hospitals (“Every row here is an individual hospital with a like a definitive care ID”); higher-level IDN hierarchy exists but is intentionally not shown to preserve blinding.
- Preference discussion: initial scope is dashboards rather than sending a “big data stream of the raw granular underlying data,” but the team wants confidence in what informs outputs; interest in an “attribute list” / data dictionary and an Excel sample cut.
- Segmentation/targeting use cases clarified as customer/competitor-focused (not title/audience level); can segment by market/category/subcategory, competitor, class of trade, geography, etc.
- Product-level capability: data tied to “Premier’s item master” with “an individual record for every product at a SKU… including drugs.”
- Pricing capability exists but with guardrails: pricing is not provided “at a facility level”; rolled up to “class of trade manufacturer,” can go to product average over time; pricing can be done “geographically… down to a three digit zip” but not placed next to facility ID due to contract/confidentiality concerns.
- Differentiators vs other industry datasets: described as “more specific… more accurate,” “more granular… with lower latency”; “almost 1/4 to 1/3 now is coming in daily.”
- Market “white space” / gap analysis: can map client taxonomy to Premier taxonomy and cross competitive products to client taxonomy to identify portfolio gaps and competitor traction.
- Scatterplot demo: hospital-level dots showing Braun market share (y) vs facility spend (x) for fluids; highlighted mid-band (20–80% share) as potential compliance/commitment opportunity.
- CAPS/compounding/nutrition and pharmacy-administered finished products: team wants to confirm those products/competitors are represented and understand category definitions; Premier proposes providing a sample cut if the team provides SKU list.
- Next steps: team needs offline debrief to choose direction; suggestion to also show a quick view of the standard (less customized, cheaper) app for immediate use; Audrey begins an app demo showing taxonomy drilldown and competitor growth.

## Decisions / confirmations
- Confirmed: Sorting by market share/volume and adding filters in Tableau is feasible but requires minor configuration time (“easy… 4 or 5 minute ad”).
- Confirmed: View is at individual hospital level for blinding; corporate parent/IDN hierarchy is intentionally excluded from the displayed model but exists in metadata.
- Confirmed: Pricing will **not** be delivered at facility level; can be rolled up (e.g., class of trade/manufacturer) and/or geographic rollups (e.g., “three digit zip”) with confidentiality constraints.
- Confirmed: Premier can map the client’s taxonomy to competitive items via SKU alignment + cross-references; competitive products inherit the client taxonomy through the crosswalk process.
- Confirmed (scope intent to date): starting point is tailored dashboards rather than providing a raw data feed, though options remain open.

## Open questions
- Whether the team wants dashboards only vs also a data stream (“Is that the right place to start or are you also interested in the data stream?”).
- Which category/product area to use as the primary example for portfolio gap/segmentation views (injectables vs infusion vs safety IV catheters, etc.); specific Premier categorization for “premix”/injectables was unclear in the moment.
- Whether the scoped next step should be:
  - cross-sell/leakage/targeting dashboards, or
  - portfolio-gap/competitor traction + pricing views, or
  - a data feed subscription (or “some degree of both”).
- For CAPS-related analysis: whether key competitors (e.g., “Fragran Sterl Service” and “QUVA”) and relevant substitute devices/products are fully represented—pending SKU validation/sample.

## Action items (with owners if present)
- **Premier (Bossemeyer/Matt):** Share/“go through a little bit of the data dictionary” and provide prepared materials to support confidence/accuracy of outputs. *(partly completed live via data dictionary screen)*
- **Premier (Bossemeyer/Matt):** Send an “Excel sample” / “a cut of the underlying data” and/or attribute list/dictionary (timing unspecified).
- **Client team (Claire/Jake/others):** Provide Premier a “list of SKUs… name, part number” (and optionally volume) for CAPS/compounding/nutrition/anesthesia/cardioplegia items to validate representation and generate a sample cut.
- **Client team (Tracy + group):** Debrief internally “as a group… a few days” and come back with preferred direction/next steps.
- **Premier (Audrey, with Sachin suggestion):** Provide a brief demo of the standard pre-built app to show category contents and portfolio views (began during this chunk).

## Notable metrics/claims (exact phrases where possible)
- “something like **1600 different facilities**”
- Data latency: “almost **1/4 to 1/3** now is coming in **daily**.”
- Premier mix coverage claim: “the **80% Premier plus the 20% non Premier**.”
- Compliance/commitment band noted: highlighted “between **20 and 80%**” share; typical commitments “either **80 or 90%** for fluids.”
- Spend opportunity claim: “There’s **$50 million of annual spend** just within this group here.” and “if you take a **third of that**, that’s still a substantial revenue impact…”
- Product categorization depth: “a **five level product categorization hierarchy**”
- Pricing limitation (quoted): “we **don’t provide price at a facility level**.”
- SKU granularity (quoted): “detail underneath goes all the way down to a **skew level**” (interpreted as SKU; exact spoken term was “skew”).
