from microcli import microcli
import sys, os


@microcli
def main(in_file, out_file, /, *flags, create_new=False, **options):
    """
    Read the contents of an input file and write to another file, adding
    ':)' to the end of each line.

    Args:
        in_file: Name of the source file.
        out_file: Name of the destination file.
        create_new: If this argument is present, create a new file.
    """
    mode = "w+" if create_new else "w"

    with open(in_file) as i_f:
        with open(out_file, mode) as o_f:
            for line in i_f:
                o_f.write(f"{line.strip()} :)\n")


if __name__ == "__main__":
    main(sys.argv)
