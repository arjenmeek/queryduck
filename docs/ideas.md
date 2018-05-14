# CrunchyVicar: Assorted ideas and considerations

# Data modeling

## Primary identifiers

The currently proposed primary identifier type for Statements is a generic UUID.

There are some alternative approaches worth further consideration, although these appear to have significant downsides.

### Content-based hash

Using a content-based hash as identifier for Statements has as its major advantage that a Statement cannot be altered without changing its identifier, guaranteeing integrity as long as the cryptographic hash function used is considered secure.

The most significant problem with this is that it prevents multiple Statements with identical values from existing independently. This is problematic because it can be necessary to make new Statements about independent instances of a given Statement. For example: Alice claims on Monday that it's raining, which at that time happens to be true. On Tuesday, Bob claims the same thing, while the sun is shining, making the second statement false. Both Statements by themselves would have the same values (i.e. "The weather condition is that it's raining"), but because the same effective statement was made twice at different times, it has different meanings both times.

This problem is significant enough to rule out a simple content-based hash as viable primary identifier.

### Salted hash

Instead of a fully deterministic content-based hash, a salted hash can be considered: Before hashing, a salt value is generated consisting of several random bytes. The salt as well as the content of the statement are then concatenated, and a hash is taken of the result. Both the hash and the salt are stored. The result is that the values of the Statement cannot be altered without invalidating the identifier, but that multiple identical statements (with different salts) can exist.

There are still some downsides to this approach when compared to the generic UUID approach:

-   Extra complexity because the identifier can no longer rely on standard UUID libraries and protocols.
-   Requirement for any statement to be serializable in one predictable way across all implementations and data types.
-   Reliance on a cryptographic hashing algorithm, which might be broken in the future.

Despite the downsides, the possibility to guarantee the integrity of Statements based on a primary identifier is a major advantage, especially when combined with cryptographic signatures. Because of this, use of a salted hash-based primary identifier should be seriously considered as a feature.

Although the structure of RFC 4122 UUIDs could theoretically provide space for both a salt value and a hash, this would not be compatible with the documented ways in which UUIDs should be generated.
