# 런처 환경 세팅

## 의존성 파일 설치

```commandline
$ pip install -r requirements.txt
```


## 이미지 데이터 `.py` 파일 생성

`res.qrc` 파일로부터 이미지 데이터가 포함된 `.py` 파일을 생성해야합니다.
해당 항목은 `PyQt5`가 설치된 상태에서 수행 가능합니다.

```commandline
$ pyrcc5 res.qrc -o res_rc.py
```

위 명령을 수행하면 `res_rc.py` 파일이 생성된 것을 확인할 수 있습니다.


## `config.ini` 파일 업데이트

추가 예정
