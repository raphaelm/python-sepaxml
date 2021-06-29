SEPA XML Generator
==================

.. image:: https://travis-ci.org/raphaelm/python-sepaxml.svg?branch=master
   :target: https://travis-ci.org/raphaelm/python-sepaxml

.. image:: https://codecov.io/gh/raphaelm/python-sepaxml/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/raphaelm/python-sepaxml

.. image:: http://img.shields.io/pypi/v/sepaxml.svg
   :target: https://pypi.python.org/pypi/sepaxml

This is a python implementation to generate SEPA XML files.

Limitations
-----------

Supported standards:

* CBIPaymentRequest.00.04.00

Usage
-----


Credit transfer
"""""""""""""""

Example:

.. code:: python

    from sepaxml import SepaTransfer
    import datetime, uuid

    config = {
    "name": "Test von Testenstein",
    "IBAN": "NL50BANK1234567890",
    "BIC": "BANKNL2A",
    "batch": True,
    "execution_date": datetime.date.today(),
    "bank code" : "abcwwoe",
    "Organisation_id" : '123aaf',
    # For non-SEPA transfers, set "domestic" to True, necessary e.g. for CH/LI
    "CBI": True,
    "currency": "EUR",  # ISO 4217
    }
    sepa = SepaTransfer(config, clean=True)

    payment1 = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 5000,  # in cents
        "execution_date": datetime.date.today(),
        "description": "Test transaction",
        "endtoend_id": str(uuid.uuid4().hex)  # optional
    }
    sepa.add_payment(payment1)
    
    payment2 = {
        "name": "Test von Testenstein",
        "IBAN": "NL50BANK1234567890",
        "BIC": "BANKNL2A",
        "amount": 5000,  # in cents
        "execution_date": datetime.date.today(),
        "document": [{"type":"CINV", "invoice_number":"1", "invoice_date":datetime.date.today(), "invoice_amount":"5000"}, {"type":"CINV", "invoice_number":"2", "invoice_date":datetime.date.today(), "invoice_amount":"7000"}],
        "endtoend_id": str(uuid.uuid4().hex)  # optional
    }
    sepa.add_payment(payment2)
    
    
    output = sepa.export(validate=True).decode('utf-8')
    print(output)
    
    with open(r"C:\Users\jibin_000\Desktop\new_cbi_strds\output.xml", "w") as f:
        f.write(output)



Development
-----------

To automatically sort your Imports as required by CI::

    pip install isort
    isort -rc .


Credits and License
-------------------

Maintainer: Raphael Michel <mail@raphaelmichel.de>

This basically started as a properly packaged, python 3 tested version
of the `PySepaDD`_ implementation that was released by The Congressus under the MIT license.
Thanks for your work!

License: MIT

.. _PySepaDD: https://github.com/congressus/PySepaDD
