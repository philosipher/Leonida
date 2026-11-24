# Local CI baseline

Snapshot taken 2026-11-24 on Windows, against `main` at
`2ebde81ec07e530a3558bc3f7c4b79da6c37ab65` (matching `origin/main` at the check).
These checks used source code and synthetic tests only; they did not read game files.
Results describe this commit and host, not the current state of later branches.

## Verified here

| Command | Result |
|---|---|
| `python -m compileall -q make_game.py tools tests` | Pass. Ran with CPython 3.14.6 embeddable; CI uses Python 3.12. |
| `python -I make_game.py --help` | Pass. |
| `python -I scripts/check_no_game_data.py .` | Pass. |
| `node --test tests/test_viewer_streaming.cjs` | 56/57 pass on Node 26.13.0. `Shift speeds the camera up and Ctrl slows it down, on either side of the keyboard` fails because `AbortController` is missing from the test VM context. |
| `python -I scripts/run_semantic_tests.py tests/semantic -j 1 -p test_exec_computed.py` | Fails on the wave32 and wave64 computed-EXEC expected words; 2 tests ran. Tracked as [#6](https://github.com/LeonidaReforge/Leonida/issues/6). |

The viewer failure and computed-EXEC correction are included in [PR #54](https://github.com/LeonidaReforge/Leonida/pull/54), which is open against `integration/ci-recovery`; they are not part of the `main` commit tested above. The combined recovery is tracked by [#20](https://github.com/LeonidaReforge/Leonida/issues/20) and [draft PR #103](https://github.com/LeonidaReforge/Leonida/pull/103). Check those threads for newer CI results before treating any fix as integrated or verified on the combined branch.

## Host prerequisites not available

The following commands cannot be run on this host until their tools are installed:

- `dotnet build tools/rpf9dump/rpf9dump.csproj -c Release`: .NET SDK is missing.
- `cargo test --locked` / Rust calibration builds: Cargo is missing.
- CMake runtime build and CTest: CMake, Ninja and the MSVC C++ compiler are missing.
- GPU shader build and validation: `llvm-mc`, `spirv-as`, `spirv-val` and `glslangValidator` are missing. `vulkaninfo` is present, but the runtime and shader-test binaries have not been built here.

This prevents local native-runtime, XMA2, and GPU-suite validation. It does not prevent the Python compile/help checks, the no-game-data check, the viewer test, or focused source-only semantic tests above. The repository's full workflow commands and platform-specific setup remain in [testing.md](testing.md) and [AGENTS.md](../AGENTS.md).
