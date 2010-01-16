from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', 'churchill.views.index'),
    (r'^echo$', 'churchill.views.echo'),
    (r'^init$', 'churchill.views.init'),
    (r'^join$', 'churchill.views.join'),
    (r'^full$', 'churchill.views.full_monty'),
    (r'^joining$', 'churchill.views.joining'),
    (r'^start$', 'churchill.views.start_game'),
    (r'^status$', 'churchill.views.status'),

)