"""Package manager setup for Sartorius driver."""
from setuptools import setup

with open('README.md') as in_file:
    long_description = in_file.read()

setup(
    name='copley',
    version="0.1.1",
    description='Python driver for Copley Tapped Density Tester.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/numat/copley',
    author='Javan Whitney-Warner',
    author_email='j.whitney-warner@numat-tech.com',
    package_data={'copley': ['py.typed']},
    packages=['copley'],
    install_requires=['pyserial'],
    extras_require={

        'test': [
            'mypy==1.10.1',
            'pytest>=8,<9',
            'pytest-cov>=4,<5',
            'pytest-asyncio==0.*',
            'ruff==0.4.7',
            'types-pyserial',
        ]
    },
    entry_points={
        'console_scripts': [('copley = copley:command_line')]
    },
    license='GPLv2',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Development Status :: 1 - Beta',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces'
    ]
)
