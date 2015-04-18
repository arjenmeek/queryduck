# CrunchyVicar: Proof of Concept 1

This document describes requirements and proposed functionality for a limited Proof of Concept (PoC) implementation.

The current PoC will be referred to as "PoC1".


# Main features

*   RESTful API: Use with specific API clients only (no web interface).
*   CLI-based API client: to be written alongside the server.
*   Create/Retrieve/Update/Delete: Basic CRUD operations. Explicit delete operations are somewhat contrary to the design principles but will greatly help with debugging in this early phase.
*   Export/Import: Being able to export and import the database content will reduce the need for complex DB schema migrations (instead we can export, drop DB, upgrade, create DB, import).


# Technologies to be used

For this first PoC phase, the primary goal is to be able to create a "basically working" implementation with as little effort as possible. This means I have chosen off-the-shelf systems and libraries that I happen to have a sufficient level of experience with. Optimization is not a significant concern at this point.

The following technologies will be used for PoC1:

*   Python 3 programming language
*   PostgreSQL database engine
*   Pyramid web framework (with pyramid\_services pluggable service layer)
*   SQLAlchemy ORM


# File structure

From the repository root:

*   `cli`: Files related to the CLI client
*   `server`: Files related to the server
