provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "k8s-honeypot-rg"
  location = var.location
}

# Virtual Network for AKS
resource "azurerm_virtual_network" "vnet" {
  name                = "honeypot-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# Subnet for AKS nodes, with NSG attached
resource "azurerm_subnet" "subnet" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Network Security Group for Honeypot Ports, with rules for Cowrie and Dionaea
resource "azurerm_network_security_group" "honeypot_nsg" {
  name                = "honeypot-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "AllowCowrieSSH" # Allow SSH access to Cowrie
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowDionaea" # Allow access to Dionaea
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_ranges    = ["21", "135", "445"]
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# Attach NSG to AKS Subnet, allowing traffic to honeypot ports
resource "azurerm_subnet_network_security_group_association" "subnet_nsg_attach" {
  subnet_id                 = azurerm_subnet.subnet.id
  network_security_group_id = azurerm_network_security_group.honeypot_nsg.id
}

# AKS Cluster with NSG-enabled Subnet
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "honeypot-aks"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "honeypot"

  default_node_pool {
    name                  = "default"
    node_count            = 1
    vm_size               = "Standard_B2s"
    vnet_subnet_id        = azurerm_subnet.subnet.id
    # temporary_name_for_rotation = "tempnp"
  }

  identity {
    type = "SystemAssigned"
  }

  linux_profile {
    admin_username = "azureuser"

    ssh_key {
      key_data = file("~/.ssh/id_rsa.pub") # Path to your SSH public key, adjust as needed
    }
  }

  network_profile { # This is where we define the network settings for the AKS cluster
    network_plugin     = "kubenet"
    load_balancer_sku  = "standard"
    outbound_type      = "loadBalancer"

    service_cidr       = "10.1.0.0/16"
    dns_service_ip     = "10.1.0.10"
  }

  tags = {
    environment = "honeypot"
  }
}
