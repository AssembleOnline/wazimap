# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-04-21 14:44
from __future__ import unicode_literals

from django.db import migrations


from sqlalchemy import inspect
from sqlalchemy.schema import AddConstraint
from wazimap.data.utils import get_session
from wazimap.data.tables import DATA_TABLES


def forwards(apps, schema_editor):
    """
    Ensure all data tables have the new geo_version column, with a default of ''
    """
    session = get_session()
    inspector = inspect(session.bind)

    try:
        for data_table in DATA_TABLES.values():
            db_model = data_table.model
            table = db_model.__table__

            cols = [c['name'] for c in inspector.get_columns(table.name)]
            if 'geo_version' in cols:
                continue

            # remove the old primary key constraint, if any
            pk = inspector.get_pk_constraint(table.name)['name']
            if pk:
                session.execute("ALTER TABLE %s DROP CONSTRAINT %s" % (table.name, pk))

            # add the new column
            session.execute("ALTER TABLE %s ADD COLUMN geo_version VARCHAR(100) DEFAULT ''" % table.name)

            # add the correct new constraint
            session.execute(AddConstraint(table.primary_key))

        session.commit()
    finally:
        session.close()


def reverse(apps, schema_editor):
    """
    Drop the new geo_version column from all data tables
    """
    session = get_session()
    inspector = inspect(session.bind)

    try:
        for data_table in DATA_TABLES.values():
            db_model = data_table.model
            table = db_model.__table__

            # remove the primary key constraint, if any
            pk = inspector.get_pk_constraint(table.name)['name']
            if pk:
                session.execute("ALTER TABLE %s DROP CONSTRAINT %s" % (table.name, pk))

            # drop the new column
            session.execute("ALTER TABLE %s DROP COLUMN geo_version" % table.name)

            # add the old pk constraint
            pk = table.primary_key
            pk.columns.remove(table.c.geo_version)
            session.execute(AddConstraint(pk))

        session.commit()
    finally:
        session.close()


class Migration(migrations.Migration):

    dependencies = [
        ('wazimap', '0006_geo-year-to-geo-version'),
    ]

    operations = [
        # We no longer need this migration in 2.x
        # Be sure to upgrade to 1.x before 2.x if you run into issues.
    ]
