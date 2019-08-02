import re
import warnings

import sqlalchemy.types

from wazimap.data.utils import get_datatable as actual_get_datatable


'''
DEPRECATED!

Legacy models for handling census data. These are deprecated and will be removed
in the next version of Wazimap. They only exist in stub form to aid with migrating
to the new, Django-based models using `manage.py upgradetables`.
'''


# Postgres has a max name length of 63 by default, reserving up to
# 13 chars for the _municipality ending
MAX_TABLE_NAME_LENGTH = 63 - 13

# Characters we strip from table names
TABLE_BAD_CHARS = re.compile('[ /-]')

# All SimpleTable and FieldTable instances by id
DATA_TABLES = {}

# Map from database table to SQLAlchemy model
DB_MODELS = {}


def get_datatable(name):
    return actual_get_datatable(name)


class SimpleTable(object):
    """ A Simple data table follows a normal spreadsheet format. Each row
    has one or more numeric values, one for each column. Each geography
    has only one row.

    A table can optionally have a total column, either named 'total' or
    controlled with the +total_column+ parameter. Without a total column,
    table values won't be shown as a percentage.

    In the web view, the total column is removed from the view and is not
    shown in the display.

    There is no way to have field combinations, such as 'Female, Age 18+'. For that,
    use a `FieldTable` below.
    """

    def __init__(self, id, universe, description, model='auto', total_column='total',
                 year='2011', dataset='Census 2011', stat_type='number', db_table=None):
        """
        Describe a new simple table.

        :param str id: table id, or None (default) to determine it based on `fields`
        :param str universe: a description of the universe this table covers (default: "Population")
        :param str description: a description of this table. If None, this is derived from
                                `universe` and the `fields`.
        :param str object model: the SQLAlchemy table model to use, or 'auto' to generate
                                 one (recommended).
        :param str total_column: the name of the column that represents the total value
                                 of all the columns in the row. This allows Wazimap to express
                                 column values as a percentage. If this is None, then
                                 the table doesn't have the concept of a total and only
                                 absolute values (not percentages) are used.
        :param str year: the year the table belongs to
        :param str dataset: the name of the dataset the table belongs to
        :param str stat_type: used to determine how the values should be displayed in the templates.
                              'number' or 'percentage'
        :param str db_table: name of an existing database table to use for this data table.
        """
        warnings.warn("SimpleTables are no longer used. Use `python manage.py upgradetables` to migrate.", DeprecationWarning)
        self.id = id.upper()
        self.db_table = db_table or self.id.lower()

        self.model = model
        self.universe = universe
        self.description = description
        self.year = year
        self.dataset_name = dataset
        self.total_column = total_column
        self.stat_type = stat_type

        DATA_TABLES[self.id] = self

    def setup_columns(self):
        """
        Work out our columns by finding those that aren't geo columns.
        """
        self.columns = OrderedDict()
        indent = 0
        if self.total_column:
            indent = 1

        for col in (c.name for c in self.model.__table__.columns if c.name not in ['geo_code', 'geo_level', 'geo_version']):
            self.columns[col] = {
                'name': capitalize(col.replace('_', ' ')),
                'indent': 0 if col == self.total_column else indent
            }

    def raw_data_for_geos(self, geos):
        # initial values
        data = {('%s-%s' % (geo.geo_level, geo.geo_code)): {
                'estimate': {},
                'error': {}}
                for geo in geos}

        session = get_session()
        try:
            geo_values = None
            rows = session\
                .query(self.model)\
                .filter(or_(and_(
                    self.model.geo_level == g.geo_level,
                    self.model.geo_code == g.geo_code,
                    self.model.geo_version == g.version)
                    for g in geos))\
                .all()

            for row in rows:
                geo_values = data['%s-%s' % (row.geo_level, row.geo_code)]

                for col in self.columns.keys():
                    geo_values['estimate'][col] = getattr(row, col)
                    geo_values['error'][col] = 0

        finally:
            session.close()

        return data

    def get_stat_data(self, geo, fields=None, key_order=None, percent=True, total=None, recode=None):
        """ Get a data dictionary for a place from this table.

        This fetches the values for each column in this table and returns a data
        dictionary for those values, with appropriate names and metadata.

        :param geo: the geography
        :param str or list fields: the columns to fetch stats for. By default, all columns except
                                   geo-related and the total column (if any) are used.
        :param str key_order: explicit ordering of (recoded) keys, or None for the default order.
                              Default order is the order in +fields+ if given, otherwise
                              it's the natural column order from the DB.
        :param bool percent: should we calculate percentages, or just include raw values?
        :param int total: the total value to use for percentages, name of a
                          field, or None to use the sum of all retrieved fields (default)
        :param dict recode: map from field names to strings to recode column names. Many fields
                            can be recoded to the same thing, their values will be summed.

        :return: (data-dictionary, total)
        """

        session = get_session()
        try:
            if fields is not None and not isinstance(fields, list):
                fields = [fields]
            if fields:
                for f in fields:
                    if f not in self.columns:
                        raise ValueError("Invalid field/column '%s' for table '%s'. Valid columns are: %s" % (
                            f, self.id, ', '.join(self.columns.keys())))
            else:
                fields = self.columns
                # if self.total_column:
                #     fields.pop(self.total_column)

            recode = recode or {}
            if recode:
                # change lambda to dicts
                if not isinstance(recode, dict):
                    recode = {f: recode(f) for f in fields}

            # is the total column valid?
            if isinstance(total, str) and total not in self.columns:
                raise ValueError("Total column '%s' isn't one of the columns for table '%s'. Valid columns are: %s" % (
                    total, self.id, ', '.join(self.columns.keys())))

            # table columns to fetch
            cols = [self.model.__table__.columns[c] for c in fields]

            if total is not None and isinstance(total, str) and total not in cols:
                cols.append(total)

            # do the query. If this returns no data, row is None
            row = session\
                .query(*cols)\
                .filter(self.model.geo_level == geo.geo_level,
                        self.model.geo_code == geo.geo_code,
                        self.model.geo_version == geo.version)\
                .first()

            if row is None:
                row = ZeroRow()

            # what's our denominator?
            if total is None:
                # sum of all columns
                total = sum(getattr(row, f) or 0 for f in fields)
            elif isinstance(total, str):
                total = getattr(row, total)

            # Now build a data dictionary based on the columns in +row+.
            # Multiple columns may be recoded into one, so we have to
            # accumulate values as we go.
            results = OrderedDict()

            key_order = key_order or fields  # default key order is just the list of fields

            for field in key_order:
                val = getattr(row, field) or 0

                # recode the key for this field, default is to keep it the same
                key = recode.get(field, field)

                # set the recoded field name, noting that the key may already
                # exist if another column recoded to it
                field_info = results.setdefault(key, {'name': recode.get(field, self.columns[field]['name'])})

                if percent:
                    # sum up existing values, if any
                    val = val + field_info.get('numerators', {}).get('this', 0)
                    field_info['values'] = {'this': p(val, total)}
                    field_info['numerators'] = {'this': val}
                else:
                    # sum up existing values, if any
                    val = val + field_info.get('values', {}).get('this', 0)
                    field_info['values'] = {'this': val}

            add_metadata(results, self)
            return results, total
        finally:
            session.close()

    def as_dict(self, columns=True):
        return {
            'title': self.description,
            'universe': self.universe,
            'denominator_column_id': self.total_column,
            'columns': self.columns,
            'table_id': self.id.upper(),
            'stat_type': self.stat_type,
        }

    def _build_model(self, db_table):
        # does it already exist?
        model = get_model_for_db_table(db_table)
        if model:
            return model

        columns = self._build_model_columns()

        class Model(Base):
            __table__ = Table(db_table, Base.metadata, *columns, autoload=True, extend_existing=True)

        return Model

    def _build_model_columns(self):
        # We build this array in a particular order, with the geo-related fields first,
        # to ensure that SQLAlchemy creates the underlying table with the compound primary
        # key columns in the correct order:
        #
        #  geo_level, geo_code, geo_version, field, [field, field, ...]
        #
        # This means postgresql will use the first two elements of the compound primary
        # key -- geo_level and geo_code -- when looking up values for a particular
        # geograhy. This saves us from having to create a secondary index.
        columns = []

        # will form a compound primary key on the fields, and the geo id
        columns.append(Column('geo_level', String(15), nullable=False, primary_key=True))
        columns.append(Column('geo_code', String(10), nullable=False, primary_key=True))
        columns.append(Column('geo_version', String(100), nullable=False, primary_key=True, server_default=''))

        return columns


