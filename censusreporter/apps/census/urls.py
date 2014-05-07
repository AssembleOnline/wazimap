from django.conf.urls import url, patterns, include
from django.contrib import admin
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView

from .views import (HomepageView, GeographyDetailView, PlaceSearchJson,
    TableSearch, TableSearchJson, GeoSearch, LocateView, HealthcheckView,
    DataView, TopicView, ExampleView, Elasticsearch, WardSearchProxy)

admin.autodiscover()

STANDARD_CACHE_TIME = 60*15 # 15-minute cache
COMPARISON_FORMATS = 'map|table|distribution'

geo_levels = 'ward|municipality|province'


urlpatterns = patterns('',
    url(
        regex   = '^$',
        view    = cache_page(STANDARD_CACHE_TIME)(HomepageView.as_view()),
        kwargs  = {},
        name    = 'homepage',
    ),

    # e.g. /profiles/16000US5367000-spokane-wa/ (Spokane, WA)
    url(
        regex   = '^profiles/(?P<geography_id>[a-zA-Z0-9]+)-(?P<slug>[-\w]+)/$',
        view    = cache_page(STANDARD_CACHE_TIME)(GeographyDetailView.as_view()),
        kwargs  = {},
        name    = 'geography_detail',
    ),

    # e.g. /profiles/16000US5367000/ (Spokane, WA)
    # this should redirect to slugged version of the URL above
    url(
        regex   = '^profiles/(?P<geography_id>[a-zA-Z0-9]+)/$',
        view    = cache_page(STANDARD_CACHE_TIME)(GeographyDetailView.as_view()),
        kwargs  = {},
        name    = 'geography_detail_geoid',
    ),

    url(
        regex   = '^data/$',
        view    = cache_page(STANDARD_CACHE_TIME)(TemplateView.as_view(template_name="data/data_builder.html")),
        kwargs  = {},
        name    = 'data_builder',
    ),

    # e.g. /table/B01001/
    url(
        regex   = '^data/(?P<format>%s)/$' % COMPARISON_FORMATS,
        view    = cache_page(STANDARD_CACHE_TIME)(DataView.as_view()),
        kwargs  = {},
        name    = 'data_detail',
    ),

    url(
        regex   = '^topics/$',
        view    = cache_page(STANDARD_CACHE_TIME)(TopicView.as_view()),
        kwargs  = {},
        name    = 'topic_list',
    ),

    url(
        regex   = '^topics/(?P<topic_slug>[-\w]+)/$',
        view    = cache_page(STANDARD_CACHE_TIME)(TopicView.as_view()),
        kwargs  = {},
        name    = 'topic_detail',
    ),

    url(
        regex   = '^examples/(?P<example_slug>[-\w]+)/$',
        view    = cache_page(STANDARD_CACHE_TIME)(ExampleView.as_view()),
        kwargs  = {},
        name    = 'example_detail',
    ),

    url(
        regex   = '^glossary/$',
        view    = cache_page(STANDARD_CACHE_TIME)(TemplateView.as_view(template_name="glossary.html")),
        kwargs  = {},
        name    = 'glossary',
    ),

    url(
        regex   = '^locate/$',
        view    = LocateView.as_view(),
        kwargs  = {},
        name    = 'locate',
    ),

    url(
        regex   = '^healthcheck$',
        view    = HealthcheckView.as_view(),
        kwargs  = {},
        name    = 'healthcheck',
    ),

    url(
        regex   = '^place-search/json/$',
        view    = PlaceSearchJson.as_view(),
        kwargs  = {},
        name    = 'place_search_json',
    ),

    url(
        regex   = '^ward-search/json/$',
        view    = WardSearchProxy.as_view(),
        kwargs  = {},
        name    = 'ward_search_json',
    ),

    ## LOCAL DEV VERSION OF API ##

    url(
        regex   = '^table-search/$',
        view    = TableSearch.as_view(),
        kwargs  = {},
        name    = 'table_search',
    ),
    url(
        regex   = '^table-search/json/$',
        view    = TableSearchJson.as_view(),
        kwargs  = {},
        name    = 'table_search_json',
    ),

    url(
        regex   = '^geo-search/$',
        view    = GeoSearch.as_view(),
        kwargs  = {},
        name    = 'geo_search',
    ),

    url(
        regex   = '^profiles/(?P<geography_id>(%s)-[\w]+)/$' % geo_levels,
        view    = GeographyDetailView.as_view(),
        kwargs  = {},
        name    = 'elasticsearch',
    ),
    ## END LOCAL DEV VERSION OF API ##
)
