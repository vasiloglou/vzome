# Pitfall Research: v1.3 Zomic-Native Local Checkpoint MVP

## Main Risks

- registering checkpoints without enough provenance to reproduce them later
- comparing adapted checkpoints against a different benchmark context than the
  baseline lane
- treating one adapted checkpoint success as proof that training automation is
  ready for scale
- hiding checkpoint incompatibility behind late runtime failures
- claiming Zomic-native improvement without a concrete validity or
  compile/conversion acceptance surface

## Prevention

- make checkpoint lineage mandatory and typed
- require shared benchmark context for adapted-vs-baseline claims
- keep training automation explicitly out of scope for this milestone
- fail early on incompatible registration or load attempts
- document rollback to baseline lanes as an operator-first workflow
