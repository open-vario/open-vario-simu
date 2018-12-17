
@set PROTOC_BASE_DIR=..\..\3rdparty\protoc
@set PROTOC_PATH=%PROTOC_BASE_DIR%\bin\protoc.exe

%PROTOC_PATH% --python_out=. requests.proto
%PROTOC_PATH% --python_out=. responses.proto
%PROTOC_PATH% --python_out=. notifications.proto
