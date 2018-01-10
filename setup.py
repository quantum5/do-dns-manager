import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='do-dns-manager',
    version='0.1',
    packages=['do_dns_manager'],
    package_data={'do_dns_manager': ['templates/*.html']},
    entry_points={
        'console_scripts': [
            'do-dns-manager = do_dns_manager:main',
        ]
    },
    install_requires=['tornado', 'tornado-http-auth'],

    author='Quantum',
    author_email='quantum@dmoj.ca',
    url='https://github.com/quantum5/do-dns-manager',
    description='A DNS record manager using DigitalOcean as backend, '
                'useful for assigning DNS records in a DHCP hook.',
    long_description=readme,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3',
    ],
)
