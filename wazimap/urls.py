from django.conf import settings

# from django.contrib import admin
from django.urls import reverse_lazy, path, re_path
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.views.generic.base import RedirectView, TemplateView

from census.views import HealthcheckView, DataView, ExampleView

from wazimap.views import (
    HomepageView,
    GeographyDetailView,
    GeographyJsonView,
    PlaceSearchJson,
    LocateView,
    DataAPIView,
    TableAPIView,
    AboutView,
    HelpView,
    GeographyCompareView,
    GeoAPIView,
    TableDetailView,
)


# admin.autodiscover()
handler500 = "census.views.server_error"

STANDARD_CACHE_TIME = settings.WAZIMAP["cache_secs"]
EMBED_CACHE_TIME = settings.WAZIMAP.get("embed_cache_secs", STANDARD_CACHE_TIME)


urlpatterns = [
    path("", cache_page(STANDARD_CACHE_TIME)(HomepageView.as_view()), name="homepage"),
    path("about", cache_page(STANDARD_CACHE_TIME)(AboutView.as_view()), name="about"),
    path("help", cache_page(STANDARD_CACHE_TIME)(HelpView.as_view()), name="help"),
    # e.g. /profiles/province-GT-gauteng/
    path(
        "profiles/<geo_level>-<geo_code>-<slug>/",
        cache_page(STANDARD_CACHE_TIME)(GeographyDetailView.as_view()),
        name="geography_detail",
    ),
    # embeds - handles the legacy static/iframe.html URL to generate the page on the fly
    #          so that settings can be injected
    path(
        "embed/iframe.html",
        cache_page(EMBED_CACHE_TIME)(
            TemplateView.as_view(template_name="embed/iframe.html")
        ),
        name="embed_iframe",
    ),
    # e.g. /profiles/province-GT.json
    re_path(
        r"^(embed_data/)?profiles/(?P<geography_id>\w+-\w+)(-(?P<slug>[\w-]+))?\.json$",
        cache_page(STANDARD_CACHE_TIME)(GeographyJsonView.as_view()),
        name="geography_json",
    ),
    # e.g. /compare/province-GT/vs/province-WC/
    re_path(
        r"^compare/(?P<geo_id1>\w+-\w+)/vs/(?P<geo_id2>\w+-\w+)/$",
        cache_page(STANDARD_CACHE_TIME)(GeographyCompareView.as_view()),
        name="geography_compare",
    ),
    # Custom data api
    path(
        "api/1.0/data/show/latest",
        cache_page(STANDARD_CACHE_TIME)(DataAPIView.as_view()),
        name="api_show_data",
    ),
    # download API
    path(
        "api/1.0/data/download/latest",
        DataAPIView.as_view(),
        kwargs={"action": "download"},
        name="api_download_data",
    ),
    # table search API
    path(
        "api/1.0/table",
        cache_page(STANDARD_CACHE_TIME)(TableAPIView.as_view()),
        name="api_list_tables",
    ),
    # geo API
    path(
        "api/1.0/geo/<geo_id>/parents",
        cache_page(STANDARD_CACHE_TIME)(GeoAPIView.as_view()),
        name="api_geo_parents",
    ),
    # TODO enable this see: https://github.com/Code4SA/censusreporter/issues/31
    # url(
    #    regex   = '^profiles/$',
    #    view    = cache_page(STANDARD_CACHE_TIME)(GeographySearchView.as_view()),
    #    kwargs  = {},
    #    name    = 'geography_search',
    # ),
    # e.g. /table/B01001/
    # url(
    #    regex   = '^tables/B23002/$',
    #    view    = RedirectView.as_view(url=reverse_lazy('table_detail',kwargs={'table':'B23002A'})),
    #    kwargs  = {},
    #    name    = 'redirect_B23002',
    # ),
    # url(
    #    regex   = '^tables/C23002/$',
    #    view    = RedirectView.as_view(url=reverse_lazy('table_detail',kwargs={'table':'C23002A'})),
    #    kwargs  = {},
    #    name    = 'redirect_C23002',
    # ),
    path(
        "tables/<table>/",
        cache_page(STANDARD_CACHE_TIME)(TableDetailView.as_view()),
        name="table_detail",
    ),
    # url(
    #    regex   = '^tables/$',
    #    view    = cache_page(STANDARD_CACHE_TIME)(TableSearchView.as_view()),
    #    kwargs  = {},
    #    name    = 'table_search',
    # ),
    path(
        "data/",
        RedirectView.as_view(url=reverse_lazy("table_search")),
        name="table_search_redirect",
    ),
    # e.g. /table/B01001/
    re_path(
        r"^data/(?P<format>map|table|distribution)/$",
        cache_page(STANDARD_CACHE_TIME)(DataView.as_view()),
        kwargs={},
        name="data_detail",
    ),
    # url(
    #    regex   = '^topics/$',
    #    view    = cache_page(STANDARD_CACHE_TIME)(TopicView.as_view()),
    #    kwargs  = {},
    #    name    = 'topic_list',
    # ),
    # url(
    #    regex   = '^topics/race-latino/?$',
    #    view    = RedirectView.as_view(url=reverse_lazy('topic_detail', kwargs={'topic_slug': 'race-hispanic'})),
    #    name    = 'topic_latino_redirect',
    # ),
    # url(
    #    regex   = '^topics/(?P<topic_slug>[-\w]+)/$',
    #    view    = cache_page(STANDARD_CACHE_TIME)(TopicView.as_view()),
    #    kwargs  = {},
    #    name    = 'topic_detail',
    # ),
    path(
        "examples/<example_slug>/",
        cache_page(STANDARD_CACHE_TIME)(ExampleView.as_view()),
        kwargs={},
        name="example_detail",
    ),
    # url(
    #    regex   = '^glossary/$',
    #    view    = cache_page(STANDARD_CACHE_TIME)(TemplateView.as_view(template_name="glossary.html")),
    #    kwargs  = {},
    #    name    = 'glossary',
    # ),
    path(
        "locate/",
        cache_page(STANDARD_CACHE_TIME)(
            LocateView.as_view(template_name="locate/locate.html")
        ),
        kwargs={},
        name="locate",
    ),
    path("healthcheck", view=HealthcheckView.as_view(), kwargs={}, name="healthcheck"),
    path(
        "robots.txt",
        lambda r: HttpResponse(
            "User-agent: *\nDisallow: /api/\n%s: /"
            % ("Disallow" if getattr(settings, "BLOCK_ROBOTS", False) else "Allow"),
            content_type="text/plain",
        ),
    ),
    path(
        "place-search/json/",
        PlaceSearchJson.as_view(),
        kwargs={},
        name="place_search_json",
    ),
    # LOCAL DEV VERSION OF API ##
    # url(
    #     regex   = '^geo-search/$',
    #     view    = GeoSearch.as_view(),
    #     kwargs  = {},
    #     name    = 'geo_search',
    # ),
    #
    # url(
    #     regex   = '^elasticsearch/$',
    #     view    = Elasticsearch.as_view(),
    #     kwargs  = {},
    #     name    = 'elasticsearch',
    # ),
    # END LOCAL DEV VERSION OF API ##
]
