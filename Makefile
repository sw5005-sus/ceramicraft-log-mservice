.PHONY: gen

gen:
	buf generate
	perl -pi -e 's/^import (.*_pb2.*)/from . import $$1/' src/ceramicraft_log_mservice/pb/audit_log_pb2_grpc.py
	touch src/ceramicraft_log_mservice/pb/__init__.py
