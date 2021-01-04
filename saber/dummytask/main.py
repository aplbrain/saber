import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--mode', help='(Required) The mode to run the performer in. {"train", "test"}')
    parser.add_argument(
        '--params_file', help='(Optional) a file with saved parameters in it.')
    parser.add_argument(
        '--images_dir', help='(Required) The path to the directory with the images in it. To access an image, prepend this to the image path.')
    parser.add_argument(
        '--data_file', help='(Required) The path to the file from which to read task data information (e.g., image filenames, labels).')
    parser.add_argument(
        '--output_file', help='(Required) The path to the file to write output to.')
    args = parser.parse_args()

    print("Arguments", args)

    with open(args.data_file) as datafile:
        data = datafile.read()


    with open(args.output_file, 'w') as output:
        output.write(data)