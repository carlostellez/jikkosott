"""
Distributed System Architecture Design for Food Delivery Startup

This module provides a comprehensive design for a scalable, reliable, and maintainable
distributed system architecture to replace a monolithic food delivery application.

Problem Statement:
A local food delivery startup is experiencing rapid growth and needs to redesign
their backend system to improve scalability, reliability, and maintainability.
The current system is a monolithic application with limited performance.

Design Goals:
1. Scalability: Handle growing user base and order volume
2. Reliability: Ensure high availability and fault tolerance
3. Maintainability: Enable independent development and deployment
4. Performance: Reduce latency and improve throughput
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class ServiceType(Enum):
    """Types of services in the microservice architecture."""
    API_GATEWAY = "api_gateway"
    USER_SERVICE = "user_service"
    RESTAURANT_SERVICE = "restaurant_service"
    ORDER_SERVICE = "order_service"
    PAYMENT_SERVICE = "payment_service"
    DELIVERY_SERVICE = "delivery_service"
    NOTIFICATION_SERVICE = "notification_service"
    RECOMMENDATION_SERVICE = "recommendation_service"


class DatabaseType(Enum):
    """Types of databases used in the system."""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"
    CASSANDRA = "cassandra"


class MessageQueueType(Enum):
    """Types of message queues for async communication."""
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"
    AWS_SQS = "aws_sqs"


@dataclass
class Service:
    """
    Represents a microservice in the distributed architecture.
    
    Attributes:
        name: Service name
        service_type: Type of service
        description: Service description
        database: Primary database type
        cache: Cache technology used
        apis: List of API endpoints
        dependencies: Other services this service depends on
        scaling_strategy: How the service scales
    """
    name: str
    service_type: ServiceType
    description: str
    database: Optional[DatabaseType]
    cache: Optional[str]
    apis: List[str]
    dependencies: List[str]
    scaling_strategy: str


@dataclass
class DistributedArchitecture:
    """
    Complete distributed architecture design for food delivery platform.
    """
    
    def __init__(self):
        """Initialize the distributed architecture design."""
        self.services = self._define_services()
        self.databases = self._define_databases()
        self.message_queues = self._define_message_queues()
        self.caching_strategy = self._define_caching_strategy()
        self.api_design = self._define_api_design()
        self.deployment_strategy = self._define_deployment_strategy()
    
    def _define_services(self) -> List[Service]:
        """
        Define all microservices in the architecture.
        
        Returns:
            List of Service objects representing the microservice architecture
        """
        return [
            Service(
                name="API Gateway",
                service_type=ServiceType.API_GATEWAY,
                description="Single entry point for all client requests, handles routing, authentication, rate limiting",
                database=None,
                cache="Redis",
                apis=["Authentication", "Rate Limiting", "Request Routing", "Response Aggregation"],
                dependencies=[],
                scaling_strategy="Horizontal with load balancer"
            ),
            
            Service(
                name="User Service",
                service_type=ServiceType.USER_SERVICE,
                description="Manages user accounts, profiles, authentication, and authorization",
                database=DatabaseType.POSTGRESQL,
                cache="Redis",
                apis=["/users", "/auth/login", "/auth/register", "/users/{id}/profile"],
                dependencies=["Notification Service"],
                scaling_strategy="Horizontal with read replicas"
            ),
            
            Service(
                name="Restaurant Service",
                service_type=ServiceType.RESTAURANT_SERVICE,
                description="Manages restaurant information, menus, availability, and business hours",
                database=DatabaseType.MONGODB,
                cache="Redis",
                apis=["/restaurants", "/restaurants/{id}/menu", "/restaurants/{id}/availability"],
                dependencies=["Recommendation Service"],
                scaling_strategy="Horizontal with geographic sharding"
            ),
            
            Service(
                name="Order Service",
                service_type=ServiceType.ORDER_SERVICE,
                description="Handles order creation, management, status tracking, and order history",
                database=DatabaseType.POSTGRESQL,
                cache="Redis",
                apis=["/orders", "/orders/{id}", "/orders/{id}/status", "/orders/history"],
                dependencies=["User Service", "Restaurant Service", "Payment Service", "Delivery Service"],
                scaling_strategy="Horizontal with order ID sharding"
            ),
            
            Service(
                name="Payment Service",
                service_type=ServiceType.PAYMENT_SERVICE,
                description="Processes payments, handles refunds, manages payment methods",
                database=DatabaseType.POSTGRESQL,
                cache="Redis",
                apis=["/payments", "/payments/{id}/refund", "/payment-methods"],
                dependencies=["User Service"],
                scaling_strategy="Vertical with redundancy (security critical)"
            ),
            
            Service(
                name="Delivery Service",
                service_type=ServiceType.DELIVERY_SERVICE,
                description="Manages delivery tracking, driver assignment, route optimization",
                database=DatabaseType.MONGODB,
                cache="Redis",
                apis=["/deliveries", "/deliveries/{id}/tracking", "/drivers/{id}/location"],
                dependencies=["Order Service", "Notification Service"],
                scaling_strategy="Horizontal with geographic clustering"
            ),
            
            Service(
                name="Notification Service",
                service_type=ServiceType.NOTIFICATION_SERVICE,
                description="Sends push notifications, emails, SMS for order updates and promotions",
                database=DatabaseType.CASSANDRA,
                cache="Redis",
                apis=["/notifications/send", "/notifications/templates", "/notifications/preferences"],
                dependencies=[],
                scaling_strategy="Horizontal with message queue buffering"
            ),
            
            Service(
                name="Recommendation Service",
                service_type=ServiceType.RECOMMENDATION_SERVICE,
                description="Provides personalized restaurant and dish recommendations using ML",
                database=DatabaseType.ELASTICSEARCH,
                cache="Redis",
                apis=["/recommendations/restaurants", "/recommendations/dishes", "/recommendations/trending"],
                dependencies=["User Service", "Order Service"],
                scaling_strategy="Horizontal with ML model distribution"
            )
        ]
    
    def _define_databases(self) -> Dict[str, Dict]:
        """
        Define database design and distribution strategy.
        
        Returns:
            Dictionary describing database architecture
        """
        return {
            "primary_databases": {
                "user_db": {
                    "type": "PostgreSQL",
                    "purpose": "User accounts, authentication, profiles",
                    "schema": "Relational with ACID compliance",
                    "scaling": "Master-slave replication with read replicas",
                    "backup": "Daily automated backups with point-in-time recovery"
                },
                "order_db": {
                    "type": "PostgreSQL", 
                    "purpose": "Orders, payments, transactions",
                    "schema": "Relational with strong consistency",
                    "scaling": "Horizontal sharding by order_id",
                    "backup": "Real-time replication with automated failover"
                },
                "restaurant_db": {
                    "type": "MongoDB",
                    "purpose": "Restaurant data, menus, availability",
                    "schema": "Document store for flexible menu structures",
                    "scaling": "Replica sets with geographic distribution",
                    "backup": "Continuous backup with geographic redundancy"
                },
                "delivery_db": {
                    "type": "MongoDB",
                    "purpose": "Delivery tracking, driver locations, routes",
                    "schema": "Document store for geospatial data",
                    "scaling": "Sharded clusters by geographic region",
                    "backup": "Regular snapshots with point-in-time recovery"
                }
            },
            
            "analytics_databases": {
                "search_index": {
                    "type": "Elasticsearch",
                    "purpose": "Restaurant search, recommendation engine",
                    "schema": "Inverted index with full-text search",
                    "scaling": "Distributed clusters with auto-sharding"
                },
                "notification_store": {
                    "type": "Cassandra",
                    "purpose": "Notification logs, user preferences",
                    "schema": "Wide-column store for high write volume",
                    "scaling": "Multi-datacenter replication"
                },
                "analytics_warehouse": {
                    "type": "Apache Spark + Parquet",
                    "purpose": "Business intelligence, reporting",
                    "schema": "Columnar storage for analytical queries",
                    "scaling": "Distributed processing clusters"
                }
            },
            
            "database_patterns": {
                "cqrs": "Command Query Responsibility Segregation for order service",
                "event_sourcing": "For order state changes and audit trail",
                "data_lake": "Raw data storage for machine learning and analytics",
                "polyglot_persistence": "Different databases for different data models"
            }
        }
    
    def _define_message_queues(self) -> Dict[str, Dict]:
        """
        Define message queue architecture for async communication.
        
        Returns:
            Dictionary describing message queue design
        """
        return {
            "primary_queue": {
                "technology": "Apache Kafka",
                "purpose": "High-throughput event streaming",
                "topics": [
                    "order.created",
                    "order.updated", 
                    "payment.processed",
                    "delivery.assigned",
                    "user.registered"
                ],
                "partitioning": "By entity ID for ordering guarantees",
                "retention": "7 days with compression",
                "replication": "3 replicas across availability zones"
            },
            
            "secondary_queues": {
                "notification_queue": {
                    "technology": "RabbitMQ",
                    "purpose": "Reliable notification delivery",
                    "features": ["Dead letter queues", "Message persistence", "Priority queuing"]
                },
                "batch_processing": {
                    "technology": "AWS SQS",
                    "purpose": "Batch jobs and analytics processing",
                    "features": ["Visibility timeout", "Long polling", "FIFO queues"]
                }
            },
            
            "event_patterns": {
                "event_sourcing": "Store all state changes as events",
                "saga_pattern": "Manage distributed transactions",
                "cqrs": "Separate command and query models",
                "event_driven_architecture": "Loose coupling between services"
            }
        }
    
    def _define_caching_strategy(self) -> Dict[str, Dict]:
        """
        Define comprehensive caching strategy.
        
        Returns:
            Dictionary describing caching architecture
        """
        return {
            "cache_layers": {
                "cdn": {
                    "technology": "CloudFlare / AWS CloudFront",
                    "purpose": "Static content delivery (images, CSS, JS)",
                    "ttl": "24 hours",
                    "geographic_distribution": "Global edge locations"
                },
                
                "api_gateway_cache": {
                    "technology": "Redis Cluster",
                    "purpose": "API response caching",
                    "ttl": "5-60 minutes depending on endpoint",
                    "invalidation": "Event-driven cache invalidation"
                },
                
                "application_cache": {
                    "technology": "Redis with Redis Sentinel",
                    "purpose": "Database query results, session data",
                    "patterns": ["Cache-aside", "Write-through", "Write-behind"],
                    "high_availability": "Master-slave with automatic failover"
                },
                
                "database_cache": {
                    "technology": "Database-specific (PostgreSQL shared_buffers, MongoDB WiredTiger)",
                    "purpose": "Query result caching at database level",
                    "optimization": "Query plan caching and index optimization"
                }
            },
            
            "cache_patterns": {
                "cache_aside": "Application manages cache explicitly",
                "write_through": "Write to cache and database simultaneously",
                "write_behind": "Write to cache immediately, database asynchronously",
                "refresh_ahead": "Proactively refresh cache before expiration"
            },
            
            "cache_invalidation": {
                "event_based": "Invalidate cache on data change events",
                "ttl_based": "Time-based expiration for different data types",
                "tag_based": "Group related cache entries for bulk invalidation",
                "version_based": "Version tags for cache consistency"
            }
        }
    
    def _define_api_design(self) -> Dict[str, Dict]:
        """
        Define API design patterns and standards.
        
        Returns:
            Dictionary describing API architecture
        """
        return {
            "api_standards": {
                "rest_principles": "RESTful design with proper HTTP methods",
                "versioning": "URL versioning (/api/v1/) with backward compatibility",
                "documentation": "OpenAPI 3.0 specification with Swagger UI",
                "authentication": "JWT tokens with refresh token rotation",
                "authorization": "Role-based access control (RBAC)"
            },
            
            "api_gateway_features": {
                "rate_limiting": "Token bucket algorithm per user/IP",
                "request_validation": "JSON schema validation",
                "response_transformation": "Format standardization",
                "circuit_breaker": "Fail-fast pattern for downstream services",
                "load_balancing": "Round-robin with health checks"
            },
            
            "error_handling": {
                "standard_errors": "RFC 7807 Problem Details format",
                "error_codes": "Consistent error code taxonomy",
                "logging": "Structured logging with correlation IDs",
                "monitoring": "Error rate and latency monitoring"
            },
            
            "security": {
                "input_validation": "Strict input sanitization",
                "sql_injection_prevention": "Parameterized queries only",
                "xss_protection": "Content Security Policy headers",
                "cors_policy": "Restrictive CORS configuration",
                "encryption": "TLS 1.3 for all communications"
            }
        }
    
    def _define_deployment_strategy(self) -> Dict[str, Dict]:
        """
        Define deployment and infrastructure strategy.
        
        Returns:
            Dictionary describing deployment architecture
        """
        return {
            "containerization": {
                "technology": "Docker containers with multi-stage builds",
                "orchestration": "Kubernetes with Helm charts",
                "service_mesh": "Istio for traffic management and security",
                "image_registry": "Private Docker registry with vulnerability scanning"
            },
            
            "cloud_infrastructure": {
                "provider": "Multi-cloud (AWS primary, Google Cloud backup)",
                "regions": "Multiple availability zones for high availability",
                "auto_scaling": "Horizontal Pod Autoscaler based on CPU/memory/custom metrics",
                "infrastructure_as_code": "Terraform for reproducible infrastructure"
            },
            
            "deployment_patterns": {
                "blue_green": "Zero-downtime deployments for critical services",
                "canary": "Gradual rollout with traffic splitting",
                "rolling_update": "Default strategy for stateless services",
                "feature_flags": "Runtime feature toggling with LaunchDarkly"
            },
            
            "monitoring_and_observability": {
                "metrics": "Prometheus with Grafana dashboards",
                "logging": "ELK stack (Elasticsearch, Logstash, Kibana)",
                "tracing": "Jaeger for distributed tracing",
                "alerting": "PagerDuty integration for critical alerts",
                "health_checks": "Kubernetes liveness and readiness probes"
            },
            
            "disaster_recovery": {
                "backup_strategy": "Automated cross-region backups",
                "rto": "Recovery Time Objective: 15 minutes",
                "rpo": "Recovery Point Objective: 5 minutes",
                "failover": "Automated failover with DNS switching",
                "testing": "Monthly disaster recovery drills"
            }
        }
    
    def get_architecture_summary(self) -> str:
        """
        Get a comprehensive summary of the distributed architecture.
        
        Returns:
            Formatted string with architecture overview
        """
        summary = f"""
