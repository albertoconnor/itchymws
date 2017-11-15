try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'itchymws',
]

requires = [
    'requests',
    'pytz',
    'python-dateutil',
]

setup(
    name='itchymws',
    version="0.1.0",
    description='Yet another Amazon MWS wrapper',
    long_description=open('README.md').read(),
    author='Albert O\'Connor',
    author_email='info@albertoconnor.ca',
    url='https://bitbucket.org/amjoconn/itchymws',
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE']},
    package_dir={},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ),
)
