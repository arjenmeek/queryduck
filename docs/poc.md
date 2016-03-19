# CrunchyVicar: Proof of Concept 1

This document describes requirements and proposed functionality for a limited Proof of Concept (PoC) implementation.

The current PoC will be referred to as "PoC1".


# Main features

- RESTful API: Use with specific API clients only (no web interface).
- CLI-based API client: to be written alongside the server.
- Create/Retrieve/Update/Delete: Basic CRUD operations. Explicit delete operations are somewhat contrary to the design principles but will greatly help with debugging in this early phase.
- Export/Import: Being able to export and import the database content will reduce the need for complex DB schema migrations (instead we can export, drop DB, upgrade, create DB, import).


# Technologies to be used

For this first PoC phase, the primary goal is to be able to create a "basically working" implementation with as little effort as possible. This means I have chosen off-the-shelf systems and libraries that I happen to have a sufficient level of experience with. Optimization is not a significant concern at this point.

The following technologies will be used for PoC1:

- Python 3 programming language
- PostgreSQL database engine
- Pyramid web framework (with pyramid\_services pluggable service layer)
- SQLAlchemy ORM


# File structure

From the repository root:

- `client`: Files related to the CLI client
- `server`: Files related to the server application
- `server/README.md`: Further documentation for the server application


# Server application design

## General structure

The server application is started through a local Python 3 script called `serve.py`. This imports the `crunchyserver` module where the rest of the code lives, and starts the WSGI server process using the configuration specified in `config.yml`.

From here, the Pyramid `Configurator` class takes over the general management of the application's components, called on by the `main` function in `__init__.py`. The most important components and files are:

- Controller classes, in `controllers.py`. These handle incoming API calls (web requests) according to the routes defined in the `main` function, and generally call on various services for more advanced functionality.
- Models, in `models.py`. These represent data objects, currently just Statements.
- Repositories, in `repositories.py`. These Repository classes are services that provide a consistent interface to the underlying data store, and handle querying and modifying the stored information.


## Models

Currently, the only model (i.e. data class) is the Statement. In principle it is meant to represent only the 4 elements making up the abstract Statement concept, but to be efficiently represented in an SQL database, various additional columns are used.

A Statement within the context of PoC1 is stored in a table containing the following columns:

- `id`: Locally unique integer identifier for Statements (mainly used for efficiently representing relationships between Statements).
- `uuid`: The UUID representing the Statement.
- `subject_id`, `predicate_id`: Integer columns referencing `id` values of Statements for corresponding elements in the Statement.
- `object_*`: Multiple columns for various data types that a Statement's *object* can contain (including Statement, through `object_statement_id`). By representing each data type through a different column, indexes can be efficiently used for querying Statements using various filters.


## Serialization / deserialization

For consistent use in RESTful API calls and export/import, Statements should have a consistent string representation. The basic format used for this is JSON; a Statement is represented as a JSON array that always consists of 4 string (Unicode) elements, representing respectively the Identifier, Subject, Predicate and Object.

Since JSON provides a very limited set of scalar datatypes, each element of a Statement is represented as a JSON string of the format `type:value`. `type` is a type identifier consisting of one or more characters from the set [a-z0-9\_]. `value` is any sequence of Unicode characters conforming to specifications that are defined for the specified `type`. Together, the type and value can fully represent a more richly typed value. For consistency, all elements of a Statement are always represented in this manner, meaning that other JSON data types (Boolean, Number, etc.) are invalid within this context.

The following data `type`s and corresponding value specifications should be supported initially. Different `type`s may represent the same actual data type, encoded in a different way.

- `uuid`: A Universally Unique IDentifier in the canonical 8-4-4-4-12 lowercase hexadecimal format.
- `st`: A Statement, referred to by its `uuid` Identifier.
- `int`: An integer number, represented by its decimal digits, optionally starting with a `-` for negative values.
- `str`: A sequence of Unicode characters.
- `bool`: Either `true` or `false`.
- `datetime`: Combination of a date and time value, without specification of timezone or time standard. The structure conforms to the Python `strptime()` format `%Y-%m-%dT%H:%M:%S.%f` (for example: `2010-03-24T15:03:56.821346`).
- `special`: A set of values with special semantic meaning. For now the only allowed value is `self`, which refers to the Statement which the element is part of.


# Client application design

The basic interaction for the CLI application is single-invocation, with input data passed as commandline arguments. Alternately, an integrated command prompt can be invoked where similar actions to the single-invocation interface can be invoked, with some preservation of state between invocations.
