# Local checks and reproducibility

The 1.3.1-rc.1 candidate uses workspace schema 1. Run these commands from the installable Skill directory:

```text
python -B -m unittest discover -s tests -v
python -B evals/run_evals.py
python -B demo/run_demo.py
```

| Check | Coverage |
| --- | --- |
| 110 engineering tests | Record/data helpers, compatibility and diagram regressions |
| 60 offline contracts | Required behaviors and failure conditions |
| End-to-end demo | A tracked investigation using the bundled tools |
| Fresh archive extraction | File integrity and execution outside the source directory |
| Figure rendering | Actual previews alongside editable vector sources |

The public repository's `verification/local-checks.json` records the checked archive and results; `verification/FILES.sha256` lists file hashes. These paths are relative to the repository root. Checks run locally. The workflow within the Skill's `.github/` directory is a sample, not an active root workflow.

Engineering checks cover implementation and contracts. Scientific writing, model topology and visual quality require review of the actual task's inputs and outputs. See [known limits](PUBLISHING_SNAPSHOT.md) and the separate [historical evaluation](EVALUATION_SUMMARY.md).
