# DNS Sync

Changing DNS providers can be a pain if you have lots of DNS records. Make the transition simpler or take control of your DNS records by syncing from a local zone file repository.

In general, the following record types are supported: `A`, `AAAA`, `CNAME`, `MX`, `SRV`, `SPF`, and `TXT`. The following record types are recognized and can be displayed however they are generally ignored for syncing purposes: `NS`, `SOA`, `PTR`.

**To submit bug reports, etc., please visit this project on [GitLab](https://gitlab.com/petris/dns-sync).**

# Running

The provided `sync.sh` script will run DNS Sync properly from anywhere. In general, your current/working directory should be a directory with zone files, however it is possible to sync directly from provider to provider without using zone files.

`python -m dnssync` can also be used if dnssync is installed globally, `PYTHONPATH` includes the path to this repository, or the current directory is the base directory of this repository.

## Parameters

* `-h` - Print help
* `-s` or `--source` - The source provider to use. Can be any of the providers listed in the Providers section, given the appropriate environment variables are available.
* `-d` or `--destination` - The destination provider to use. Can be any of hte providers listed in the Providers section, other than `zonefile`, given the appropriate environment variables are available. _This is the provider that changes will be made to._
* `-z` or `--zone` - A zone (domain) to sync. Multiple zones can be synced by specifying this parameter multiple times. If not specified, all zones that exist in both the source and destination providers will be synced.

# Providers

## Zone Files (`zonefile`)

Reads from local a local [zone file](https://en.wikipedia.org/wiki/Zone_file) repository. This repository has the following limitations:

* Zone files must be in the current directory, or the `ZONEFILE_PATH` environment variable must be specified.
* Zone files names must be the domain name suffixed with `.db`. For example, the zone file for domain `example.org` must be named `example.org.db`.
* A single record must not span multiple lines.
* Host names must be relative to the origin, and records that belong to the origin must specify `@` as the host name.
* TTL is not required on a per-record basis, however if not specifying a TTL on all records, the `$TTL` keyboard should be used to supply a default TTL.
* The `$INCLUDE` keyword can be used to include other files. Files are included as if they were inserted directly into the original file.

## Linode (`linode`)

Reads and writes dns records to a domain in a [Linode](https://www.linode.com/) account.

The `LINODE_API_TOKEN` environment variable must be populated with a personal access token for this provider to work or show up in the list of available providers. Please refer to the [Linode API documentation](https://developers.linode.com/api/v4/) for more information.

Linode does not support the `SPF` record type, and therefore any `SPF` records from a source provider will be ignored when syncing.

## Digital Ocean (`digitalocean`)

Reads and writes dns records to a domain in a [Digital Ocean](https://www.digitalocean.com/) account.

The `DO_API_TOKEN` environment variable must be populated with an OAuth token for this provider to work or show up in the list of available providers. Please refer to the [Digital Ocean API documentation](https://developers.digitalocean.com/documentation/v2/#authentication) for more information.

Digital Ocean does not support the `SPF` record type, and therefore any `SPF` records from a source provider will be ignored when syncing.

## Cloudflare (`cloudflare`)

Reads and writes dns records to a domain in a [Cloudflare](https://www.cloudflare.com/) account.

The `CF_API_TOKEN` environment variable must be populated with an API Token for this provider to work or show up in the list of available providers. Please refer to the [Cloudflare API documentation](https://api.cloudflare.com/#getting-started-requests) for more information.

# GoDaddy (`godaddy`)
Reads and writes dns records to a domain in a [GoDaddy](https://www.godaddy.com/) account.

The `GD_API_KEY` and `GD_API_SECRET` environment variables must be populated with an API Key and Secret for this provider to work or show up in the list of available providers. Please refer to the [GoDaddy API documentation](https://developer.godaddy.com/) for more information.

**NOTE:** GoDaddy by default includes a `CNAME` record with a subdomain of `_domainconnect` and a value of `_domainconnect.gd.domaincontrol.com`. This record **does not** get removed automatically, even though the API that is being used is supposed to replace _all_ DNS records with _only_ the ones specified. This is a bug in GoDaddy's API. Please either add this record to your zone file or manually remove it via GoDaddy's user interface to avoid unnecessary syncing.