DISTRIBUTED FOOD DELIVERY ARCHITECTURE SUMMARY
{'='*60}

MICROSERVICES ARCHITECTURE:
{len(self.services)} core services with clear separation of concerns:
"""
        
        for service in self.services:
            summary += f"  • {service.name}: {service.description}\\n"
        
        summary += f"""
DATABASE DESIGN:
• Polyglot persistence with appropriate database selection
• PostgreSQL for transactional data (users, orders, payments)
• MongoDB for document-based data (restaurants, deliveries)
• Elasticsearch for search and recommendations
• Redis for caching and session management
• Cassandra for high-volume notification logs

MESSAGE QUEUES:
• Kafka for high-throughput event streaming
• RabbitMQ for reliable notification delivery
• Event-driven architecture with CQRS pattern

CACHING STRATEGY:
• Multi-layer caching (CDN, API Gateway, Application, Database)
• Redis clustering with automatic failover
• Event-based cache invalidation

DEPLOYMENT & INFRASTRUCTURE:
• Kubernetes orchestration with Docker containers
• Multi-cloud deployment for redundancy
• Auto-scaling based on demand
• Blue-green and canary deployment strategies

SCALABILITY FEATURES:
• Horizontal scaling for all services
• Database sharding and replication
• Geographic distribution for global performance
• Load balancing with health checks

