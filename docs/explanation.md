# QueryDuck: General explanation - Introduction

Welcome to the QueryDuck project. This project's goal is to establish a technical standard for expressing and exchanging digital information that is structured in a semantically meaningful way.

This document is meant to serve as a general introduction to the project that is easier to read but less thorough than the [design document](design.md).

NOTICE: Until this notice is removed, this document is too incomplete to be of any practical use. Please wait until it's more complete, or ask me if you have particularly urgent questions.


## What does "semantically meaningful" mean?

Digital information only has a meaning when it is processed within a certain context. For example, a particular bunch of bytes might be interpreted as a picture, or as a page of text.

In such cases, the information is primarily meaningful to humans, who may look at the picture or read the text. For a computer program to attach meaning to this kind of information, it first has to attempt to process it.

Within this context, *semantically meaningful* refers to information that is structured in such a way that it is directly meaningful (without additional processing) to computer programs.


# Context


## Comparison to RDF and the Semantic Web

The obvious comparison for QueryDuck is RDF, the [Resource Description Framework](https://en.wikipedia.org/wiki/Resource_Description_Framework). Both are centered around storing and exchanging knowledge in a highly structured way. Both also rely on variations of the subject-predicate-object model for expressing information. There are many more specific similarities, not in the least because QueryDuck borrows concepts and terminology from RDF (why reinvent what works?).

There is one particularly important difference between QueryDuck and RDF: The latter's design is heavily centered around the concept of the [Semantic Web](https://en.wikipedia.org/wiki/Semantic_Web), an attempt to standardize data exchange protocols on the World Wide Web. Despite all the strengths and use cases of the Semantic Web concept, the connection to the structure of the World Wide Web also places many restrictions on the ways information can be stored and exchanged, such as the focus on generalized Uniform Resource Identifiers (URI's) that are meant to correspond to web resources. QueryDuck, by contrast, forces every resource it expresses to be identifiable by a UUID.


# TODO

There's no more text. Yet. Stay tuned?
