import plotly
import plotly.graph_objs as go

import folium
from folium.plugins import HeatMap

import pandas as pd, numpy as np, matplotlib.pyplot as plt, time
from math import ceil
import seaborn as sns
from sklearn.cluster import DBSCAN
from geopy.distance import great_circle
from shapely.geometry import MultiPoint
import mpld3

pd.options.mode.chained_assignment = None
sns.set_style("whitegrid")

class Aidplot:
    def __init__(self,path='/Users/Paul-Tristan/Documents/Columbia/Cours/Fall16/Data Analytics for OR/Project/Datasets/'):
        self.path_data = path
        self.columns = ['year', 'commitment_date',
                        'commitment_amount_usd_constant', 'donor',
                        'aiddata_sector_name', 'recipient_iso']

    def aids_df(self, datafile, country_iso2=''):
        '''
        This function takes an iso code (2) to filter and clean the csv to return results for the country required.
        Results returned can also be controlled by inputting the columns required.

        List of Iso-codes 2:
        Afghanistan: AF; Central Africa Republic:CF; Syria:SY

        List of columns:
        ['year','commitment_date','commitment_amount_usd_constant','donor','aiddata_sector_name','recipient_iso']
        '''

        if country_iso2=='AF':
            self.prefix='afgha_'
        if country_iso2=='CF':
            self.prefix='car_'

        data = pd.read_csv(self.path_data + datafile, usecols=self.columns)
        date_col_title = self.columns[0]
        date_col2_title = self.columns[1]

        # Filtering data for required country only - creating new_dataframe
        clean_data = data[data['recipient_iso'] == country_iso2]

        # Cleaning and sorting by dates - removing inf values, and converting in datetime
        clean_data = clean_data.replace(to_replace='1/1/9999',
                                        value=np.nan).replace(
            to_replace='1/1/1900', value=np.nan)
        clean_data = clean_data[clean_data['year'] != 9999]
        clean_data[date_col2_title] = pd.to_datetime(
            clean_data[date_col2_title],
            errors='ignore')
        clean_data = clean_data.sort_values(by=self.columns)

        # Re-indexing data-frame and moving columns
        clean_data = clean_data.reset_index(drop=True)
        clean_data = clean_data.reindex(columns=self.columns)

        # Adding columns for cumulative sum
        clean_data.insert(3, 'aggregate_commitments', clean_data[
            'commitment_amount_usd_constant'].cumsum())

        self.df=clean_data
        self.donor_name = list(self.df['donor'].unique())
        return clean_data

    def aids_update_plot(self, donor_name):
        '''
        This function need to run the function that processes the aids csv first:
            df = aids_df(datafile,columns=[],country_iso2='')

        The interact function will add the input donor_name and run the plotting function (plot requres online access for now)
        '''

        # Determining donated amount per country each year, resetting index as keys
        org_yearly = self.df.groupby(['year', 'donor']).sum()
        org_yearly = org_yearly.reset_index(level=['year', 'donor']).drop(
            'aggregate_commitments', 1)

        # Determining total donation for a given year, resetting index as keys
        total_yearly = self.df.groupby('year').sum()
        total_yearly = total_yearly.reset_index(
            level=['year', 'donor']).drop('aggregate_commitments', 1)

        # Creating Plot - here for total yearly
        data_1 = go.Scatter(
            x=total_yearly['year'],  # assign x as the dataframe column 'x'
            y=total_yearly['commitment_amount_usd_constant'],
            name='Global')

        data_2 = go.Scatter(
            x=org_yearly[org_yearly['donor'] == donor_name].reset_index(
                drop=True)['year'],  # assign x as the dataframe column 'x'
            y=org_yearly[org_yearly['donor'] == donor_name].reset_index(
                drop=True)['commitment_amount_usd_constant'],
            name=donor_name)

        layout = go.Layout(
            title='Yearly Committed Amount for International Development (in USD)',
            hovermode='closest',
            xaxis=dict(
                title='Year',
                ticklen=5,
                zeroline=False,
                gridwidth=2),
                #rangeslider=dict(range=[1996, 2013])),
            # range= [total_yearly['year'].min(),total_yearly['year'].max()]),
            yaxis=dict(
                title='Committed Amount (in USD)',
                ticklen=5,
                gridwidth=2, ),
            showlegend=True)

        data = [data_1, data_2]

        fig = go.Figure(data=data, layout=layout)
        return plotly.offline.plot(fig,filename='templates/'+self.prefix+'aidplot.html',auto_open=False)