RELIABILITY FEATURES:
• Circuit breaker pattern for fault tolerance
• Automated failover and disaster recovery
• Multi-region backup and replication
• Comprehensive monitoring and alerting

SECURITY MEASURES:
• JWT authentication with RBAC authorization
• TLS encryption for all communications
• Input validation and SQL injection prevention
• Network security with service mesh
"""
        return summary
    
    def get_migration_strategy(self) -> str:
        """
        Get strategy for migrating from monolith to microservices.
        
        Returns:
            Formatted string with migration plan
        """
        return """
MONOLITH TO MICROSERVICES MIGRATION STRATEGY
{'='*60}

PHASE 1: PREPARATION (Weeks 1-4)
• Set up development and staging environments
• Implement monitoring and logging infrastructure
• Create CI/CD pipelines for microservices
• Establish API Gateway as single entry point
• Begin database separation planning

PHASE 2: DATA LAYER MIGRATION (Weeks 5-8)
• Extract user management to separate database
• Implement database per service pattern
• Set up cross-service communication via events
• Migrate to message queue architecture
• Implement caching layer

PHASE 3: SERVICE EXTRACTION (Weeks 9-16)
• Extract User Service first (least dependencies)
• Migrate Restaurant Service with menu management
• Extract Payment Service with PCI compliance
• Implement Order Service with state management
• Deploy Notification Service for async communication

