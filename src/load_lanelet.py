import argparse
import json
import os
import typing

import lanelet2
from autoware_lanelet2_extension_python.projection import MGRSProjector
from lanelet2.io import Origin
from models.lenelet import LaneletPolygon3d
from models.base import ListTemplate

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ORIGIN: Origin = lanelet2.io.Origin(35.681236, 139.767125)  # 東京駅付近

def get_lane_polygon(osm_file_path: str, origin: lanelet2.io.Origin = DEFAULT_ORIGIN) -> ListTemplate[LaneletPolygon3d]:
    projector = MGRSProjector(origin)
    lane_map = lanelet2.io.load(osm_file_path, projector)

    lane_polygon_list: typing.List[LaneletPolygon3d] = []
    for lanelet in lane_map.laneletLayer:
        polygon = lanelet.polygon3d()
        x = []
        y = []
        z = []
        for p in polygon:
            x.append(p.x)
            y.append(p.y)
            z.append(p.z)
        # polygonを閉じるために始点を追加
        if len(x) > 0:
            x.append(x[0])
            y.append(y[0])
            z.append(z[0])

        lane_polygon_list.append(
            LaneletPolygon3d(x=x,
                             y=y,
                             z=z,
                             left_bound_id=lanelet.leftBound.id,
                             right_bound_id=lanelet.rightBound.id,
                             lane_id=lanelet.id))
    return ListTemplate[LaneletPolygon3d](root=lane_polygon_list)


def main(map_path: str, output_dir: str):
    lanelet_polygon_list = get_lane_polygon(map_path, DEFAULT_ORIGIN)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'lanelet.json'), 'w', encoding='utf-8') as fout:
        fout.write(lanelet_polygon_list.model_dump_json(indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='create trajectory charts from json')

    parser.add_argument('arg1', help='data source (json) dirctory path')
    parser.add_argument('-o', '--output', help='output dirctory path')
    args = parser.parse_args()

    map_path = os.path.abspath(args.arg1)
    output_dir = os.path.abspath(args.output) if args.output is not None else os.path.dirname(map_path)
    output_dir = os.path.join(output_dir, 'lanelet')

    print(json.dumps({
        'lanelet file path': map_path,
        'output path': output_dir,
    }, indent=2))

    main(map_path, output_dir)
