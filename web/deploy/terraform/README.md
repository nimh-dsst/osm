# Resource Deployment

## General Notes

Deployment of infrastructure resources requires [OpenTofu](https://opentofu.org/) (version >=1.8.0).

When calling modules, the relevant input variables can be found in their `variables.tf` file or sometimes their `variables_state.tf` file. This is where the parametrization takes place. In general, a module's `main.tf` file should only be modified if you would like to change what infrastructure is created. Modifying a module's `main.tf` file should seldom be necessary. 

