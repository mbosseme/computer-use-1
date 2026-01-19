# Rental Calendar Feasibility — 30+ day minimum

Goal: assess whether multiple 2-week owner blocks fragment the year such that we cannot reliably book **30/60/90-day** tenant blocks.

Status: Draft; now includes an initial quantified calendar check.

## Owner-use scenarios (required)
### Scenario A — two owner trips
- ~2 weeks in Feb or Apr
- ~2 weeks in Aug

### Scenario B — three owner trips
- Scenario A + ~2 weeks post-Christmas

## Initial quantified calendar check (directional)
Assumptions (from `runs/2026-01-19__vineyard-point/inputs/model_inputs.json`):
- Minimum lease term: 30 days
- Turnover buffer around owner blocks: 2 days before + 2 days after
- Year analyzed: 2026

Results (calendar-only, before applying market fill/seasonality):
- Scenario A (`two_trips_feb_aug` or `two_trips_apr_aug`):
	- Owner-use days: 28
	- Max leasable days: 270 (9 x 30-day leases)
	- Implied unusable days (calendar fragmentation + owner + buffers): ~95 days
- Scenario B (`three_trips_feb_aug_dec`):
	- Owner-use days: 42
	- Max leasable days: 270 (9 x 30-day leases)
	- Implied unusable days (calendar fragmentation + owner + buffers): ~95 days

Interpretation:
- The additional 2-week block (Scenario B) doesn't reduce the *maximum* 30-day-leaseable time in this simplified model; it mostly increases the "wasted" partial-month time that can't be sold as a full 30-day lease.
- The bigger real-world risk is seasonal demand + difficulty placing leases that start/stop on the exact boundaries required by the owner blocks.

## What this memo will include
- Example schedules that satisfy a 30-day minimum lease term
- Calculated tenant days/months feasible given the owner blocks
- Conclusion: calendar viable vs too fragmented (with quantified occupancy hit)