class Mapplot:
    def __init__(self,path='/Users/Paul-Tristan/Documents/Columbia/Cours/Fall16/Data Analytics for OR/Project/Datasets/',country=''):
        '''
        This function takes an iso code (2) to filter and clean the csv to return results for the country required.
        Results returned can also be controlled by inputting the columns required.

        List of countries:
        Afghanistan; Central African Republic; Syria

        Note that Syria returns no results (absent from initial csv)

        List of columns:
        ['date_start','date_end','country','deaths_a','deaths_b','deaths_civilians','deaths_unknown','side_a','side_b','latitude','longitude]
        '''

        self.datafile=path+"ged50.csv"
        self.columns=['date_start','date_end','country','deaths_a','deaths_b','deaths_civilians','deaths_unknown','side_a','side_b','latitude','longitude']
        self.kms_per_radian = 6371.0088
        self.eps_rad = 20 / self.kms_per_radian
        self.country = country

        self.hm_columns=['Year', 'Country', 'Location Name', 'F: Total', 'M: Total','Overall total']
        self.datafile_refugees = path + 'Refugees.csv'
        self.datafile_geoloc = path + 'Location_Cross_Ref.csv'

        if country=='Afghanistan':
            self.location=[33.94, 67.71]
            self.prefix='afgha_'
            self.hm_data=refugees_df(self.datafile_refugees, self.datafile_geoloc, columns=self.hm_columns,country_name=country, start_date=2007, end_date=2014)
        if country=='Central African Republic':
            self.location = [6.61, 20.94]
            self.prefix = 'car_'
            self.hm_data = refugees_df(self.datafile_refugees,
                                       self.datafile_geoloc, columns=self.hm_columns,
                                       country_name='Central African Rep.', start_date=2003,
                                       end_date=2014)

        lat_list = self.hm_data['Latitude'].tolist()
        lon_list = self.hm_data['Longitude'].tolist()
        self.hm_coords = [[lat_list[i], lon_list[i]] for i in range(len(lat_list))]

        data = pd.read_csv(self.datafile, sep=None, engine='python')

        date_col_title = self.columns[0]
        date_col2_title = self.columns[1]

        clean_data = data[data['country'] == country][self.columns]

        # Cleaning and sorting by dates - removing inf values, and converting in datetime
        clean_data[date_col_title] = pd.to_datetime(clean_data[date_col_title],
                                                    errors='ignore')
        clean_data[date_col2_title] = pd.to_datetime(
            clean_data[date_col2_title], errors='ignore')
        clean_data = clean_data.sort_values(by=self.columns)

        # clean_data = clean_data.sort_values(by='date_start')
        clean_data['total_deaths'] = clean_data['deaths_a'].cumsum() + \
                                     clean_data['deaths_b'].cumsum() + \
                                     clean_data['deaths_civilians'].cumsum() + \
                                     clean_data['deaths_unknown'].cumsum()

        # Re-indexing data-frame and moving columns
        clean_data = clean_data.reset_index(drop=True)

        self.data = clean_data.reindex(columns=self.columns)

    def render_map_country(self,start_date,end_date):
        map_object = folium.Map(location=self.location, zoom_start=5,tiles="Stamen toner", max_zoom=6, min_zoom=5)

        # The three next lines are here to not override the bootstrap theme.
        folium_figure = map_object.get_root()
        folium_figure.header._children['bootstrap_css'] = folium.element.JavascriptLink('')
        folium_figure.header._children['bootstrap_theme_css'] = folium.element.JavascriptLink('')
        folium_figure.header._children['jquery'] = folium.element.JavascriptLink('')
        folium_figure.header._children['bootstrap'] = folium.element.JavascriptLink('')

        mask = (self.data['date_end'] >= start_date) & (self.data['date_end'] <= end_date)
        df = self.data.loc[mask]

        conflicts_plot_data=self.dbscan_reduce(epsilon=self.eps_rad,start_date=start_date,
                                    end_date=end_date)

        hm = HeatMap(self.hm_coords,gradient={0.4: 'wheat', 0.65: 'peachpuff', 1: 'burlywood'})
        map_object.add_children(hm)

        if conflicts_plot_data is not None:
            for i in range(len(conflicts_plot_data['latitude'])):
                size_on_map = min(20 * conflicts_plot_data['clustered_deaths_all'][i],150000)
                marker = folium.features.CircleMarker(
                    [conflicts_plot_data['latitude'][i], conflicts_plot_data['longitude'][i]],
                    radius=size_on_map, color='#E82C0C', fill_color='#E82C0C',
                    popup=str(conflicts_plot_data['clustered_deaths_all'][i]) + ' killed')
                map_object.add_children(marker)

        folium.Map.save(map_object, "templates/"+self.prefix+"map.html")


    def dbscan_reduce(self, epsilon, x='latitude', y='longitude', start_date='',end_date=''):

        ''''
        This function need to run the function that processes the deaths csv first:
            df = deaths_df(datafile,columns=[],country_iso2='')

        Add inputs start and dates to filter initial df and the required radius filter (in radians). It will then
        cluster the points from the original dataframe in order to reduce the number of displayed points on the map.
        '''''

        start_time = time.time()

        # Create mask to locate rows between two input dates in initial dataframe (date filter)
        mask = (self.data['date_end'] >= start_date) & (self.data['date_end'] <= end_date)
        df = self.data.loc[mask]
        if df.empty:
            return None
        df = df.reset_index(drop=True)

        df['date_start'] = start_date
        df['date_end'] = end_date
        # represent points consistently as (lat, lon) and convert to radians to fit using haversine metric
        coords = df.as_matrix(columns=[y, x])
        db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree',
                    metric='haversine').fit(np.radians(coords))

        # Create labels corresponding to assigned cluster
        cluster_labels = db.labels_
        num_clusters = len(set(cluster_labels))
        print('Number of clusters: {:,}'.format(num_clusters))

        # Adding assigned labels to original dataframe and creating empty clustered deaths counts
        df['cluster_labels'] = cluster_labels
        df['clustered_deaths_all'] = 0
        df['clustered_deaths_military'] = 0
        df['clustered_deaths_civilians'] = 0
        df['clustered_deaths_unknown'] = 0

        # Creating pivot df to sum death count at each cluster
        temp_df = df.groupby(['cluster_labels']).sum()
        temp_df = temp_df.reset_index(level=['cluster_labels']).drop(
            ['latitude', 'longitude', 'clustered_deaths_all',
             'clustered_deaths_military', 'clustered_deaths_civilians',
             'clustered_deaths_unknown'], 1)

        # Matching the cluster labels between pivot df and filtered df to determine total death count at each cluster
        for n in range(num_clusters):
            for m in range(len(df.index)):

                if df['cluster_labels'][m] == temp_df['cluster_labels'][n]:
                    df['clustered_deaths_all'][m] = temp_df['deaths_a'][n] + \
                                                    temp_df['deaths_b'][n] + \
                                                    temp_df[
                                                        'deaths_civilians'][
                                                        n] + \
                                                    temp_df['deaths_unknown'][
                                                        n]
                    df['clustered_deaths_military'][m] = temp_df['deaths_a'][
                                                             n] + \
                                                         temp_df['deaths_b'][n]
                    df['clustered_deaths_civilians'][m] = \
                    temp_df['deaths_civilians'][n]
                    df['clustered_deaths_unknown'][m] = \
                    temp_df['deaths_unknown'][n]
                else:
                    pass

        clusters = pd.Series(
            [coords[cluster_labels == n] for n in range(num_clusters)])

        # find the point in each cluster that is closest to its centroid
        centermost_points = clusters.map(get_centermost_point)

        # unzip the list of centermost points (lat, lon) tuples into separate lat and lon lists
        lats, lons = zip(*centermost_points)
        rep_points = pd.DataFrame({x: lons, y: lats})

        rep_points.tail()

        # pull row from original data set where lat/lon match the lat/lon of each row of representative points
        rs = rep_points.apply(
            lambda row: df[(df[y] == row[y]) & (df[x] == row[x])].iloc[0],
            axis=1)

        # all done, print outcome
        message = 'Clustered {:,} points down to {:,} points, for {:.2f}% compression in {:,.2f} seconds.'
        print(message.format(len(df), len(rs),
                             100 * (1 - float(len(rs)) / len(df)),
                             time.time() - start_time))

        # Cleaning returned df
        rs = rs.drop(
            ['deaths_a', 'deaths_b', 'deaths_civilians', 'deaths_unknown',
             'cluster_labels'], 1)

        total_deaths=rs['clustered_deaths_all'].cumsum()

        return rs


