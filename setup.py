from setuptools import setup, find_packages

setup(
    name="appian",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit',
        'groq',
        'Pillow',
        'beautifulsoup4',
        'cssutils',
    ]
) 