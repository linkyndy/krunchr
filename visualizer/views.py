import rethinkdb as r
from flask import flash, redirect, render_template, url_for
from flask.ext.classy import FlaskView, route

from visualizer import db
from visualizer.forms import DatasetAddForm, VisualizationAddForm


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
            r.table('datasets').insert({
                'name': form.name.data,
                'url': form.url.data,
                'added_at': r.now()}).run(db.conn)
            flash('Your dataset is being analysed at the moment. Please wait while we finish to create your first visualization.', 'success')
            return redirect(url_for('DatasetView:index'))
        return render_template('datasets/post.html', form=form)

    @route('/<ds_id>/visualizations/<v_id>')
    def get_visualization(self, ds_id, v_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        visualization = r.table('visualizations').get(v_id).run(db.conn)
        return render_template('datasets/get_visualization.html',
            dataset=dataset, visualization=visualization)

    @route('/<ds_id>/visualizations/add', methods=['GET', 'POST'])
    def post_visualization(self, ds_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        form = VisualizationAddForm()
        if form.validate_on_submit():
            r.table('visualizations').insert({
                'name': form.name.data,
                'type': form.type.data,
                'dataset_id': ds_id,
            flash('Your visualization is being prepared, wait a while')
                'added_at': r.now()}).run(db.conn)
            return redirect(url_for('DatasetView:get', ds_id=ds_id))
        return render_template('datasets/post_visualization.html',
            form=form, dataset=dataset)
