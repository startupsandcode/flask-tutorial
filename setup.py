from setuptools import setup

setup(
    setup_requires=['libsass >= 0.6.0'],
    sass_manifests={
        'app': ('static\scss', 'static\css', '\static\css')
    }
)