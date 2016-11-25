Release notes
=============

This project uses `semantic versioning <http://semver.org/>`_.

1.0.1
-----

Changed
^^^^^^^

- Internal refactoring of msmtpq.queue (no public API changes).

1.0.0 (2016-11-20)
------------------

Changed
^^^^^^^

- API is now stable.
- Queued message format changed; 1.0.0 cannot send 0.2.0 messages and
  vice versa.

Fixed
^^^^^

- Fixed messages being removed even if sending failed.

0.2.0 (2016-10-09)
------------------

Changed
^^^^^^^

- ``--manage`` changed significantly.  ``s`` is now ``send``, ``l`` is now
  ``list``, ``d`` and ``o`` removed.

0.1.0 (2016-09-11)
------------------

Initial release.
