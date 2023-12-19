from setuptools import setup

long_description = """\
mailProc
========

Mail services creation microframework http://mailproc.readthedocs.io
"""

setup(
    name='mailProc',
    version='0.5.0',
    packages=['mailproc', 'mailproc.transports'],
    url='https://github.com/daxslab/mailproc',
    license='LGPL 3.0',
    author='Carlos Cesar Caballero Diaz',
    author_email='ccesar@daxslab.com',
    description='Mail services creation microframework',
    long_description=long_description,
    platforms='any',
    python_requires='>=3.4, <4',
    extras_require={
            'dev': [
                'pytest',
                'pytest-pep8',
                'pytest-cov',
                'sphinx',
                'tox'
            ]
        },
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        # Specify the Python versions you support here.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ]
)
