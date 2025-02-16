from setuptools import setup, find_packages

setup(
    name="Apple Music Importer",
    version="0.1.0",
    description="Search and import local music files to Apple Music",
    author="Soh Satoh",
    packages=find_packages(),
    url="https://github.com/sohsatoh/Apple-Music-Importer",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["apple-music-importer=apple_music_importer.cli:app"],
    },
)
