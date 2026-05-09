################################################################################
# OpenSearch Serverless — Encryption Policies
################################################################################
resource "aws_opensearchserverless_security_policy" "encryption_public" {
  name        = "${var.project}-${var.environment}-enc-public"
  type        = "encryption"
  description = "Encryption policy for public clinical content collection"

  policy = jsonencode({
    Rules = [{
      Resource     = ["collection/${var.project}-${var.environment}-public"]
      ResourceType = "collection"
    }]
    AWSOwnedKey = false
    KmsARN      = var.public_kms_key_arn
  })
}

resource "aws_opensearchserverless_security_policy" "encryption_phi" {
  name        = "${var.project}-${var.environment}-enc-phi"
  type        = "encryption"
  description = "Encryption policy for PHI clinical trials collection"

  policy = jsonencode({
    Rules = [{
      Resource     = ["collection/${var.project}-${var.environment}-phi"]
      ResourceType = "collection"
    }]
    AWSOwnedKey = false
    KmsARN      = var.phi_kms_key_arn
  })
}

################################################################################
# OpenSearch Serverless — Network Policies (VPC-only)
################################################################################
resource "aws_opensearchserverless_security_policy" "network_public" {
  name        = "${var.project}-${var.environment}-net-public"
  type        = "network"
  description = "Network policy for public collection — VPC-only access"

  policy = jsonencode([{
    Rules = [
      {
        Resource     = ["collection/${var.project}-${var.environment}-public"]
        ResourceType = "collection"
      },
      {
        Resource     = ["dashboards/${var.project}-${var.environment}-public"]
        ResourceType = "dashboard"
      }
    ]
    AllowFromPublic = false
  }])
}

resource "aws_opensearchserverless_security_policy" "network_phi" {
  name        = "${var.project}-${var.environment}-net-phi"
  type        = "network"
  description = "Network policy for PHI collection — strictly VPC-only"

  policy = jsonencode([{
    Rules = [
      {
        Resource     = ["collection/${var.project}-${var.environment}-phi"]
        ResourceType = "collection"
      }
    ]
    AllowFromPublic = false
  }])
}

################################################################################
# OpenSearch Serverless — Collections
################################################################################
resource "aws_opensearchserverless_collection" "public" {
  name             = "${var.project}-${var.environment}-public"
  type             = "VECTORSEARCH"
  description      = "Public clinical content: WHO protocols, treatment guidelines, PubMed"
  standby_replicas = var.environment == "prod" ? "ENABLED" : "DISABLED"

  depends_on = [
    aws_opensearchserverless_security_policy.encryption_public,
    aws_opensearchserverless_security_policy.network_public
  ]

  tags = merge(var.tags, {
    Name               = "${var.project}-${var.environment}-opensearch-public"
    DataClassification = "Internal"
  })
}

resource "aws_opensearchserverless_collection" "phi" {
  name             = "${var.project}-${var.environment}-phi"
  type             = "VECTORSEARCH"
  description      = "PHI clinical trial reports — restricted access"
  standby_replicas = var.environment == "prod" ? "ENABLED" : "DISABLED"

  depends_on = [
    aws_opensearchserverless_security_policy.encryption_phi,
    aws_opensearchserverless_security_policy.network_phi
  ]

  tags = merge(var.tags, {
    Name               = "${var.project}-${var.environment}-opensearch-phi"
    DataClassification = "PHI"
    Compliance         = "HIPAA"
  })
}

################################################################################
# OpenSearch Serverless — Data Access Policies
################################################################################
resource "aws_opensearchserverless_access_policy" "public_access" {
  name        = "${var.project}-${var.environment}-access-public"
  type        = "data"
  description = "Data access for public collection — Lambda, ECS, pipeline"

  policy = jsonencode([{
    Rules = [
      {
        Resource     = ["collection/${var.project}-${var.environment}-public"]
        Permission   = ["aoss:CreateCollectionItems", "aoss:DeleteCollectionItems", "aoss:UpdateCollectionItems", "aoss:DescribeCollectionItems"]
        ResourceType = "collection"
      },
      {
        Resource     = ["index/${var.project}-${var.environment}-public/*"]
        Permission   = ["aoss:CreateIndex", "aoss:DeleteIndex", "aoss:UpdateIndex", "aoss:DescribeIndex", "aoss:ReadDocument", "aoss:WriteDocument"]
        ResourceType = "index"
      }
    ]
    Principal = [
      var.lambda_pipeline_role_arn,
      var.ecs_task_role_arn
    ]
  }])
}

resource "aws_opensearchserverless_access_policy" "phi_access" {
  name        = "${var.project}-${var.environment}-access-phi"
  type        = "data"
  description = "Data access for PHI collection — restricted to phi-researcher and pipeline roles"

  policy = jsonencode([{
    Rules = [
      {
        Resource     = ["collection/${var.project}-${var.environment}-phi"]
        Permission   = ["aoss:CreateCollectionItems", "aoss:DeleteCollectionItems", "aoss:UpdateCollectionItems", "aoss:DescribeCollectionItems"]
        ResourceType = "collection"
      },
      {
        Resource     = ["index/${var.project}-${var.environment}-phi/*"]
        Permission   = ["aoss:CreateIndex", "aoss:DeleteIndex", "aoss:UpdateIndex", "aoss:DescribeIndex", "aoss:ReadDocument", "aoss:WriteDocument"]
        ResourceType = "index"
      }
    ]
    Principal = [
      var.lambda_pipeline_role_arn,
      var.phi_researcher_role_arn
    ]
  }])
}
