

HOOKS = {
    'APPNAMES':{
        'sorl-thumbnail':['sorl.thumbnail'],
        'django-cms':[
            'cms',
            'cms.plugins.text',
            ## 'cms.plugins.picture',
            ## 'cms.plugins.link',
            ## 'cms.plugins.file',
            ## 'cms.plugins.snippet',
            ## 'cms.plugins.googlemap',
            'menus',
            'mptt',
            'publisher'
            ],
        },
    'EXTRA_SETTINGS':{
        'django-debug-toolbar':{
            'MIDDLEWARE_CLASSES':['debug_toolbar.middleware.DebugToolbarMiddleware'],
            'INTERNAL_IPS':['127.0.0.1'],
            },
	'django-speedtracer':{
	    'MIDDLEWARE_CLASSES':['speedtracer.middleware.SpeedTracerMiddleware'],
	    },
        'django-cms':{ ## work in progress
            'MIDDLEWARE_CLASSES':[
                'cms.middleware.page.CurrentPageMiddleware',
                'cms.middleware.user.CurrentUserMiddleware',
                'cms.middleware.media.PlaceholderMediaMiddleware',
                ],
            'TEMPLATE_CONTEXT_PROCESSORS':[
                "django.core.context_processors.auth",
                "django.core.context_processors.i18n",
                "django.core.context_processors.request",
                "django.core.context_processors.media",
                "cms.context_processors.media",
                ],
            'CMS_TEMPLATES':(
                ('default.html', 'default'),
                )
            }
        
        },
    'TEMPLATES':{
        'django-cms':{
            'default.html':"""{% extends "base.html" %}
            
{% load cms_tags menu_tags %}

{% block content %}
<div id="menu">{% show_menu 0 100 100 100 %}</div>
<div id="breadcrumb">{% show_breadcrumb %}</div>
<div id="languagechooser">{% language_chooser %}</div>
<div id="content">{% placeholder "content" %}</div>
{% endblock %}
"""
            }
        }
    }
