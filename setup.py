from setuptools import setup, find_packages

setup(
    name='fems_dashboard',
    version='0.1.0',
    author='Kristen Allison',
    author_email='your.email@example.com',
    description='A Streamlit dashboard for visualizing fire index data from FEMS',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/fems_dashboard',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit',
        'pandas',
        'matplotlib',
        'numpy',
        'requests'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    python_requires='>=3.7',
)
