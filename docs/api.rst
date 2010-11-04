.. _api:

===
API
===


.. module:: tablib

This part of the documentation covers all the interfaces of Tablib.  For
parts where Tablib depends on external libraries, we document the most
important right here and provide links to the canonical documentation.


--------------
Dataset Object
--------------


.. autoclass:: Dataset
   :inherited-members:


---------------
Databook Object
---------------


.. autoclass:: Databook
   :inherited-members:



---------
Functions
---------


.. autofunction:: detect

.. autofunction:: import_set


----------
Exceptions
----------


.. class:: InvalidDatasetType

    You're trying to add something that doesn't quite look right.


.. class:: InvalidDimensions

    You're trying to add something that doesn't quite fit right.


.. class:: UnsupportedFormat

    You're trying to add something that doesn't quite taste right.


Now, go start some :ref:`Tablib Development <development>`.