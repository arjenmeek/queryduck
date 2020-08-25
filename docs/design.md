# QueryDuck: Design document - Introduction

This document describes important considerations and design desicions regarding the QueryDuck project and the specification that is to be established.

It is not intended to be a general, easy-to-read general explanation of the project, which instead can be found [here](explanation.md).

The information in this document is meant to offer a point of reference for discussion of the specification. It is expected to change based on new insights and decisions. In its current form, it's too loosely structured to be worth applying explicit version numbers to. If you need to refer to a specific revision, do so using the timestamp and/or hash of the commit it was part of.



# Design considerations

## Objective

The general objective of the project can be described as follows:

*To establish a formalized specification for efficiently expressing and exchanging semantically structured digital information.*


## Core concepts

*Statement*: A single expression of information. A Statement consists of four elements:

1.  Identifier: A token used to identify the Statement.
2.  Subject: A reference to the thing the Statement is about.
3.  Predicate: A reference to the kind of information the Statement expresses about the Subject.
4.  Object: The information being expressed about the Subject.

*Value*: A single element of a Statement, which is defined by a particular Value Type and a specific value within the range of the Value Type.

*Value Type*: The data type of a Value. At minimum, the following Value Types must be supported by any implementation:

1.  Identifier Type: A specific, to-be-determined scalar Value Type which serves as the primary Identifier of any Statement.
2.  Statement: The Value Type for Values which refer to a Statement. The Subject, Predicate and Object elements of a Statement must support this Value Type.

Additional Value Types should be agreed upon for storing literal values in an efficient and semantically meaningful way. The process for agreeing on Value Types is to be determined.

*Information Repository*: Any autonomous storage system containing a collection of statements.


## Requirements

The following properties are requirements for the specification to be considered complete.

1.  Expression of Statements does not rely on an external namespace or authority.
2.  Any Statement can refer directly to any other Statement.
3.  Any Statement can be expressed without expressing Statements it refers to.
4.  Statements can be exchanged between Information Repositories in an efficient and flexible manner.
5.  Any information which can be expressed digitally as a series of byte values is theoretically (that is, barring practical implementation limits such as storage size) expressable as a Value.


## Nice-to-haves

The following properties are desired, but may be reduced or abandoned if (and *only* if) it becomes sufficiently clear that they cannot be combined with the Requirements within a single specification.

1.  There is no bias towards specific implementations or types of information (though a bias in favour of smaller units of information is acceptable).
2.  Arbitrary Value Types can be added, either by expanding the specification, or by a separate process that works within boundaries set by the specification (the latter is preferred).
3.  Using higher-level protocols, data (sub)sets on separate Information Repositories can be reliably synchronized incrementally & asynchronously.


## Challenges

Considering the requirements as well as existing systems with comparable goals, there are certain challenges that are readily apparent. The viability of a particular candidate for the specification will depend to a large extent on the degree to which it provides, or at least allows, solutions to these challenges.

1.  The ability to query information quickly and efficiently.
2.  The ability to utilize storage space efficiently.
3.  Keeping the specification straightforward and understandable, and allowing higher-level protocols to also be straightforward and understandable.
4.  Dealing efficiently with real-world value types that are essentially 'compound' values (example: a time period defined as starting June 25th 2000 and ending somewhere in the second quarter of 2001).


## Important questions to be answered

1.  How can independent resources be represented without having to establish another unit of information besides the Statement?
2.  How should literal (non-Statement) values be referenced?
3.  How can implementations optimize storage or querying of certain common types of information, while keeping implementations without these optimizations sufficiently efficient?


# Design proposals

TODO

This section will contain specific proposals that attempt to satisfy the conditions described in the *Design considerations* section.
