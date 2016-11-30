from flask_wtf import Form
from wtforms.fields.html5 import DateField,IntegerField
from wtforms import SelectField, RadioField, BooleanField,validators
from datetime import date

class AfghaMapFeatureForm(Form):
    countries=[('World Bank - International Development Association (IDA)',
      'World Bank - International Development Association (IDA)'),
     ('Kuwait', 'Kuwait'),
     ('Italy', 'Italy'),
     ('Germany', 'Germany'),
     ('European Communities (EC)', 'European Communities (EC)'),
     ('Switzerland', 'Switzerland'),
     ('Netherlands', 'Netherlands'),
     ('Arab Fund for Economic & Social Development (AFESD)',
      'Arab Fund for Economic & Social Development (AFESD)'),
     ('United Arab Emirates', 'United Arab Emirates'),
     ('United States', 'United States'),
     (
     'World Bank - International Bank for Reconstruction and Development (IBRD)',
     'World Bank - International Bank for Reconstruction and Development (IBRD)'),
     ('Japan', 'Japan'),
     ('France', 'France'),
     ('Saudi Arabia', 'Saudi Arabia'),
     ('Islamic Development Bank (ISDB)', 'Islamic Development Bank (ISDB)'),
     ('OPEC Fund for International Development (OFID)',
      'OPEC Fund for International Development (OFID)'),
     ('Belgium', 'Belgium'),
     ('United Kingdom', 'United Kingdom'),
     ('International Fund for Agricultural Development (IFAD)',
      'International Fund for Agricultural Development (IFAD)'),
     ('Canada', 'Canada'),
     ('Austria', 'Austria'),
     ('Finland', 'Finland'),
     ('Norway', 'Norway'),
     ('Spain', 'Spain'),
     ('Sweden', 'Sweden'),
     (
     'Global Environment Facility (GEF)', 'Global Environment Facility (GEF)'),
     ('United Nations Development Programme (UNDP)',
      'United Nations Development Programme (UNDP)'),
     ('United Nations Children`s Fund (UNICEF)',
      'United Nations Children`s Fund (UNICEF)'),
     ('World Bank - International Finance Corporation (IFC)',
      'World Bank - International Finance Corporation (IFC)'),
     ('United Nations Population Fund (UNFPA)',
      'United Nations Population Fund (UNFPA)'),
     ('Joint United Nations Programme on HIV/AIDS (UNAIDS)',
      'Joint United Nations Programme on HIV/AIDS (UNAIDS)'),
     ('Greece', 'Greece'),
     ('New Zealand', 'New Zealand'),
     ('Ireland', 'Ireland'),
     ('World Bank - Managed Trust Funds', 'World Bank - Managed Trust Funds'),
     ('Cyprus', 'Cyprus'),
     ('Korea', 'Korea'),
     ('World Trade Organization (WTO)', 'World Trade Organization (WTO)'),
     ('Denmark', 'Denmark'),
     ('Global Fund to Fight Aids, Tuberculosis and Malaria (GFATM)',
      'Global Fund to Fight Aids, Tuberculosis and Malaria (GFATM)'),
     ('Australia', 'Australia'),
     ('India', 'India'),
     (
     'United Nations Relief and Works Agency for Palestine Refugees in the Near East (UNRWA)',
     'United Nations Relief and Works Agency for Palestine Refugees in the Near East (UNRWA)'),
     ('World Health Organization (WHO)', 'World Health Organization (WHO)'),
     ('Portugal', 'Portugal'),
     ('Iceland', 'Iceland'),
     ('Luxembourg', 'Luxembourg'),
     ('Czech Republic', 'Czech Republic'),
     ('United Nations High Commissioner for Refugees (UNHCR)',
      'United Nations High Commissioner for Refugees (UNHCR)'),
     ('Slovenia', 'Slovenia'),
     ('Slovak Republic', 'Slovak Republic'),
     ('Poland', 'Poland'),
     ('Estonia', 'Estonia'),
     ('Bill & Melinda Gates Foundation', 'Bill & Melinda Gates Foundation')]

    years=(1988,2016)

    choice_years=[(str(i),str(i)) for i in range(years[0],years[1])]
    choiceswhat = RadioField('lol', choices=[('value', 'description'),
                                             ('value_two', 'whatever')])
    camp = RadioField('Camp', choices=[('rebels', 'The Rebels'),('empire', 'The Empire'),('ewoks', 'The Ewoks')],default='empire')
    conflicts = BooleanField('Conflicts')
    schools = BooleanField('Schools')
    displacements = BooleanField('Displacements')
    updatemap = BooleanField('Update map')
    updatedonation = BooleanField('Update donation plot')
    selectfields = [conflicts, schools, displacements]
    #self.dtfrom = DateField('Start date', format='%Y-%m-%d',default=date(2016, 1, 1))
    #self.dtto = DateField('End date', format='%Y-%m-%d', default=date(2016, 1, 2))
    #self.datestart = IntegerField('Number of points',default=10,validators=[validators.NumberRange(min=1970, max=2014)])
    datestart = SelectField('Number of points', choices=choice_years,default=1988)
    dateend = SelectField('Number of points',choices=choice_years,default=1993)
    country = SelectField('Country of donation',choices=countries,default=countries[0][0])

