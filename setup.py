from setuptools import setup, find_packages

setup(
    name="wsweng",
    version="0.0.1a",
    author="Bill Williams",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
    ],
    include_package_data=True,
)
