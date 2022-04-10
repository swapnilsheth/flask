##https://towardsdatascience.com/complete-beginners-guide-to-processing-whatsapp-data-with-python-781c156b5f0b
import os
import datetime
import pandas as pd
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import ColumnDataSource, Plot, LabelSet
from bokeh.models.tools import HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral5
from bokeh.layouts import row, column


class chat_processing:

    def read_file(file):
        '''Reads Whatsapp text file into a list of strings'''
        os.chdir('C:/Users/swapnilsheth/flask/uploads')
        x = open(file,'r', encoding = 'utf-8') #Opens the text file into variable x but the variable cannot be explored yet
        y = x.read() #By now it becomes a huge chunk of string that we need to separate line by line
        content = y.splitlines() #The splitline method converts the chunk of string into a list of strings
        return content


    def text_clean(chat):

        for i in range(len(chat)):
            try:
                datetime.datetime.strptime(chat[i].split(',')[0], '%m/%d/%y') #Converts string date into a date object
            except ValueError: #Returns an error if the string is not a datetime object
                chat[i-1] = chat[i-1] + ' ' + chat[i] #Appends the next line to the previous line
                chat[i] = "NA" #Replace the unwanted text element with 'NA'

    #Handle more than double-line texting
        for i in range(len(chat)):
            if chat[i].split(' ')[0] == 'NA':
                chat[i] = 'NA'

        while True:
            try:
                chat.remove("NA")
            except ValueError:
                break
        return chat

    def convert_to_df(chat):
    ##continuation of cleaning up of data from previous section
    ## Get time
        date = [chat[i].split(',')[0] for i in range(len(chat))]
    ## Get time
        time = [chat[i].split(',')[1].split('-')[0] for i in range(len(chat))]
        time = [s.strip(' ') for s in time] # Remove spacing

        ## Get name
        name = [chat[i].split('- ')[1].split(':')[0] for i in range(len(chat))]

    ## Get content
        content = []
        for i in range(len(chat)):
            try:
                content.append(chat[i].split(':')[2])
            except IndexError:
                content.append('Missing Text')

        df = pd.DataFrame(list(zip(date, time, name, content)), columns = ['Date', 'Time', 'Name', 'Content'])
        df['Date'] = pd.to_datetime(df['Date'])##convert Date column to Date object to enable filtering later on
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        return df

    def df_enhance(dataframe):

        df = dataframe
        ##add a new column for birth date and month
        df['Month'] = pd.DatetimeIndex(df['Date']).month
        df['Day'] = pd.DatetimeIndex(df['Date']).day
        df['Year'] = pd.DatetimeIndex(df['Date']).year
        df['Hour'] = pd.DatetimeIndex(df['Time']).hour
        #df['MM-DD'] = df['month'].astype(str)+'/'+df['day'].astype(str)+'/'+df['year'].astype(str)
        #df['MM-DD'] = pd.to_datetime(df['MM-DD'])
        df['MM-DD'] = df['Date'].dt.to_period('M').dt.to_timestamp()

        return df

    def visualizations(dataframe):
        #visualizations
        df = dataframe
        df_temp = df.groupby('Name')[['Date']].count()
        df_temp.sort_values(by='Date', inplace=True, ascending=False)
        df_temp.reset_index(inplace=True)
        df_name = df_temp[df_temp['Date'] > 10]
        #df_name['Name'] = df_name['Name'].astype(str)
        ##Visualization #1 Vertical Bar Count by Name
        source1 = ColumnDataSource(df_name)
        names1 = source1.data['Name'].tolist()

        p1 = figure(x_range=names1, plot_width=1000, plot_height=500, sizing_mode='scale_width')
        p1.xaxis.major_label_orientation = "vertical"
        labels1 = LabelSet(x='Name', y='Date', text='Date', level='glyph',
                x_offset=-13.5, y_offset=0, source=source1, render_mode='canvas')
        p1.vbar(x='Name', top='Date', source=source1, width=0.7, color='red')
        p1.title.text ='Total Messages by Family Member'
        p1.xaxis.axis_label = 'Name'
        p1.yaxis.axis_label = 'Count of Messages'
        #p1.add_layout(labels1)

        ##Visualization #2 Line Chart Count by Month and Year
        df_moyr = df.groupby('MM-DD')[['Date']].count()
        df_moyr.sort_values(by='MM-DD', inplace=True, ascending=True)
        df_moyr.reset_index(inplace=True)
        df_moyr['MM-DD'] = df_moyr['MM-DD'].astype(str)
        source2 = ColumnDataSource(df_moyr)
        name2 = source2.data['MM-DD'].tolist()
        p2 = figure(x_range=name2, plot_width=750, plot_height=300, sizing_mode='scale_width')
        p2.xaxis.major_label_orientation = "vertical"
        labels2 = LabelSet(x='MM-DD', y='Date', text='Date',x_offset=5, y_offset=5,source=source2, render_mode='canvas')
        p2.line(x='MM-DD', y='Date', source=source2, line_width = 2, color='red')
        p2.circle(x='MM-DD', y='Date', source=source2, fill_color="orange", line_color='orange', size=8)
        p2.title.text ='Total Messages by Month'
        p2.xaxis.axis_label = 'Month-Year'
        p2.yaxis.axis_label = 'Count of Messages'
        #p2.add_layout(labels2)

        ##Visualization #3: Line Chart by Hour
        df_hour = df.groupby('Hour')[['Date']].count()
        df_hour.sort_values(by='Hour', inplace=True, ascending=True)
        df_hour.reset_index(inplace=True)
        df_hour['Hour'] = df_hour['Hour'].astype(str)
        source3=ColumnDataSource(df_hour)
        name3=source3.data['Hour'].tolist()
        p3 = figure(x_range=name3, plot_width=750, plot_height=300, sizing_mode='scale_width')
        p3.xaxis.major_label_orientation = "vertical"
        p3.line(x='Hour', y='Date', source=source3, line_width = 2, color='red')
        p3.circle(x='Hour', y='Date', source=source3, fill_color="orange", line_color='orange', size=8)
        p3.title.text ='Total Messages by Hour'
        p3.xaxis.axis_label = 'Hour'
        p3.yaxis.axis_label = 'Count of Messages'


        ##Active Users per Month
        df_user = df.groupby('MM-DD')['Name'].agg(['nunique'])
        df_user.sort_values(by='MM-DD', inplace=True, ascending=True)
        df_user.reset_index(inplace=True)
        df_user['MM-DD'] = df_user['MM-DD'].astype(str)
        source4 = ColumnDataSource(df_user)
        names4 = source4.data['MM-DD'].tolist()
        p4 = figure(x_range=names4, plot_width=750, plot_height=300, sizing_mode='scale_width')
        p4.xaxis.major_label_orientation = "vertical"
        labels4 = LabelSet(x='MM-DD', y='nunique', text='nunique', level='glyph',
                x_offset=-13.5, y_offset=0, source=source4, render_mode='canvas')
        p4.vbar(x='MM-DD', top='nunique', source=source4, width=0.7, color='red')
        p4.title.text ='Users per Month'
        p4.xaxis.axis_label = 'Month-Year'
        p4.yaxis.axis_label = 'Count of Users'
        #p4.add_layout(labels4)

        ##Message per User per Month
        df_peruser = df_moyr
        df_peruser['MessagePerMonth'] = df_moyr['Date']/df_user['nunique']
        df_peruser.sort_values(by='MM-DD', inplace=True, ascending=True)
        df_peruser.reset_index(inplace=True)
        df_peruser['MM-DD'] = df_peruser['MM-DD'].astype(str)
        df_peruser['MessagePerMonth']=df_peruser['MessagePerMonth'].round(1)
        source5 = ColumnDataSource(df_peruser)
        names5 = source5.data['MM-DD'].tolist()
        p5 = figure(x_range=names5, plot_width=750, plot_height=300, sizing_mode='scale_width')
        p5.xaxis.major_label_orientation = "vertical"
        labels5 = LabelSet(x='MM-DD', y='MessagePerMonth', text='MessagePerMonth', level='glyph',
                x_offset=-13.5, y_offset=0, source=source5, render_mode='canvas')
        p5.vbar(x='MM-DD', top='MessagePerMonth', source=source5, width=0.7, color='red')
        p5.title.text ='Messages per User per Month'
        p5.xaxis.axis_label = 'Month-Year'
        p5.yaxis.axis_label = 'Messages per User'
        #p5.add_layout(labels5)

        #show(column(p1,p2,p3,p4,p5))
        lst=[p1,p2,p3,p4,p5]
        x=1
        for i in lst:
            output_file("c:/users/swapnilsheth/flask/results/chart_{}.html".format(x))
            save(i)
            x=x+1
        #save(column(p1,p2,p3,p4,p5))
        return
