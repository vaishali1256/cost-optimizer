terraform {
  required_providers {
    azurerm = {
        source = "hashicorp/azurerm"
        version = "~>4.70.0"
    }
  }
  backend "azurerm" {
      resource_group_name  = "vaishali-tfstate"
      storage_account_name = "vaishalitf25135"
      container_name       = "tfstate"
      key                  = "dev.terraform.tfstate"
  }
  required_version = ">=1.15.2"
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}