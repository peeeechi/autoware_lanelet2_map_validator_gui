import subprocess
import os
from models.validation_results import ValidationResults

base_dir = os.path.dirname(os.path.abspath(__file__))

def run_validator(map_path: str, output_path: str) -> ValidationResults:

  if not os.path.exists(output_path):
    os.makedirs(output_path, exist_ok=True)

  output_json_path = os.path.join(output_path, 'lanelet2_validation_results.json')
  # シェルスクリプトを直接実行
  try:
      command = f"/home/autoware/autoware/release_package/autoware_lanelet2_map_validator \
        -p mgrs \
        -l ja \
        -m {map_path} \
        -i /home/autoware/autoware/release_package/map_requirements/pilot-auto/cargo_transport-v2025_6_0.json \
        -o {output_path}"
      print("Executing command:", command)
      _ = subprocess.run(command, capture_output=True, text=True, check=True, shell=True, executable="/bin/bash")
      with open(output_json_path, 'r', encoding='utf-8') as fin:
        json_str = fin.read()
        return ValidationResults.model_validate_json(json_str)
  except subprocess.CalledProcessError as e:
      print("STDOUT:", e.stdout)
      print("STDERR:", e.stderr)
      raise e
  finally:
    if os.path.exists(output_path):
      print('delete output dir !!!!')


if __name__ == "__main__":
  pass