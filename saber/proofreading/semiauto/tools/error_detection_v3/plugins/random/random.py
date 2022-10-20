"""
Baseline Error Detection Algorithm. 

Creates random bounding boxes and IDs for errors.
"""
import numpy as np 

def run(segmentation_data, image_data, *args, **kwargs):
    shape = np.array(kwargs['shape'])
    num_of_bboxes = int(kwargs['num_of_bboxes'])
    extents = segmentation_data.shape
    return generate_random_bboxes(shape, extents, num_of_bboxes)

def generate_random_bboxes(shape, extents, n=1):
    """
    Generate n number of random bounding boxes in the data. Useful for testing purposes.

    shape (tuple[int]): shape of the data
    extents (tuple(int))
    """
    bboxes = []
    for i in range(n):
        x_max = extents[0] - shape[0]
        y_max = extents[1] - shape[1]
        z_max = extents[2] - shape[2]

        x_start = np.random.randint(x_max)
        y_start = np.random.randint(y_max)
        z_start = np.random.randint(z_max)

        bboxes.append(
            (
                [x_start, x_start+shape[0]],
                [y_start, y_start+shape[1]],
                [z_start, z_start+shape[2]]
            )
        )
    return bboxes