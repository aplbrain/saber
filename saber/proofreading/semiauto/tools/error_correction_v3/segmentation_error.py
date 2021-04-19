from typing import List, Tuple
import numpy as np
from intern import array
import json
import uuid

class SegmentationError:
    def __init__(self,
                 host: str,
                 seg_uri: str,
                 image_uri: str,
                 resolution: int,
                 error_type: str,
                 loc: List=None,
                 ids: Tuple=None,
                 x_bounds: List=None,
                 y_bounds: List=None,
                 z_bounds: List=None,
                 binary_error_mask: np.array=None):
        
        # data information
        self.host = host
        self.seg_uri = seg_uri
        self.image_uri = image_uri
        self.resolution = resolution

        # Get parts of URI for UUID
        protocol, path = seg_uri.split("://")
        if "boss" in protocol:
            col, exp, chan = path.split('/')[:3]
            self.seg_col = col
            self.seg_exp = exp
            self.seg_chan = chan

        if image_uri:
            protocol, path = image_uri.split("://")
            if "boss" in protocol:
                col, exp, chan = path.split('/')[:3]
                self.image_col = col
                self.image_exp = exp
                self.image_chan = chan

        # create unique ID
        self.uuid = f"{self.seg_col}&{self.seg_exp}&{self.seg_chan}&" + str(uuid.uuid4())[-6:]

        # error information
        self.error_type = error_type
        
        # single coordinate pointing to the error
        self.loc = loc
        self.ids = ids
        
        # extent of a volume that contains the error
        self.volume_extent_x = x_bounds
        self.volume_extent_y = y_bounds
        self.volume_extent_z = z_bounds
       
        # binary mask that contains the error
        self.binary_error_mask = binary_error_mask

        self.colocarpy_vol_id = None
        self.keypoint_nodes: List = None
        self.keypoint_ids: List = None

        if self.loc is None:
            if self.volume_extent_x is not None:
                self.get_centroid_from_extent()
            else:
                raise ValueError('Must provide either a location or xyz bounds for the error')

        if self.ids is None:
            self.ids = self.get_id_from_coordinate(self.loc[0], self.loc[1], self.loc[2])

        self.ng_link = self.generate_ng_link()

    def get_centroid_from_extent(self):
        x = self.volume_extent_x[0] + ((self.volume_extent_x[1] - self.volume_extent_x[0])/2)
        y = self.volume_extent_y[0] + ((self.volume_extent_y[1] - self.volume_extent_y[0]) / 2)
        z = self.volume_extent_z[0] + ((self.volume_extent_z[1] - self.volume_extent_z[0]) / 2)
        self.loc = [x, y, z]
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
        cutout_array = array(self.seg_uri)
        cutout_data = cutout_array[z - 1:z + 1, y - 1:y + 1, x - 1:x + 1]
        return cutout_data[z - (z - 1), y - (y - 1), x - (x - 1)]

    def generate_ng_link(self):
        state = {
            "layers": [
                {
                    "source": self.seg_uri,
                    "type": "segmentation",
                    "name": "seg",
                    "selectedAlpha": 0.3
                },
                {
                    "source": self.image_uri,
                    "type": "image",
                    "name": "em"
                },
            ],
            "navigation": {
                "pose": {
                    "position": {
                        "voxelCoordinates": [
                            self.loc[2],
                            self.loc[1],
                            self.loc[0]
                        ],
                    },
                },
                "zoomFactor": 8,
            },
            "showAxisLines": False,
            "layout": "xy",
        }

        return "https://neuroglancer.bossdb.io/#!" + json.dumps(state)