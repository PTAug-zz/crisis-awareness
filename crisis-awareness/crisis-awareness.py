from flask import Flask, session, render_template,url_for,request
from flask_wtf import Form
from wtforms.fields.html5 import DateField
from wtforms import SelectField
from flaskext.mysql import MySQL

from datetime import date
import gmplot

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '------'
app.config['MYSQL_DATABASE_DB'] = 'flask'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

app.secret_key = 'A0Zr98slkjdf984jnflskj_sdkfjhT'

class MapParamsForm(Form):
  dtfrom = DateField('DatePicker', format='%Y-%m-%d', default=date(2016,1,1))
  dtto = DateField('DatePicker', format='%Y-%m-%d', default=date(2016,1,2))

class AnalyticsForm(Form):
    attributes = SelectField('Data Attributes', choices=[('Agency', 'Agency'), ('Borough', 'Borough'), ('Complaint_Type', 'Complaint Type')])


def get_homepage_links():
    return 	[{"href": url_for('map'), "label":"Draw the Map"},{"href": url_for('analytics'), "label":"Analytics"},]
def get_data(dtfrom,dtto):
    query = "select latitude, longitude from incidents where created_date >= '" + dtfrom + "' and created_date <= '" + dtto + "';"
    cursor.execute(query)
    return cursor.fetchall()

def get_df_data():
    import pandas
    query = "select unique_key, agency, complaint_type, borough from incidents;"
    cursor.execute(query)
    data = cursor.fetchall()
    df = pandas.DataFrame(data=list(data),columns=['Unique_key','Agency','Complaint Type','Borough'])
    return df

@app.route("/")
def home():
    session["data_loaded"] = True
    return render_template('home.html', links=get_homepage_links())

@app.route("/map", methods=['GET','POST'])
def map():
    form = MapParamsForm()
    if form.validate_on_submit():
        dtfrom =  form.dtfrom.data.strftime('%Y-%m-%d')
        dtto =  form.dtto.data.strftime('%Y-%m-%d')
        coordinates = get_data(dtfrom, dtto)
        latitudes, longitudes = ([],[])
        if (len(coordinates)>0):
            for pair in coordinates:
                latitudes.append(pair[0])
                longitudes.append(pair[1])
        gmap = gmplot.GoogleMapPlotter.from_geocode("New York",8)
        gmap.heatmap(latitudes, longitudes)
        gmap.draw('templates/mapoutput.html')
        return render_template('map.html', mapfile = 'mapoutput.html')

    return render_template('mapparams.html', form=form)

@app.route('/analytics/',methods=['GET','POST'])
def analytics():
    form = AnalyticsForm()
    if form.validate_on_submit():
        import pandas
        df = get_df_data()
        column = request.form.get('attributes')
        group = df.groupby(column)
        ax = group.size().plot(kind='bar')
        fig = ax.get_figure()
        fig.savefig('static/group_by_fig.png')
        return render_template('analyticsoutput.html')


    return render_template('analyticsparams.html', form=form)

if __name__ == '__main__':
   app.run(debug = True)