try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='midgardmvc',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='',
    install_requires=[
        "python-midgard2",
        "Pylons>=0.9.7",
        "Babel>=0.9.4",
        "cssutils",
        "WebHelpers>=1.0b5"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    test_suite='nose.collector',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'midgardmvc': ['i18n/*/LC_MESSAGES/*.mo', 'public/midcom-static/*']},
    message_extractors={'midgardmvc': [
           ('**.py', 'python', None),
           ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
           ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = midgardmvc.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
