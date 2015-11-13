import codecs
import os
import setuptools


VERSION = '0.0.1'
HERE = os.path.abspath(os.path.dirname(__file__))


def read(*path):
    with codecs.open(os.path.join(HERE, *path), "rb", "utf-8") as file_p:
        return file_p.read()

setuptools.setup(
    name='oscar.flag',
    description='Configuration flags for libraries and applications.',
    license='Apache Software License 2.0',
    long_description=read('README.rst'),
    version=VERSION,
    url='https://github.com/oscarhealth/oscar.flag',
    namespace_packages=['oscar'],
    author='Oscar Engineering',
    author_email='open-source+oscar.flag@hioscar.com',
    maintainer='Oscar Engineering',
    maintainer_email='open-source+oscar.flag@hioscar.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Systems Administration',
    ],
    keywords='command-line arguments environment flags argv',
    packages=[
        'oscar.flag',
        'oscar.flag.contrib',
    ],
    package_data={'oscar.flag': ['setup.cfg']},
    package_dir={
        'oscar.flag': 'oscar/flag',
        'oscar.flag.contrib': 'oscar/flag',
        'test': 'test',
    },
    scripts=[],
    zip_safe=True,
    extras_require={
        'test': 'pytest',
    },
)
