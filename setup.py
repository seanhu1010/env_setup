from setuptools import setup

__version__ = '1.0.0'

REQUIRES = []

# with open('requirements.txt') as f:
#     REQUIRES = f.readlines()

setup(
    name='envlib',
    version=__version__,
    description='预置库',
    author_email='',
    author='测试团队',
    license='MIT License',
    url='',
    keywords=["env", "setup", ],
    install_requires=REQUIRES,
    packages=['envlib', 'envlib.envsetup', 'envlib.env_resources'],
    # include_package_data=True,
    long_description='http://1.1.1.1:8080/',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
