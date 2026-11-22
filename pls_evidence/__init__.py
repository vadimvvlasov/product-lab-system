"""Offline evidence tools for Product Lab System.

Two read-only helpers that work on locally saved web clippings and never touch
the network or an LLM:

* ``verify`` checks evidence-table rows against a clipping (excerpt, URL, date,
  author) and writes a log. It does not confirm a claim and does not replace
  human verification (see ``templates/evidence.md``).
* ``report`` lists clippings with simple heuristic flags for the intake step.
"""

__version__ = "0.1.0"
