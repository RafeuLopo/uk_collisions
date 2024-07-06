#%%
import os

import pandas as pd
import geopandas as gpd

import matplotlib.pyplot as plt
import folium

from folium.plugins import HeatMapWithTime

from processing import read_file, get_color

#%%
os.environ['SHAPE_RESTORE_SHX'] = 'YES'
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

#%%
accidents_05_07 = pd.read_csv(r'D:\Kaggle\Data\accidents_2005_to_2007.csv')
accidents_09_11 = pd.read_csv(r'D:\Kaggle\Data\accidents_2009_to_2011.csv')
accidents_12_14 = pd.read_csv(r'D:\Kaggle\Data\accidents_2012_to_2014.csv')
accidents_22 = pd.read_csv(r'D:\Kaggle\Data\accidents_2022.csv')

# %%
columns_to_drop = ['accident_year', 'accident_reference',
                   'local_authority_ons_district', 'trunk_road_flag']

columns_names = ['Accident_Index', 'Location_Easting_OSGR', 'Location_Northing_OSGR',
       'Longitude', 'Latitude', 'Police_Force', 'Accident_Severity',
       'Number_of_Vehicles', 'Number_of_Casualties', 'Date', 'Day_of_Week',
       'Time', 'Local_Authority_(District)', 'Local_Authority_(Highway)',
       '1st_Road_Class', '1st_Road_Number', 'Road_Type', 'Speed_limit',
       'Junction_Detail', 'Junction_Control', '2nd_Road_Class',
       '2nd_Road_Number', 'Pedestrian_Crossing-Human_Control',
       'Pedestrian_Crossing-Physical_Facilities', 'Light_Conditions',
       'Weather_Conditions', 'Road_Surface_Conditions',
       'Special_Conditions_at_Site', 'Carriageway_Hazards',
       'Urban_or_Rural_Area', 'Did_Police_Officer_Attend_Scene_of_Accident',
       'LSOA_of_Accident_Location']

# %%
accidents_22.drop(labels=columns_to_drop, axis=1, inplace=True)
accidents_22.columns = columns_names

# %%
shapefile = gpd.read_file(r'D:\Kaggle\Data\Areas.shp')
shapefile.crs = 'EPSG:4326'
shapefile = shapefile.to_crs(epsg=4326)

# %%
fig, ax = plt.subplots()
ax.set_title('Shapefile Plot')
shapefile.plot(ax=ax, color='blue', edgecolor='black')

plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()

# %%
authority_districts = pd.read_csv(r'D:\Kaggle\Data\Local_Authority_Districts_Dec_2016.csv')

# %%
accidents_full = pd.concat(
            [accidents_05_07, accidents_09_11, accidents_12_14],ignore_index=True)

accidents_full['Date'] = pd.to_datetime(accidents_full['Date'], format='%d/%m/%Y')
accidents_full['Year'] = accidents_full['Date'].dt.year
accidents_full['Month'] = accidents_full['Date'].dt.month

accidents_full = accidents_full.dropna(subset=['Latitude', 'Longitude'])

accidents_per_light = accidents_full.groupby('Light_Conditions').size().reset_index()
accidents_per_light.rename(columns={0: "Count"}, inplace=True)

accidents_per_weather = accidents_full.groupby('Weather_Conditions').size().reset_index()
accidents_per_weather.rename(columns={0: "Count"}, inplace=True)

accidents_per_year = accidents_full.groupby('Year').size().reset_index()
accidents_per_year.rename(columns={0: "Count"}, inplace=True)

accidents_per_month = accidents_full.groupby('Month').size().reset_index()
accidents_per_month.rename(columns={0: "Count"}, inplace=True)

accidents_per_day_of_week = accidents_full.groupby('Day_of_Week').size().reset_index()
accidents_per_day_of_week.rename(columns={0: "Count"}, inplace=True)

accidents_per_cars_and_light = (
                            accidents_full[['Number_of_Vehicles', 'Light_Conditions']]
                                .groupby(by='Light_Conditions')
                                .count()
                                            ).reset_index()

# %%
plt.figure()

plt.bar(accidents_per_light['Light_Conditions'], accidents_per_light['Count'])
plt.title('Número de Acidentes por Condições de Iluminação')
plt.xlabel('Condições de Iluminação')
plt.ylabel('Número de Acidentes')
plt.xticks(rotation=90)
plt.show()

# %%
plt.figure()

plt.bar(accidents_per_weather['Weather_Conditions'], accidents_per_weather['Count'])
plt.title('Carros Envolvidos por Condições Climáticas')
plt.xlabel('Condições Climáticas')
plt.ylabel('Acidentes')
plt.xticks(rotation=90)
plt.show()

# %%
plt.figure()

plt.plot(accidents_per_year['Year'], accidents_per_year['Count'], marker='o', linestyle='-', color='b')
plt.title('Number of Accidents per Year')
plt.xlabel('Date')
plt.ylabel('Number of Accidents')
plt.xticks(rotation=45)
plt.show()

# %%
plt.figure()

plt.plot(accidents_per_month['Month'], accidents_per_month['Count'], marker='o', linestyle='-', color='b')
plt.title('Number of Accidents per Month')
plt.xlabel('Date')
plt.ylabel('Number of Accidents')
plt.xticks(rotation=45)
plt.show()

# %%
plt.figure()

plt.plot(accidents_per_day_of_week['Day_of_Week'], accidents_per_day_of_week['Count'], marker='o', linestyle='-', color='b')
plt.title('Number of Accidents per Day of Week')
plt.xlabel('Date')
plt.ylabel('Number of Accidents')
plt.xticks(rotation=45)
plt.show()

# %%
plt.figure()

plt.bar(accidents_per_cars_and_light['Light_Conditions'], accidents_per_cars_and_light['Number_of_Vehicles'])
plt.title('Carros Envolvidos por Condições de Iluminação')
plt.xlabel('Condições de Iluminação')
plt.ylabel('Número de Carros')
plt.xticks(rotation=90)
plt.show()

# %%
accidents_filtered, grouped, heatmap_data, time_index = read_file(accidents_22)

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
                Speed Limit: {row['Speed_limit']}<br>
                Light Conditions: {row['Light_Conditions']}<br>
                Pedestrian Crossing (Human Control): {row['Pedestrian_Crossing-Human_Control']}<br>
                Pedestrian Crossing (Physical Facilities): {row['Pedestrian_Crossing-Physical_Facilities']}
            """, max_width=300)
        ).add_to(fg)
    fg.add_to(m)

folium.LayerControl().add_to(m)

m.save(r'D:\Kaggle\Mapas\heatmap_2022.html')

# %%