class CARMapFeatureForm(Form):
    countries=[('World Bank - International Development Association (IDA)',
      'World Bank - International Development Association (IDA)'),
     ('Kuwait', 'Kuwait'),
     ('Italy', 'Italy'),
     ('Germany', 'Germany'),
     ('European Communities (EC)', 'European Communities (EC)'),
     ('Switzerland', 'Switzerland'),
     ('Netherlands', 'Netherlands'),
     ('Arab Fund for Economic & Social Development (AFESD)',
      'Arab Fund for Economic & Social Development (AFESD)'),
     ('United Arab Emirates', 'United Arab Emirates'),
     ('United States', 'United States'),
     (
     'World Bank - International Bank for Reconstruction and Development (IBRD)',
     'World Bank - International Bank for Reconstruction and Development (IBRD)'),
     ('Japan', 'Japan'),
     ('France', 'France'),
     ('Saudi Arabia', 'Saudi Arabia'),
     ('Islamic Development Bank (ISDB)', 'Islamic Development Bank (ISDB)'),
     ('OPEC Fund for International Development (OFID)',
      'OPEC Fund for International Development (OFID)'),
     ('Belgium', 'Belgium'),
     ('United Kingdom', 'United Kingdom'),
     ('International Fund for Agricultural Development (IFAD)',
      'International Fund for Agricultural Development (IFAD)'),
     ('Canada', 'Canada'),
     ('Austria', 'Austria'),
     ('Finland', 'Finland'),
     ('Norway', 'Norway'),
     ('Spain', 'Spain'),
     ('Sweden', 'Sweden'),
     (
     'Global Environment Facility (GEF)', 'Global Environment Facility (GEF)'),
     ('United Nations Development Programme (UNDP)',
      'United Nations Development Programme (UNDP)'),
     ('United Nations Children`s Fund (UNICEF)',
      'United Nations Children`s Fund (UNICEF)'),
     ('World Bank - International Finance Corporation (IFC)',
      'World Bank - International Finance Corporation (IFC)'),
     ('United Nations Population Fund (UNFPA)',
      'United Nations Population Fund (UNFPA)'),
     ('Joint United Nations Programme on HIV/AIDS (UNAIDS)',
      'Joint United Nations Programme on HIV/AIDS (UNAIDS)'),
     ('Greece', 'Greece'),
     ('New Zealand', 'New Zealand'),
     ('Ireland', 'Ireland'),
     ('World Bank - Managed Trust Funds', 'World Bank - Managed Trust Funds'),
     ('Cyprus', 'Cyprus'),
     ('Korea', 'Korea'),
     ('World Trade Organization (WTO)', 'World Trade Organization (WTO)'),
     ('Denmark', 'Denmark'),
     ('Global Fund to Fight Aids, Tuberculosis and Malaria (GFATM)',
      'Global Fund to Fight Aids, Tuberculosis and Malaria (GFATM)'),
     ('Australia', 'Australia'),
     ('India', 'India'),
     (
     'United Nations Relief and Works Agency for Palestine Refugees in the Near East (UNRWA)',
     'United Nations Relief and Works Agency for Palestine Refugees in the Near East (UNRWA)'),
     ('World Health Organization (WHO)', 'World Health Organization (WHO)'),
     ('Portugal', 'Portugal'),
     ('Iceland', 'Iceland'),
     ('Luxembourg', 'Luxembourg'),
     ('Czech Republic', 'Czech Republic'),
     ('United Nations High Commissioner for Refugees (UNHCR)',
      'United Nations High Commissioner for Refugees (UNHCR)'),
     ('Slovenia', 'Slovenia'),
     ('Slovak Republic', 'Slovak Republic'),
     ('Poland', 'Poland'),
     ('Estonia', 'Estonia'),
     ('Bill & Melinda Gates Foundation', 'Bill & Melinda Gates Foundation')]

    years=(2012,2016)

    choice_years=[(str(i),str(i)) for i in range(years[0],years[1])]
    choiceswhat = RadioField('lol', choices=[('value', 'description'),
                                             ('value_two', 'whatever')])
    camp = RadioField('Camp', choices=[('rebels', 'The Rebels'),('empire', 'The Empire'),('ewoks', 'The Ewoks')],default='empire')
    conflicts = BooleanField('Conflicts')
    schools = BooleanField('Schools')
    displacements = BooleanField('Displacements')
    updatemap = BooleanField('Update map')
    updatedonation = BooleanField('Update donation plot')
    selectfields = [conflicts, schools, displacements]
    #self.dtfrom = DateField('Start date', format='%Y-%m-%d',default=date(2016, 1, 1))
    #self.dtto = DateField('End date', format='%Y-%m-%d', default=date(2016, 1, 2))
    #self.datestart = IntegerField('Number of points',default=10,validators=[validators.NumberRange(min=1970, max=2014)])
    datestart = SelectField('Number of points', choices=choice_years,default=2012)
    dateend = SelectField('Number of points',choices=choice_years,default=2014)
    country = SelectField('Country of donation',choices=countries,default=countries[0][0])

class AnalyticsForm(Form):
    attributes = SelectField('Data Attributes', choices=[('Agency', 'Agency'),
                                                         (
                                                         'Borough', 'Borough'),
                                                         ('Complaint_Type',
                                                          'Complaint Type')])
