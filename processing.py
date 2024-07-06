import pandas as pd
from haversine import haversine, Unit

def read_file (dataset):
    dataset['Date'] = pd.to_datetime(dataset['Date'], format='%d/%m/%Y')
    dataset['Year'] = dataset['Date'].dt.year

    dataset = dataset.dropna(subset=['Latitude', 'Longitude'])

    target_coords = [52.489471, -1.898575]
    distance_threshold_km = 10

    dataset['Distance'] = dataset.apply(lambda row: haversine((row['Latitude'], row['Longitude']), target_coords, unit=Unit.KILOMETERS), axis=1)
    accidents_filtered = dataset[dataset['Distance'] <= distance_threshold_km]
    grouped = accidents_filtered.groupby(['Year', 'Latitude', 'Longitude']).size().reset_index(name='Count')

    heatmap_data = []
    time_index = grouped['Year'].unique()

    for year in time_index:
        yearly_data = grouped[grouped['Year'] == year]
        heatmap_data.append([[row['Latitude'], row['Longitude'], row['Count']] for index, row in yearly_data.iterrows()])
    
    return accidents_filtered, grouped, heatmap_data, time_index


def get_color(severity):
    if severity == 1:
        return 'red'
    elif severity == 2:
        return 'blue'
    elif severity == 3:
        return 'gray'
