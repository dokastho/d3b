# d3b

Dokasfam Distributed Database: A restful distributed database webserver

## Summary

This webserver provides linearized replicated state across multiple endpoints. It uses an associated schema webserver ([servers/schema]()) to manage the underlying .sqlite3 database files that the replica can use. This program uses [Paxos](https://github.com/dokastho/cppaxos) to provide a sequence of operations for an arbitrary amount of replicas to commit. Each d3b replica has an associated locally-hosted Paxos server for making database operations with. For more information on how Paxos works, read this [super helpful guide](https://martinfowler.com/articles/patterns-of-distributed-systems/paxos.html).

## Schema Server

The schema webserver provides basic access and operations for managing the databases themselves. It does not provide cli-level access, but does support deleting existing databases and uploading new ones. Each uploaded database has an associated user-defined name, and is hashed to preserve uniqueness & anonymity within the replicas. In order to index into the correct database, each d3b operation requires a "table" property that corresponds to the name of an existing database. The schema server uses a translational database to map database names to their hash ID. The schemaserver database is stored in each replica alongside all other media.

## Paxos Media Operations

Database operations with an associated file are made more complicated by Paxos. Each Paxos operation is necessarily lightweight, and does not include attachments. Therefore in cases where an attached file are relevant, such as a file upload, Paxos peers will request the file directly from the peer that originally received the upload request. Each database operation for inserting the file metadata is still applied linearly, and the file request is a simple "GET" request.

Additionally, media "GET" requests are not linearized operations. This is done to optimize API responsiveness. Many sites, media galleries in particular, will submit many n "GET" requests for any k others s.t. n >> k. These "GET" requests are safe and idempotent, and therefore can be applied in any order so long as the state of the requested media does not change. To enforce this, each media "GET" request is preceded by a metadata fetch to each endpoint, thus forcing each replica to update their paxos log prior to serving the request. This sequence is aggregate linearized, meaning if you treat the group of operations as a whole (metadata fetch + subsequent media "GET" requests) then the operation is linearized. This optimization does have one key tradeoff: if a third party client requests an update to a media file, all other clients that submit a media "GET" request for that file will not see the update until after sending another metadata fetch, which could prevent the media from being served in the case where the third party deleted it. This is a worthy tradeoff due to the rarity of this case.
