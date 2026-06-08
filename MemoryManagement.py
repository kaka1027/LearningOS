
class MemoryManager:
    def __init__(self, allocator):
        self.allocator = allocator

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


