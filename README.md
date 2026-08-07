# Worker Workwear

**Version 1.0.0**

Worker Workwear is a TesmioLoader plugin for **Workers & Resources: Soviet Republic** that changes the game's dedicated manual-work worker appearance pool so the male worker variants use the two overall-clad materials instead of the shirt-and-trouser variants.

The change is visual only. It does not alter worker productivity, jobs, movement, pathfinding, animations, construction mechanics, or citizen clothing outside the dedicated manual-work renderer.

## What it changes

The manual-work renderer normally loads four male materials:

- `workers2/working2/muz1.mtl`
- `workers2/working2/muz2.mtl`
- `workers2/working2/muz3.mtl`
- `workers2/working2/muz4.mtl`

Worker Workwear redirects the two non-overall variants:

- `muz3` → `muz1`
- `muz4` → `muz2`

This leaves the native renderer, worker meshes, animations, positions, and selection logic intact while restricting the visible workwear to the two overall variants.

## Requirements

- Workers & Resources: Soviet Republic on 64-bit Windows
- TesmioLoader API 3
- The game must be launched through TesmioLoader

Version 1.0.0 was built and tested against **Workers & Resources: Soviet Republic v1.1.1.7**.

## Installation

Copy:

```text
worker_workwear.dll
```

into:

```text
Steam\steamapps\common\SovietRepublic\tesmioloader\build\plugins
```

Then launch the game through TesmioLoader and enable `worker_workwear.dll` if required by your TesmioLoader configuration.

Steam Workshop subscriptions place plugin files in the Workshop content directory; TesmioLoader plugins must still be copied into its `build\plugins` directory.

## Building from source

The repository includes the source and the TesmioLoader API header used to build the plugin.

Requirements:

- LLVM `clang-cl`
- LLVM `lld-link`

From the `source` directory, run:

```text
build_freestanding.cmd
```

The resulting `worker_workwear.dll` is a freestanding x64 DLL with no normal C runtime dependency.

## Repository

https://github.com/Ultimate-Universe/WRSR-TesmioLoader-WorkerWorkwear

## Licence

Worker Workwear is distributed under the **GNU General Public License version 3**. See `LICENSE.txt`.

Workers & Resources: Soviet Republic, TesmioLoader, Steam, and their respective names and assets belong to their owners. This project is not affiliated with or endorsed by 3DIVISION, Hooded Horse, Valve, or the TesmioLoader author.
