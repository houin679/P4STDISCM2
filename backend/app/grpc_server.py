"""gRPC Server Implementation"""
import grpc
from concurrent import futures
from .grpc_services import (
    grade_service_pb2_grpc,
    course_service_pb2_grpc,
    user_service_pb2_grpc,
)
from .grpc_services.grade_servicer import GradeServicer
from .grpc_services.course_servicer import CourseServicer
from .grpc_services.user_servicer import UserServicer
import logging
import os

logger = logging.getLogger(__name__)

# Set gRPC environment variables for Windows compatibility
os.environ['GRPC_DNS_RESOLVER'] = 'native'


def start_grpc_server(port: int = 50051):
    """Start the gRPC server on the specified port"""
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        # Register servicers
        grade_service_pb2_grpc.add_GradeServiceServicer_to_server(
            GradeServicer(), server
        )
        course_service_pb2_grpc.add_CourseServiceServicer_to_server(
            CourseServicer(), server
        )
        user_service_pb2_grpc.add_UserServiceServicer_to_server(
            UserServicer(), server
        )
        
        # Bind to port (use localhost for IPv4/IPv6 compatibility)
        server.add_insecure_port(f"0.0.0.0:{port}")
        server.start()
        logger.info(f"gRPC server started on port {port}")
        print(f"✅ gRPC server started on 0.0.0.0:{port}")
        return server
    except Exception as e:
        logger.error(f"Failed to start gRPC server: {e}")
        print(f"❌ Failed to start gRPC server: {e}")
        raise


def stop_grpc_server(server):
    """Stop the gRPC server"""
    try:
        server.stop(0)
        logger.info("gRPC server stopped")
    except Exception as e:
        logger.error(f"Error stopping gRPC server: {e}")
