try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'Netgear GS108T management utilities',
    'author': 'Philip Peshin',
    'author_email': 'phil.peshin@gmail.com',
    'version': '0.1',
    'install_requires': ['requests'],
    'packages': ['netgear'],
    'entry_points': {
        'console_scripts': [
            'netgear = netgear.netgear:main'
        ]
    }
}

setup(**config)