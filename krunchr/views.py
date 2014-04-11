import requests
import rethinkdb as r
from flask import flash, jsonify, redirect, render_template, url_for
from flask.ext.classy import FlaskView, route

from krunchr import db
from krunchr.forms import DatasetAddForm, VisualizationAddForm


class DatasetView(FlaskView):
    def index(self):
        datasets = list(r.table('datasets').order_by(r.desc('added_at')).run(db.conn))
        return render_template('datasets/index.html', datasets=datasets)

    def get(self, ds_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        visualizations = list(r.table('visualizations').filter(
            {'dataset_id': ds_id}).order_by(r.desc('added_at')).run(db.conn))
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
            print dataset;raise
            ds_id = dataset['new_val']['id']
            try:
                requests.get('%s%s' % (app.config['API_DATASET_ANALYSE'], ds_id))
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
        return render_template('datasets/get_visualization.html',
            dataset=dataset, visualization=visualization, data=[], canvas_data=[])

    @route('/<ds_id>/visualizations/add', methods=['GET', 'POST'])
    def post_visualization(self, ds_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        avlb_fields = [field['name'] for field in dataset['fields']]

        form = VisualizationAddForm()
        form.dataset = dataset
        form.fields.description = 'Available fields: %s' % ', '.join(avlb_fields)

        if form.validate_on_submit():
            fields = []
            for line in form.fields.data.splitlines():
                m = re.match(r'(\w+) is (\w+) of (.*)', line)
                fields.append({
                    'field': m.group(1),
                    'func': m.group(2),
                    'fields': m.group(3).split(', ')
                })
            r.table('visualizations').insert({
                'name': form.name.data,
                'type': form.type.data,
                'dataset_id': ds_id,
                'fields': fields,
                'added_at': r.now()}).run(db.conn)
            flash('Your visualization is being prepared, wait a while', 'success')
            return redirect(url_for('DatasetView:get', ds_id=ds_id))
        return render_template('datasets/post_visualization.html',
            form=form, dataset=dataset)