PHASE 4: ADVANCED SERVICES (Weeks 17-20)
• Implement Delivery Service with real-time tracking
• Deploy Recommendation Service with ML capabilities
• Optimize performance and scaling
• Complete monitoring and alerting setup

PHASE 5: OPTIMIZATION (Weeks 21-24)
• Performance tuning and optimization
• Security hardening and penetration testing
• Load testing and capacity planning
• Documentation and team training
• Gradual traffic migration with canary deployments

MIGRATION PRINCIPLES:
• Strangler Fig pattern for gradual replacement
• Database-per-service with eventual consistency
• Event-driven communication for loose coupling
• Backward compatibility during transition
• Continuous monitoring and rollback capabilities

RISK MITIGATION:
• Feature flags for safe rollbacks
• Parallel systems during transition
• Comprehensive testing at each phase
• Team training and knowledge transfer
• 24/7 monitoring during critical migrations
"""


def generate_architecture_diagram() -> str:
    """
    Generate a text-based architecture diagram.
    
    Returns:
        ASCII diagram of the distributed architecture
    """
    return """
DISTRIBUTED FOOD DELIVERY ARCHITECTURE DIAGRAM
{'='*60}

┌─────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATIONS                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   Mobile    │ │     Web     │ │      Partner APIs       │ │
│  │     App     │ │   Browser   │ │   (Restaurants/Drivers) │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY                           │
│            (Authentication, Rate Limiting, Routing)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MICROSERVICES LAYER                     │
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │    User     │ │ Restaurant  │ │         Order           │ │
│ │   Service   │ │   Service   │ │        Service          │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │   Payment   │ │  Delivery   │ │     Notification        │ │
│ │   Service   │ │   Service   │ │       Service           │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │              Recommendation Service                     │ │
│ │                 (ML/AI Engine)                          │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    MESSAGE QUEUES                          │
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │    Kafka    │ │  RabbitMQ   │ │        AWS SQS          │ │
│ │ (Events)    │ │(Notifications)│ │   (Batch Processing)    │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                            │
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │ PostgreSQL  │ │   MongoDB   │ │        Redis            │ │
│ │(Users/Orders)│ │(Restaurants)│ │       (Cache)           │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │Elasticsearch│ │  Cassandra  │ │      Data Lake          │ │
│ │  (Search)   │ │(Notifications)│ │     (Analytics)         │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

