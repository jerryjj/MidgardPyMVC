try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='midgardmvc',
    version='0.1.2',
    description='Midgard MVC in Python',
    author='Jerry Jalava',
    author_email='jerry.jalava@iki.fi',
    url='',
    namespace_packages = ['midgardmvc', 'midgardmvc.components', 'midgardmvc.controllers'],
    install_requires=[
        #"python-midgard2",
        "Pylons>=0.9.7",
        "Babel>=0.9.4",
        "repoze.who>=2.0a2",
        "repoze.who-friendlyform",
        "repoze.who-testutil",
        "cssutils",
        "WebHelpers>=1.0b5",
        "Routes>=1.12.1",
        "pytz",
        "PyYAML",
        #"turbomail", #Uncomment to enable TurboMail features
        #"cogen", #Uncomment this if you wish to use Cogen
    ],
    setup_requires=["PasteScript>=1.6.3"],
    test_suite='nose.collector',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'midgardmvc': ['i18n/*/LC_MESSAGES/*.mo', 'public/midcom-static/*.*']},
    message_extractors={'midgardmvc': [
           ('**.py', 'python', None),
           ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
           ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    # If you wish to use Cogen change paste.app_factory below to be:
    # main = midgardmvc.config.cogen_middleware:make_app
    entry_points="""
    [paste.app_factory]
    main = midgardmvc.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
