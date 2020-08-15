from microcli import microcli


@microcli
def main(in_file, out_file, *, create_new=False):
    """
    Read the contents of an input file and write to another file, adding
    '3==D~' to the end of each line.

    Args:
        in_file: Name of the source file.
        out_file: Name of the destination file.
        create_new: If this argument is present, create a new file.
    """
    pass


if __name__ == "__main__":
    main()
