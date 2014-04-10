from flask.ext.wtf import Form
from wtforms.fields import SelectField, StringField
from wtforms.validators import InputRequired, URL


class DatasetAddForm(Form):
    name = StringField('name', validators=[InputRequired()])
    url = StringField('url', validators=[InputRequired(), URL()])


class VisualizationAddForm(Form):
    name = StringField('name', validators=[InputRequired()])
    type = SelectField('type', choices=[('table', 'Table'), ('map', 'Map'), ('pie', 'Pie chart')])
