from setuptools import setup, find_packages
setup(
    name = "django-install",
    version = "0.1",
    packages = find_packages(exclude=["test_project"]),
    install_requires = ['pip'],
    
    
    author = "dvrasp",
    author_email = "dvrasp@gmail.com",
    description = "App installation helper for Django",
    url = "https://github.com/dvrasp/django-install",


    ## ripped from django-extensions
    license = 'New BSD License',
    platforms = ['any'],
    
    classifiers = [#'Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],    
    )
