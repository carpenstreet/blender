# Introduction

이 레포는 스케치업의 `.skp` 파일을 ABLER 용 `.blend` 파일로 변환할 수 있는 애드온의 레포지토리이며, private repo입니다.

# Getting Started

0. 요구 사항

> - 로컬 파이썬 버전을 `Python 3.9`로 맞춰주세요.
> - `Cython`을 사용하기 위해서는 pip로 cython을 설치해야 합니다.
>
> ```sh
> $ python --version
> $ pip install Cython
> ```

1. 위 레포 `SKP_Converter`가 포함되어 있는 ABLER 브랜치로 이동하고 서브모듈을 업데이트하면 `io_skp` 디렉터리가 생성됩니다.

```sh
$ git checkout ...
$ git submodule update --init --recursive --remote
$ cd ~/blender/release/scripts/addons_abler/io_skp
```

2. 처음 레포를 클론 했거나 Cython 코드를 업데이트하고 새로 빌드할 때는 아래와 같은 명령어를 사용합니다.

```sh
$ cd ~/blender/release/scripts/addons_abler/io_skp/pyslapi_ACON
$ python setup.py install
```

3. 다시 ABLER 브랜치 디렉터리로 돌아가서 에이블러를 빌드하고 실행합니다.

```sh
$ cd ~/blender
# macOS & Linux
$ make
# Windows
$ ./make.bat
```

4. 에이블러 메뉴에서 `Edit > Preference > Addons` 로 들어가서 ACON3D: ACON3D SketchUp Converter를 체크하여 활성화해줍니다.

![image](https://user-images.githubusercontent.com/43770096/142163273-2e215ac1-f1f9-4355-b568-c28cd6b212fe.png)

5. 에이블러 패널의 가장 아래에 Converter Tab이 생깁니다.

![image](https://user-images.githubusercontent.com/43770096/142163486-4b14a508-0871-4806-87af-3b4e13c37da8.png)

6. SKP 파일을 임포트하고 터미널에서 내 코드가 왜 잘못된건지 확인합니다 :(

7. 개발중 필요한 `.skp` 및 `.blend` 파일은 [노션 링크](https://www.notion.so/acon3d/424d760821a64a918dd72fba5aedbc6e)에서 확인해주세요.