DEPLOYMENT INFRASTRUCTURE:
┌─────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                      │
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │   Pod 1     │ │   Pod 2     │ │        Pod N            │ │
│ │ (Service A) │ │ (Service B) │ │     (Service X)         │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │              Service Mesh (Istio)                      │ │
│ │        (Traffic Management & Security)                 │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

MONITORING & OBSERVABILITY:
┌─────────────────────────────────────────────────────────────┐
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │ Prometheus  │ │   Grafana   │ │        Jaeger           │ │
│ │ (Metrics)   │ │(Dashboards) │ │      (Tracing)          │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    ELK Stack                           │ │
│ │         (Elasticsearch, Logstash, Kibana)              │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
"""


def main():
    """
    Main function to demonstrate the distributed architecture design.
    """
    print("DISTRIBUTED FOOD DELIVERY SYSTEM ARCHITECTURE")
    print("=" * 60)
    
    # Create architecture instance
    architecture = DistributedArchitecture()
    
    # Display architecture summary
    print(architecture.get_architecture_summary())
    
    # Display architecture diagram
    print(generate_architecture_diagram())
    
    # Display migration strategy
    print(architecture.get_migration_strategy())
    
    # Additional considerations
    print(f"""
ADDITIONAL CONSIDERATIONS
{'='*60}

BUSINESS CONTINUITY:
• 99.9% uptime SLA with financial penalties
• Disaster recovery plan with RTO < 15 minutes
• Multi-region deployment for geographic redundancy
• Automated backup and restore procedures

COMPLIANCE & SECURITY:
• PCI DSS compliance for payment processing
• GDPR compliance for user data protection
• SOC 2 Type II certification for security controls
• Regular security audits and penetration testing

PERFORMANCE OPTIMIZATION:
• Sub-second API response times
• Real-time order tracking and notifications
• Efficient search with sub-100ms latency
• Geographic content delivery optimization

COST OPTIMIZATION:
• Auto-scaling to minimize infrastructure costs
• Reserved instances for predictable workloads
• Spot instances for batch processing
• Resource utilization monitoring and optimization

TEAM ORGANIZATION:
• Service ownership model with dedicated teams
• DevOps culture with shared responsibility
• On-call rotation for critical services
• Continuous learning and knowledge sharing

TECHNOLOGY EVOLUTION:
• Regular technology stack evaluation
• Gradual migration to cloud-native solutions
• Adoption of emerging technologies (GraphQL, gRPC)
• Investment in machine learning and AI capabilities
""")


if __name__ == "__main__":
    main()
