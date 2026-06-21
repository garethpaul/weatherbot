# Hosted Checkout Credential Isolation

Status: Completed

## Problem

The hosted workflow used a read-only repository token but allowed
`actions/checkout` to persist that token in local Git configuration. Later
steps do not need Git authentication, so retaining the credential widened the
impact of a compromised dependency or test process.

## Change

- Set `persist-credentials: false` on the immutable-pinned checkout step.
- Bind the setting to the checkout step in the dependency-free repository
  contract.
- Reject missing, writable, and decoy-only credential settings.

## Verification Results

- The full pinned `make check` gate passed from the repository root and an
  external working directory.
- The checkout-isolation contract rejected all three hostile mutations.
- No provider credential was loaded and no live provider request was sent.
