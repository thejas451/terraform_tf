


# Configure the Azure provider
provider "azurerm" {
  features {}
  subscription_id = "515c0d20-04b3-4037-9c54-b00fa69942ed"
}
 
# Create a resource group
resource "azurerm_resource_group" "rg" {
  name     = "thejGP"
  location = "East US"
}
 
# Create a storage account (must be globally unique)
resource "azurerm_storage_account" "storage" {
  name                     = "blobstoretheju"  # ⚠️ change to a unique name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "RAGRS"
}
 
# Create a blob container inside the storage account
resource "azurerm_storage_container" "container" {
  name                  = "thejascon"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}
 
# Output details
output "resource_group" {
  value = azurerm_resource_group.rg.name
}
 
output "storage_account" {
  value = azurerm_storage_account.storage.name
}
 
output "container_name" {
  value = azurerm_storage_container.container.name
}
