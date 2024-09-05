#!/usr/bin/env python2.7

import os
import sys

def deduplicate_with_hardlinks(total_rows):
    spinner = ['|', '/', '-', '\\']
    spinner_index = 0
    rows_processed = 0

    # Read from stdin
    for line in sys.stdin:
        duplicates = line.strip().split()
        if len(duplicates) < 2:
            continue

        # The first file in the list will be kept as the original
        original_file = duplicates[0]
        if not os.path.exists(original_file) or not os.access(original_file, os.R_OK):
            sys.stderr.write("\nOriginal file %s does not exist or is not readable.\n" % original_file)
            continue

        # Replace all other files with hard links to the original
        for duplicate in duplicates[1:]:
            #test if the original file exists and is readable
            if not os.path.exists(original_file) or not os.access(original_file, os.R_OK):
                sys.stderr.write("\nOriginal file %s does not exist or is not readable.\n" % original_file)
                continue

            #test if the duplicated file exists and is writable
            if not os.path.exists(duplicate) or not os.access(duplicate, os.W_OK):
                sys.stderr.write("\nDuplicate file %s does not exist or is not writable.\n" % duplicate)
                continue

            #test if the duplicated file is a hardlink to the original file
            if os.path.samefile(original_file, duplicate):
                sys.stderr.write("\nDuplicate file %s is already a hardlink to the original file %s.\n" % (duplicate, original_file))
                continue

            try:
                # Remove the duplicate file before linking
                try:
                    os.remove(duplicate)
                except Exception as e:
                    sys.stderr.write("\nFailed to remove %s\n" % str(e))
                    continue

                # Create a hard link pointing to the original file
                os.link(original_file, duplicate)
            except Exception as e:
                sys.stderr.write("\nFailed to link %s to %s: %s\n" % (duplicate, original_file, str(e)))
                raise e

        # Update progress bar and spinner only after a certain number of rows
        rows_processed += 1
        if rows_processed % 10 == 0:  # Update every 10 rows
            progress = float(rows_processed) / total_rows * 100

            # Display progress and spinner
            sys.stderr.write("\r[{0:50s}] {1:.1f}% {2}".format('#' * int(progress / 2), progress, spinner[spinner_index]))
            sys.stderr.flush()

            spinner_index = (spinner_index + 1) % len(spinner)

    sys.stderr.write("\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python deduplicate.py <total_rows>\n")
        sys.exit(1)
