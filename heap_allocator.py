# Adrian Potok
# 4/23/2023
# CS4541
# Project 3
# I implemented implicit first and implicit best fits.


def main():
    # I use globals so that the function signatures can match the assignment instructions, normally I would not do this, the instructions should be updated
    # so that this is not an ambigious problem
    global word_size, heap_size, max_heap_size, heap, pointers, zero_mask, fit

    word_size = 4
    heap_size = 1000
    max_heap_size = 100000

    heap = [0] * heap_size

    heap[0] = heap[999] = 0x00000001
    heap[1] = heap[998] = 0x00000F98

    pointers = {}

    zero_mask = ~1
    
    file_path = input("What is the file name?\n")

    fit = None
    while fit not in ["best", "first"]:
        fit = input("What fit would you like to use? (best or first)\n")

    allocations = read_input_file(file_path)

    for allocation in allocations:
        if allocation[0] == "a":
            size = int(allocation[1].strip())
            pointer_index = int(allocation[2].strip())
            pointers[pointer_index] = myalloc(size)
            
        elif allocation[0] == "f":
            myfree(pointers[int(allocation[1])])

        elif allocation[0] == "r":
            size = int(allocation[1].strip())
            pointer_index = int(allocation[3].strip())
            pointers[pointer_index] = myrealloc(pointers[int(allocation[2])], size)

    print_heap()

def read_input_file(file_path):
    # Open file
    with open(file_path, "r") as f:
        allocations = []

        # Read file
        for line in f.readlines():
            allocations.append(line.strip().split(","))

        # Return file contents
        return allocations
    
