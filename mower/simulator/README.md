# Mower simulator — unbuilt prototype

A rigid-body simulation of the mower driving over a patch of grass, written
twice: once in C++ (`cpp/`) and once in Python (`python/`).

> **Status: source only. Nothing here is built, packaged, or tested, and CI
> does not compile it.** The gates in `tests/` check that these files parse and
> that this README does not overstate them — not that the simulator runs.
> Treat it as a sketch you can pick up, not a tool you can use today.

## What is actually here

| Path | Lines | What it is |
|---|---|---|
| `cpp/main.cpp` | 471 | Native sim — [raylib](https://www.raylib.com/) for rendering, [Bullet](https://pybullet.org/) for physics |
| `cpp/main_web.cpp` | 368 | The same sim retargeted at Emscripten/WASM |
| `cpp/CMakeLists.txt` | 21 | Builds `mowbot_sim` from `main.cpp`; `find_package(Bullet REQUIRED)` + `find_package(raylib REQUIRED)` |
| `cpp/build_wasm.sh` | 22 | `emcc` invocation for the web build |
| `cpp/shell.html` | 62 | Emscripten shell page for the WASM build |
| `python/main.py` | 220 | Earlier prototype on [PyBullet](https://pybullet.org/), GUI mode |

## Why it does not run as-is

Three things are missing, and all three are the reader's to supply:

1. **The mesh is not in this repo.** Both implementations load a file called
   `mowbot.stl` (`cpp/main.cpp:133`, `cpp/main_web.cpp:134`,
   `python/main.py:43`, and `--preload-file mowbot.stl` in
   `cpp/build_wasm.sh`). No `mowbot.stl` is checked in anywhere — the chassis
   meshes in `../` are named `mowbot3-Body.stl`, `mowbot4-Body.stl` and so on.
   The Python version degrades to a box and says so; the C++ version only logs
   the failure. Export or rename a chassis mesh to `mowbot.stl` next to the
   binary.
2. **`cpp/build_wasm.sh` has placeholder paths.** `RAYLIB_PATH` and
   `BULLET_PATH` are literally `path/to/raylib` and `path/to/bullet`.
3. **Both need a display.** raylib opens a window; PyBullet connects with
   `p.GUI`. Neither has a headless mode, which is the reason CI cannot run
   either one.

## If you want to pick it up

```sh
# native
cd cpp && cmake -B build && cmake --build build && ./build/mowbot_sim

# python
pip install pybullet numpy && cd python && python3 main.py
```

Neither command has been verified from a clean checkout on a machine that is
not the original author's — if you get one working, say so here and add a gate
for it.
