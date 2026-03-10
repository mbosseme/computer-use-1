import pandas as pd
df = pd.read_excel("runs/2026-03-04__portfolio-competitiveness/Category_Competitive_Heat_Map.xlsx", sheet_name="Top Category Opportunities")
row = df[df['Contract_Category'] == 'GASTROINTESTINAL ENDOSCOPY PRODUCTS']
print(row[['Contract_Category', 'Annualized_Total_Spend', 'Annualized_Benchmarked_Spend', 'Annualized_Savings_Opportunity']])

df_interventional = df[df['Contract_Category'] == 'INTERVENTIONAL SHEATHS AND INTRODUCERS']
print(df_interventional[['Contract_Category', 'Annualized_Total_Spend', 'Annualized_Benchmarked_Spend', 'Annualized_Savings_Opportunity']])