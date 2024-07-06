# %%
from processing import read_file, get_color
import folium
from folium.plugins import HeatMapWithTime
import pandas as pd

# %%
accidents_2022 = pd.read_csv(r'D:\Kaggle\Data\accidents_2022.csv')

# %%
accidents_filtered, grouped, heatmap_data, time_index = read_file(accidents_2022)

# %%
m = folium.Map(location=[accidents_filtered['Latitude'].mean(),

                         accidents_filtered['Longitude'].mean()],
                         zoom_start=10)

HeatMapWithTime(heatmap_data, index=[str(year) for year in time_index], radius=15,
                auto_play=False, max_opacity=0.8).add_to(m)

for year in time_index:
    yearly_data = accidents_filtered[accidents_filtered['Year'] == year]
    fg = folium.FeatureGroup(name=str(year))
    for _, row in yearly_data.iterrows():
        color = get_color(row['Accident_Severity'])
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=2,
            fill=True,
            fill_opacity=1,
            color=color,
            popup=folium.Popup(f"""
                Date: {row['Date'].strftime('%d-%m-%Y')}<br>
                Severity: {row['Accident_Severity']}<br>
                Casualties: {row['Number_of_Casualties']}<br>
                Number of Vehicles: {row['Number_of_Vehicles']}<br>
                Speed Limit: {row['Speed_Limit']}<br>
                Light Conditions: {row['Light_Conditions']}<br>
                Pedestrian Crossing (Human Control): {row['Pedestrian_Crossing-Human_Control']}<br>
                Pedestrian Crossing (Physical Facilities): {row['Pedestrian_Crossing-Physical_Facilities']}
            """, max_width=300)
        ).add_to(fg)
    fg.add_to(m)

folium.LayerControl().add_to(m)

map_name = ''

m.save(rf'D:\Kaggle\Mapas\heatmap{map_name}.html')
