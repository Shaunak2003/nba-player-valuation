import pandas as pd

def clean_data():

    raw_stats = pd.read_csv("../data/raw_stats.csv")
    advanced_stats = pd.read_csv("../data/advanced_stats.csv")
    salaries = pd.read_csv("../data/salaries.csv")

    raw_stats = raw_stats.drop_duplicates(subset=['Rk'])
    raw_stats = raw_stats.reset_index(drop=True)

    advanced_stats = advanced_stats.drop_duplicates(subset=['Rk'])
    advanced_stats = advanced_stats.reset_index(drop=True)

    merged = pd.merge(raw_stats, advanced_stats, on="Player-additional", suffixes=('', '_drop'))
    merged.drop([col for col in merged.columns if '_drop' in col], axis=1, inplace=True)
  
    salaries = salaries.rename(columns={'-9999' : 'Player-additional', 'Tm': 'Team'})
    merged = pd.merge(salaries, merged, on="Player-additional", how="left", suffixes=('', '_drop'))
    merged = merged.drop(["2025-26", "2026-27", "2027-28", "2028-29", "2029-30", "Guaranteed"], axis=1)
    merged.drop([col for col in merged.columns if '_drop' in col], axis=1, inplace=True)

    merged.to_csv("merged.csv")
    print(merged)


print(clean_data())