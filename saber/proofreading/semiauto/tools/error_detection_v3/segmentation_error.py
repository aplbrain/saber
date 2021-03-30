from typing import List
import numpy as np
from intern import array
import json
import uuid

class SegmentationError:
    def __init__(self,
                 host: str,
                 collection: str,
                 experiment: str,
                 channel_seg: str,
                 channel_em: str,
                 error_type: str,
                 centroid: List = None,
                 centroid_id=None,
                 x_bounds: List = None,
                 y_bounds: List = None,
                 z_bounds: List = None,
                 binary_error_mask: np.array = None):
        # create unique ID
        self.uuid = f"{collection}&{experiment}&{channel_seg}" + str(uuid.uuid4())[-6:]

        # data information
        self.collection = collection
        self.experiment = experiment
        self.channel_segmentation = channel_seg
        self.channel_em = channel_em
        self.host = host

        # error information
        self.error_type = error_type
        # single coordinate pointing to the error
        self.centroid = centroid
        self.centroid_id = centroid_id
        # extent of a volume that contains the error
        self.volume_extent_x = x_bounds
        self.volume_extent_y = y_bounds
        self.volume_extent_z = z_bounds
        # binary mask that contains the error
        self.binary_error_mask = binary_error_mask

        self.colocarpy_vol_id = None
        self.keypoint_nodes: List = None
        self.keypoint_ids: List = None

        if self.centroid is None:
            if self.volume_extent_x is not None:
                self.get_centroid_from_extent()
            else:
                raise ValueError('Must provide either a centroid or xyz bounds for the error')

        if self.centroid_id is None:
            self.centroid_id = self.get_id_from_coordinate(self.centroid[0], self.centroid[1], self.centroid[2])

        self.ng_link = self.generate_ng_link()

        return

    def get_centroid_from_extent(self):
        x = self.volume_extent_x[0] + ((self.volume_extent_x[1] - self.volume_extent_x[0])/2)
        y = self.volume_extent_y[0] + ((self.volume_extent_y[1] - self.volume_extent_y[0]) / 2)
        z = self.volume_extent_z[0] + ((self.volume_extent_z[1] - self.volume_extent_z[0]) / 2)
        self.centroid = [x, y, z]
        return

    # removed colocard function for now. 
    # def update_keypoints_from_colocard(self, c_args: ColocArgs):
    #     nodes = c_args.c.get_nodes({"type": self.error_type, "volume": self.colocarpy_vol_id, 'active': True,
    #                                 'author': c_args.author})
    #     self.keypoint_nodes = nodes.coordinate

    #     self.get_ids_from_keypoint_nodes()
    #     return

    def get_ids_from_keypoint_nodes(self):
        self.keypoint_ids = []
        for centroid in self.keypoint_nodes:
            self.keypoint_ids.append(self.get_id_from_coordinate(centroid[0], centroid[1], centroid[2]))
        return

    def get_id_from_coordinate(self, x, y, z):
        z = int(z)
        y = int(y)
        x = int(x)
        cutout_array = array(f"boss://{self.collection}/{self.experiment}/{self.channel_segmentation}")
        cutout_data = cutout_array[z - 1:z + 1, y - 1:y + 1, x - 1:x + 1]
        return cutout_data[z - (z - 1), y - (y - 1), x - (x - 1)]

    def generate_ng_link(self, source="boss://"):
        segsource = source + f'{self.host}/{self.collection}/{self.experiment}/{self.channel_segmentation}'
        emsource = source + f'{self.host}/{self.collection}/{self.experiment}/{self.channel_em}'
        state = {
            "layers": [
                {
                    "source": segsource,
                    "type": "segmentation",
                    "name": "seg",
                    "selectedAlpha": 0.3
                },
                {
                    "source": emsource,
                    "type": "image",
                    "name": "em"
                },
            ],
            "navigation": {
                "pose": {
                    "position": {
                        "voxelCoordinates": [
                            self.centroid[2],
                            self.centroid[1],
                            self.centroid[0]
                        ],
                    },
                },
                "zoomFactor": 8,
            },
            "showAxisLines": False,
            "layout": "xy",
        }

        return "https://neuroglancer.bossdb.io/#!" + json.dumps(state)