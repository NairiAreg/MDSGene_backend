import argparse
import os

# Create the argument parser
parser = argparse.ArgumentParser(
    description="Process directories from terminal arguments."
)

# Add arguments
parser.add_argument("dir1", type=str, help="First directory path")
parser.add_argument("dir2", type=str, help="Second directory path")

# Parse arguments
args = parser.parse_args()

# Get the directories
dir1 = args.dir1
dir2 = args.dir2

# Print the directories and list their contents
print(f"First directory: {dir1}")
print(f"Second directory: {dir2}")

print("\nContents of first directory:")
print(os.listdir(dir1))

print("\nContents of second directory:")
print(os.listdir(dir2))
