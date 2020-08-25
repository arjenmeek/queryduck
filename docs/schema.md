# QueryDuck: Schema specifications

Although the QueryDuck project is primarily centered around the specifications of the Statement and how to store them, in practice almost all potential use cases involve establishing a higher-level standard defining the structure of Statements and the relationships between them.

In order to create more realistic Proof of Concept implementations, and maybe also provide an initial direction for eventual real-world applications, this document attempts to specify a general-purpose data schema structure to be used with Statements. It will be referred to in a generalized way as the Schema.



# Representing Resources and making Statements about them

At the most basic level, semantically structured information amounts to making statements about *things*, where a *thing* is anything that a statement can be made about. The generic term *Resource* will be used for any such *thing* from here on.

The QueryDuck specification, however, only provides for Statements, not Resources. In order to still be able to make practically useful Statements, an important equivalence is introduced: a Statement that has itself as its Subject, and with its Predicate and Object indicating that its Subject is a Resource, the Statement itself is considered to represent the Resource.

This approach is chosen because the lack of an explicit Resource type in the QueryDuck specification means Statements about Resources can be made in the same manner as Statements about other Statements, greatly increasing flexibility.


## Example

To give an example of a set of pseudo-Statements in the form "Identifier: **Subject** *Predicate* **Object**"

Statement1:  **Statement1** *is a* **Resource**
Statement2:  **Statement1** *is a* **Person**
Statement3:  **Statement1** *is called* **Alice**

As these 3 Statements imply, Statement1 is now used to represent a specific Resource, in this case a person called "Alice". All further Statements that are meant to say something about Alice are now made with Statement1 as its Subject.


## Bootstrapping the Schema

Those familiar with schema design concepts will quickly realize that the above example becomes tricky once we attempt to represent what a Resource actually is. In order to define this, a number of relatively unusual Statements must be made, providing a solid foundation for more regular Statements.

In the example above, the Resource in the Object of Statement1 is also a reference to another Statement, which represents the Resource "class" itself. If we also change the Predicate *is a* to *type*. With this, the Statement representing Resource.

**Resource** *type* **Resource**

Which makes it a statement that has itself as both its Subject and Object (since it tells us that *Resource* is itself a *Resource*). The Predicate, *type*, is another Resource:

**type** *type* **Resource**

This Statement has itself as both Subject and Predicate (after all, it's a Statement defining what the *type* of *type* is.

The combination of these two Resources is sufficient to build a more elaborate schema on.


# Tying the Schema to applications

Even with a clear idea of what the Schema should look like, it remains tricky to actually use it in applications: even though we've used readable identifiers so far, Statements are normally identified by a UUID, which is a sequence of (usually random) hexadecimal digits. In order for an application to effectively use a Schema, it will have to somehow find all the Statements the Schema that are relevant to the concepts it deals with.

The most basic way to do this would be to configure a separate UUID in the application for each relevant program concept. However, this quickly becomes cumbersome for more elaborate applications as a long list of UUIDs would have to be registered somewhere, and updated whenever relevant changes happen.

Instead, two special types of Statements are defined which are intended to make this situation less complicated:
