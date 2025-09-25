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
                             type='lanelet',
                            #  left_bound_id=lanelet.leftBound.id,
                            #  right_bound_id=lanelet.rightBound.id,
                             lane_id=lanelet.id))
    for elm in lane_map.areaLayer:
        outer_bounds = list(elm.outerBound())
        if not outer_bounds:
            print(f"Area {elm.id} has no outer bounds")
            return

        outer_bound = outer_bounds[0]
        x = []
        y = []
        z = []
        for p in outer_bound:
            x.append(p.x)
            y.append(p.y)
            z.append(p.z)
        lane_polygon_list.append(
            LaneletPolygon3d(x=x,
                             y=y,
                             z=z,
                             type='area',
                             lane_id=elm.id))

    for elm in lane_map.lineStringLayer:
        x = []
        y = []
        z = []
        for p in elm:
            x.append(p.x)
            y.append(p.y)
            z.append(p.z)
        lane_polygon_list.append(
            LaneletPolygon3d(x=x,
                             y=y,
                             z=z,
                             type='linestring',
                             lane_id=elm.id))
    for elm in lane_map.regulatoryElementLayer:
        position = None
        x = []
        y = []
        z = []
        type_str =''
        if hasattr(elm, "trafficLights") and callable(getattr(elm, "trafficLights")):
            type_str = 'traffic_light'
            tl_refs = elm.trafficLights()
            if tl_refs and len(tl_refs) > 0:
                tl_ref = tl_refs[0]
                if len(tl_ref) > 0:
                    pt = tl_ref[0]
                    x.append(pt.x)
                    y.append(pt.y)
                    z.append(pt.z)

        elif hasattr(elm, "refLines") and callable(getattr(elm, "refLines")):
            type_str = 'refLines'
            ref_lines = elm.refLines()
            if ref_lines and len(ref_lines) > 0:
                ref_line = ref_lines[0]
                if hasattr(ref_line, "centerline"):
                    pt = ref_line.centerline[0]
                    x.append(pt.x)
                    y.append(pt.y)
                    z.append(pt.z)
                elif len(ref_line) > 0:
                    pt = ref_line[0]
                    x.append(pt.x)
                    y.append(pt.y)
                    z.append(pt.z)
        elif hasattr(elm, "stopLine") and callable(getattr(elm, "stopLine")):
            type_str = 'stop_line'
            stop_line = elm.stopLine()
            if stop_line:
                if len(stop_line) > 0:
                    pt = stop_line[0]
                    x.append(pt.x)
                    y.append(pt.y)
                    z.append(pt.z)

        lane_polygon_list.append(
            LaneletPolygon3d(x=x, y=y, z=z, type=type_str,
                                lane_id=elm.id))

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
