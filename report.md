# Memory Management Assessment Report

## Question 1: Implementing the Algorithm

I implemented the memory allocation algorithm in `MemoryManagement.py`. The algorithm uses memory compaction before each allocation. After running `Tester.py`, all five test cases completed successfully with no allocation failures.

The testing results are shown below:

| Test Case | Error Number | Score |
| --- | ---: | ---: |
| Task 1 | 0 | 10 |
| Task 2 | 0 | 10 |
| Task 3 | 0 | 10 |
| Task 4 | 0 | 10 |
| Task 5 | 0 | 10 |
| **Total** | **0** | **50 / 50** |

The code of the `allocate()` function in the `MemoryManager` class is:

```python
def allocate(self, process, request_size):
    memory_view = self.allocator.memory_view()

    processes = []
    seen = set()

    for current_process in memory_view:
        if current_process is not None and id(current_process) not in seen:
            seen.add(id(current_process))
            length = current_process.get_memory()[1]
            processes.append((current_process, length))

    for current_process, length in processes:
        self.allocator.free_memory(current_process)

    block_start = 0

    for current_process, length in processes:
        self.allocator.allocate_memory(block_start, length, current_process)
        block_start += length

    if block_start + request_size > len(memory_view):
        raise AssertionError('no enough contiguous memory')


    self.allocator.allocate_memory(block_start, request_size, process)
```

This function first reads the current memory state using `memory_view()`. It scans the memory array and records each active process only once, together with the size of its current allocation. Then it frees all recorded processes and reallocates them from address `0` onward. This compacts the used memory to the front of the memory space and leaves one continuous free area after the last active process. After compaction, `block_start` represents the beginning of that free area. The function then checks whether the requested memory size can fit into the remaining memory. If there is enough space, the process is allocated starting from `block_start`. If there is not enough space, an assertion error is raised, and the allocation is counted as failed by the tester.

## Question 2: Designing the Algorithm

My memory allocation algorithm is based on memory compaction. Instead of using a traditional placement strategy such as first-fit, best-fit, or worst-fit, the algorithm reorganizes memory before every new allocation. The main idea is to move all currently allocated processes to the beginning of memory, while preserving their existing order. After this compaction step, all free memory is combined into one large contiguous block at the end of memory. The new process can then be allocated directly after the last occupied block.

The algorithm is implemented directly inside `allocate()`. The function first reads the current memory state by calling `self.allocator.memory_view()`. Since each allocated process may occupy multiple memory blocks, the function scans the memory array and records each active process only once. A `seen` set is used to avoid adding the same process repeatedly. For each unique process, the algorithm stores both the process object and its allocated length, which is obtained from `current_process.get_memory()[1]`. After collecting all active processes, the function frees them from memory and reallocates them from address `0` onward. During this process, `block_start` is updated to represent the next available memory position. When compaction finishes, `block_start` points to the beginning of the large continuous free area.

After rebuilding the compacted memory layout, `allocate()` checks whether the remaining memory is large enough for the new request:

```python
if block_start + request_size > len(memory_view):
    raise AssertionError('no enough contiguous memory')
```

If the request can fit into the remaining memory, the function allocates the new process at `block_start`:

```python
self.allocator.allocate_memory(block_start, request_size, process)
```

This means that after compaction, allocation will succeed as long as the total remaining memory is sufficient. The algorithm does not need to search through many separate holes because all free memory has already been merged into one continuous region.

In Python, I implemented this design by using the public API provided by the framework. I did not directly modify the private memory array inside `MemoryAllocator`. Instead, I used `memory_view()` to inspect the current memory state, `free_memory()` to release existing allocations, and `allocate_memory()` to assign memory blocks again. This keeps the implementation consistent with the simulator framework.

One challenge was that each process appears multiple times in `memory_view()` because every memory block occupied by a process stores a reference to that process. If the algorithm simply recorded every non-empty memory cell, the same process would be freed and reallocated multiple times, causing errors. I solved this by using `id(process)` and a `seen` set to make sure each active process is recorded only once.

Another challenge was preserving the correct size of each allocated process during compaction. The algorithm stores the process objects before freeing memory, and then uses each process's recorded memory length when reallocating it. This allows the memory layout to be rebuilt correctly after compaction.

This algorithm performs well in the simulator because it removes scattered free holes before every allocation. In my testing, all five test cases had zero allocation failures, so each test case received a score of 10. The total score for the five test cases was therefore 50 out of 50. The main disadvantage of this approach is that compaction can be expensive because it may move every allocated process during each allocation. In a real operating system, moving allocated memory would require updating addresses and could affect running processes. However, in this simulation framework, compaction is an effective way to avoid allocation failure caused by external fragmentation.

## Question 3: Discussion of Internal and External Fragmentation

The memory allocation problem in this project is mainly related to external fragmentation rather than internal fragmentation. This is because the simulator requires each process to be allocated a continuous sequence of memory blocks. When memory has been used for a period of time, processes may be allocated and released in different orders. As a result, the free memory may become separated into many small holes between allocated processes. Even if the total amount of free memory is enough for a new process, the allocation can still fail if there is no single continuous free region large enough to satisfy the request. This situation is the typical problem of external fragmentation.

