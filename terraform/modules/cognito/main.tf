################################################################################
# Cognito User Pool — clinical staff and hospital client authentication
################################################################################
resource "aws_cognito_user_pool" "main" {
  name = "${var.project}-${var.environment}-users"

  # HIPAA: Strong password policy
  password_policy {
    minimum_length                   = var.password_minimum_length
    require_lowercase                = true
    require_uppercase                = true
    require_numbers                  = true
    require_symbols                  = true
    temporary_password_validity_days = 1
  }

  # MFA required for clinical staff
  mfa_configuration = var.mfa_configuration

  software_token_mfa_configuration {
    enabled = true
  }

  # Account recovery
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Email verification
  auto_verified_attributes = ["email"]

  # User attributes
  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true
    string_attribute_constraints {
      min_length = 1
      max_length = 254
    }
  }

  schema {
    name                = "department"
    attribute_data_type = "String"
    required            = false
    mutable             = true
    string_attribute_constraints {
      min_length = 0
      max_length = 64
    }
  }

  schema {
    name                = "hospital_client_id"
    attribute_data_type = "String"
    required            = false
    mutable             = true
    string_attribute_constraints {
      min_length = 0
      max_length = 64
    }
  }

  # Advanced security: block compromised credentials, adaptive auth
  user_pool_add_ons {
    advanced_security_mode = "ENFORCED"
  }

  # Token expiry settings
  user_attribute_update_settings {
    attributes_require_verification_before_update = ["email"]
  }

  admin_create_user_config {
    allow_admin_create_user_only = true
    invite_message_template {
      email_subject = "Nova Health Tech — Your clinical assistant account"
      email_message = "Your username is {username} and temporary password is {####}. You must reset your password and set up MFA on first login."
      sms_message   = "Hello {username}, your Nova Health Tech temp password is: {####}"
    }
  }

  # HIPAA: 7-year audit retention for user events
  deletion_protection = var.environment == "prod" ? "ACTIVE" : "INACTIVE"

  tags = var.tags
}

################################################################################
# Cognito User Groups — map to IAM roles (RBAC)
################################################################################
resource "aws_cognito_user_group" "clinical_staff" {
  name         = "clinical-staff"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Internal clinical staff — access to public protocols, no PHI index"
  precedence   = 10
}

resource "aws_cognito_user_group" "phi_researchers" {
  name         = "phi-researchers"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Clinical researchers — full access including PHI clinical trial index"
  precedence   = 5
}

resource "aws_cognito_user_group" "hospital_clients" {
  name         = "hospital-clients"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "External hospital client users — read-only access to public protocols"
  precedence   = 20
}

resource "aws_cognito_user_group" "admins" {
  name         = "admins"
  user_pool_id = aws_cognito_user_pool.main.id
  description  = "Platform administrators"
  precedence   = 1
}

################################################################################
# Cognito User Pool Domain
################################################################################
resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.project}-${var.environment}-auth"
  user_pool_id = aws_cognito_user_pool.main.id
}

################################################################################
# Cognito App Client — clinical assistant UI
################################################################################
resource "aws_cognito_user_pool_client" "clinical_app" {
  name         = "${var.project}-${var.environment}-clinical-app"
  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret                      = false
  refresh_token_validity               = 1
  access_token_validity                = 1
  id_token_validity                    = 1

  token_validity_units {
    refresh_token = "days"
    access_token  = "hours"
    id_token      = "hours"
  }

  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  allowed_oauth_flows_user_pool_client = true
  callback_urls                        = var.callback_urls
  logout_urls                          = var.logout_urls
  supported_identity_providers         = ["COGNITO"]

  # Prevent user enumeration
  prevent_user_existence_errors = "ENABLED"

  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  read_attributes  = ["email", "custom:department", "custom:hospital_client_id"]
  write_attributes = ["email", "custom:department", "custom:hospital_client_id"]
}

################################################################################
# Cognito Identity Pool — federate to IAM roles based on group
################################################################################
resource "aws_cognito_identity_pool" "main" {
  identity_pool_name               = "${var.project}-${var.environment}-identity"
  allow_unauthenticated_identities = false
  allow_classic_flow               = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.clinical_app.id
    provider_name           = aws_cognito_user_pool.main.endpoint
    server_side_token_check = true
  }

  tags = var.tags
}
