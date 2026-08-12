# Worker Workwear

**Version 1.1.0**

Worker Workwear is a TesmioLoader plugin for **Workers & Resources: Soviet Republic** that restricts the game's dedicated manual-work male worker appearance pool to the two overall-clad material variants.

The change is visual only. It does not alter productivity, workplaces, jobs, movement, pathfinding, animations, construction mechanics, citizen inventories, or ordinary citizen clothing.

## What it changes

The manual-work renderer loads four male materials:

- `workers2/working2/muz1.mtl`
- `workers2/working2/muz2.mtl`
- `workers2/working2/muz3.mtl`
- `workers2/working2/muz4.mtl`

Worker Workwear redirects the two shirt-and-trouser variants:

- `muz3` to `muz1`
- `muz4` to `muz2`

The native meshes, animations, positions, and selection logic remain unchanged.

## Requirements

- Workers & Resources: Soviet Republic v1.1.1.9
- 64-bit Windows
- TesmioLoader b0.3.5 / API 4
- The game must be launched through TesmioLoader

No DLC is required. The plugin uses the game's existing base worker materials and does not add external assets.

## Installation

Copy `Mod Files/plugins/worker_workwear.dll` into:

```text
Steam\steamapps\common\SovietRepublic\tesmioloader\build\plugins
```

Ensure the plugin is enabled in `tesmioloader.ini`:

```ini
[plugins]
worker_workwear=1
```

Then launch WRSR through `tesmiolauncher.exe`.

Steam Workshop cannot directly replace files inside the TesmioLoader installation. After a Workshop update, copy the current DLL from the subscribed Workshop item into `tesmioloader\build\plugins` again.

## Configuration

Worker Workwear has no gameplay settings or hotkeys. It is enabled or disabled through the TesmioLoader plugin list.

## Compatibility

Version 1.1.0 was validated in-game with WRSR v1.1.1.9 and the supplied TesmioLauncher b0.3.5/API 4.

The plugin patches the current `C3D_MATERIAL::Load` import through TesmioLoader and preserves the function already present in the import slot. This permits normal hook chaining with other plugins that use the same import-patching mechanism.

The hook is intentionally narrow: only paths ending in the two dedicated manual-worker material names are redirected. Unrelated material loads pass through unchanged.

## Troubleshooting

The TesmioLoader log should report:

```text
workwear  init v1.1.0 - WRSR 1.1.1.9 / API 4
workwear  installed v1.1.0 - muz3/muz4 redirected to muz1/muz2
```

The first use of each affected material also records a one-time redirect message. If the log contains `workwear  FAILED`, confirm that the game version and TesmioLoader version meet the requirements and include `tesmioloader.log` when reporting the problem.

## Building from source

The complete reproducible plugin source is in `source`.

Requirements:

- LLVM `clang-cl`
- LLVM `clang`
- LLVM `lld-link`
- Python 3

Run `source/build_freestanding.cmd` from a Windows LLVM command environment. It produces `source/worker_workwear.dll` and removes intermediate object files.

The build is a native x64 DLL without a C runtime dependency. `finalize_pe.py` adds the release version resource, normal Windows version declarations, and PE checksum.

## Repository

https://github.com/Ultimate-Universe/WRSR-TesmioLoader-WorkerWorkwear

## Licence

Worker Workwear is distributed under the **GNU General Public License version 3**. See `LICENSE.txt`.

Workers & Resources: Soviet Republic, TesmioLoader, Steam, and their respective names and assets belong to their owners. This project is not affiliated with or endorsed by 3DIVISION, Hooded Horse, Valve, or the TesmioLoader author.
