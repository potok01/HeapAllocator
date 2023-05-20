import os

def test_first():
    # path to the first group of files
    group1_path = "examples/"
    
    # path to the second group of files
    group2_path = "first_output/"

    for i in range(1, 12):
        # generate file paths for the first group of files
        group1_file_path = os.path.join(group1_path, str(i) + ".implicit.first.out")
        
        # generate file paths for the second group of files
        group2_file_path = os.path.join(group2_path, "my." + str(i) + ".implicit.first.out")
        
        # compare the two files
        print("Comparing files {} and {}".format(group1_file_path, group2_file_path))
        compare_files(group1_file_path, group2_file_path)

def test_best():
    # path to the first group of files
    group1_path = "examples/"
    
    # path to the second group of files
    group2_path = "best_output/"

    for i in range(1, 12):
        # generate file paths for the first group of files
        group1_file_path = os.path.join(group1_path, str(i) + ".implicit.best.out")
        
        # generate file paths for the second group of files
        group2_file_path = os.path.join(group2_path, "my." + str(i) + ".implicit.best.out")
        
        # compare the two files
        print("Comparing files {} and {}".format(group1_file_path, group2_file_path))
        compare_files(group1_file_path, group2_file_path)

def compare_files(file1_path, file2_path):
    with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
        f1_contents = f1.read().splitlines()
        f2_contents = f2.read().splitlines()
        num_lines = min(len(f1_contents), len(f2_contents))

        for i in range(num_lines):
            if f1_contents[i] != f2_contents[i]:
                print("Difference at line {}:".format(i+1))
                print("{}: {}".format(file1_path, f1_contents[i]))
                print("{}: {}".format(file2_path, f2_contents[i]))
                print()

        if len(f1_contents) != len(f2_contents):
            print("Files have different number of lines.")
            print("{} has {} lines.".format(file1_path, len(f1_contents)))
            print("{} has {} lines.".format(file2_path, len(f2_contents)))
        else:
            print("The files {} and {} are the same.".format(file1_path, file2_path))

test_best()
