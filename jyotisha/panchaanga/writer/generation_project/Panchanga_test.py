import argparse
import os
import sys
import sys

from pathlib import Path # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[4]
sys.path.append(str(root))

# Additionally remove the current file's directory from sys.path
try:
    sys.path.remove(str(parent))
except ValueError: # Already removed
    pass

from jyotisha.panchaanga import spatio_temporal
from jyotisha.panchaanga.temporal import era, festival, ComputationSystem
from jyotisha.panchaanga.writer import generation_project

bengaLUru = spatio_temporal.City.get_city_from_db("sahakAra nagar, bengaLUru")
chennai = spatio_temporal.City.get_city_from_db("Chennai")
today = bengaLUru.get_timezone_obj().current_time()

parser = argparse.ArgumentParser(description='panchAnga generator.')
parser.add_argument('--year', type=int, default=today.year, nargs='?')
args = parser.parse_args()
year = args.year
# year = 2017


kauNdinyaayana_bhaaskara_gRhya_computation_system = ComputationSystem.read_from_file(filename=os.path.join(os.path.dirname(festival.__file__), "data/computation_systems", "kauNdinyaayana_bhaaskara_gRhya.toml"))
vish_bhaaskara_computation_system = ComputationSystem.read_from_file(filename=os.path.join(os.path.dirname(festival.__file__), "data/computation_systems", "vishvAsa_bhAskara.toml"))

# bengaLUru
# Used by https://t.me/bengaluru_panchaanga
#generation_project.dump_detailed(year=year, city=bengaLUru, year_type=era.ERA_GREGORIAN, computation_system=kauNdinyaayana_bhaaskara_gRhya_computation_system)
#generation_project.dump_detailed(year=year, city=bengaLUru, year_type=era.ERA_GREGORIAN, computation_system=vish_bhaaskara_computation_system)
generation_project.dump_detailed(year=year, city=chennai, year_type=era.ERA_GREGORIAN)


# chennai
# Requested for bAlAsubrahmaNya's father. And kArtik potentially.
# chennai = spatio_temporal.City.get_city_from_db("Chennai")
# generation_project.dump_detailed(year=year, city=chennai, year_type=era.ERA_GREGORIAN)
