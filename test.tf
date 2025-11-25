provider "azurerm" {
  features {}
}

# Existing Resource Group
variable "resource_group_name" {
  description = "AzureGRP"
  type        = string
}

# Fixed prefix
variable "storage_prefix" {
  description = "Prefix for Storage Account"
  type        = string
  default     = "thejasblob"
}

variable "container_prefix" {
  description = "Prefix for Container"
  type        = string
  default     = "thejcon"
}

# Random suffix for uniqueness
resource "random_string" "suffix" {
  length  = 6
  upper   = false
  special = false
}

# Fetch existing resource group
data "azurerm_resource_group" "existing" {
  name = var.resource_group_name
}

# Create Storage Account with prefix + random suffix
resource "azurerm_storage_account" "main" {
  name                     = "${var.storage_prefix}${random_string.suffix.result}" # e.g., thejasblobabc123
  resource_group_name      = data.azurerm_resource_group.existing.name
  location                 = data.azurerm_resource_group.existing.location
  account_tier             = "Standard"
  account_replication_type = "RAGRS"
  kind                     = "StorageV2"
}

# Create Container with prefix + random suffix
resource "azurerm_storage_container" "main" {
  name                  = "${var.container_prefix}${random_string.suffix.result}" # e.g., thejconabc123
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Output names
output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

output "container_name" {
  value = azurerm_storage_container.main.name
}