FIELD_TABLE_FIELDS = set()
FIELD_TABLES = {}


class FieldTable(SimpleTable):
    """
    A field table is an 'inverted' simple table that has only one numeric figure
    per row, but allows multiple combinations of classifying fields for each row.

    It shares functionality with a `SimpleTable` but handles the more complex
    column definitions and raw data extraction.

    For example: ::

        geo_code  gender  age group   total
        ZA        female  < 18        100
        ZA        female  > 18        200
        ZA        male    < 18        80
        ZA        male    > 18        20

    What are called +columns+ here are actually an abstraction used by the
    data API. They are nested combinations of field values, such as: ::

        col0: total
        col1: female
        col2: female, < 18
        col3: female, > 18
        col4: male
        col5: male < 18
        col6: male > 18

    """
    def __init__(self, fields, id=None, universe='Population', description=None, denominator_key=None,
                 has_total=True, value_type='Integer', stat_type='number', db_table=None, **kwargs):
        """
        Describe a new field table.

        :param list fields: list of field names, in nesting order
        :param str id: table id, or None (default) to determine it based on `fields`
        :param str universe: a description of the universe this table covers (default: "Population")
        :param str description: a description of this table. If None, this is derived from
                                `universe` and the `fields`.
        :param str denominator_key: the key value of the rightmost field that should be
                                    used as the "total" column, instead of summing over
                                    the values for each row. This is necessary when the
                                    table doesn't describe a true partitioning of the
                                    dataset (ie. the row values sum to more than the
                                    total population).
                                    This will be used as the total column once
                                    the id of the column has been calculated.
        :param bool has_total: does it make sense to calculate a total column and express percentages
                                  for values in this table? (default: True)
        :param str value_type: the data type for the total column (default: 'Integer')
        :param str stat_type: used to determine how the values should be displayed in the templates.
                              'number' or 'percentage'
        :param str db_table: name of an existing database table to use for this data table.
                             Used when a model has two fields, e.g. `gender` and `population group`,
                             and we would like two data tables, with a different ordering of fields,
                             i.e. `population group` by `gender`, and `gender` by `population group`,
                             to use the same database table.
        """
        warnings.warn("FieldTables are no longer used. Use `python manage.py upgradetables` to migrate.", DeprecationWarning)
        description = description or (universe + ' by ' + ', '.join(fields))
        id = id or get_table_id(fields)

        self.fields = fields
        self.field_set = set(fields)
        self.denominator_key = denominator_key
        self.has_total = has_total
        self.value_type = getattr(sqlalchemy.types, value_type)

        super(FieldTable, self).__init__(
            id=id, model=None, universe=universe, description=description, stat_type=stat_type,
            db_table=db_table, **kwargs)

        FIELD_TABLE_FIELDS.update(self.fields)
        FIELD_TABLES[self.id] = self


def get_table_id(fields):
    sorted_fields = sorted(fields)
    table_id = TABLE_BAD_CHARS.sub('', '_'.join(sorted_fields))

    return table_id[:MAX_TABLE_NAME_LENGTH].upper()
