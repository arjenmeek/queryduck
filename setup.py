import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="QueryDuck",
    version="0.5.1.1",
    author="Arjen Meek",
    author_email="arjen@meeknet.nl",
    description="The QueryDuck project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arjenmeek/queryduck",
    packages=['queryduck'],
    package_data={
        "queryduck": ["schemas/*.json"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
)
