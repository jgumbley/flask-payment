"""
Flask Payments
--------------

Description goes here...

Links
`````

* `documentation <http://packages.python.org/Flask-Payments>`_

"""
from setuptools import setup


setup(
    name='Flask-Payments',
    version='0.1',
    url='http://github.com/LeonigMig/flask-payment/',
    license='BSD',
    author='jgumbley',
    author_email='your-email-here@example.com',
    description='<enter short description here>',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
