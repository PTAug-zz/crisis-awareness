from flask import Flask, session, render_template, url_for, request
#from flaskext.mysql import MySQL

from analysis import *
from customforms import *

app = Flask(__name__)



#### INITIAL LOAD ####
print('***** INITIAL DATA LOAD *****')

#print('Connection to MySQL')
#mysql = MySQL()
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = '------'
#app.config['MYSQL_DATABASE_DB'] = 'nytimesconflicts'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)
#conn = mysql.connect()
#cursor = conn.cursor()
#print('Connection to MySQL successful')

#print('Loading Afghanistan aid database...')
#aids_afgha = Aidplot()
#aids_afgha.aids_df(datafile='aiddata.csv', country_iso2='AF')

#print('Loading Central Africa aid database...')
#aids_car = Aidplot()
#aids_car.aids_df(datafile='aiddata.csv', country_iso2='CF')

#print('Loading Afghanistan map database...')
afgha_map=Mapplot(country='Afghanistan')

#print('Loading Central Africa map database...')
car_map=Mapplot(country='Central African Republic')

### UNCOMMENT THESE IF YOU WANT TO REPLOT ALL GRAPHS ###

#print('Loading Afghanistan development data...')
#afgha_dev=Development(country='Afghanistan')
#print('Trying to update all graphs')
#afgha_dev.update_all()

#print('Loading Central African Republic development data...')
#car_dev=Development(country='Central African Republic')
#print('Updating all CAR development graphs')
#car_dev.update_all()

#print('Loading Afghanistan NYTimes database...')
#afgha_nytimes=NYTimes(cursordb=cursor,country='Afghanistan')
#print('Updating Afghanistan NYTimes graphs...')
#afgha_nytimes.update_all_plots()

#print('Loading Central Africa NYTimes database...')
#car_nytimes=NYTimes(cursordb=cursor,country='CAR')
#print('Updating Central Africa NYTimes database...')
#car_nytimes.update_all_plots()

# print('Loading Afghanistan water data...')
# afgha_water=WaterGraphs(country='Afghanistan')
# print('Trying to update all graphs')
# afgha_water.update_all()

# print('Loading Afghanistan water data...')
# car_water=WaterGraphs(country='Central African Republic')
# print('Trying to update all graphs')
# car_water.update_all()

### END OF UNCOMMENT ###

print('***** END OF INITIAL DATA LOAD *****')
#### END INITIAL LOAD ####

app.secret_key = 'A0Zr98slkjdf984jnflskj_sdkfjhT'

def get_homepage_links():
    return [{"href": url_for('map'), "label": "Draw the Map"},
            {"href": url_for('analytics'), "label": "Analytics"}, ]

@app.route("/")
def home():
    session["data_loaded"] = True
    return render_template('home.html')


@app.route("/afghanistan", methods=['GET', 'POST'])
def afghanistan():
    formmap = AfghaMapFeatureForm()

    formmap.choiceswhat.data='value'

    #Get data
    dtfrom=formmap.datestart.data+'-01-01'
    dtto = formmap.dateend.data + '-12-31'


    if formmap.updatemap.data == True:
        afgha_map.render_map_country(start_date=dtfrom,end_date=dtto)

    if formmap.updatedonation.data==True:
        aids_afgha.aids_update_plot(formmap.country.data)

    return render_template('afghanistan.html', active='afgha', formmap=formmap,
                           mapfile='afgha_map.html',aidplot='afgha_aidplot.html',
                           deathrate='afgha_deathrate.html',
                           lifeexpectancy='afgha_life_expectancy.html',
                           nutrition='afgha_nutrition.html',
                           schoolenrollment='afgha_school_enrollment.html',
                           nyt_mentions='afgha_mentions.html',
                           nyt_sentiment = 'afgha_sentiment.html',
                           water='afgha_access_water.html',
                           sanitation='afgha_sanitation.html')


@app.route("/car", methods=['GET', 'POST'])
def car():
    formmap = CARMapFeatureForm()

    dtfrom=formmap.datestart.data+'-01-01'
    dtto = formmap.dateend.data + '-12-31'

    if formmap.updatemap.data == True:
        car_map.render_map_country(start_date=dtfrom,end_date=dtto)

    if formmap.updatedonation.data==True:
        aids_car.aids_update_plot(formmap.country.data)


    return render_template('car.html', active='afric',formmap=formmap,
                           mapfile='car_map.html',aidplot='car_aidplot.html',
                           deathrate='car_deathrate.html',
                           lifeexpectancy='car_life_expectancy.html',
                           nutrition='car_nutrition.html',
                           schoolenrollment='car_school_enrollment.html',
                           nyt_mentions='car_mentions.html',
                           nyt_sentiment='car_sentiment.html',
                           water='car_access_water.html',
                           sanitation='car_sanitation.html')

@app.route("/howtouse", methods=['GET', 'POST'])
def howtouse():
    return render_template('howtouse.html', active='howtouse')

@app.route("/aboutdata", methods=['GET', 'POST'])
def aboutdata():
    return render_template('aboutdata.html', active='aboutdata')

@app.route("/team", methods=['GET', 'POST'])
def team():
    return render_template('team.html', active='team')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
