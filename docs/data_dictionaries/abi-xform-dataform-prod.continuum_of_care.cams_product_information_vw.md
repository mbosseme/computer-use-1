# Data Dictionary: `cams_product_information_vw`

- **Project**: `abi-xform-dataform-prod`
- **Dataset**: `continuum_of_care`
- **Table**: `cams_product_information_vw`
- **Type**: View

## Purpose
This view provides manufacturer-reported on-contract sales data (tracings) at the Reference Number level. It is used as the "ground truth" for validation, as it represents what the supplier (B. Braun) officially reported as sold to Premier members under contract.

## Schema

| Column Name | Type | Description |
|:---|:---|:---|
| `Spend_Period_YYYYQMM` | INTEGER | Time period key (Year-Quarter-Month, of format YYYYQMM). requires parsing to Month-Year. |
| `Contract_Name` | STRING | Name of the GPO contract. |
| `Contract_Number` | STRING | Contract identifier. |
| `Facility_Name` | STRING | Name of the purchasing facility. |
| `Premier_Entity_Code` | STRING | **Key Join Column**. Unique identifier for the facility in Premier's system. |
| `Product_Description` | STRING | Description of the product sold. |
| `Sales_Volume_Paid_Reported` | FLOAT | **Key Measure**. Total sales amount reported by the supplier. |
| `Rebate_Paid_Amount` | FLOAT | Rebate amount paid. |
| `units_sold` | FLOAT | **Key Measure**. Quantity of units sold. |
| `Supplier_Catalog_Number` | STRING | Vendor's catalog number for the product. |
| `Reference_Number` | STRING | **Key Join Column**. Premier's internal identifier for the product. |
| `Supplier_Name` | STRING | Name of the supplier. |
| `Supplier_Top_Parent_Entity_Code` | STRING | Top parent entity code. For B. Braun, verify if this is `606326`. |
| `Supplier_Top_Parent_Name` | STRING | Name of the top parent supplier. |

## Query Notes
- **Time Grain**: `Spend_Period_YYYYQMM` suggests a Quarterly or Monthly grain encoded as integer. Need to verify format with a distinct sample.
- **Product Key**: `Reference_Number` is the primary key for product. `Supplier_Catalog_Number` is auxiliary.
- **Validation Scope**: Filter `Supplier_Top_Parent_Entity_Code` or Name for 'B. BRAUN'.
