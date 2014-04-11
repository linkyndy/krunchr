import re

from flask.ext.wtf import Form
from wtforms.fields import SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, URL, ValidationError

from krunchr.utils import VISUALIZATION_TYPES, VISUALIZATION_FUNCS, FUNC_TYPES


class DatasetAddForm(Form):
    name = StringField('name', validators=[InputRequired()])
    url = StringField('url', validators=[InputRequired(), URL()])


class VisualizationAddForm(Form):
    name = StringField('Name', validators=[InputRequired()])
    type = SelectField('Type', choices=VISUALIZATION_TYPES.items())
    fields = TextAreaField('Fields', validators=[InputRequired()])

    def validate_fields(self, field):
        def _validate_table_fields():
            for line in field.data.splitlines():
                m = re.match(r'(\w+) is (\w+) of (.*)', line)
                if not m:
                    raise ValidationError('Fields declaration is invalid')

                new_field, func, fields = m.group(1), m.group(2), m.group(3).split(', ')
                if func not in VISUALIZATION_FUNCS[visualization_type]:
                    raise ValidationError('Function `%s` is not available to `%s` visualization type' % (func, visualization_type))
                if not all([f in ds_field_types.keys() for f in fields]):
                    raise ValidationError('Fields specified in `of` clause must be fields on the dataset')
                if not all([ds_field_types[f] in FUNC_TYPES[func] for f in fields]):
                    raise ValidationError('Fields specified in `of` clause must be of same type as used function')

        def _validate_pie_fields():
            for line in field.data.splitlines():
                m = re.match(r'(\w+) is (\w+) of (\w+) group by (\w+)', line)
                if not m:
                    raise ValidationError('Fields declaration is invalid')

                new_field, func, old_field, group_by_field = m.group(1), m.group(2), m.group(3), m.group(4)
                if func not in VISUALIZATION_FUNCS[visualization_type]:
                    raise ValidationError('Function `%s` is not available to `%s` visualization type' % (func, visualization_type))
                if not old_field in ds_field_types.keys():
                    raise ValidationError('Field specified in `of` clause must be field on the dataset')
                if not ds_field_types[old_field] in FUNC_TYPES[func]:
                    raise ValidationError('Field specified in `of` clause must be of same type as used function')
                if not group_by_field in ds_field_types.keys():
                    raise ValidationError('Field specified in `group by` clause must be field on the dataset')

        _validate_doughnut_fields = _validate_pie_fields

        # Dataset fields that are available
        ds_field_types = {f['name']: f['type'] for f in self.dataset['fields']}

        # Selected visualization type
        visualization_type = self.type.data

        if visualization_type == 'table':
            _validate_table_fields()
        elif visualization_type == 'pie':
            _validate_pie_fields()
        elif visualization_type == 'doughnut':
            _validate_doughnut_fields()
