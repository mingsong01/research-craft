# Systems Performance Checks

Read only for systems or performance measurements.

Define the measured layer before running or interpreting a benchmark:

- logical data;
- serialized bytes;
- application payload;
- protocol traffic;
- wire traffic;
- memory;
- disk.

Specify KB versus KiB/MB versus MiB, per-operation versus cumulative, one-way versus bidirectional, metadata inclusion, serialization, compression, batching, cache state, warm-up, concurrency, timer placement, machine, and software version. Separate throughput, latency distribution, resource use, and correctness. An improvement in one layer or metric does not imply end-to-end improvement.

For an anomaly, first reproduce with the smallest stable workload, instrument boundaries, and vary one likely cause. Check workload drift, environment, cache, warm-up, concurrency, sampling, clock, and aggregation before attributing a mechanism.

Freeze workload-defining parameters before optimization: input distribution and size, request mix, concurrency/arrival process, cache state, dataset, query plan, batch size, payload, protocol, retries, timeouts, and correctness criteria. A benchmark result is invalid for comparison if an undisclosed change makes the workload easier.

Use production-relevant load shapes and distinguish latency percentiles from means, cold from warm behavior, offered from achieved load, throughput from goodput, and steady state from ramp-up. Measure saturation, queueing, tail latency, errors, drops, retries, resource utilization, and cost where they affect the decision. Randomize or interleave A/B run order when temporal drift is plausible.

Profile before optimizing. Localize CPU, memory/GC, I/O, database, network, serialization, lock/contention, or downstream wait time with the narrowest suitable instrumentation. Validate the improvement against an unchanged correctness oracle, the full relevant workload, and a performance budget or regression threshold.
