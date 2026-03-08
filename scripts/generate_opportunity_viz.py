import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.dates as mdates

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("colorblind")

# Load data
file_path = "runs/2026-03-04__portfolio-competitiveness/Contract_Competitive_Heat_Map.xlsx"
df = pd.read_excel(file_path, sheet_name="Top 50 Opportunities")

# Convert Expiration_Date to datetime
df['Expiration_Date'] = pd.to_datetime(df['Expiration_Date'])

# Create a figure and axis
fig, ax = plt.subplots(figsize=(14, 8))

# Scatter plot: x=Expiration_Date, y=Opportunity_Pct, size=Annualized_Savings_Opportunity, color=Program
scatter = sns.scatterplot(
    data=df,
    x='Expiration_Date',
    y='Opportunity_Pct',
    size='Annualized_Savings_Opportunity',
    hue='Program',
    sizes=(200, 4000),
    alpha=0.7,
    ax=ax
)

# Formatting
ax.set_title('Top 50 Expiring Contracts: Savings Opportunity vs Timing', fontsize=18, pad=20, fontweight='bold')
ax.set_xlabel('Contract Expiration Date', fontsize=12)
ax.set_ylabel('Gap to Benchmark Target (%)', fontsize=12)

# Format axes
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# Customize legend
handles, labels = scatter.get_legend_handles_labels()

# In seaborn, the size legend shows numeric values, we can format them as currency
new_labels = []
for label in labels:
    try:
        val = float(label)
        if val > 100:  # Simple check for the size values vs categorical values
            new_labels.append('${:,.0f}M'.format(val / 1e6))
        else:
            new_labels.append(label)
    except ValueError:
        new_labels.append(label)

ax.legend(handles, new_labels, bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., title="Legend")

# Annotate the top 5 largest opportunities
top_5 = df.nlargest(5, 'Annualized_Savings_Opportunity')
for _, row in top_5.iterrows():
    ax.annotate(
        f"{row['Contract_Number']}\n(${row['Annualized_Savings_Opportunity']/1e6:.1f}M)", 
        (row['Expiration_Date'], row['Opportunity_Pct']),
        xytext=(15, 15), textcoords='offset points',
        fontsize=9, weight='bold', color='#333333',
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color="gray")
    )

plt.tight_layout()

# Save the plot
output_dir = "runs/2026-03-04__portfolio-competitiveness/"
out_file = os.path.join(output_dir, "Opportunity_Timing_Bubble_Chart.png")
fig.savefig(out_file, dpi=300, bbox_inches='tight')
print(f"Saved visualization to {out_file}")
