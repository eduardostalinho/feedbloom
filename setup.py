from setuptools import setup

setup(name='feedbloom',
    version='0.1',
    description='Feed Reader inspired by news channels bottom stripes.',
    url='http://github.com/eduardostalinho/feedbloom',
    author='Eduardo Stalinho',
    author_email='eduardooc.86@gmail.com',
    license='GPLv3',
    packages=['feedbloom'],
    entry_points={'console_scripts': ['feedbloom=feedbloom.feedbloom:main']},
    install_requires=['feedparser'],
    zip_safe=False)
