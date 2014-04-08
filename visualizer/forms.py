from flask.ext.wtf import Form
from wtforms.fields import StringField
from wtforms.validators import InputRequired, URL


class DatasetAddForm(Form):
    name = StringField('name', validators=[InputRequired()])
    url = StringField('url', validators=[InputRequired(), URL()])
