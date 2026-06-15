terraform {
  required_providers {
    petstore = {
      source  = "Speakeasy/petstore"
      version = "0.1.0"
    }
  }
}

provider "petstore" {
  # Configuration options
}