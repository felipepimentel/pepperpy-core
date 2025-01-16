Installation
============

PepperPy Core can be installed using pip or poetry. We recommend using poetry for development.

Using Poetry (Recommended)
------------------------

.. code-block:: bash

    poetry add pepperpy-core

Using pip
--------

.. code-block:: bash

    pip install pepperpy-core

Development Installation
----------------------

To install PepperPy Core for development:

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/yourusername/pepperpy-core.git
       cd pepperpy-core

2. Install dependencies with Poetry:

   .. code-block:: bash

       poetry install

3. Install pre-commit hooks:

   .. code-block:: bash

       poetry run pre-commit install

Requirements
-----------

- Python 3.12 or higher
- Poetry (for development installation)

Optional Dependencies
------------------

Some features require additional dependencies. You can install them using Poetry:

.. code-block:: bash

    poetry install --with dev  # Development dependencies
    poetry install --with docs  # Documentation dependencies 