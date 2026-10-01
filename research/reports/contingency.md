# Contingency procedure

1. Mark the run as `failure_interrupted`, preserving logs, UTC timestamps, commit, model, quantization, prompt, configuration, and group.
2. Record node/IP/MAC, symptom, UTC time, last log, and diagnosis; do not silently replace evidence.
3. Select the first eligible reserve, verifying SSH, sudo, system/runtime version, model, quantization, configuration, and load state.
4. Record `replacement: former -> reserve`, reason, and UTC time in the run manifest.
5. Restart the affected run from the beginning. Assess with the experiment owner whether previous groups must be repeated to preserve pairing and comparability.
6. If an identity, storage, network, or temperature error occurs, remove the node from the testbed pending investigation; do not repair automatically.
