// Minimal sample used by the infra example pipeline.
targetScope = 'resourceGroup'

@description('Short environment name, for example dev.')
param environmentName string

@description('Azure region.')
param location string = resourceGroup().location

@description('Storage SKU.')
@allowed([
  'Standard_LRS'
  'Standard_GRS'
])
param skuName string = 'Standard_LRS'

var storageName = take('stcontoso${environmentName}${uniqueString(resourceGroup().id)}', 24)

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  sku: {
    name: skuName
  }
  kind: 'StorageV2'
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}

output storageAccountName string = storage.name
