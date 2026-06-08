# LearningOS

LearningOS is a small Python project for experimenting with operating-system memory allocation. It simulates processes requesting and releasing fixed-size memory blocks, then visualizes how the allocator uses a 256-block memory space while running predefined task sequences.

## What This Project Contains

- `AllocationAPI.py` defines the basic simulation objects:
  - `Process`: stores a process id, requested block size, duration, and assigned memory range.
  - `MemoryAllocator`: owns the memory array and exposes allocation, free, and memory-view operations.
- `MemoryManagement.py` implements the allocation strategy used by the simulation.
- `TaskDefine.py` contains predefined task sequences made from process allocation and free events.
- `Tester.py` runs all tasks, displays memory usage, and reports allocation failures and task scores.
- `TaskAbilityTest.py` calculates peak memory usage for one task.

## Requirements

- Python 3.x
- No third-party dependencies are required.

## Quick Start

Run the visual task tester:

```bash
python Tester.py
```

Run the peak-memory helper:

```bash
python TaskAbilityTest.py
```

## How It Works

The simulation uses a fixed memory size of 256 blocks. Each task is a sequence of process events:

- Allocation event: a process requests a number of contiguous memory blocks.
- Free event: a process releases the blocks it previously held.

`MemoryManager.allocate()` currently uses a compacting strategy:

1. Read all currently allocated processes from the allocator.
2. Free those processes temporarily.
3. Repack them from the start of memory.
4. Allocate the new process after the compacted region.
5. Raise an allocation failure if there is not enough contiguous memory.

The tester catches allocation failures, updates the score for each task, and prints a simple text view of memory where `X` means an occupied block.

## Project Structure

```text
.
├── AllocationAPI.py
├── MemoryManagement.py
├── TaskAbilityTest.py
├── TaskDefine.py
├── Tester.py
└── README.md
```

## Notes

- `TaskDefine.memory_size` and `AllocationAPI.memory_size` are both set to `256`.
- The current implementation focuses on contiguous allocation and compaction.
- `Tester.py` clears the terminal while running so the memory view appears animated.
