# autoware_lanelet2_map_validator GUI

## Description
[autoware_lanelet2_map_validator](https://github.com/tier4/autoware_lanelet2_map_validator) の機能をより使用しやすくするGUIを提供します。  
また、Validation でErrorのあったLaneletを可視化し、修正の手助けとなる直感的な情報を提供します

## Future
- StreamLit によるWebGUIの提供
  - FileUploaderを使用して対象のlanelet2_map.osm を直感的に指定します
- エラーの詳細表示
  - エラーの内容と対応するReferenceDesignのmap-requirementsをセットで表示します
- lanelet の可視化(WIP)
  - エラーのあったlanelet をChart上で可視化します
- Docker化
  - docker compose による環境構築

## Usage

### Image build & Run Docker container
```bash
$ run.sh
```

### Access

[http://127.0.0.1:8080/](http://127.0.0.1:8080/) にアクセス