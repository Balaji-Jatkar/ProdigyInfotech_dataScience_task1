import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np


INDICATORS = {
    'male_pop': 'SP.POP.TOTL.MA.IN',
    'female_pop': 'SP.POP.TOTL.FE.IN',
    'age_0_14': 'SP.POP.0014.TO.ZS',
    'age_15_64': 'SP.POP.1564.TO.ZS', 
    'age_65_plus': 'SP.POP.65UP.TO.ZS'
}

def fetch_wb_demographic_data(countries="USA;CHN;IND;BRA;DEU;JPN;GBR;FRA", year="2022"):
    """
    Fetch demographic data from World Bank API
    """
    all_data = {}
    
    for indicator_name, indicator_code in INDICATORS.items():
        url = f"https://api.worldbank.org/v2/country/{countries}/indicator/{indicator_code}"
        params = {
            'format': 'json',
            'per_page': 1000,
            'date': year
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if len(data) > 1 and data[1]:
                df = pd.DataFrame(data[1])
                all_data[indicator_name] = df
                print(f"✓ Fetched {indicator_name} data")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching {indicator_name}: {e}")
    
    return all_data

def create_sample_demographic_data():
    """
    Create sample demographic data for demonstration
    """
    countries = ['United States', 'China', 'India', 'Germany', 'Japan', 'Brazil', 'United Kingdom', 'France']
    
    data = {
        'countries': countries,
        'male_population': [163, 723, 717, 41, 61, 106, 33, 33],     # millions
        'female_population': [168, 689, 663, 42, 64, 109, 34, 35],   # millions
        'age_0_14_percent': [18.1, 17.3, 26.2, 13.9, 12.5, 21.1, 17.9, 17.9],
        'age_15_64_percent': [65.0, 70.1, 67.0, 64.9, 59.2, 69.6, 64.2, 61.7],
        'age_65_plus_percent': [16.9, 12.6, 6.8, 21.2, 28.3, 9.3, 17.9, 20.4]
    }
    
    return data


print("Fetching World Bank demographic data...")
wb_data = fetch_wb_demographic_data()


if wb_data and len(wb_data) > 2:
    print("Processing World Bank data...")
    
    first_dataset = list(wb_data.values())[0]
    
    if 'country' in first_dataset.columns:
        if isinstance(first_dataset['country'].iloc[0], dict):
            countries = [country['value'] for country in first_dataset['country']]
        else:
            countries = first_dataset['country'].tolist()
    else:
        countries = [f"Country_{i+1}" for i in range(len(first_dataset))]
    
    data = {'countries': countries}
    
    for indicator_name, df in wb_data.items():
        if not df.empty:
            values = pd.to_numeric(df['value'], errors='coerce').fillna(0).tolist()
            data[indicator_name] = values
    
else:
    print("Using sample demographic data...")
    data = create_sample_demographic_data()


num_countries = min(8, len(data['countries']))
for key in data:
    if isinstance(data[key], list):
        data[key] = data[key][:num_countries]

countries_short = [country[:12] + '...' if len(country) > 12 else country for country in data['countries']]


if 'male_population' in data and 'female_population' in data:
    male_data = data['male_population']
    female_data = data['female_population']
else:
    # Use male_pop and female_pop if available
    male_data = data.get('male_pop', [100] * num_countries)[:num_countries]
    female_data = data.get('female_pop', [100] * num_countries)[:num_countries]

age_0_14 = data.get('age_0_14_percent', data.get('age_0_14', [20] * num_countries))[:num_countries]
age_15_64 = data.get('age_15_64_percent', data.get('age_15_64', [65] * num_countries))[:num_countries]
age_65_plus = data.get('age_65_plus_percent', data.get('age_65_plus', [15] * num_countries))[:num_countries]


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))


x = np.arange(len(countries_short))
width = 0.35

bars1 = ax1.bar(x - width/2, male_data, width, label='Male', color='lightblue', alpha=0.8)
bars2 = ax1.bar(x + width/2, female_data, width, label='Female', color='lightpink', alpha=0.8)

ax1.set_xlabel('Countries')
ax1.set_ylabel('Population (Millions)')
ax1.set_title('Gender Distribution by Country', fontweight='bold', fontsize=14)
ax1.set_xticks(x)
ax1.set_xticklabels(countries_short, rotation=45, ha='right')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)


age_categories = ['0-14 years', '15-64 years', '65+ years']
avg_age_dist = [
    np.mean(age_0_14),
    np.mean(age_15_64), 
    np.mean(age_65_plus)
]

bars = ax2.bar(age_categories, avg_age_dist, color=['lightgreen', 'orange', 'lightcoral'], alpha=0.8)
ax2.set_ylabel('Average Percentage')
ax2.set_title('Global Age Distribution', fontweight='bold', fontsize=14)
ax2.grid(axis='y', alpha=0.3)


for bar, value in zip(bars, avg_age_dist):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.show()


print("\n" + "="*50)
print("DEMOGRAPHIC SUMMARY")
print("="*50)
print(f"Countries analyzed: {len(countries_short)}")
print(f"Average age distribution:")
print(f"  - Children (0-14): {np.mean(age_0_14):.1f}%")
print(f"  - Working age (15-64): {np.mean(age_15_64):.1f}%")
print(f"  - Elderly (65+): {np.mean(age_65_plus):.1f}%")
print("="*50)