class Development:
    def __init__(self,country='Afghanistan',path='/Users/Paul-Tristan/Documents/Columbia/Cours/Fall16/Data Analytics for OR/Project/Datasets/'):
        datafile = path+"WDI_Data.csv"
        if country == 'Afghanistan':
            self.country = "Afghanistan"
            self.prefix='afgha_'
            self.start_date = 1970
            self.end_date = 2015

        if country == 'Central African Republic':
            self.country = "Central African Republic"
            self.prefix='car_'
            self.start_date = 2010
            self.end_date = 2015

        dates = ['Country Name', 'Country Code', 'Indicator Code',
                 'Indicator Name']
        for i in range(self.start_date, self.end_date + 1):
            dates.append(i)
            dates = list(map(str, dates))

        indicator = ['SP.DYN.CDRT.IN', 'SN.ITK.DFCT', 'SP.DYN.LE00.IN',
                     'SE.ENR.PRIM.FM.ZS', 'SE.ENR.SECO.FM.ZS',
                     'SE.ENR.TERT.FM.ZS']

        data = pd.read_csv(datafile, sep=None, engine='python')
        data = data[data['Country Name'] == country][dates]

        all_indicators = []
        for i in data['Indicator Code']:
            all_indicators.append(i)

        for i in all_indicators:
            if i not in indicator:
                data = data[data['Indicator Code'] != i]

        self.df=data

    def update_death_rate(self):
        # Clearing the dataframe to extract 'Death Rate'
        df_death_rate_a = self.df[:1]
        df_death_rate_b = df_death_rate_a.T
        df_death_rate_c = df_death_rate_b[3:]
        df_death_rate_d = df_death_rate_c.T

        df_death_rate_e = df_death_rate_d.set_index('Indicator Name')
        df_death_rate_f = df_death_rate_e.T

        fig, ax = plt.subplots(figsize=(9,4))

        ax.plot(df_death_rate_f)
        ax.set_ylabel('Number of deaths per 1000 people')
        ax.set_xlabel('Year')
        ax.set_title('Death rate evolution')

        mpld3.save_html(fig, 'templates/'+self.prefix+'deathrate.html')

    def update_nutritional_deficit(self):
        df_calories_a = self.df[1:2]
        df_calories_b = df_calories_a.T
        df_calories_c = df_calories_b[3:]
        df_calories_d = df_calories_c.T
        df_calories_e = df_calories_d.set_index('Indicator Name')
        df_calories_f = df_calories_e.T

        fig, ax = plt.subplots(figsize=(9,4))

        ax.plot(df_calories_f)
        ax.set_ylabel('Nutritional deficit (in kilocalories)')
        ax.set_xlabel('Year')
        ax.set_title('Nutritional deficit evolution')

        mpld3.save_html(fig, 'templates/' + self.prefix + 'nutrition.html')

    def update_life_expectancy(self):
        df_life_expectancy_a = self.df[2:3]
        df_life_expectancy_b = df_life_expectancy_a.T
        df_life_expectancy_c = df_life_expectancy_b[3:]
        df_life_expectancy_d = df_life_expectancy_c.T
        df_life_expectancy_e = df_life_expectancy_d.set_index('Indicator Name')
        df_life_expectancy_f = df_life_expectancy_e.T

        fig, ax = plt.subplots(figsize=(9,4))

        ax.plot(df_life_expectancy_f)
        ax.set_ylabel('Life expectancy (in years)')
        ax.set_xlabel('Year')
        ax.set_title('Life expectancy evolution')

        mpld3.save_html(fig, 'templates/' + self.prefix + 'life_expectancy.html')

    def update_school_enrollment(self):
        df_primary_school_enrolment_a = self.df[3:4]
        df_primary_school_enrolment_b = df_primary_school_enrolment_a.T
        df_primary_school_enrolment_c = df_primary_school_enrolment_b[3:]
        df_primary_school_enrolment_d = df_primary_school_enrolment_c.T
        df_primary_school_enrolment_e = df_primary_school_enrolment_d.set_index(
            'Indicator Name')
        df_primary_school_enrolment_f = df_primary_school_enrolment_e.T

        df_secondary_school_enrolment_a = self.df[4:5]
        df_secondary_school_enrolment_b = df_secondary_school_enrolment_a.T
        df_secondary_school_enrolment_c = df_secondary_school_enrolment_b[3:]
        df_secondary_school_enrolment_d = df_secondary_school_enrolment_c.T
        df_secondary_school_enrolment_e = df_secondary_school_enrolment_d.set_index(
            'Indicator Name')
        df_secondary_school_enrolment_f = df_secondary_school_enrolment_e.T

        df_tertiary_school_enrolment_a = self.df[5:6]
        df_tertiary_school_enrolment_b = df_tertiary_school_enrolment_a.T
        df_tertiary_school_enrolment_c = df_tertiary_school_enrolment_b[3:]
        df_tertiary_school_enrolment_d = df_tertiary_school_enrolment_c.T
        df_tertiary_school_enrolment_e = df_tertiary_school_enrolment_d.set_index(
            'Indicator Name')
        df_tertiary_school_enrolment_f = df_tertiary_school_enrolment_e.T

        fig, ax = plt.subplots(figsize=(9,4))

        ax.plot(df_primary_school_enrolment_f, label='Primary school')
        ax.plot(df_secondary_school_enrolment_f, label='Secondary school')
        ax.plot(df_tertiary_school_enrolment_f, label='Tertiary school')
        ax.legend(loc='upper center')
        ax.set_ylabel('Proportion of children enrolled')
        ax.set_xlabel('Year')
        ax.set_title('School enrollment evolution')

        mpld3.save_html(fig,'templates/' + self.prefix + 'school_enrollment.html')

    def update_all(self):
        self.update_school_enrollment()
        self.update_death_rate()
        self.update_life_expectancy()
        self.update_nutritional_deficit()