def myalloc(size):
    # Round the requested block size up to meet alignment requirements
    # This will be in the size of words
    rounded_size = ((size + ((2*word_size)-1) + (2*word_size)) // (2*word_size)) * 2

    # Find a free block large enough to fit the requested size
    free_block = find_free_block(rounded_size)

    # Make sure a block was found
    if free_block is None:
        return None

    # Split the free block into an allocated block and a free block
    split_block(free_block, rounded_size)

    # Return a pointer to the start of the allocated block, adding 1 block to skip the header
    return free_block + 1

def myrealloc(pointer_to_free, size):
    pointer = myalloc(size)

    # Get old payload size in words
    old_payload_size = int((heap[pointer_to_free - 1] & zero_mask) / word_size) - 2

    for i in range(0, old_payload_size):
        heap[pointer + i] = heap[pointer_to_free + i]

    myfree(pointer_to_free)
    return pointer

def myfree(pointer):
    if pointer not in pointers.values():
        raise PointerNotAllocatedError("The pointer has not been allocated.")
    
    # Subtract 1 block to get to the beginning of the header in words
    header_index = pointer - 1

    # Get size of allocated block in bytes
    size = (heap[header_index] & zero_mask)

    # Get footer index in words
    footer_index = header_index + int(size/word_size) - 1

    # Coalesce
    while True:
        coalesced = False

        # Case 1
        if(heap[header_index - 1] & 1 == 1 and heap[footer_index + 1] & 1 == 1 and heap[header_index] & 1 == 1):
            heap[header_index] = size & zero_mask
            heap[footer_index] = size & zero_mask

            coalesced = True

        # Case 2
        elif(heap[header_index - 1] & 1 == 1 and heap[footer_index + 1] & 1 == 0):
            next_block_size = (heap[footer_index + 1] & zero_mask)
            next_block_footer_index = footer_index + int(next_block_size / word_size)

            heap[header_index] = (size + next_block_size) & zero_mask
            heap[next_block_footer_index] = (size + next_block_size) & zero_mask 
        
            coalesced = True

            # Update footer index
            footer_index = next_block_footer_index
        # Case 3
        elif(heap[header_index - 1] & 1 == 0 and heap[footer_index + 1] & 1 == 1):
            previous_block_size = (heap[header_index - 1] & zero_mask)
            previous_block_header_index = header_index - int(previous_block_size / word_size)
            
            heap[previous_block_header_index] = (size + previous_block_size) & zero_mask
            heap[footer_index] = (size + previous_block_size) & zero_mask

            coalesced = True
                    
            # Update header index
            header_index = previous_block_header_index

        # Case 4
        elif(heap[header_index - 1] & 1 == 0 and heap[footer_index + 1] & 1 == 0):
            next_block_size = (heap[footer_index + 1] & zero_mask)
            previous_block_size = (heap[header_index - 1] & zero_mask)

            previous_block_header_index = header_index - int(previous_block_size / word_size)
            next_block_footer_index = footer_index + int(next_block_size / word_size)

            heap[previous_block_header_index] = (previous_block_size + size + next_block_size) & zero_mask
            heap[next_block_footer_index] = heap[previous_block_header_index]

            coalesced = True
        
            # Update header and footer indices
            header_index = previous_block_header_index
            footer_index = next_block_footer_index

        if not coalesced:
            break

        # Update size of block
        size = (heap[header_index] & zero_mask)
        
# Size is in words
def mysbrk(size):
    global heap_size, heap, max_heap_size

    # Calculate new desired heap size
    new_heap_size = heap_size + size

    # If the new heap size will be bigger than max allowable heap size, end simulation
    if new_heap_size > max_heap_size:
        raise ValueError("Heap size exceeds maximum size")
        
    # Create temporary new heap
    new_heap = [0] * new_heap_size 

    # Copy all items from old heap to temp heap
    for i in range(0, len(heap)):
        new_heap[i] = heap[i]

    # Copy temp heap into heap
    heap = new_heap

    # Initialize the header and footer of the free block that was just added
    new_heap[-(size + 1)] = (size) * word_size
    new_heap[-2] = (size) * word_size

    # Initalize place holder at end of heap
    new_heap[-1] = 1

    # Change global heap size
    heap_size = new_heap_size



# Helper functions
# This takes a size in the size of words
def find_free_block(size):
    if(fit == "first"):
        i = 1
        while i < heap_size - 1:
            # Check if the current block is free and large enough to fit the requested size
            if heap[i] & 1 == 0 and (heap[i] & zero_mask)/word_size >= size:
                return i
            
            # Increment by the size stored in the header to get to the next header
            i += int((heap[i] & zero_mask)/ word_size)

    elif(fit == "best"):
        best_fit_index = None
        i = 1
        while i < heap_size - 1:
            # Check if the current block is free and large enough to fit the requested size
            if heap[i] & 1 == 0 and (heap[i] & zero_mask)/word_size >= size:
                # If this is the first free block we found, set it as the best fit
                if best_fit_index is None:
                    best_fit_index = i
                # If this free block is smaller than the current best fit, update the best fit
                elif (heap[i] & zero_mask) < (heap[best_fit_index] & zero_mask):
                    best_fit_index = i
            
            # Increment by the size stored in the header to get to the next header
            i += int((heap[i] & zero_mask) / word_size)

        # If a best fit was found, return it
        if(best_fit_index is not None):
            return best_fit_index

    mysbrk(size)

    return heap_size - (size + 1)



# This takes a size in the size of words
def split_block(block_start, size):
    # Get remaining size in words
    remaining_size = int((heap[block_start] & zero_mask)/word_size) - size

    # If we have enough remaining room for a header and footer then set both the allocated and free block headers and footers
    if remaining_size >= 2:
        # Check if the remaining free block is just a header and footer with no free blocks in between
        if remaining_size == 2:
            # Add the header and footer to the allocated block
            heap[block_start] = ((word_size * (size + 2))) | 1
            heap[block_start + size + 1] = ((word_size * (size + 2))) | 1

        else:
            # Set the header and footer of the allocated block
            heap[block_start] = (word_size * size) | 1
            heap[block_start + size - 1] = (word_size * size) | 1

            # Set the header and footer of the remaining free block
            heap[block_start + size] = word_size * remaining_size
            heap[block_start + size + remaining_size - 1] = word_size * remaining_size

    elif remaining_size == 0:
        heap[block_start] = ((word_size * size)) | 1
        heap[block_start + size - 1] = ((word_size * size)) | 1


def print_heap():
    i = 0
    while i < heap_size:
        if(heap[i] != 0):
            print(f"{i}, 0x{format(heap[i], '08x').upper()}")
        else:
            print(f"{i}, ")
        i += 1

def write_output(output_file_path):
    with open(output_file_path, 'w') as f:
        i = 0
        while i < heap_size:
            if(heap[i] != 0):
                f.write(f"{i}, 0x{format(heap[i], '08x').upper()}\n")
            else:
                f.write(f"{i}, \n")
            i += 1
    

class PointerNotAllocatedError(Exception):
    pass

main()