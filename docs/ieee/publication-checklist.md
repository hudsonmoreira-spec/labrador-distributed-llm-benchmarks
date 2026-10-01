# Pre-publication checklist

The current material is useful for internal auditing, but should not be published without privacy and completeness review.

- [ ] Remove or pseudonymize IP addresses, hostnames, `machine-id`, MAC addresses, serial numbers, and user paths.
- [ ] Review `research/data/ssh/known_hosts/` and all SSH logs before a public commit.
- [ ] Confirm that logs contain no private keys, tokens, passwords, or credentials.
- [ ] Pin a release/commit identifier for the supplementary artifact.
- [ ] Add hardware, operating-system, runtime, model, and quantization versions to each benchmark manifest.
- [ ] Add scripts that regenerate every table and figure from the published data.
- [ ] Document inclusion/exclusion criteria, failures, and repetitions.
- [ ] Clearly separate preliminary inventory from inference results.
- [ ] Review licenses for models, datasets, dependencies, and third-party tools.

Sanitization should produce a public copy of the data; the original internal data should remain outside the public repository and under the testbed owner's control.