class NYTimes:
    def __init__(self,cursordb,country):
        '''
        Create the sentiment analysis graph handler.

        :param cursordb: Cursor on the MySQL database
        :param country: 'CAR' or 'Afghanistan'
        '''
        self.cursordb=cursordb
        self.country = country
        if country == 'CAR':
            self.cursordb.execute("SELECT * FROM car")
            a = cursordb.fetchall()
            self.df = pd.DataFrame(list(a[i] for i in range(len(a))),
                              columns=['Date', 'Mentions', 'Negativity',
                                       'Positivity'])
            self.prefix='car_'

        if country == 'Afghanistan':
            self.cursordb.execute("SELECT * FROM afghanistan")
            a = self.cursordb.fetchall()
            self.df = pd.DataFrame(list(a[i] for i in range(len(a))),
                              columns=['Date', 'Mentions', 'Negativity',
                                       'Positivity'])
            self.prefix='afgha_'

        self.ticks=takespread(list(self.df["Date"]),10)

    def update_sentiment_plot(self):
        fig, ax = plt.subplots(figsize=(9, 4))

        # plt.xticks(range(len(df["Positivity"])),ticks,rotation=45)
        # plt.xticks(range(len(ticks)),ticks,rotation=45)
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.plot(self.df['Negativity'], color="red",label='Negativity')
        plt.plot(self.df['Positivity'], color="green",label='Positivity')
        plt.legend(loc='upper center')
        plt.locator_params(nbins=10)
        plt.title('Sentiment analysis of the articles')
        plt.ylabel('Strength of the feeling')

        mpld3.save_html(fig, 'templates/' + self.prefix + 'sentiment.html')

    def update_mentions_plot(self):
        fig, ax = plt.subplots(figsize=(9, 4))

        # plt.xticks(range(len(df["Positivity"])),ticks,rotation=45)
        # plt.xticks(range(len(ticks)),ticks,rotation=45)
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.plot(self.df['Mentions'])
        plt.locator_params(nbins=10)
        plt.title('Number of articles mentioning the conflict')
        plt.ylabel('Number of articles')

        mpld3.save_html(fig, 'templates/' + self.prefix + 'mentions.html')

    def update_all_plots(self):
        self.update_mentions_plot()
        self.update_sentiment_plot()

