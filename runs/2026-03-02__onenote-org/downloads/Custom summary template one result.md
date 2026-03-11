### 1. COMPREHENSIVE DISCUSSION LOG

- The meeting centered on the technical roadmap for consolidating purchasing data across acute and non-acute (COC) sites, focusing on data maturity, entity matching, and system limitations.  
- Melanie outlined the current state: member PO data is aggregated and lacks invoice-level detail; Med Surg/Lab distributor data has invoice-level detail; pharmacy wholesaler data is being enhanced to include invoice-level detail and both sold-to/ship-to; food distributor data is limited, with US Foods unable to provide invoice-level detail due to DOS-based system constraints. Other food distributors can provide the required detail and are being onboarded.  
- The admin fee data is more granular but the processing system ("Sarah") cannot handle the current or increased data volume, especially at the ship-to level. The team discussed interim solutions like storing granular data in Excel and aggregating for processing, but this limits downstream analytics and entity matching.  
- US Foods’ inability to provide invoice-level detail is a major blocker. Their system upgrade is tied to contract renewal, possibly not until 2029/2030. This restricts visibility into food spend and impacts the unified data model.  
- The team is working to enhance the pharmacy wholesaler spec and onboard more wholesalers. Five have been boarded, and the technology can now consume the new spec.  
- There is ongoing work to process and integrate data using Databricks, Tableau, and BigQuery. The goal is a single, comprehensive data model that supports both high-level and transaction-level analysis, with the ability to drill down by service line, distributor, and member.  
- Entity matching and data granularity are recurring challenges. Without consistent invoice-level detail and matching keys across all data sources, the team cannot accurately combine or de-duplicate spend, especially for alternate sites and affiliates.  
- The team debated the sequencing of data integration: acute (hospital) data is prioritized, with COC/alternate site data to follow. There is uncertainty about whether COC should be a parallel or subsequent effort, pending leadership guidance.  
- There is a need for ongoing master data management, especially for non-clinical categories and standardizing vendors. Melanie’s team is working on standardizing pharmacy and food distributor vendors and cleaning up direct vendor spend not currently captured.  
- The group discussed the need for automation and maintenance of processes that integrate distributor data into the TSA, as previous efforts were not maintained.  
- Manual processes are still required for some rebate and service fee data, which are tracked outside the main systems and need to be integrated for a complete view.  
- The team acknowledged that the current Excel-based dashboards are sufficient for immediate needs, but automation and more granular data are required for future phases and advanced analytics.

### 2. SPEAKER ATTRIBUTION & DEBATE

**Melanie Proctor**
- Emphasized the need for invoice-level detail and consistent entity matching logic across all data sets.
- Highlighted technical limitations with US Foods and Sarah, and the need for system upgrades.
- Pushed for integrating more granular admin fee and direct vendor data, and standardizing vendors.
- Noted that Med Surg/Lab distributor data includes both acute and non-acute spend, correcting Matt’s assumption.
- Advocated for using the distributor data to fill gaps in member PO data, especially for affiliates and alternate sites.

**Matt Bossemeyer**
- Focused on building a consolidated data model, prioritizing acute data first, then expanding to COC.
- Questioned the materiality of Med Surg/Lab distributor data for hospitals not covered by member PO.
- Proposed layering pharmacy wholesaler tracings on top of TSA data as the next step.
- Debated with Melanie about the coverage and overlap of data sources, and the best approach for integrating distributor data.
- Highlighted the need for automation and maintenance in integrating distributor data into TSA.

**Brian Hall**
- Facilitated the discussion, ensuring alignment on priorities and timelines.
- Raised concerns about US Foods’ system limitations and contract renewal timing.
- Sought clarity on what can be delivered in the short term versus long term, and how to set expectations with leadership.
- Pointed out manual data integration challenges for rebates and service fees.

**Caitlin Rounds**
- Provided context on leadership expectations and the convergence of acute and COC projects.
- Flagged the need for clear guidance from leadership on whether COC data integration should be parallel or sequential.
- Tracked dashboard requirements and highlighted the need for clarity on KPI definitions and dashboard specs.

**Debate & Friction**
- Matt and Melanie debated the coverage and necessity of Med Surg/Lab distributor data for acute sites, with Melanie clarifying that it includes both acute and non-acute spend.
- There was discussion about the best way to integrate distributor data—whether to layer it downstream or feed it into TSA upstream—and who should own the maintenance.
- The team discussed the limitations of current systems (Sarah, US Foods) and the impact on data granularity and analytics.

### 3. DECISIONS & RATIONALE

- **Prioritize Integration of TSA and Pharmacy Wholesaler Data:** The team agreed to first combine TSA (member PO/AP) and pharmacy wholesaler tracings to cover clinical, non-clinical, and pharmacy spend for acute sites.  
  *Rationale:* These sources are most mature, have the best data quality, and cover the largest spend categories. This approach allows for a phased build-out and immediate value.  
- **Defer Full Food Distributor Integration:** US Foods’ system limitations mean invoice-level detail for food will not be available until at least 2029/2030.  
  *Rationale:* Technical constraints and contract timing prevent earlier integration.  
- **Automate and Maintain Distributor Data Integration:** The team will automate the process of adding distributor data for top parents not covered in TSA, ensuring ongoing maintenance.  
  *Rationale:* Previous manual processes were not maintained, leading to data gaps. Automation ensures completeness and sustainability.  
- **Continue Manual Tracking for Service Fees and Rebates:** Manual integration will continue for now, with plans to automate as systems mature.  
  *Rationale:* Some data is only available outside core systems and must be tracked manually until integration is possible.  
- **Standardize Vendor and Category Data:** Melanie’s team will continue standardizing vendors and cleaning up direct vendor spend, especially for pharmacy and food.  
  *Rationale:* Standardization is required for accurate matching, categorization, and reporting.

### 4. ACTION ITEMS & OWNERS

- **Onboard Additional Pharmacy Wholesalers to Enhanced Spec** – Melanie to continue working with Shelley Scavo and wholesalers to complete onboarding and ensure technology can consume new data.  
- **Push US Foods for Invoice-Level Detail** – John Merendino to continue discussions with US Foods leadership and escalate to CEO level as needed.  
- **Automate Distributor Data Integration into TSA** – Matt to coordinate with Stephen and the Fusion team to automate and maintain the process of adding distributor data for uncovered top parents.  
- **Standardize Vendor and Category Data** – Melanie’s team to continue work on standardizing pharmacy and food distributor vendors and cleaning up direct vendor spend.  
- **Integrate Service Fee and Rebate Data** – Brian to coordinate with finance and other stakeholders to pull in manual rebate and service fee data for food and pharmacy.  
- **Clarify COC Data Integration Strategy** – Caitlin to follow up with leadership (Bruce and others) to determine if COC data integration should proceed in parallel or as a subsequent phase.  
- **Build Tableau Dashboard for Scorecard Automation** – Zach to stand up the table in BigQuery and coordinate with Jenny (when back from PTO) to build the Tableau dashboard; Matt to follow up as needed.  
- **Document Missing Data Elements** – Melanie to send an email summarizing any additional data elements missing from the current model for consideration in future phases.  
- **Review Layered Data Model for Pharmacy Spend** – Matt to review the first integration of pharmacy wholesaler tracings on top of TSA with Ed and Shelley to ensure all relevant pharmacy spend is captured.
