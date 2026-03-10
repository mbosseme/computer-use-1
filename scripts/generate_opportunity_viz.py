import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.dates as mdates
from adjustText import adjust_text
import textwrap
import argparse

def generate_chart(df, output_path, title_prefix, top_n_count=50):
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("colorblind")

    # Limit to Top N based strictly on opportunity size
    plot_df = df.nlargest(top_n_count, 'Annualized_Savings_Opportunity').copy()
    plot_df['Expiration_Date'] = pd.to_datetime(plot_df['Expiration_Date'])

    fig, ax = plt.subplots(figsize=(16, 9))

    scatter = sns.scatterplot(
        data=plot_df,
        x='Expiration_Date',
        y='Opportunity_Pct',
        size='Annualized_Savings_Opportunity',
        hue='Service_Line',
        sizes=(100, 3500),
        alpha=0.75,
        edgecolor='gray',
        linewidth=1.2,
        ax=ax
    )

    ax.xaxis.grid(False)
    sns.despine(ax=ax, top=True, right=True)

    ax.axhline(0.20, color='red', linestyle='--', alpha=0.3, zorder=0)
    ax.text(plot_df['Expiration_Date'].min(), 0.205, 'Priority Action Threshold (20% Gap)', color='red', alpha=0.6, fontsize=9, fontstyle='italic')
    
    fig.suptitle(f'{title_prefix}: Savings Opportunity vs Timing', fontsize=20, fontweight='bold', y=0.98)
    ax.set_title('Bubble size = Annualized Savings | Y-Axis = Gap to Benchmark Target', fontsize=12, pad=15, color='gray')
    ax.set_xlabel('Contract Expiration Date', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylabel('Gap to Benchmark Target (%)', fontsize=12, fontweight='bold', labelpad=10)
    ax.set_ylim(bottom=0)

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

    def quarter_formatter(x, pos):
        dt = mdates.num2date(x)
        quarter = (dt.month - 1) // 3 + 1
        return f"Q{quarter} {dt.year}"

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 4, 7, 10)))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(quarter_formatter))

    handles, labels = scatter.get_legend_handles_labels()
    new_labels = []
    for label in labels:
        if label == 'Annualized_Savings_Opportunity':
            new_labels.append('Annualized Savings Opportunity')
        else:
            try:
                val = float(label)
                if val > 100:  
                    new_labels.append('${:,.0f}M'.format(val / 1e6))
                else:
                    new_labels.append(label)
            except ValueError:
                new_labels.append(label)

    ax.legend(handles, new_labels, bbox_to_anchor=(1.02, 1), loc='upper left', 
              borderaxespad=0., title='Legend', labelspacing=2.5, handletextpad=2.0,
              scatterpoints=1, frameon=False)

    def abbrev(text):
        text = str(text)
        reps = {
            'CARDIAC RHYTHM MANAGEMENT DEVICES': 'CRM Devices',
            'GENERAL ORTHOPEDIC TRAUMA PRODUCTS': 'Ortho Trauma',
            'PULSE OXIMETRY AND CAPNOGRAPHY DEVICES': 'Pulse Oximetry',
            'CONTRAST MEDIA INJECTORS AND DISPOSABLES': 'Contrast Media Injectors',
            'TRANSCATHETER AORTIC VALVE IMPLANTS AND PRODUCTS': 'TAVR',
            'SPECIALTY WOMENS HEALTH SURGICAL PRODUCTS': 'Women\'s Health Surgical',
            'NEUROSURGICAL - DURAL REPAIR AND RELATED PRODUCTS': 'Neuro Dural Repair',
            'LIQUID MEDICAL WASTE MANAGEMENT SYSTEMS': 'Liquid Med Waste',
            ', INC.': '', ' INC.': '', ' CORPORATION': '', ' LLC': '', ' LP': '', ', LP': '', ' DEVICES': '', ' PRODUCTS': ''
        }
        for k, v in reps.items():
            text = text.replace(k, v)
        if 'STRYKER' in text:
            text = 'Stryker'
        if 'MEDICAL IMAGING' in text:
            text = text.replace(' MEDICAL IMAGING', '')
        return text.strip().title() if text.isupper() else text.strip()

    def format_label(row):
        name = abbrev(row['Contract_Name'])
        wrapped_name = textwrap.fill(name, width=22)
        return f"{wrapped_name}\n${row['Annualized_Savings_Opportunity']/1e6:.1f}M"

    top_n = plot_df.nlargest(12, 'Annualized_Savings_Opportunity')

    texts = []
    for _, row in top_n.iterrows():
        lines = format_label(row)
        texts.append(ax.text(
            row['Expiration_Date'], 
            row['Opportunity_Pct'], 
            lines,
            fontsize=8.5, 
            weight='bold', 
            color='#222222',
        ))

    if texts:
        adjust_text(texts, ax=ax, arrowprops=dict(arrowstyle='-', color='#888888', lw=1.2, alpha=0.7))

    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved visualization to {output_path}')

def main():
    file_path = "runs/2026-03-04__portfolio-competitiveness/Contract_Competitive_Heat_Map_All_Programs_and_Categories.xlsx"
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}. Run export script first.")
        return
        
    df = pd.read_excel(file_path, sheet_name="All Opportunities")
    output_dir = 'runs/2026-03-04__portfolio-competitiveness/'
    
    print(f"Generating All Programs Chart...")
    generate_chart(
        df=df, 
        output_path=os.path.join(output_dir, 'Opportunity_Timing_Bubble_Chart_All_Programs.png'),
        title_prefix='FY27 Expiring Contracts (All Programs)'
    )

    print(f"Generating National Only Chart...")
    national_df = df[df['Program'] == 'National']
    generate_chart(
        df=national_df, 
        output_path=os.path.join(output_dir, 'Opportunity_Timing_Bubble_Chart_National.png'),
        title_prefix='FY27 Expiring Contracts (National Only)'
    )

if __name__ == "__main__":
    main()