#UTILS

def get_centermost_point(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)

def takespread(sequence, num):
    length = float(len(sequence))
    for i in range(num):
        yield sequence[int(ceil(i * length / num))]


def refugees_df(datafile_refugees, datafile_geoloc, columns=[],country_name='', start_date=2001, end_date=2014):
    '''
    This function reads (and cleans) two CSV:
        - datafile_refugees: file that include yearly count of refugees in each region
        - datafile_geoloc: used to assign geocordinate to regions from original refugee file

    List of countries that can be filtered:
    Afghanistan; Central African Rep.

    List of columns:
    ['Year','Country','Location Name','F: Total','M: Total','Overall total']
    '''

    import pandas as pd
    import numpy as np

    data = pd.read_csv(datafile_refugees, usecols=columns)

    # Filtering data for required country only - creating new_dataframe
    clean_data = data[data['Country'] == country_name].reset_index(drop=True)

    # Create mask to locate rows between two input dates in initial dataframe (date filter)
    mask = (clean_data['Year'] >= start_date) & (
    clean_data['Year'] <= end_date)
    clean_data = clean_data.loc[mask].reset_index(drop=True)

    # Removing additional information on location
    clean_data = clean_data.replace(
        {' : Wllayat - Province': '', ': Wilayat - Province': '',
         ':Wllayet - Province': '', ' : Wolaswalei - District': '',
         ' : Prefecture': '', ' : Sous-pr̩fecture': '',
         ' : sous prefecture': '',
         ' : Sous-prefecture': '', ' : Economic prefecture': '',
         ' : Economic Prefecture': '', ' : Commune': '',
         ': Obo/Mboki': '', ': Pladama-Ouaka': '', '-': ' ', '  ': ' ',
         ' : Point': ''}, regex=True)

    clean_location = clean_data['Location Name'].str.strip().str.lower()
    clean_data['Location Name'] = clean_location

    # Correcting errors
    clean_data = clean_data.replace(
        {'momou': 'mbomou', 'sar e pol': 'sar e pul', 'sare pul': 'sar e pul',
         'sari pul': 'sar e pul', 'saripul': 'sar e pul',
         'hautte kotto': 'haute kotto',
         'zabul': 'kabul', 'nana  gribizi': 'nana grebizi',
         'urozgan': 'uruzgan',
         'nana gribizi': 'nana grebizi', 'nana griizi': 'nana grebizi',
         'nana  mambere': 'nana mambere',
         'haut mboumou': 'haut mbomou', 'jawzjan': 'jowzjan',
         'various': 'unknown',
         "ombella m'poko": "ombella mpoko", 'eleveurs': 'unknown',
         'pastoralists': 'unknown',
         'afghanistan : dispersed in the country / territory': 'unknown',
         'bamingui bangora': 'bamingui bangoran',
         'central african republic : dispersed in the country / territory': 'unknown',
         'bamingui bangorann': 'bamingui bangoran',
         'nomadic herders': 'unknown'}, regex=True)

    # Group by location name to get a net sum between two dates
    clean_data = clean_data.groupby(['Location Name']).sum()
    clean_data = clean_data.reset_index(level=['Location Name']).drop(['Year'],
                                                                      1)

    # Re-creating lost columns (note lose f and m split as include *)
    clean_data['Country'] = country_name
    clean_data['Start Date'] = start_date
    clean_data['End Date'] = end_date

    clean_data = clean_data.reindex(
        columns=['Start Date', 'End Date', 'Country', 'Location Name',
                 'Overall total', 'Latitude', 'Longitude'])

    # Cross referencing coordinates
    clean_data['Latitude'] = 0
    clean_data['Longitude'] = 0

    georef_cross = pd.read_csv(datafile_geoloc)

    for m in range(len(clean_data.index)):
        for n in range(len(georef_cross.index)):
            if clean_data['Location Name'][m] == georef_cross['Location Name'][
                n]:
                clean_data['Latitude'][m] = georef_cross['Latitude'][n]
                clean_data['Longitude'][m] = georef_cross['Longitude'][n]

    # Removing Nan rows
    clean_data = clean_data[clean_data['Location Name'] != 'baghi shirkat']
    clean_data = clean_data[clean_data['Location Name'] != 'sam ouandja']
    clean_data = clean_data[
        clean_data['Location Name'] != 'unknown'].reset_index(drop=True)

    # Creating n times point for each lat/long: n = number of refugees at any given location/x (adjust x!)
    pivot_list = []

    # Iterating through each row from clean data frame to create tupple with info from row
    for i in range(len(clean_data.index)):
        inter_tupple = [(
                        clean_data['Start Date'][i], clean_data['End Date'][i],
                        clean_data['Country'][i],
                        clean_data['Location Name'][i],
                        clean_data['Overall total'][i],
                        clean_data['Latitude'][i],
                        clean_data['Longitude'][i])]

        # creating second tupple that has n times first tupple (ADJUST n HERE!!)
        inter_tupple2 = inter_tupple * round(
            clean_data['Overall total'][i] / 100)

        # creating list that includes all the tupples generated (required to recreate dataframe)
        for j in range(len(inter_tupple2)):
            pivot_list.append(inter_tupple2[j])

    # Re creating dataframe with n points for each location
    final_df = pd.DataFrame(pivot_list,
                            columns=['Start Date', 'End Date', 'Country',
                                     'Location Name', 'Overall total',
                                     'Latitude', 'Longitude'])

    return final_df