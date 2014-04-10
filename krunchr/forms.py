import re

from flask.ext.wtf import Form
from wtforms.fields import SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, URL, ValidationError

from krunchr.utils import FUNC_TYPES


class DatasetAddForm(Form):
    name = StringField('name', validators=[InputRequired()])
    url = StringField('url', validators=[InputRequired(), URL()])


class VisualizationAddForm(Form):
    name = StringField('name', validators=[InputRequired()])
    type = SelectField('type', choices=[('table', 'Table'), ('pie', 'Pie chart'), ('doughnut', 'Doughnut chart')])
    fields = TextAreaField('fields', validators=[InputRequired()])

    def validate_fields(self, field):
        field_types = {f['name']: f['type'] for f in self.dataset['fields']}

        for line in field.data.splitlines():
            m = re.match(r'(\w+) is (\w+) of (.*)', line)
            if not m:
                raise ValidationError('Fields declaration is invalid')

            new_field, func, fields = m.group(1), m.group(2), m.group(3).split(', ')
            if func not in FUNC_TYPES.keys():
                raise ValidationError('Function is not known')
            if not all([f in field_types.keys() for f in fields]):
                raise ValidationError('Fields specified in `of` clause must be fields on the dataset')
            if not all([field_types[f] in FUNC_TYPES[func] for f in fields]):
                raise ValidationError('Fields specified in `of` clause must be of same type as used function')

