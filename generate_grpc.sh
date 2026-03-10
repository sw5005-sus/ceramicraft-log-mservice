#!/bin/bash
set -e

# Target directory for gRPC python stubs
TARGET_DIR="src/ceramicraft_log_mservice/pb"

echo "Cleaning up old generated files..."
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"
touch "$TARGET_DIR/__init__.py"

echo "Generating gRPC files from proto..."
uv run python -m grpc_tools.protoc \
    -Iprotos \
    --python_out="$TARGET_DIR" \
    --pyi_out="$TARGET_DIR" \
    --grpc_python_out="$TARGET_DIR" \
    protos/audit_log.proto

echo "Fixing exact relative imports..."
if [ "$(uname)" == "Darwin" ]; then
    # macOS sed requires an empty string for the extension
    sed -i '' -e 's/import audit_log_pb2 as audit__log__pb2/from . import audit_log_pb2 as audit__log__pb2/g' "$TARGET_DIR/audit_log_pb2_grpc.py"
else
    # Linux sed
    sed -i -e 's/import audit_log_pb2 as audit__log__pb2/from . import audit_log_pb2 as audit__log__pb2/g' "$TARGET_DIR/audit_log_pb2_grpc.py"
fi

echo "Done! Stubs are updated in $TARGET_DIR."