External fragmentation occurs outside allocated memory blocks. It describes the situation where free memory exists, but it is divided into small non-contiguous pieces. For example, a system may have 80 free memory blocks in total, but these blocks may be split into several small gaps, such as 20 blocks, 25 blocks, and 35 blocks. If a new process requests 60 continuous blocks, the allocation will fail, even though the total free memory is greater than 60. The reason is that the allocator cannot combine separated holes unless the system performs compaction or uses a non-contiguous memory management technique.

Internal fragmentation is different. Internal fragmentation occurs inside allocated memory blocks. It happens when the system allocates more memory to a process than the process actually needs. The unused part of the allocated region is wasted because it belongs to that process and cannot be used by other processes. This usually happens in systems that use fixed-size partitions or fixed-size pages. For example, if memory is allocated in units of 16 blocks and a process only needs 10 blocks, the remaining 6 blocks inside that allocation are wasted. That waste is internal fragmentation.

In this simulator, internal fragmentation is not the main concern because each process receives exactly the number of memory blocks it requests. The allocation function does not round the request up to a larger fixed partition. Therefore, there is little or no unused space inside each allocated process region. The main issue is whether the available free memory is continuous enough to satisfy future requests.

My implementation addresses external fragmentation by using memory compaction before every allocation. The algorithm first scans the current memory view, records all active processes, frees them, and then reallocates them from the beginning of memory in order. After this process, all allocated memory is grouped together at the front, and all free memory becomes one large continuous area at the end. Therefore, the allocator can avoid failures caused by scattered free holes. In this project, the question is mainly about external fragmentation because the success of allocation depends on the availability of contiguous free memory, not on wasted space inside allocated regions.

## Question 4: Discussion of External Fragmentation

External fragmentation is an important issue in contiguous memory allocation systems, and it is directly related to the behavior tested in this project. In the provided simulator, every process requests a specific number of continuous memory blocks. Over time, processes are allocated and freed in different orders. This naturally creates holes in memory. Some holes may be small, while others may be located between active processes. When these holes are separated from each other, the allocator may not be able to use them for a large request, even if the total free memory is sufficient. This is the main way external fragmentation can reduce allocation success.

Based on my implementation and the testing results, my algorithm successfully reduces external fragmentation by performing memory compaction before each new allocation. The compaction process moves all currently allocated processes to the beginning of memory and places them next to each other. After that, all remaining free memory is combined into one continuous block at the end of memory. This design means that a new allocation will fail only when the total remaining free memory is not large enough. It will not fail simply because the free memory is scattered. In my testing, this approach allowed all five test cases to complete with zero allocation failures.

The aspect of the original memory allocation problem that contributes most to external fragmentation is the repeated freeing of processes in the middle of memory. When a process is released, it leaves behind a free hole. If the surrounding processes are still active, that hole cannot be combined with other free areas. Later allocations may fill some holes but leave smaller unusable spaces behind. Over many allocation and free operations, memory can become increasingly fragmented. Variable-sized requests make this worse because different processes need different amounts of memory. A small request may occupy part of a large free hole, leaving behind a smaller fragment that may not be useful for future larger requests.

In my current implementation, this problem is reduced by compaction, but compaction has an important limitation in a real operating system. Moving already allocated memory blocks can be expensive and complicated. The system would need to update memory addresses and make sure that running processes still access the correct data. Because of this, although compaction is effective in the simulator, real systems often use other strategies to control external fragmentation without moving allocated blocks.

One possible method is to use a better placement strategy. For example, a best-fit algorithm chooses the smallest free block that is large enough for the request. This can reduce wasted space in larger holes, although it may also create many very small holes. A first-fit algorithm is simpler and faster because it chooses the first suitable free block. In some situations, first-fit can perform well because it avoids searching the whole memory space every time. A worst-fit algorithm uses the largest available hole, with the aim of leaving behind a reasonably large remaining free block. Each strategy has advantages and disadvantages, but the choice of placement policy affects how quickly external fragmentation develops.

Another important method is free-space coalescing. When a process is freed, the allocator should check whether the neighboring memory regions are also free. If they are, the allocator can merge them into a larger free block. This does not require moving allocated processes, but it helps reduce fragmentation by combining adjacent holes. Coalescing is especially useful when many processes terminate over time because it prevents the free list from being filled with many small separate entries.

A more structured solution is to use a buddy allocation system. In a buddy system, memory is divided into blocks whose sizes are powers of two. When memory is allocated, a larger block can be split into two smaller buddy blocks. When memory is freed, two free buddy blocks can be merged back into a larger block. This makes coalescing easier and more systematic. The buddy system can still have some internal fragmentation because requests may be rounded up to a power-of-two size, but it helps control external fragmentation and keeps memory management efficient.

The most effective system-level solution is to use paging. Paging removes the requirement that a process must occupy one continuous physical memory region. Instead, a process is divided into fixed-size pages, and physical memory is divided into frames. The pages of a process can be stored in different frames across memory. Because the process no longer needs a single contiguous block, external fragmentation is largely eliminated. Paging may introduce some internal fragmentation in the last page of a process, but it is widely used because it makes memory allocation more flexible and reliable.

Overall, external fragmentation is caused by the separation of free memory into many small holes. In my implementation, memory compaction greatly reduces this problem and leads to successful results in the simulator. However, if moving already allocated memory blocks is not allowed, the system should reduce external fragmentation through careful placement policies, immediate coalescing of adjacent free blocks, structured allocation methods such as the buddy system, or non-contiguous memory management methods such as paging. These techniques make the memory manager more practical for real operating systems while still addressing the main cause of allocation failure in contiguous memory allocation.
