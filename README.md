# Terraform Backend HTTP

A HTTP Backend for Terraform state. Supporting terraform versions 0.11.x and 0.12.x

## Background

https://www.terraform.io/docs/backends/types/http.html

Terraform has a pluggable backend state management system. One of the backends
is a HTTP (JSON/REST) client that works with any webserver that supports the protocol.

Importantly, the state is stored after a deserialization step. Unlink most backends,
it is possible to query (and manipulate) the state using SQL. This includes fields
with arbitrary Object keys, i.e. resource attributes, Postgres JSONb is used to
store and query data.

## Example

Configure Terraform to use the HTTP backend.

```hcl
terraform {
  backend "http" {
    address = "http://localhost:8000/example"
  }
}
```

Create a fresh Postgresql database

```sql
CREATE ROLE tf login;
CREATE DATABASE tf OWNER tf;
```

Setup the runtime environment

```bash
$ pipenv install
$ export DATABASE_URL=postgres://tf@localhost/tf
$ pipenv run ./manage.py migrate
```

Run the webserver

```bash
$ pipenv run ./manage.py runserver
```

Use Terraform normally

```bash
$ terraform init
$ terraform plan -out plan.tfrun
$ terraform apply ./plan.tfrun
```

## Capabilities

- Works with 0.11 and 0.12 (v3 and v4 of the state format)
- Does not blindly store JSON objects in the database. All fields are queryable
- View state in a web browser

## TODO

- This is a Django/DRF app and could be incorporated into other Django projects.
  e.g. Authentication/Authorization can be added by setting `DEFAULT_PERMISSION_CLASSES` in `settings.REST_FRAMEWORK`.
- Different WSGI Servers config, e.g. `gunicorn`, `uWSGI` or `mod_wsgi`.
- Migrate state between scopes (i.e. reparent `Resource`s to different `State`s)
- Migrate state between `0.11` and `0.12`.
- (optional) State locking.

## Status

This is a side project, to see if it would work.
The only testing I have done is to write the `examples/`, I have not tested this with other
resources or providers.
