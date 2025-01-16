Contributing
============

We love your input! We want to make contributing to PepperPy Core as easy and transparent as possible.

Development Process
-----------------

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code follows our coding standards.
6. Issue that pull request!

Code Style
---------

- Follow PEP 8 guidelines
- Use black for code formatting with line length of 88
- Use double quotes for strings
- Use type hints for all function parameters and return types
- Use async/await for I/O operations
- Follow the principle of least privilege

Pull Request Process
------------------

1. Update the README.md with details of changes to the interface, if applicable.
2. Update the documentation with any new features or changes.
3. The PR may be merged once you have the sign-off of at least one other developer.

Testing
------

We use pytest for testing. To run tests:

.. code-block:: bash

    poetry run pytest

Make sure to write tests for new features and bug fixes.

Documentation
-----------

We use Sphinx for documentation. To build docs locally:

.. code-block:: bash

    cd docs
    poetry run make html

View the docs by opening `build/html/index.html` in your browser.

Code of Conduct
-------------

Our Pledge
~~~~~~~~~

We pledge to make participation in our project and our community a harassment-free experience for everyone.

Our Standards
~~~~~~~~~~~

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

License
-------

By contributing, you agree that your contributions will be licensed under the project's license. 