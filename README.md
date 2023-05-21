# Dokasfam Distributed Database
Schema server for my distributed DB servers

## Purpose

Provide an endpoint for uploading, modifying and deleting db schema on the DB service cluster.

## Background

This web service allows me to upload & make changes to sqlite schemas on a distributed db service. This service works by replicating an arbitrary amount of sqlite database files, and provides linearized access to these database files using Paxos. The DB servers communicate using POST requests and are served using Python's Flask API. The servers then send RPC's to the Paxos protocol, which is written in golang.

## Request Format

Each request to this server should be a POST request with JSON content. This content is composed of a parameterized sql string and a list of arguments for that string.