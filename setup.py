from setuptools import setup, find_packages

setup(
    name="aitest",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "click",
        "gitpython",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "aitest=aitest:main",
            'aitest-config=aitest.config_manager:manage_config'
        ],
    },
)
