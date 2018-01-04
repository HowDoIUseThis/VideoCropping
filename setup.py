#!/usr/bin/env python
from setuptools import setup, find_packages
import sys


long_description = ''

if 'upload' in sys.argv:
    with open('README.md') as f:
        long_description = f.read()


setup(
    name='video-crop-roi',
    version='0.1.0',
    description=(
        'A script used to crop sections of video to train a'
        ' neural network with.'
    ),
    author='Chris Stewart',
    packages=find_packages(),
    long_description=long_description,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT',
        'Natural Language :: English',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    url='https://github.com/HowDoIUseThis/VideoCropping',
    entry_points={
        'console_scripts': [
            'video-crop-roi = video_crop_roi:main',
        ],
    },
    install_requires=['click', 'opencv-python'],
)
