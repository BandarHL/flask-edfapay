from setuptools import setup

setup(name='flask-edfapay',
      version='0.1',
      url='https://github.com/BandarHL/flask-edfapay',
      author='BandarHelal',
      author_email='bandarhelal190@gmail.com',
      description='A Flask library for edfapay API',
      long_description='Please visit https://github.com/BandarHL/flask-edfapay',
      packages=['flask_edfapay'],
      zip_safe=False,
      include_package_data=True,
      platforms='any',
      install_requires=['Flask', 'requests', 'teritorio'])