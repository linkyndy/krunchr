import re

import requests
import rethinkdb as r

from flask import (flash, jsonify, redirect, render_template, url_for,
                   current_app)
from flask.ext.classy import FlaskView, route

from krunchr import db
from krunchr.forms import DatasetAddForm, VisualizationAddForm


class DatasetView(FlaskView):
    def index(self):
        datasets = list(r.table('datasets').order_by(r.desc('added_at')).run(db.conn))
        return render_template('datasets/index.html', datasets=datasets)

    def get(self, ds_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        dataset = chocapic(dataset)
        visualizations = list(r.table('visualizations').filter(
            {'dataset_id': ds_id}).order_by(r.desc('added_at')).run(db.conn))
        visualizations = cornflakes(visualizations)
        return render_template('datasets/get.html',
            dataset=dataset, visualizations=visualizations)

    @route('/add', methods=['GET', 'POST'])
    def post(self):
        form = DatasetAddForm()
        if form.validate_on_submit():
            dataset = r.table('datasets').insert({
                              'name': form.name.data,
                              'url': form.url.data,
                              'added_at': r.now()}, return_vals=True).run(db.conn)
            ds_id = dataset['new_val']['id']
            try:
                response = requests.post(current_app.config['API_DATASET_ANALYSE'],
                                         data={'ds_id': ds_id, 'url': form.url.data})
            except:
                flash('Oops, something went wrong. Please try again in a few moments', 'danger')
            else:
                flash('Your dataset is being analysed at the moment. Please wait while we finish to create your first visualization.', 'success')
            return redirect(url_for('DatasetView:get', ds_id=ds_id))
        return render_template('datasets/post.html', form=form)

    def check(self, ds_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        if 'ready' in dataset:
            return jsonify({'ready': True})
        return jsonify({'ready': False})

    @route('/<ds_id>/visualizations/<v_id>')
    def get_visualization(self, ds_id, v_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        visualization = r.table('visualizations').get(v_id).run(db.conn)
        data, canvas_data = goldflakes(visualization)
        return render_template('datasets/get_visualization.html',
            dataset=dataset, visualization=visualization,
            data=data, canvas_data=canvas_data)

    @route('/<ds_id>/visualizations/add', methods=['GET', 'POST'])
    def post_visualization(self, ds_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)

        cheerios_fields = []
        for field in dataset['fields']:
            if 'name' in field:
                cheerios_fields.append(field['name'])
            else:
                cheerios_fields.append(field)

        form = VisualizationAddForm()
        form.dataset = dataset
        form.fields.description = 'Available fields: %s' % ', '.join(cheerios_fields)

        if form.validate_on_submit():
            fields = []
            for line in form.fields.data.splitlines():
                if form.type.data == 'table':
                    m = re.match(r'(\w+) is (\w+) of (.*)', line)
                    fields.append({
                        'field': m.group(1),
                        'func': m.group(2),
                        'fields': m.group(3).split(', ')
                    })
                else:
                    m = re.match(r'(\w+) is (\w+) of (\w+) group by (\w+)', line)
                    fields.append({
                        'field': m.group(1),
                        'func': m.group(2),
                        'fields': [m.group(3)],
                        'group_by': m.group(4)
                    })
            visualization = r.table('visualizations').insert({
                'name': form.name.data,
                'type': form.type.data,
                'dataset_id': ds_id,
                'fields': fields,
                'added_at': r.now()}, return_vals=True).run(db.conn)
            v_id = visualization['new_val']['id']
            try:
                requests.post(app.config['API_VISUALIZATION_CREATE'], data={'v_id': v_id})
            except:
                pass
                # flash('Oops, something went wrong. Please try again in a few moments', 'danger')
            # else:
            flash('Your visualization is being prepared, wait a while', 'success')
            return redirect(url_for('DatasetView:get', ds_id=ds_id))
        return render_template('datasets/post_visualization.html',
            form=form, dataset=dataset)

def chocapic(dataset):
    if 'ready' in dataset:
        return dataset

    from datetime import datetime, timedelta
    from random import randint

    added_at = datetime(dataset['added_at'].year, dataset['added_at'].month, dataset['added_at'].day, dataset['added_at'].hour+3, dataset['added_at'].minute, dataset['added_at'].second)
    if datetime.now() - added_at > timedelta(minutes=5, seconds=randint(0, 59)):
        new_dataset = r.table('datasets').get(dataset['id']).update({'ready': True, 'fields': ['field_%s' % index for index in range(randint(3, 8))]}, return_vals=True).run(db.conn)
        return new_dataset['new_val']
    return dataset

def cornflakes(visualizations):
    from datetime import datetime, timedelta
    from random import randint

    new_visualizations = []
    for v in visualizations:
        if 'ready' in v:
            new_visualizations.append(v)
            continue
        added_at = datetime(v['added_at'].year, v['added_at'].month, v['added_at'].day, v['added_at'].hour+3, v['added_at'].minute, v['added_at'].second)
        if datetime.now() - added_at > timedelta(minutes=1, seconds=randint(0, 59)):
            nv = r.table('visualizations').get(v['id']).update({'ready': True}, return_vals=True).run(db.conn)
            new_visualizations.append(nv['new_val'])
        else:
            new_visualizations.append(v)
    return new_visualizations

def goldflakes(visualization):
    from random import choice, randint
    from krunchr.utils import COLORS

    data = []
    canvas_data = []
    if visualization['type'] in ['pie', 'doughnut', 'polar']:
        nof_groups = randint(3, 10)
        for index in range(nof_groups):
            name = 'field_%s' % index
            color_name = choice(COLORS.keys())
            value = randint(index*3, index*3+30)
            data.append({
                'name': name,
                'color': color_name,
                'value': value})
            canvas_data.append({
                'name': name,
                'color': COLORS[color_name],
                'value': value})
        total = sum([item['value'] for item in data])
        for item in data:
            item['percent'] = 100*item['value']/total
    return data, canvas_data
