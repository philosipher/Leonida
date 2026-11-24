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
| `python -I scripts/check_no_game_data.py` | Pass with Python 3.14.10 on pinned `main` `2ebde81ec07e530a3558bc3f7c4b79da6c37ab65` and the pre-rebase tree based on `765b138426974fd6b44029680d3288f0d03aac0d`; with no path argument, the scanner checked tracked files. |
| `node --test tests/test_viewer_streaming.cjs` | 56/57 pass on Node 26.13.0. `Shift speeds the camera up and Ctrl slows it down, on either side of the keyboard` fails because `AbortController` is missing from the test VM context. |
| `python -I scripts/run_semantic_tests.py tests/semantic -j 1 -p test_exec_computed.py` | Fails on the wave32 and wave64 computed-EXEC expected words; 2 tests ran. Tracked as [#6](https://github.com/LeonidaReforge/Leonida/issues/6). |

The viewer and computed-EXEC corrections were included in [PR #54](https://github.com/LeonidaReforge/Leonida/pull/54), merged into `integration/ci-recovery`, then included in the partial recovery merge [PR #103](https://github.com/LeonidaReforge/Leonida/pull/103) to `main` at `e2c26c0`. The failures above remain observations on the earlier `2ebde81` baseline; they do not verify the fixes on current `main`. See [#20](https://github.com/LeonidaReforge/Leonida/issues/20) and [#103](https://github.com/LeonidaReforge/Leonida/pull/103) for the recovery scope and its latest validation status.

## Host prerequisites not available

The following commands cannot be run on this host until their tools are installed:

- `dotnet build tools/rpf9dump/rpf9dump.csproj -c Release`: .NET SDK is missing.
- `cargo test --locked` / Rust calibration builds: Cargo is missing.
- CMake runtime build and CTest: CMake, Ninja and the MSVC C++ compiler are missing.
- GPU shader build and validation: `llvm-mc`, `spirv-as`, `spirv-val` and `glslangValidator` are missing. `vulkaninfo` is present, but the runtime and shader-test binaries have not been built here.

This prevents local native-runtime, XMA2, and GPU-suite validation. It does not prevent the Python compile/help checks, the no-game-data check, the viewer test, or focused source-only semantic tests above. The repository's full workflow commands and platform-specific setup remain in [testing.md](testing.md) and [AGENTS.md](../AGENTS.md).
