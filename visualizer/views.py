import rethinkdb as r
from flask import redirect, render_template, url_for
from flask.ext.classy import FlaskView, route

from visualizer import db
from visualizer.forms import DatasetAddForm


class DatasetView(FlaskView):
    def index(self):
        datasets = list(r.table('datasets').run(db.conn))
        return render_template('datasets/index.html', datasets=datasets)

    def get(self, ds_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        return render_template('datasets/get.html', dataset=dataset)

    @route('/add', methods=['GET', 'POST'])
    def post(self):
        form = DatasetAddForm()
        if form.validate_on_submit():
            r.table('datasets').insert(
                {'name': form.name.data, 'url': form.url.data}).run(db.conn)
            return redirect(url_for('DatasetView:index'))
        return render_template('datasets/post.html', form=form)

    @route('/<ds_id>/visualizations')
    def visualizations(self, ds_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        visualizations = list(r.table('visualizations').filter(
            {'dataset_id': ds_id}).run(db.conn))
        return render_template('datasets/visualizations.html',
            dataset=dataset, visualizations=visualizations)

    @route('/<ds_id>/visualizations/<v_id>')
    def visualization(self, ds_id, v_id):
        dataset = r.table('datasets').get(ds_id).run(db.conn)
        visualization = r.table('visualizations').get(v_id).run(db.conn)
        return render_template('datasets/visualization.html',
            dataset=dataset, visualization=visualization)

    @route('/<ds_id>/visualizations/<v_id>', methods=['POST'])
    def post_visualization(self, ds_id, v_id):
        pass
